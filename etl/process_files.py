#processs_files.py

import csv
import re
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd

RAW_DIR = Path("data/raw")
EXTRACTED_DIR = Path("data/extracted")
OUTPUT_DIR = Path("data/output")


def extrair_ano_tri_do_zip(zip_path: Path):
    nome = zip_path.name
    m = re.search(r"(20\d{2})_T([1-4])_", nome, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    m2 = re.search(r"([1-4])T(20\d{2})", nome, re.IGNORECASE)
    if m2:
        return int(m2.group(2)), int(m2.group(1))
    return None, None


def extrair_todos_zips(raw_dir: Path = RAW_DIR, extracted_dir: Path = EXTRACTED_DIR):
    extracted_dir.mkdir(parents=True, exist_ok=True)
    extraidos = []

    for zip_path in raw_dir.glob("*.zip"):
        ano, tri = extrair_ano_tri_do_zip(zip_path)
        subdir = extracted_dir / (f"{ano}_T{tri}" if ano and tri else zip_path.stem)
        subdir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as z:
            for member in z.namelist():
                if member.endswith("/"):
                    continue
                dest_path = subdir / member
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with z.open(member) as src, open(dest_path, "wb") as dst:
                    dst.write(src.read())
                extraidos.append(dest_path)

    return extraidos


def detectar_formato(path: Path):
    suf = path.suffix.lower()
    if suf in [".csv", ".txt"]:
        return "csv"
    if suf in [".xlsx", ".xls"]:
        return "excel"
    return None


def ler_dataframe(path: Path):
    formato = detectar_formato(path)
    if not formato:
        return None

    try:
        if formato == "excel":
            # lê tudo como string para evitar REG_ANS virar float
            return pd.read_excel(path, dtype=str)

        # CSV/TXT: tenta encodings e detecta separador
        for enc in ("utf-8-sig", "utf-8", "latin1"):
            try:
                with open(path, "r", encoding=enc) as f:
                    primeira = f.readline()
                sep = ";" if primeira.count(";") > primeira.count(",") else ","
                return pd.read_csv(path, sep=sep, encoding=enc, dtype=str)
            except Exception:
                continue

        return None
    except Exception:
        return None


def inferir_ano_tri_pelo_caminho(path: Path):
    for p in path.parts:
        m = re.match(r"(20\d{2})_T([1-4])", p, re.IGNORECASE)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None, None


def filtrar_eventos_sinistros(df: pd.DataFrame):
    if "DESCRICAO" not in df.columns:
        return df.iloc[0:0]

    desc = df["DESCRICAO"].astype(str).str.lower()
    mask = desc.str.contains(r"evento|sinistro", na=False)
    return df[mask]


def to_float_br(x: Any):
    if pd.isna(x):
        return None
    s = str(x).strip().replace(" ", "")

    if s == "" or s.lower() == "nan":
        return None

    # "1.234,56" -> "1234.56"
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")

    try:
        return float(s)
    except Exception:
        return None


def normalizar_reg_ans(x: Any) -> str:
    """
    Garante que REG_ANS vire uma chave limpa:
    - remove ".0" (caso típico de float serializado)
    - remove qualquer caractere não-dígito
    - retorna "" se não sobrar dígito
    """
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    s = str(x).strip()
    if re.fullmatch(r"\d+\.0", s):
        s = s.split(".")[0]
    s = re.sub(r"\D", "", s)
    return s


def processar_arquivo(path: Path):
    df = ler_dataframe(path)
    if df is None or df.empty:
        print("DESCARTADO (nao leu ou vazio):", path)
        return []

    df.columns = [str(c).strip().upper() for c in df.columns]

    required = {"REG_ANS", "DESCRICAO", "VL_SALDO_FINAL"}
    if not required.issubset(set(df.columns)):
        print("DESCARTADO (faltam colunas):", path)
        print("COLUNAS:", list(df.columns))
        return []

    ano, tri = inferir_ano_tri_pelo_caminho(path)
    if not ano or not tri:
        print("DESCARTADO (nao inferiu ano/tri):", path)
        return []

    df2 = filtrar_eventos_sinistros(df)
    if df2.empty:
        print("DESCARTADO (sem evento/sinistro na descricao):", path)
        return []

    # Converte valor
    df2 = df2.copy()
    df2["VALOR"] = df2["VL_SALDO_FINAL"].apply(to_float_br)
    df2 = df2.dropna(subset=["VALOR"])

    # Normaliza REG_ANS antes de agrupar (evita 477.0 e NaN)
    df2["REG_ANS_NORM"] = df2["REG_ANS"].apply(normalizar_reg_ans)
    df2 = df2[df2["REG_ANS_NORM"] != ""]

    if df2.empty:
        print("DESCARTADO (REG_ANS vazio/invalidado apos normalizacao):", path)
        return []

    # Agrega por operadora no trimestre
    agg = (
        df2.groupby("REG_ANS_NORM", as_index=False)["VALOR"]
        .sum()
        .rename(columns={"REG_ANS_NORM": "RegistroANS", "VALOR": "ValorDespesas"})
    )

    registros = []
    for _, row in agg.iterrows():
        registros.append(
            {
                "CNPJ": "",
                "RazaoSocial": "",
                "RegistroANS": str(row["RegistroANS"]).strip(),
                "Trimestre": tri,
                "Ano": ano,
                "ValorDespesas": float(row["ValorDespesas"]),
            }
        )

    return registros


def consolidar_dados(extracted_dir: Path = EXTRACTED_DIR, output_dir: Path = OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    todos = []

    for path in extracted_dir.rglob("*"):
        if path.is_file():
            regs = processar_arquivo(path)
            if regs:
                print(f"{path} -> {len(regs)} regs (REG_ANS)")
                todos.extend(regs)

    if not todos:
        raise RuntimeError("Nenhum registro consolidado. Verifique filtros/arquivos extraídos.")

    # Consolida duplicidades entre arquivos (mesmo RegistroANS/Ano/Trimestre)
    df_all = pd.DataFrame(todos)
    df_all["RegistroANS"] = df_all["RegistroANS"].apply(normalizar_reg_ans)
    df_all = df_all[df_all["RegistroANS"] != ""]

    df_final = (
        df_all.groupby(["RegistroANS", "Ano", "Trimestre"], as_index=False)["ValorDespesas"]
        .sum()
    )

    # Formato final exigido no 1.3 (CNPJ/RazaoSocial serão preenchidos no enrich_cadop.py)
    df_final.insert(0, "RazaoSocial", "")
    df_final.insert(0, "CNPJ", "")

    out_csv = output_dir / "consolidado_despesas.csv"
    df_final = df_final[["CNPJ", "RazaoSocial", "RegistroANS", "Trimestre", "Ano", "ValorDespesas"]]
    df_final.to_csv(out_csv, index=False, encoding="utf-8")

    return out_csv


def compactar_saida(csv_path: Path):
    zip_path = csv_path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(csv_path, arcname=csv_path.name)
    return zip_path


def pipeline_parte1():
    print("Extraindo ZIPs...")
    extraidos = extrair_todos_zips()
    print(f"Arquivos extraidos: {len(extraidos)}")

    print("Consolidando dados...")
    csv_path = consolidar_dados()

    print("Compactando...")
    zip_path = compactar_saida(csv_path)

    print("Pronto:", zip_path)


if __name__ == "__main__":
    pipeline_parte1()
