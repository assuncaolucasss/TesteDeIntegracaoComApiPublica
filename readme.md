# Teste de Integração com API Pública

[Repositório](https://github.com/assuncaolucasss/TesteDeIntegracaoComApiPublica)

Uma aplicação full‑stack para integrar, processar e visualizar dados públicos (ANS). O projeto inclui um pipeline ETL em Python, uma API (FastAPI) que consulta um banco PostgreSQL e um frontend em Vue 3 que consome essa API para apresentar dashboards, listas e detalhes por operadora.

---

## Visão geral
1. ETL (Python) baixa arquivos trimestrais (ZIP), extrai CSVs e gera arquivos consolidados em `data/output/`.
2. Dados consolidados são importados para PostgreSQL (scripts em `etl/`).

> Observação: o banco utilizado neste projeto foi provisionado no **Neon** (https://neon.tech). Use a connection string fornecida pelo Neon para configurar `DATABASE_URL` quando aplicável.

3. Backend (FastAPI + SQLAlchemy) expõe uma API REST que consulta o banco.
4. Frontend (Vite + Vue) consome a API e apresenta um dashboard com gráficos, ranking e detalhes por operadora.

> O frontend inclui testes (Vitest) cobrindo casos de sucesso, erro e estado vazio.

---

## Links (Deploy e repositório)
- **Frontend (deploy):** [Vercel (deploy)](https://teste-de-integracao-com-api-publica-final-nvtbmhvz6.vercel.app/)
- **Backend (API):** [API (Render)](https://testedeintegracaocomapipublica.onrender.com)

---

## Funcionalidades (organizado por tela) ✨

- **Home**
  - Mini‑métricas: Total de despesas, Média por operadora, Top operadora (consome `GET /api/estatisticas`).
  - Estado de carregamento com skeletons.
  - Comportamento quando o backend está offline: exibe **“Indicadores indisponíveis (backend offline)”** e um botão **“Tentar novamente”**; a navegação permanece funcional.

- **Operadoras**
  - Lista responsiva: **cards no mobile** e **tabela no desktop**.
  - Busca por texto usando o query param `search`.
  - Paginação com `page` e `limit` (itens por página).
  - Filtros persistidos na URL (`?search=&page=&limit=`): a tela lê esses parâmetros no carregamento e atualiza a URL ao alterar filtros.

- **Dashboard**
  - Exibe métricas consolidadas e ranking (Top 5) — consome `GET /api/estatisticas`.
  - Panorama por UF (gráfico em desktop, lista em mobile) — consome `GET /api/estatisticas/uf`.

---

## Stack 🔧
- Backend: **Python**, FastAPI, SQLAlchemy, Uvicorn
- Frontend: **Vue 3**, **Vite**, **Vue Router**, **Tailwind CSS**, **Chart.js**
- Testes: **Vitest**, **@vue/test-utils**
- Banco: **PostgreSQL (Neon)**
- Deploys conhecidos: Frontend em **Vercel**, Backend em **Render**

---

## Como rodar localmente ▶️

**Pré-requisitos**: Node.js (LTS recomendado) + npm/pnpm/yarn; Python 3.x + pip para o backend.

**Frontend**
1. Acesse a pasta `frontend`:
   ```bash
   cd frontend
   ```
2. Instale dependências:
   ```bash
   npm install
   ```
3. Configure `.env` (veja abaixo) e rode em dev:
   ```bash
   npm run dev
   ```
4. Build e preview (opcional):
   ```bash
   npm run build
   npm run preview
   ```

**Backend (mínimo)**
1. Acesse a pasta `backend`:
   ```bash
   cd backend
   ```
2. (Opcional) crie e ative um virtualenv:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   source .venv/bin/activate  # macOS / Linux
   ```
3. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Rode a API (exemplo):
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## Configuração (.env) ⚙️
- O frontend usa a variável **`VITE_API_BASE`** (definida em `frontend/src/api.js`) como `API_BASE` para as chamadas `fetch`.
  - Exemplo de `.env` em `frontend/`:
    ```env
    VITE_API_BASE=http://localhost:8000
    ```
- O backend usa `DATABASE_URL` para conexão com PostgreSQL (ex.: `postgresql://user:pass@host:port/dbname`).

> Observação: no passado o README usava `VITE_API_URL`; a implementação atual lê `VITE_API_BASE` em `frontend/src/api.js`.

---

## Endpoints consumidos (resumo) 🗂️

| Rota | Descrição |
|---|---|
| `GET /health` | Checagem básica de saúde da API |
| `GET /api/estatisticas` | Estatísticas gerais (total_despesas, media_despesas, top5_operadoras) — usado por Home e Dashboard |
| `GET /api/estatisticas/uf` | Distribuição de despesas por UF — usado no Dashboard |
| `GET /api/operadoras?search=&page=&limit=` | Lista paginada de operadoras; `search` para filtro; `page` e `limit` controlam paginação |
| `GET /api/operadoras/:cnpj` | Metadados de uma operadora (use apenas dígitos no CNPJ) |
| `GET /api/operadoras/:cnpj/despesas` | Histórico de despesas agregadas por ano/trimestre para a operadora |

---

## Comportamento offline 🚨
- Quando o backend estiver indisponível, as métricas na **Home** mostram **“Indicadores indisponíveis (backend offline)”** com opção de **Tentar novamente**.
- A navegação e a maioria das telas do frontend continuam operacionais; componentes mostrarão mensagens de erro ou estados vazios conforme o caso.

---

## Contribuição & Commits 🧩
Seguimos **Conventional Commits**. Exemplos:
- `feat(frontend): adicionar skeleton nas métricas da Home`
- `fix(operadoras): corrigir paginação com page e limit`
- `docs: atualizar README com endpoints e instruções de uso`

Contribuições via PRs são bem‑vindas; por favor inclua testes quando aplicável.

---

## Licença
MIT

Este repositório é disponibilizado para estudo e aprendizado sob os termos da **MIT License**. Consulte o arquivo `LICENSE` para o texto completo.

---

## Checklist TODO ✅
- [ ] Confirmar URL pública da API para atualizar links diretos no README.
- [ ] Confirmar o nome do repositório/organização (se quiser que eu coloque o link no cabeçalho).
- [x] Definir licença do projeto (MIT).
- [ ] Confirmar comandos de deploy/preview se diferentes de `npm run preview`.

---

Se quiser que eu remova seções antigas, adicione badges ou publique este README no repositório com formatação diferente, me avise e aplico as mudanças.






