# Teste de Integração com API Pública

## Visão geral
Projeto full‑stack para integração e visualização de dados públicos (ANS). O fluxo principal é:

1. ETL (Python) baixa arquivos trimestrais (ZIP), extrai CSVs e gera arquivos consolidados em `data/output/`.
2. Dados consolidados são importados para PostgreSQL (scripts em `etl/`).

> Observação: o banco utilizado neste projeto foi provisionado no **Neon** (https://neon.tech). Use a connection string fornecida pelo Neon para configurar `DATABASE_URL` quando aplicável.

3. Backend (FastAPI + SQLAlchemy) expõe uma API REST que consulta o banco.
4. Frontend (Vite + Vue) consome a API e apresenta um dashboard com gráficos, ranking e detalhes por operadora.

> O projeto inclui testes de frontend (Vitest) cobrindo casos de sucesso, erro e estado vazio.

## Links (Deploy e repositório)
- **Repositório:** [[URL do repositório](https://github.com/assuncaolucasss/TesteDeIntegracaoComApiPublica)]  
- **Frontend (deploy):** teste-de-integracao-com-api-publica-final-q5keugaj0.vercel.app  
- **Backend (API):** https://testedeintegracaocomapipublica.onrender.com  
- **Dashboard:** [URL do dashboard]

## Funcionalidades
- Listagem paginada de operadoras com busca por CNPJ/razão social ✅
- Detalhe de operadora por CNPJ (metadados + histórico de despesas) ✅
- Histórico de despesas agregadas por ano/trimestre ✅
- Estatísticas gerais (total, média) e Top5 operadoras ✅
- Distribuição de despesas por UF (gráfico) ✅
- Testes automatizados do frontend (Vitest) ✅

## Stack
- Backend: **Python**, FastAPI, SQLAlchemy, Uvicorn
- Frontend: **Vue 3**, Vite, Tailwind CSS
- Banco: **PostgreSQL (Neon)** 🗄️
- Deploy: Frontend em **Vercel**; Backend em **Render**

## Rotas da API
Abaixo estão as rotas principais e exemplos de request (curl). Substitua `[API_BASE]` por `https://testedeintegracaocomapipublica.onrender.com` ou sua URL local.

- GET /health
  - Descrição: checagem de saúde da API
  - Exemplo:
    ```bash
    curl -i https://testedeintegracaocomapipublica.onrender.com/health
    ```

- GET /api/operadoras?page=&limit=&search=
  - Descrição: lista paginada de operadoras; parâmetros opcionais: `page` (>=1), `limit` (1..100), `search` (CNPJ ou razão social)
  - Exemplo:
    ```bash
    curl -i "https://testedeintegracaocomapipublica.onrender.com/api/operadoras?page=1&limit=20&search=operadora"
    ```
  - Exemplo de resposta (JSON):
    ```json
    {
      "data": [{ "cnpj": "12345678000195", "razao_social": "Operadora X", "uf": "SP", "modalidade": "AMB" }],
      "page": 1,
      "limit": 20,
      "total": 1234
    }
    ```

- GET /api/operadoras/{cnpj}
  - Descrição: retorna metadados da operadora identificada pelo CNPJ (use CNPJ apenas com dígitos)
  - Exemplo:
    ```bash
    curl -i https://testedeintegracaocomapipublica.onrender.com/api/operadoras/12345678000195
    ```
  - Erro: 404 com `detail: "Operadora não encontrada"` se não existir.

- GET /api/operadoras/{cnpj}/despesas
  - Descrição: histórico de despesas agregadas por ano e trimestre para a operadora
  - Exemplo:
    ```bash
    curl -i https://testedeintegracaocomapipublica.onrender.com/api/operadoras/12345678000195/despesas
    ```
  - Exemplo de resposta:
    ```json
    [
      { "ano": 2025, "trimestre": 1, "valor_despesas": 123.45 },
      { "ano": 2025, "trimestre": 2, "valor_despesas": 234.56 }
    ]
    ```

- GET /api/estatisticas
  - Descrição: estatísticas gerais (total, média) e `top5_operadoras`
  - Exemplo:
    ```bash
    curl -i https://testedeintegracaocomapipublica.onrender.com/api/estatisticas
    ```
  - Exemplo de resposta:
    ```json
    {
      "total_despesas": 12345.67,
      "media_despesas": 123.45,
      "top5_operadoras": [ /* 5 items */ ]
    }
    ```

- GET /api/estatisticas/uf
  - Descrição: distribuição de despesas por UF
  - Exemplo:
    ```bash
    curl -i https://testedeintegracaocomapipublica.onrender.com/api/estatisticas/uf
    ```
  - Exemplo de resposta:
    ```json
    [ { "uf": "SP", "total_uf": 123.45 }, { "uf": "RJ", "total_uf": 67.89 } ]
    ```

## Como rodar localmente
Passos mínimos para desenvolvimento. Substitua comandos ou nomes por `[ajuste conforme seu projeto]` quando necessário.

Backend (API)
1. Entre na pasta do backend:
   ```bash
   cd backend
   ```
2. Crie e ative um ambiente virtual (opcional):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   source .venv/bin/activate  # macOS / Linux
   ```
3. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure variáveis de ambiente (veja seção abaixo).
5. Rode a API com Uvicorn:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

Frontend (Vite)
1. Entre na pasta do frontend:
   ```bash
   cd frontend
   ```
2. Instale dependências:
   ```bash
   npm install
   ```
3. Configure variáveis de ambiente (`.env` ou painel de host):
   ```env
   VITE_API_URL=https://testedeintegracaocomapipublica.onrender.com
   ```
4. Rode em modo dev:
   ```bash
   npm run dev
   ```
5. Build de produção:
   ```bash
   npm run build
   npm run preview   # [ajuste conforme seu projeto]
   ```

> Abra o frontend em `http://localhost:5173` (ou URL indicada pelo Vite).

## Variáveis de ambiente
- **DATABASE_URL** — URL de conexão PostgreSQL (formato: `postgresql://USER:PASSWORD@HOST:PORT/DBNAME`). Ex.: `postgresql://postgres:senha@localhost:5432/ans_db`.
  - Se estiver usando **Neon**, copie a connection string do painel do Neon e use-a como `DATABASE_URL` (ex.: `postgresql://user:pass@<host>:<port>/dbname`).
- **VITE_API_URL** — URL base usada pelo frontend para a API (ex.: `https://testedeintegracaocomapipublica.onrender.com`).

Onde definir:
- Localmente: use `.env` ou defina no shell antes de rodar os serviços.
- Render (backend): configure `DATABASE_URL` e outros secrets no painel do serviço (ouponha a connection string do Neon quando usado como DB). 
- Vercel (frontend): configure `VITE_API_URL` nas Environment Variables do projeto.

## Deploy
- Frontend (Vercel) ✅
  - Crie um projeto apontando para a pasta `frontend` do repositório.
  - Configure `VITE_API_URL` nas Environment Variables do projeto no painel da Vercel.
  - Ajuste build commands se necessário (`npm run build` / `npm run preview` como placeholder).

- Backend (Render) ✅
  - Crie um Web Service (ou container) apontando para o backend.
  - Configure `DATABASE_URL` e quaisquer outras env vars no painel da Render.
  - Para aplicações em Python, defina o comando de start como: `uvicorn app.main:app --host 0.0.0.0 --port 10000` (ajuste conforme o ambiente de deploy).
  - Observação: neste projeto o banco foi provisionado no **Neon**; copie a connection string do Neon e configure `DATABASE_URL` na Render (ou use-a localmente em `.env`).

> Configure secrets (DATABASE_URL, VITE_API_URL) no painel da plataforma usada para que não fiquem em código-fonte.

## Troubleshooting
- CORS (origem sem "/" no final) ⚠️
  - Sintoma: Erros CORS quando o frontend tenta acessar a API.
  - Solução: verifique as origens permitidas no backend (CORSMiddleware) e use a origem **sem barra final**, ex.: `https://meu-front.vercel.app` (não `https://meu-front.vercel.app/`).

- 404 ao recarregar rotas (Vercel) 🛠️
  - Sintoma: Ao dar refresh em uma rota SPA, recebe 404.
  - Solução: adicione um rewrite no `vercel.json` para redirecionar todas as rotas para `/index.html`:
    ```json
    {
      "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
    }
    ```

- Layout mobile no gráfico de UF (lista no mobile, gráfico no desktop) 📱💻
  - Sintoma: componente de UF não troca para lista em telas pequenas.
  - Solução: ajuste os breakpoints/responsividade nos componentes `src/components/UFsBarChart.vue` e `src/components/UFsUFList.vue` (ou nas classes Tailwind) para garantir: **lista** em telas pequenas e **gráfico** em telas médias/grandes.







