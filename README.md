# rocketlab_2026_atividade_genai

Projeto de Text-to-SQL para consultas e análises em um banco de dados de um Sistema de Gerenciamento de E-Commerce.

O objetivo é permitir que usuários não técnicos façam perguntas em linguagem natural e recebam respostas baseadas em consultas SQL executadas diretamente no banco. O projeto também inclui guardrails, execução em lote para perguntas principais e uma interface visual opcional.

## Requisitos do projeto

Este projeto foi desenvolvido para atender aos seguintes requisitos:

- Agente capaz de realizar consultas e análises sobre dados de um banco de dados de E-Commerce.
- Suporte a perguntas em linguagem natural com geração de SQL.
- Modelo utilizado: Gemini 2.5 Flash / Flash Lite.
- Linguagem: Python.
- Entregável: projeto Python com backend FastAPI e suporte a execução em lote.
- README com passo a passo de execução.

## Categorias de perguntas atendidas

Obs: "Pedidos" ≈ "Vendas"

- Análise de Vendas e Receita
  - Top 10 produtos mais vendidos
  - Receita total por categoria de produto
- Análise de Entrega e Logística
  - Quantidade de pedidos por status
  - Percentual de pedidos entregues no prazo por estado dos consumidores
- Análise de Satisfação e Avaliações
  - Média de avaliação geral dos pedidos
  - Média de avaliação por vendedor (top 10)
- Análise de Consumidores
  - Estados com maior volume de pedidos e maior ticket médio
  - Estados com maior atraso
- Análise de Vendedores e Produtos
  - Produtos mais vendidos por estado
  - Categorias com maior taxa de avaliação negativa

Também é possível explorar funcionalidades adicionais como guardrails, interface visual, gráficos e outras formas de análise.

## Estrutura do projeto

```text
backend/
  requirements.txt
  data/
  src/
    main.py
    main_batch.py
    api/
      app.py
      routes.py
      schemas.py
      services.py
    formatters/
      result_formatter.py
    services/
      text_to_sql_service.py
    text_to_sql/
      agent.py
      chase.py
      db.py
      guardrail.py
frontend/
  package.json
  pnpm-lock.yaml
  src/
    App.tsx
    main.tsx
    components/
    hooks/
    lib/
    types/
```

## Stack utilizada

- Framework de agentes: implementação própria com `pydantic_ai`
- Modelo: Gemini 2.5 Flash Lite
- Linguagem: Python
- Backend: FastAPI
- Interface visual: Vite + frontend em React/TypeScript
- Banco de dados: SQLite

## Pré-requisitos

- Python 3.11+ recomendado
- Node.js 18+ recomendado
- `pip`
- `pnpm`

## Configuração do ambiente

### 1. Criar e ativar o ambiente virtual

Antes de instalar qualquer dependência, entre na pasta `backend`, crie o ambiente virtual e ative-o:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

### 2. Criar o arquivo `.env`

Ainda na pasta `backend`, crie o arquivo `.env` a partir do `.env.example` e substitua pelo valor real da sua chave da Gemini:

```bash
cp .env.example .env
```

Depois, edite o arquivo `.env` e defina a variável:

```bash
GEMINI_API_KEY=sua_chave_api_real
```

## Instalação

### 1. Backend

Com o ambiente virtual ativado dentro de `backend`, instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Frontend

Entre na pasta do frontend antes de executar a interface visual:

```bash
cd frontend
pnpm install
```

## Modos de operação

O projeto possui três modos principais de uso.

### 1. Execução em lote das perguntas principais

Este é o modo recomendado para rodar as perguntas principais do projeto e validar o comportamento do agente.

```bash
cd backend
python -m src.main_batch
```

### 2. Chat interativo no terminal

Modo para testar perguntas manualmente no terminal.

```bash
cd backend
python -m src.main
```

### 3. Interface visual

Antes de iniciar a interface visual, suba o backend FastAPI em um terminal separado:

```bash
cd backend
source .venv/bin/activate
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Depois, em outro terminal, inicie a interface visual no frontend com:

```bash
cd frontend
pnpm run dev
```

Depois, abra no navegador:

```text
http://localhost:5173
```

## Backend FastAPI

O backend também expõe uma API FastAPI para integração programática.

### Executar a API

```bash
cd backend
source .venv/bin/activate
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

### Endpoints disponíveis

- `GET /health`
- `POST /ask`

### Exemplo de payload para `/ask`

```json
{
  "question": "Quais são os top 10 produtos mais vendidos?"
}
```

## Fluxo recomendado de uso

1. Entre em `backend`.
2. Crie e ative o ambiente virtual com `python -m venv .venv` e `source .venv/bin/activate`.
3. Crie o `.env` a partir de `.env.example` e informe a sua `GEMINI_API_KEY`.
4. Instale as dependências com `pip install -r requirements.txt`.
5. Rode a execução em lote com `python -m src.main_batch` para validar as principais perguntas.
6. Use o chat interativo em terminal com `python -m src.main` para testes manuais.
7. Suba o backend FastAPI com `uvicorn src.api.app:app --host 0.0.0.0 --port 8000`.
8. Somente depois inicie a interface visual com `cd frontend` e `pnpm run dev`.
9. Acesse `http://localhost:5173`.

## Observações

- Sempre execute os comandos do backend a partir da pasta `backend`.
- Sempre execute a interface visual a partir da pasta `frontend`.
- Sempre suba o backend FastAPI antes de abrir a interface web.
- O guardrail foi projetado para bloquear perguntas fora do escopo do banco e permitir perguntas legítimas sobre os dados, inclusive em linguagem mais abstrata.
- O pipeline principal de Text-to-SQL usa CHASE com self-consistency e validação por consulta executada no banco.

## Exemplos de perguntas

- Quais são os 10 produtos mais vendidos?
- Qual a receita total por categoria de produto?
- Quantos pedidos foram entregues no prazo por estado?
- Qual a média de avaliação por vendedor?
- Quais estados têm maior volume de pedidos?

## Licença

Projeto acadêmico para fins de estudo e demonstração.
