# TesteDeIntegracaoComApiPublica

Projeto full-stack para integração e visualização de dados da ANS, composto por:

- **ETL (Python)**: baixa, extrai, processa e consolida dados em CSV/ZIP.
- **Backend (FastAPI + SQLAlchemy)**: consulta o PostgreSQL e expõe uma API REST.
- **Frontend (Vite + Vue)**: dashboard, gráficos e detalhes por operadora (com filtros).
- **Testes (Vitest)**: cobre casos de sucesso/erro/vazio e filtros no frontend.

---

## Visão geral (como funciona)

1. **ETL** baixa arquivos trimestrais (ZIP), extrai CSVs e gera consolidados em `data/output/`.
2. Os dados processados são **importados no PostgreSQL** (via script do ETL).
3. O **backend FastAPI** consulta o banco (SQLAlchemy) e expõe endpoints em `/api/...`.
4. O **frontend Vue** consome a API (base configurada em `VITE_API_BASE`) e apresenta:
   - Dashboard com estatísticas e gráfico por UF
   - Detalhes por operadora (CNPJ) + histórico de despesas (ano/trimestre)

---

## Estrutura do repositório

```text
.
├─ backend/
│  ├─ app/
│  │  ├─ db.py
│  │  ├─ main.py
│  │  └─ __init__.py
│  └─ __init__.py
├─ etl/
│  ├─ downloadans.py
│  ├─ processfiles.py
│  ├─ agregarezipar.py
│  ├─ enrichcadop.py
│  ├─ enrichufmodalidadeporcnpj.py
│  └─ importpostgres.py
├─ data/
│  ├─ raw/            # arquivos .zip baixados
│  ├─ extracted/      # CSVs extraídos por trimestre
│  └─ output/         # CSV/ZIP consolidados + consultas (query1.csv, query2.csv, query3.csv, etc.)
└─ frontend/
   ├─ src/
   │  ├─ api.js
   │  └─ views/
   │     ├─ Dashboard.vue
   │     └─ OperadoraDetalhe.vue
   ├─ tests/
   ├─ vite.config.js
   ├─ package.json
   └─ .env

Requisitos
Backend / ETL
Python 3.x

PostgreSQL (recomendado), pois o backend consulta tabelas como:

dim_operadora

fato_despesas_consolidadas

despesas_agregadas

Frontend
Node.js (recomendado LTS)

npm

Configuração de ambiente
Backend (PostgreSQL)
O backend monta a DATABASE_URL a partir das env vars (ver backend/app/db.py):

POSTGRES_HOST (default: localhost)

POSTGRES_PORT (default: 5432)

POSTGRES_DB (default: ans_db)

POSTGRES_USER (default: postgres)

POSTGRES_PASSWORD (obrigatória; o backend lança erro se não existir)

Formato:
postgresql://POSTGRES_USER:POSTGRES_PASSWORD@POSTGRES_HOST:POSTGRES_PORT/POSTGRES_DB

Exemplo (Windows PowerShell)
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5432"
$env:POSTGRES_DB="ans_db"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="SUA_SENHA_AQUI"

Exemplo (Linux/macOS)
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DB="ans_db"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="SUA_SENHA_AQUI"

Frontend (URL do backend)
O frontend usa import.meta.env.VITE_API_BASE (arquivo frontend/src/api.js).

Crie/edite frontend/.env:
VITE_API_BASE=http://localhost:8000

Como rodar (local)
1) ETL (opcional)
Use se você precisar baixar/processar dados e gerar arquivos em data/output/.

Exemplos:
python etl/downloadans.py
python etl/processfiles.py

Saídas típicas em data/output/:

consolidadodespesas.csv / .zip

consolidadodespesasenriquecido.csv / .zip

consolidadodespesasvalidadoenriquecido.csv

despesasagregadas.csv

query1.csv, query2.csv, query3.csv

2) Subir o backend (FastAPI)
O app é app = FastAPI(...) em backend/app/main.py.

Windows (PowerShell)
py -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

Linux/macOS
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

Health check:
GET /health → { "status": "ok" }

3) Subir o frontend (Vite + Vue)
cd frontend
npm install
npm run dev

Abra:
http://localhost:5173

API (endpoints)
Health
GET /health

Operadoras (paginação + busca)
GET /api/operadoras?page=1&limit=20&search=...

Parâmetros:

page (>= 1)

limit (1..100)

search (opcional; busca por CNPJ ou Razão Social)

Resposta (json):
{
  "data": [
    { "cnpj": "…", "razao_social": "…", "uf": "…", "modalidade": "…" }
  ],
  "page": 1,
  "limit": 20,
  "total": 1234
}

Detalhes de uma operadora
GET /api/operadoras/{cnpj}

Observações:

O backend normaliza o CNPJ removendo caracteres não numéricos antes de consultar.

Se não existir: 404 com detail: "Operadora não encontrada".

Histórico de despesas (por ano/trimestre)
GET /api/operadoras/{cnpj}/despesas

Retorna(json):
[
  { "ano": 2025, "trimestre": 1, "valor_despesas": 123.45 },
  { "ano": 2025, "trimestre": 2, "valor_despesas": 234.56 }
]

Estatísticas gerais (Dashboard)
GET /api/estatisticas

Retorna:

total_despesas (float)

media_despesas (float)

top5_operadoras (lista com 5 itens)

Estatísticas por UF
GET /api/estatisticas/uf

Retorna(json):
[
  { "uf": "SP", "total_uf": 123.45 },
  { "uf": "RJ", "total_uf": 67.89 }
]

Queries SQL usadas (backend)
Abaixo estão as queries do backend/app/main.py (executadas via sqlalchemy.text(...)).

1) Listagem paginada de operadoras (com busca)

Contagem total (sql):
SELECT COUNT(*)
FROM dim_operadora
WHERE 1=1
  AND (cnpj ILIKE :s OR razao_social ILIKE :s);

Página de dados (sql):
SELECT cnpj, razao_social, uf, modalidade
FROM dim_operadora
WHERE 1=1
  AND (cnpj ILIKE :s OR razao_social ILIKE :s)
ORDER BY razao_social
LIMIT :limit OFFSET :offset;

Como funciona

page e limit controlam paginação (offset = (page-1)*limit).

O parâmetro search aplica ILIKE para suportar busca case-insensitive.

2) Detalhe da operadora por CNPJ (sql):
SELECT cnpj, razao_social, uf, modalidade
FROM dim_operadora
WHERE cnpj = :cnpj;

Como funciona

O backend normaliza o CNPJ com regex removendo tudo que não é dígito antes de consultar.

3) Histórico de despesas por operadora ano/trimestre (sql):
SELECT
  ano,
  trimestre,
  SUM(valor_despesas) AS valor_despesas
FROM fato_despesas_consolidadas
WHERE cnpj = :cnpj
GROUP BY ano, trimestre
ORDER BY ano, trimestre;

Como funciona

A rota agrega por período (ano/trimestre) para retornar uma série temporal consolidada para o frontend.

4) Estatísticas gerais - total + média (sql):

SELECT
  COALESCE(SUM(total_despesas), 0) AS total_despesas,
  COALESCE(AVG(total_despesas), 0) AS media_despesas
FROM despesas_agregadas;

omo funciona

Usa a tabela despesas_agregadas para calcular SUM e AVG de forma mais barata/consistente.

5) Top 5 operadoras por despesas - soma no fato (sql):
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
ORDER BY t.total_despesas DESC;

Como funciona

O subselect calcula o total por CNPJ no fato e retorna só os 5 maiores.

Em seguida faz JOIN com dim_operadora para obter metadados.

6) Distribuição de despesas por UF (sql):
SELECT
  d.uf,
  SUM(f.valor_despesas) AS total_uf
FROM fato_despesas_consolidadas f
JOIN dim_operadora d ON d.cnpj = f.cnpj
WHERE d.uf IS NOT NULL AND d.uf <> ''
GROUP BY d.uf
ORDER BY total_uf DESC;

Modelo de dados (tabelas esperadas)
dim_operadora (dimensão)
Campos usados pelo backend:

cnpj (chave)

razao_social

uf

modalidade

fato_despesas_consolidadas (fato)
Campos usados pelo backend:

cnpj (FK para dim_operadora)

ano

trimestre

valor_despesas

despesas_agregadas (agregada)
Campos usados pelo backend:

total_despesas (usado para SUM e AVG no endpoint /api/estatisticas)

Índices recomendados - performance

Em bases maiores, esses índices ajudam(sql):
-- Busca/joins por CNPJ
CREATE INDEX IF NOT EXISTS idx_dim_operadora_cnpj
ON dim_operadora (cnpj);

CREATE INDEX IF NOT EXISTS idx_fato_cnpj_ano_tri
ON fato_despesas_consolidadas (cnpj, ano, trimestre);

-- Agregação por UF (group by/join)
CREATE INDEX IF NOT EXISTS idx_dim_operadora_uf
ON dim_operadora (uf);

CORS (desenvolvimento)
O backend usa CORSMiddleware permitindo origens locais como:

http://localhost:5173 (Vite)

http://localhost:8080

http://localhost:3000

Testes (frontend)
Os testes ficam em frontend/tests/ e usam Vitest.

Rodar em modo watch (powersheel):
cd frontend
npm run test

Rodar uma vez e finalizar (powershell):
cd frontend
npm run test:run

Funcionalidades do frontend
Dashboard
Total de despesas

Média

Ranking Top 5 operadoras por despesas

Distribuição por UF (gráfico)

Detalhes da operadora
Exibe dados (razão social, CNPJ, UF, modalidade)

Histórico de despesas com filtro por ano e/ou trimestre

Quando Ano = Todos os anos, as opções de trimestre refletem os trimestres realmente existentes no dataset (inclui T4 se existir)





