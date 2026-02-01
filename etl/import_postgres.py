import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import String, Text, Numeric, SmallInteger


PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB   = os.getenv("POSTGRES_DB", "ans_db")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASS = os.getenv("POSTGRES_PASSWORD")

if not PG_PASS:
    raise RuntimeError(
        "POSTGRES_PASSWORD não definido. "
        "Defina a variável de ambiente POSTGRES_PASSWORD e rode novamente."
    )

engine = create_engine(f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}")

PATH_DIM = "data/output/consolidado_despesas_validado_enriquecido.csv"
PATH_FATO = "data/output/consolidado_despesas_enriquecido.csv"
PATH_AGG = "data/output/despesas_agregadas.csv"

DDL = """
DROP TABLE IF EXISTS despesas_agregadas CASCADE;
DROP TABLE IF EXISTS fato_despesas_consolidadas CASCADE;
DROP TABLE IF EXISTS dim_operadora CASCADE;

CREATE TABLE dim_operadora (
  cnpj          CHAR(14) PRIMARY KEY,
  razao_social  TEXT NOT NULL,
  uf            CHAR(2),
  modalidade    TEXT
);

CREATE TABLE fato_despesas_consolidadas (
  id             BIGSERIAL PRIMARY KEY,
  cnpj           CHAR(14) NOT NULL REFERENCES dim_operadora(cnpj),
  registro_ans   VARCHAR(20) NOT NULL,
  trimestre      SMALLINT NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
  ano            SMALLINT NOT NULL,
  valor_despesas NUMERIC(18,2) NOT NULL
);

CREATE INDEX idx_fato_cnpj_periodo ON fato_despesas_consolidadas (cnpj, ano, trimestre);

CREATE TABLE despesas_agregadas (
  razao_social     TEXT NOT NULL,
  uf               CHAR(2) NOT NULL,
  total_despesas   NUMERIC(18,2) NOT NULL,
  media_trimestral NUMERIC(18,2) NOT NULL,
  desvio_padrao    NUMERIC(18,2) NOT NULL,
  n_linhas         INTEGER,
  n_validos        INTEGER,
  PRIMARY KEY (razao_social, uf)
);

CREATE INDEX idx_agregadas_total_desc ON despesas_agregadas (total_despesas DESC);
"""

def only_digits(s: str) -> str:
    import re
    return re.sub(r"\D", "", "" if s is None else str(s))

def main():
    print("Recriando schema (DDL tipado)...")
    with engine.connect() as conn:
        conn.execute(text(DDL))
        conn.commit()

    # 1) DIM_OPERADORA
    print("1/3) Importando dim_operadora...")
    df_dim = pd.read_csv(PATH_DIM, encoding="utf-8-sig", dtype=str)
    df_dim = (
        df_dim[["CNPJ", "RazaoSocial", "UF", "Modalidade"]]
        .drop_duplicates("CNPJ")
        .rename(columns={"CNPJ": "cnpj", "RazaoSocial": "razao_social", "UF": "uf", "Modalidade": "modalidade"})
    )
    df_dim["cnpj"] = df_dim["cnpj"].apply(only_digits)
    df_dim = df_dim[df_dim["cnpj"].str.len() == 14]

    df_dim.to_sql(
        "dim_operadora",
        engine,
        if_exists="append",
        index=False,
        dtype={
            "cnpj": String(14),
            "razao_social": Text(),
            "uf": String(2),
            "modalidade": Text(),
        },
        method="multi",
        chunksize=2000,
    )  # dtype ajuda a respeitar o schema [web:647]
    print(f"   OK: {len(df_dim)} operadoras")

    # 2) FATO
    print("2/3) Importando fato_despesas_consolidadas...")
    df_fato = pd.read_csv(PATH_FATO, encoding="utf-8-sig", dtype=str)
    df_fato = df_fato[["CNPJ", "RegistroANS", "Trimestre", "Ano", "ValorDespesas"]].rename(
        columns={
            "CNPJ": "cnpj",
            "RegistroANS": "registro_ans",
            "Trimestre": "trimestre",
            "Ano": "ano",
            "ValorDespesas": "valor_despesas",
        }
    )
    df_fato["cnpj"] = df_fato["cnpj"].apply(only_digits)
    df_fato = df_fato[df_fato["cnpj"].str.len() == 14]
    df_fato["trimestre"] = pd.to_numeric(df_fato["trimestre"], errors="coerce")
    df_fato["ano"] = pd.to_numeric(df_fato["ano"], errors="coerce")
    df_fato["valor_despesas"] = pd.to_numeric(df_fato["valor_despesas"], errors="coerce")

    df_fato = df_fato.dropna(subset=["trimestre", "ano", "valor_despesas"])
    df_fato["trimestre"] = df_fato["trimestre"].astype("int16")
    df_fato["ano"] = df_fato["ano"].astype("int16")

    # Garante 2 casas (NUMERIC(18,2))
    df_fato["valor_despesas"] = df_fato["valor_despesas"].round(2)

    df_fato.to_sql(
        "fato_despesas_consolidadas",
        engine,
        if_exists="append",
        index=False,
        dtype={
            "cnpj": String(14),
            "registro_ans": String(20),
            "trimestre": SmallInteger(),
            "ano": SmallInteger(),
            "valor_despesas": Numeric(18, 2),
        },
        method="multi",
        chunksize=5000,
    )
    print(f"   OK: {len(df_fato)} linhas")

    # 3) AGREGADOS
    print("3/3) Importando despesas_agregadas...")
    df_agg = pd.read_csv(PATH_AGG, encoding="utf-8-sig", dtype=str)
    # O CSV já sai com nomes: RazaoSocial, UF, total_despesas, media_trimestral, ...
    df_agg = df_agg.rename(columns={"RazaoSocial": "razao_social", "UF": "uf"})
    for col in ["total_despesas", "media_trimestral", "desvio_padrao", "n_linhas", "n_validos"]:
        if col in df_agg.columns:
            df_agg[col] = pd.to_numeric(df_agg[col], errors="coerce")
    df_agg["uf"] = df_agg["uf"].fillna("").astype(str).str.strip()

    df_agg.to_sql(
        "despesas_agregadas",
        engine,
        if_exists="append",
        index=False,
        dtype={
            "razao_social": Text(),
            "uf": String(2),
            "total_despesas": Numeric(18, 2),
            "media_trimestral": Numeric(18, 2),
            "desvio_padrao": Numeric(18, 2),
        },
        method="multi",
        chunksize=5000,
    )
    print(f"   OK: {len(df_agg)} agregados")

    print("\nIMPORT FINALIZADO (schema tipado).")

if __name__ == "__main__":
    main()
