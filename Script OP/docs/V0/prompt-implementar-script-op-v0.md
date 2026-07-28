# Implementação — Script OP v0 (versão mínima)

**Contexto:** A estrutura fundacional já existe em `Script OP/` (ver `ARCHITECTURE_ScriptOP.md`, `BUSINESS_RULES_ScriptOP.md`, `SCENARIOS_EP-01_ScriptOP.md`, `CLAUDE.md`). Esta tarefa implementa a **versão mínima**, cortando escopo deliberadamente: sem hierarquia Pai/Filho, sem interface gráfica, sem edição de work packages existentes. Só criação em lote via CSV, rodando no terminal.

## Escopo desta implementação

**Dentro do escopo:**
- Ler um arquivo CSV com as colunas: assunto, descricao, tipo, situacao, prioridade, versao, modulo, sistema, gravidade, projeto.
- Validar cada linha:
  - Campos obrigatórios preenchidos (todos exceto descrição) — RN-002.
  - Gravidade obrigatória e válida se tipo ∈ {Bug, Tech Debt}; senão, aceitar "-" — RN-001.
  - Versão deve existir no projeto informado (consultar API) — RN-005.
- Resolver Sistema/Módulo/Gravidade de texto para `href` de custom_option, usando o mapa em `config/custom_fields_map.yaml`.
- Antes de processar qualquer linha, validar conexão com a API do OpenProject (RN-007) — se falhar, abortar sem processar nada.
- Para cada linha válida, criar o work package via `POST /api/v3/work_packages`.
- Linha inválida não interrompe as demais (RN-003) — apenas essa linha é pulada, com mensagem de erro.
- Ao final, imprimir no terminal um resumo: quantas linhas com sucesso (com ID gerado), quantas com erro (e o motivo de cada erro).

**Fora do escopo desta versão (não implementar agora):**
- Coluna `pai_linha` / hierarquia entre work packages — ignorar essa coluna se presente no CSV, ou nem seu suportar ainda.
- Edição de work packages existentes.
- Qualquer interface gráfica ou web — só CLI via terminal.
- Log em arquivo — só print no terminal.

## Onde implementar (respeitar a estrutura já definida)

- `src/script_op/csv_parser.py` — leitura do CSV, retorna lista de dicts/objetos representando cada linha.
- `src/script_op/validators.py` — implementa RN-001, RN-002, RN-005 (retorna lista de erros por linha, vazia se válida).
- `src/script_op/custom_fields.py` — lê `config/custom_fields_map.yaml`, resolve texto → href.
- `src/script_op/api_client.py` — funções de: testar conexão (RN-007), buscar versões de um projeto (para validar RN-005), criar work package.
- `src/script_op/output.py` — toda formatação de mensagens ao terminal (sucesso/erro por linha, resumo final). Nenhum `print()` fora deste arquivo.
- `src/script_op/main.py` — entrypoint Typer, orquestra o fluxo: ler .env → testar conexão → ler CSV → validar cada linha → resolver custom fields → criar work packages → imprimir resumo via `output.py`.

## Passo a passo esperado

1. Complete `config/custom_fields_map.yaml` com o mapeamento completo de valores conhecidos (ver `doc_uso_openproject.md` para a lista de valores possíveis de Sistema, Módulo, Gravidade — os hrefs específicos que não tivermos confirmado via API, deixe como comentário `# TODO: confirmar href` para não travar a implementação).

2. Implemente `api_client.py` com:
   - Autenticação via `.env` (`OPENPROJECT_BASE_URL`, `OPENPROJECT_API_TOKEN`).
   - Função de teste de conexão (ex: `GET /api/v3/users/me`).
   - Função de listar versões de um projeto (`GET /api/v3/projects/{id}/versions` ou equivalente — confirmar endpoint correto).
   - Função de criar work package (`POST /api/v3/work_packages`), montando o payload correto incluindo `_links` para tipo, status, prioridade, projeto e custom fields.

3. Implemente `validators.py` com as 3 regras de validação, retornando erros claros e específicos por linha (ex: `"Linha 3: Gravidade obrigatória para tipo Bug"`).

4. Implemente `csv_parser.py` para ler o arquivo e devolver estrutura de dados limpa para o `main.py` processar.

5. Implemente `output.py` com funções tipo `print_line_success(line_num, wp_id)`, `print_line_error(line_num, motivo)`, `print_summary(total, sucesso, erro)`.

6. Implemente `main.py` com Typer, comando único (ex: `script-op importar caminho/do/arquivo.csv`), orquestrando tudo.

7. Crie um CSV de exemplo (`exemplo.csv` ou similar) com 3-5 linhas de teste, incluindo pelo menos uma linha inválida de propósito, para eu conseguir testar o fluxo completo.

8. Rode o script localmente contra o OpenProject real (`localhost:8090`) usando o CSV de exemplo, e relate o resultado real da execução (não apenas "deveria funcionar" — rode de verdade e cole o output).

## Regras gerais (de `CLAUDE.md`, reforçando)

- Toda validação centralizada em `validators.py`.
- Nenhum `print()` fora de `output.py`.
- Commits prefixados com `[SCRIPT-OP-XX]`.

## Finalização

Ao final, informe:
- O que foi implementado.
- Resultado real de uma execução de teste (colar o output do terminal).
- Quaisquer TODOs deixados no `custom_fields_map.yaml` que precisam de confirmação via API antes de considerar isso pronto para uso real.
