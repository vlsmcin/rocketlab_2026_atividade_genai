# rocketlab_2026_atividade_genai

Projeto de Text-to-SQL com CHASE (self-consistency), guardrails e interfaces de uso em:

- chat interativo no terminal
- execução em lote
- backend FastAPI

## Estrutura

```
src/
	text_to_sql/
		agent.py      # Criação/configuração do agente LLM
		chase.py      # Pipeline CHASE e consenso entre candidatos
		db.py         # Operações e validações SQL no banco
	services/
		text_to_sql_service.py  # Orquestração do fluxo question -> CHASE
	formatters/
		result_formatter.py     # Formatação da saída do app terminal
	main.py           # Chat interativo
	main_batch.py     # Execução das perguntas em lote
	api/
		app.py          # App factory do FastAPI
		routes.py       # Endpoints HTTP
		schemas.py      # Modelos de request/response
		services.py     # Regras de aplicação para API
```

## Instalação

1. Criar/ativar ambiente virtual.
2. Instalar dependências:

```
pip install -r requirements.txt
```

## Execução

### Chat interativo

```
python -m src.main
```

### Lote

```
python -m src.main_batch
```

### API FastAPI

```
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Endpoints:

- GET /health
- POST /ask

Payload de exemplo para POST /ask:

```json
{
	"question": "Quais são os top 10 produtos mais vendidos?"
}
```