# Script OP

CLI Python que cria work packages em lote no OpenProject a partir de um arquivo CSV, evitando a criação manual um-a-um pela interface web.

Ver `docs/ARCHITECTURE_ScriptOP.md`, `docs/BUSINESS_RULES_ScriptOP.md` e `docs/SCENARIOS_EP-01_ScriptOP.md` para as regras completas de negócio e arquitetura.

## Instalação

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Configuração

```bash
cp .env.example .env
```

Preencha `.env` com a URL da instância do OpenProject e o token de API (`OPENPROJECT_BASE_URL`, `OPENPROJECT_API_TOKEN`). Nunca commitar o `.env`.

## Uso

> A lógica do CLI ainda não está implementada nesta etapa (setup fundacional). O comando abaixo é um placeholder do formato esperado:

```bash
python -m script_op.main --csv caminho/para/arquivo.csv
```
