# ARCHITECTURE.md — Script OP

> Ver `DECISOES_GLOBAIS.md` para decisões que se aplicam a todo o repositório `Gestao-de-Projetos`.

---

## Decisões Técnicas

- **Linguagem/Stack:** Python 3, com **Typer** para a interface de linha de comando.
- **Execução:** venv Python local, isolado dentro da própria pasta do projeto — sem Docker, sem dependência do `docker-compose.yml` principal do repositório (ver DECISOES_GLOBAIS.md).
- **Autenticação:** API token do OpenProject via variável de ambiente (`.env`), nunca hardcoded.
- **Resolução de Custom Fields:** mapa estático texto → `href` de `custom_option`, mantido em arquivo de configuração separado (`config/custom_fields_map.yaml`), atualizado manualmente quando novos valores forem cadastrados no OpenProject.
- **Decisão futura (v2, não implementar agora):** interface gráfica em React, empacotada como `.exe` para Windows. A lógica de negócio desta v1 (parsing, validação, chamadas à API) deve permanecer desacoplada da apresentação (hoje: `output.py` cuidando só de prints no terminal) para ser reaproveitada como backend/motor da v2 sem reescrita.
- **Hierarquia Pai/Filho no CSV:** representada por uma coluna `pai_linha` no CSV, contendo o número da linha (1-indexed, desconsiderando o cabeçalho) da linha-pai dentro do mesmo arquivo. Vazio = sem pai (work package raiz). Escolhido em vez de referenciar por Assunto (frágil a duplicatas/erros de digitação) ou por ID externo do OP (a v1 não cria pai fora do próprio CSV, conforme Spec).

---

## Estrutura de Pastas

```
Infraestrutura/                          (raiz do repositório Gestao-de-Projetos)
├── docker-compose.yml                   (stack de infra existente — não tocar)
├── docs/
│   ├── DECISOES_GLOBAIS.md
│   └── PIPELINE_DESENVOLVIMENTO.md
└── Script OP/
    ├── .env.example
    ├── .gitignore
    ├── requirements.txt
    ├── README.md
    ├── config/
    │   └── custom_fields_map.yaml       (mapa texto → href de custom_option)
    └── src/
        └── script_op/
            ├── __init__.py
            ├── main.py                  (entrypoint Typer/CLI)
            ├── csv_parser.py            (leitura e parsing do CSV)
            ├── validators.py            (RN-001 a RN-005: validações de linha)
            ├── hierarchy.py             (resolução de pai_linha, RN-004)
            ├── custom_fields.py         (leitura do config/custom_fields_map.yaml, resolução texto→href)
            ├── api_client.py            (comunicação com API v3 do OpenProject: conexão, criação de work package)
            └── output.py                (formatação de mensagens de sucesso/erro no terminal — única camada de apresentação)
```

## Modelagem de Dados (Conceitual)

Não há banco de dados próprio nesta v1 — o Script OP é stateless, lê o CSV e escreve na API do OpenProject. Não há necessidade de armazenamento intermediário.

**Estrutura do CSV de entrada** (conceitual, para orientar `csv_parser.py`):

| Coluna | Tipo | Obrigatório |
|---|---|---|
| assunto | string | sim |
| descricao | string | não |
| tipo | string (enum) | sim |
| situacao | string (enum) | sim |
| prioridade | string (enum) | sim |
| versao | string | sim |
| modulo | string (enum) | sim |
| sistema | string (enum) | sim |
| gravidade | string (enum condicional) | condicional (RN-001) |
| projeto | string (enum) | sim |
| pai_linha | inteiro (referência a outra linha do mesmo CSV) | não |
