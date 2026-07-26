# CLAUDE.md — Script OP

Contexto para qualquer sessão do Claude Code trabalhando nesta subpasta (`Script OP/`) do repositório `Gestao-de-Projetos`.

## O que é este projeto

CLI Python que cria work packages em lote no OpenProject via arquivo CSV, evitando criação manual um-a-um pela UI. Ver `ARCHITECTURE.md`, `BUSINESS_RULES_ScriptOP.md` e `SCENARIOS_EP-01_ScriptOP.md` para regras completas.

## Onde cada coisa vai

| Categoria | Local |
|---|---|
| Entrypoint CLI (Typer) | `src/script_op/main.py` |
| Parsing de CSV | `src/script_op/csv_parser.py` |
| Validações de linha (RN-001 a RN-005) | `src/script_op/validators.py` |
| Resolução de hierarquia Pai/Filho | `src/script_op/hierarchy.py` |
| Resolução de custom fields (texto→href) | `src/script_op/custom_fields.py` |
| Comunicação com API do OpenProject | `src/script_op/api_client.py` |
| Formatação de saída no terminal | `src/script_op/output.py` (única camada de apresentação — não colocar `print()` fora daqui) |
| Mapa estático de custom options | `config/custom_fields_map.yaml` |
| Variáveis de ambiente | `.env` (nunca commitado; usar `.env.example` como referência) |

## Verificar antes de criar

Antes de criar qualquer função, classe ou módulo novo, verificar se já existe algo equivalente nos arquivos acima. Em especial:
- Toda lógica de validação de negócio (RN-001 a RN-005) deve ficar centralizada em `validators.py` — nunca espalhada em `main.py` ou `api_client.py`.
- Nenhum `print()` ou output direto ao usuário fora de `output.py` — isso é o que garante que a v2 (interface gráfica) possa reaproveitar toda a lógica sem reescrita.
- Se encontrar duplicação entre módulos, reportar antes de implementar.

## Regras de negócio críticas (resumo — ver BUSINESS_RULES_ScriptOP.md para o completo)

- Gravidade só é válida/obrigatória para Tipo ∈ {Bug, Tech Debt}; demais tipos usam "-" (RN-001).
- Linha inválida não interrompe o processamento das demais (RN-003).
- Falha em linha-Pai propaga bloqueio para as Filhas dela (RN-004).
- Versão deve existir no Projeto informado, senão bloqueia a linha (RN-005).
- Antes de processar qualquer linha, validar conexão com a API do OpenProject (RN-007) — se falhar, não processar nada.

## Commits

Toda mensagem de commit deve começar com o ID da tarefa do Backlog/OpenProject correspondente (ex: `[SCRIPT-OP-01] feat: ...`).
