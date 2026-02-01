#agregar_e_zipar.py

import zipfile
from pathlib import Path
import pandas as pd

IN_PATH = Path("data/output/consolidado_despesas_validado_enriquecido.csv")  # precisa ter UF
OUT_CSV = Path("data/output/despesas_agregadas.csv")
OUT_ZIP = Path("data/output/Teste_LucasAssuncaoBraga.zip")

def main():
    if not IN_PATH.exists():
        raise FileNotFoundError(
            f"Não encontrei {IN_PATH}. "
            "Você precisa gerar o consolidado enriquecido COM UF (passo 2.2)."
        )

    df = pd.read_csv(IN_PATH, encoding="utf-8-sig", dtype=str, encoding_errors="strict")

    required = {"RazaoSocial", "UF", "Trimestre", "Ano", "ValorDespesas"}
    if not required.issubset(df.columns):
        raise ValueError(f"Faltam colunas {sorted(required)}. Achei: {list(df.columns)}")

    # Normalização mínima
    df["RazaoSocial"] = df["RazaoSocial"].fillna("").astype(str).str.strip()
    df["UF"] = df["UF"].fillna("").astype(str).str.strip()
    df["Trimestre"] = df["Trimestre"].fillna("").astype(str).str.strip()
    df["Ano"] = df["Ano"].fillna("").astype(str).str.strip()

    # Converte para número; valores inválidos viram NaN e não contam no mean/std [web:515]
    df["ValorDespesas_num"] = pd.to_numeric(df["ValorDespesas"], errors="coerce")

    # Agregação por RazaoSocial e UF (exatamente como pedido) [web:510]
    agg = (
        df.groupby(["RazaoSocial", "UF"], as_index=False)
          .agg(
              total_despesas=("ValorDespesas_num", "sum"),
              media_trimestral=("ValorDespesas_num", "mean"),
              desvio_padrao=("ValorDespesas_num", "std"),
              n_linhas=("ValorDespesas_num", "size"),
              n_validos=("ValorDespesas_num", "count"),
          )
    )

    # std pode ficar NaN quando há 1 valor válido; preenche 0 para facilitar leitura
    agg["desvio_padrao"] = agg["desvio_padrao"].fillna(0.0)

    # Ordena por total (maior -> menor)
    agg = agg.sort_values("total_despesas", ascending=False)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    # Compacta exatamente com o nome pedido
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(OUT_CSV, arcname=OUT_CSV.name)

    print("OK CSV:", OUT_CSV)
    print("OK ZIP:", OUT_ZIP)
    print("Preview:")
    print(agg.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
