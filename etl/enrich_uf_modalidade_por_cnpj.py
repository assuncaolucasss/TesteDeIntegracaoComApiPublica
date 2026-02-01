#enrich_uf_modalidade_por_cnpj.py

import re
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
import ftfy

CADOP_ATIVAS_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
CADOP_CANCELADAS_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_canceladas/Relatorio_cadop_canceladas.csv"

IN_PATH = Path("data/output/consolidado_despesas_enriquecido.csv")
OUT_PATH = Path("data/output/consolidado_despesas_validado_enriquecido.csv")
AUDIT_NO_UF = Path("data/output/cnpj_sem_uf.csv")

CTRL = re.compile(r"[\x00-\x1f\x7f]")

def only_digits(x) -> str:
    return re.sub(r"\D", "", "" if x is None else str(x))

def limpar_texto(x) -> str:
    s = "" if x is None else str(x)
    s = s.replace('"', "").strip()
    s = CTRL.sub("", s)
    s = ftfy.fix_text(s)
    return s.strip()

def baixar_cadop(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(BytesIO(r.content), sep=";", encoding="latin1", dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def preparar_lookup_cnpj(df: pd.DataFrame) -> pd.DataFrame:
    required = {"CNPJ", "UF", "Modalidade", "REGISTRO_OPERADORA"}
    if not required.issubset(df.columns):
        raise ValueError(f"CADOP sem colunas esperadas. Achei: {list(df.columns)}")

    out = df.copy()
    out["CNPJ_digits"] = out["CNPJ"].apply(only_digits)
    out["UF"] = out["UF"].apply(limpar_texto)
    out["Modalidade"] = out["Modalidade"].apply(limpar_texto)
    # registro só para auditoria/validação (opcional)
    out["RegistroANS_cadop"] = out["REGISTRO_OPERADORA"].astype(str).str.replace(r"\D", "", regex=True)

    out = out[out["CNPJ_digits"].str.len() == 14]
    out = out.drop_duplicates(subset=["CNPJ_digits"], keep="first")
    return out[["CNPJ_digits", "UF", "Modalidade", "RegistroANS_cadop"]]

def main():
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Não encontrei {IN_PATH}. Rode antes o enrich_cadop (CNPJ/RazaoSocial).")

    df = pd.read_csv(IN_PATH, encoding="utf-8-sig", dtype=str, encoding_errors="strict")
    required = {"CNPJ", "RazaoSocial", "RegistroANS", "Trimestre", "Ano", "ValorDespesas"}
    if not required.issubset(df.columns):
        raise ValueError(f"Entrada sem colunas esperadas. Precisa ter {sorted(required)}. Achei: {list(df.columns)}")

    df["CNPJ_digits"] = df["CNPJ"].apply(only_digits)

    print("Baixando CADOP (ativas)...")
    lk_a = preparar_lookup_cnpj(baixar_cadop(CADOP_ATIVAS_URL))

    print("Baixando CADOP (canceladas)...")
    lk_c = preparar_lookup_cnpj(baixar_cadop(CADOP_CANCELADAS_URL))

    print("Enriquecendo UF/Modalidade por CNPJ (ativas -> fallback canceladas)...")
    tmp = df.merge(lk_a, how="left", on="CNPJ_digits", suffixes=("", "_a"))
    tmp = tmp.merge(lk_c, how="left", on="CNPJ_digits", suffixes=("", "_c"))

    # Preferir ativas; se vazio, usar canceladas
    tmp["UF_final"] = tmp["UF"].fillna("")
    tmp["UF_final"] = tmp["UF_final"].mask(tmp["UF_final"].eq(""), tmp["UF_c"].fillna(""))

    tmp["Modalidade_final"] = tmp["Modalidade"].fillna("")
    tmp["Modalidade_final"] = tmp["Modalidade_final"].mask(tmp["Modalidade_final"].eq(""), tmp["Modalidade_c"].fillna(""))

    # RegistroANS do CADOP (opcional; não sobrescreve seu RegistroANS)
    tmp["RegistroANS_cadop_final"] = tmp["RegistroANS_cadop"].fillna("")
    tmp["RegistroANS_cadop_final"] = tmp["RegistroANS_cadop_final"].mask(
        tmp["RegistroANS_cadop_final"].eq(""), tmp["RegistroANS_cadop_c"].fillna("")
    )

    out = tmp[["CNPJ", "RazaoSocial", "RegistroANS", "Trimestre", "Ano", "ValorDespesas"]].copy()
    out["UF"] = tmp["UF_final"].apply(limpar_texto)
    out["Modalidade"] = tmp["Modalidade_final"].apply(limpar_texto)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print("OK:", OUT_PATH)

    # Auditoria: CNPJ que não achou UF
    sem = out[out["UF"].fillna("").astype(str).str.strip().eq("")].copy()
    if not sem.empty:
        AUDIT_NO_UF.parent.mkdir(parents=True, exist_ok=True)
        sem[["CNPJ", "RazaoSocial", "RegistroANS"]].drop_duplicates().to_csv(AUDIT_NO_UF, index=False, encoding="utf-8-sig")
        print("OK Auditoria (sem UF):", AUDIT_NO_UF, "| qtd:", len(sem))

    print(out.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
