from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .db import engine
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
  "https://teste-de-integracao-com-api-publica-8hufwjrj3.vercel.app",
  "https://teste-de-integracao-com-api-publica.vercel.app",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/operadoras")
def listar_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Busca por CNPJ ou Razao Social"),
):
    offset = (page - 1) * limit

    with engine.connect() as conn:
        base = "FROM dim_operadora WHERE 1=1"
        params = {}

        if search:
            base += " AND (cnpj ILIKE :s OR razao_social ILIKE :s)"
            params["s"] = f"%{search}%"

        total = conn.execute(text(f"SELECT COUNT(*) {base}"), params).scalar_one()

        rows = conn.execute(
            text(f"""
                SELECT cnpj, razao_social, uf, modalidade
                {base}
                ORDER BY razao_social
                LIMIT :limit OFFSET :offset
            """),
            {**params, "limit": limit, "offset": offset},
        ).mappings().all()  # retorna dict por linha [web:741]

    return {
        "data": rows,
        "page": page,
        "limit": limit,
        "total": total,
    }

@app.get("/api/operadoras/{cnpj}")
def detalhes_operadora(cnpj: str):
    cnpj_digits = re.sub(r"\D", "", cnpj)

    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT cnpj, razao_social, uf, modalidade
                FROM dim_operadora
                WHERE cnpj = :cnpj
            """),
            {"cnpj": cnpj_digits},
        ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    return row

@app.get("/api/operadoras/{cnpj}/despesas")
def historico_despesas(cnpj: str):
    import re
    cnpj_digits = re.sub(r"\D", "", cnpj)

    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                  ano,
                  trimestre,
                  SUM(valor_despesas) AS valor_despesas
                FROM fato_despesas_consolidadas
                WHERE cnpj = :cnpj
                GROUP BY ano, trimestre
                ORDER BY ano, trimestre
            """),
            {"cnpj": cnpj_digits},
        ).mappings().all()

    return rows

@app.get("/api/estatisticas")
def estatisticas():
    """
    Retorna:
    - total de despesas (geral)
    - média (usando a tabela agregada por RazaoSocial+UF)
    - top 5 operadoras por soma de despesas no fato (3 trimestres)
    """
    with engine.connect() as conn:
        # Total e média usando a tabela agregada (barato e consistente)
        row = conn.execute(
            text("""
                SELECT
                  COALESCE(SUM(total_despesas), 0) AS total_despesas,
                  COALESCE(AVG(total_despesas), 0) AS media_despesas
                FROM despesas_agregadas
            """)
        ).mappings().one()

        # Top 5 operadoras por total no fato (soma dos 3 trimestres)
        top5 = conn.execute(
            text("""
                SELECT
                  d.cnpj,
                  d.razao_social,
                  d.uf,
                  d.modalidade,
                  t.total_despesas
                FROM dim_operadora d
                JOIN (
                    SELECT cnpj, SUM(valor_despesas) AS total_despesas
                    FROM fato_despesas_consolidadas
                    GROUP BY cnpj
                    ORDER BY total_despesas DESC
                    LIMIT 5
                ) t ON t.cnpj = d.cnpj
                ORDER BY t.total_despesas DESC
            """)
        ).mappings().all()

    return {
        "total_despesas": float(row["total_despesas"]),
        "media_despesas": float(row["media_despesas"]),
        "top5_operadoras": [
            {
                "cnpj": r["cnpj"],
                "razao_social": r["razao_social"],
                "uf": r["uf"],
                "modalidade": r["modalidade"],
                "total_despesas": float(r["total_despesas"]),
            }
            for r in top5
        ],
    }

@app.get("/api/estatisticas/uf")
def estatisticas_por_uf():
    """
    Retorna distribuição de despesas por UF:
    [{ "uf": "SP", "total_uf": 123.45 }, ...]
    """
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                  d.uf,
                  SUM(f.valor_despesas) AS total_uf
                FROM fato_despesas_consolidadas f
                JOIN dim_operadora d ON d.cnpj = f.cnpj
                WHERE d.uf IS NOT NULL AND d.uf <> ''
                GROUP BY d.uf
                ORDER BY total_uf DESC
            """)
        ).mappings().all()

    return [{"uf": r["uf"], "total_uf": float(r["total_uf"])} for r in rows]



