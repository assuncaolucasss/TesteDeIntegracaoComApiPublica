#enlrich_cadop.py

import re
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
import ftfy

CADOP_ATIVAS_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
CADOP_CANCELADAS_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_canceladas/Relatorio_cadop_canceladas.csv"

CONSOLIDADO_IN = Path("data/output/consolidado_despesas.csv")
CONSOLIDADO_OUT = Path("data/output/consolidado_despesas_enriquecido.csv")
OUTPUT_ZIP = Path("data/output/consolidado_despesas_enriquecido.zip")
SEM_MATCH_CSV = Path("data/output/registroans_sem_match.csv")

# NÃO remover \x80-\x9f (C1). Removemos só C0 e DEL para não “comer” caracteres
# quando o arquivo é lido como latin1. (Esse foi o bug principal.)
CTRL = re.compile(r"[\x00-\x1f\x7f]")


def only_digits(x) -> str:
    return re.sub(r"\D", "", "" if x is None else str(x))


def key_reg_ans(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if re.fullmatch(r"\d+\.0", s):
        s = s.split(".")[0]
    s = re.sub(r"\D", "", s)
    return s.lstrip("0")  # 000477 -> 477


def limpar_texto(x) -> str:
    s = "" if x is None else str(x)
    s = s.replace('"', "").strip()
    s = CTRL.sub("", s)
    s = ftfy.fix_text(s)  # corrige mojibake/glitches quando há informação [page:1]
    return s.strip()


def assert_no_replacement_char(series: pd.Series, label: str):
    s = series.fillna("").astype(str)
    if s.str.contains("\uFFFD").any():  # "�"
        ex = s[s.str.contains("\uFFFD")].head(10).tolist()
        raise ValueError(f"{label} contém '�' (U+FFFD). Exemplos: " + " | ".join(ex))


def ler_consolidado(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    return pd.read_csv(path, encoding="utf-8-sig", dtype=str, encoding_errors="strict")


def baixar_cadop(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=120)
    r.raise_for_status()

    # latin1 nunca quebra e preserva byte-a-byte; depois limpamos/normalizamos.
    df = pd.read_csv(BytesIO(r.content), sep=";", encoding="latin1", dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def compactar(csv_path: Path, zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(csv_path, arcname=csv_path.name)
    return zip_path


def preparar_cadop(df: pd.DataFrame) -> pd.DataFrame:
    required = {"REGISTRO_OPERADORA", "CNPJ", "Razao_Social"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"CADOP sem colunas esperadas. Achei: {list(df.columns)}")

    df = df.copy()
    df["__REG_KEY__"] = df["REGISTRO_OPERADORA"].apply(key_reg_ans)
    df["CNPJ"] = df["CNPJ"].apply(only_digits)
    df["Razao_Social"] = df["Razao_Social"].apply(limpar_texto)

    # se aparecer '�' aqui, já houve perda antes (não deveria acontecer)
    assert_no_replacement_char(df["Razao_Social"], "CADOP.Razao_Social")

    df = df[df["__REG_KEY__"] != ""]
    df = df[df["CNPJ"].str.len() == 14]
    df = df.drop_duplicates(subset=["__REG_KEY__"], keep="first")
    return df[["__REG_KEY__", "CNPJ", "Razao_Social"]]


def aplicar_lookup(df_base: pd.DataFrame, df_lookup: pd.DataFrame, tag: str) -> pd.DataFrame:
    df_lookup = df_lookup.rename(
        columns={"CNPJ": f"CNPJ_{tag}", "Razao_Social": f"Razao_Social_{tag}"}
    )
    return df_base.merge(df_lookup, how="left", on="__REG_KEY__")


def main():
    print("Lendo consolidado:", CONSOLIDADO_IN)
    df_cons = ler_consolidado(CONSOLIDADO_IN)
    df_cons.columns = [str(c).strip() for c in df_cons.columns]

    required = {"RegistroANS", "Ano", "Trimestre", "ValorDespesas"}
    if not required.issubset(set(df_cons.columns)):
        raise ValueError(
            f"Consolidado sem colunas esperadas. Precisa ter {sorted(required)}. Achei: {list(df_cons.columns)}"
        )

    if "CNPJ" not in df_cons.columns:
        df_cons["CNPJ"] = ""
    if "RazaoSocial" not in df_cons.columns:
        df_cons["RazaoSocial"] = ""

    df_cons["__REG_KEY__"] = df_cons["RegistroANS"].apply(key_reg_ans)
    df_cons["CNPJ"] = df_cons["CNPJ"].fillna("").apply(only_digits)
    df_cons["RazaoSocial"] = df_cons["RazaoSocial"].fillna("").apply(limpar_texto)

    assert_no_replacement_char(df_cons["RazaoSocial"], "Entrada.RazaoSocial")

    print("Baixando CADOP ATIVAS...")
    lookup_ativas = preparar_cadop(baixar_cadop(CADOP_ATIVAS_URL))

    print("Baixando CADOP CANCELADAS...")
    lookup_cancel = preparar_cadop(baixar_cadop(CADOP_CANCELADAS_URL))

    print("Enriquecendo (ativas -> fallback canceladas)...")
    df_out = aplicar_lookup(df_cons, lookup_ativas, "ativas")
    df_out = aplicar_lookup(df_out, lookup_cancel, "canceladas")

    cnpj_ativas = df_out["CNPJ_ativas"].fillna("")
    cnpj_cancel = df_out["CNPJ_canceladas"].fillna("")
    rz_ativas = df_out["Razao_Social_ativas"].fillna("")
    rz_cancel = df_out["Razao_Social_canceladas"].fillna("")

    df_out["CNPJ"] = df_out["CNPJ"].mask(df_out["CNPJ"].eq(""), cnpj_ativas)
    df_out["CNPJ"] = df_out["CNPJ"].mask(df_out["CNPJ"].eq(""), cnpj_cancel)

    df_out["RazaoSocial"] = df_out["RazaoSocial"].mask(df_out["RazaoSocial"].eq(""), rz_ativas)
    df_out["RazaoSocial"] = df_out["RazaoSocial"].mask(df_out["RazaoSocial"].eq(""), rz_cancel)

    df_out["RazaoSocial"] = df_out["RazaoSocial"].apply(limpar_texto)
    df_out["CNPJ"] = df_out["CNPJ"].apply(only_digits)

    colunas_final = ["CNPJ", "RazaoSocial", "RegistroANS", "Trimestre", "Ano", "ValorDespesas"]
    df_out_final = df_out[colunas_final].copy()

    assert_no_replacement_char(df_out_final["RazaoSocial"], "Saída.RazaoSocial")

    CONSOLIDADO_OUT.parent.mkdir(parents=True, exist_ok=True)
    df_out_final.to_csv(CONSOLIDADO_OUT, index=False, encoding="utf-8-sig")

    sem = df_out_final[df_out_final["CNPJ"].astype(str).str.strip().eq("")].copy()
    if not sem.empty:
        SEM_MATCH_CSV.parent.mkdir(parents=True, exist_ok=True)
        sem[["RegistroANS", "Ano", "Trimestre", "ValorDespesas"]].drop_duplicates().to_csv(
            SEM_MATCH_CSV, index=False, encoding="utf-8-sig"
        )
        print("OK Auditoria sem match:", SEM_MATCH_CSV)

    compactar(CONSOLIDADO_OUT, OUTPUT_ZIP)

    total = len(df_out_final)
    sem_match = int(df_out_final["CNPJ"].astype(str).str.strip().eq("").sum())

    print("OK Saída:", CONSOLIDADO_OUT)
    print("OK ZIP:", OUTPUT_ZIP)
    print(f"Linhas: {total} | Sem match de CNPJ: {sem_match}")


if __name__ == "__main__":
    main()
