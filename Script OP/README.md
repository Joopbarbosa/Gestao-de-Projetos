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

```bash
PYTHONPATH=src python -m script_op.main caminho/para/arquivo.csv
```

Exemplo com o CSV de teste incluído no repositório:

```bash
PYTHONPATH=src python -m script_op.main exemplo.csv
```

O script valida a conexão com a API antes de processar qualquer linha (RN-007). Linhas inválidas são puladas e reportadas — não interrompem o processamento das demais (RN-003). Ao final, imprime um resumo com total de sucesso/erro.
