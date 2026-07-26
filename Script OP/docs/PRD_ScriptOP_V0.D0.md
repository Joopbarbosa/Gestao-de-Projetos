# PRD — Script OP
> **Versão:** V0.D0 | **Data:** 26/07/2026 | **Status:** Aguardando Validação

---

## 1. Visão Geral

Hoje, work packages no OpenProject (instância local, projeto Script OP e demais projetos da Pense Software) são criados um a um, manualmente, pela UI. Isso é lento para cadastro em lote (ex: importar um backlog de 10+ bugs/tarefas de uma vez).

O Script OP resolve isso permitindo que João descreva várias tarefas num arquivo CSV e rode um script Python que as cria em lote no OpenProject via API v3 — sem custo de LLM/token, sem depender do Claude Code ou de MCP para essa operação recorrente.

**Objetivo de negócio:** agilizar o cadastro de work packages, reduzindo tempo e custo (de token) frente às alternativas já avaliadas (MCP + LLM).

## 2. Perfil de Usuário

- **Ator único:** João, desenvolvedor e administrador do próprio OpenProject.
- **Uso:** individual, via terminal/CLI (Pop!_OS, inicialmente).
- **Objetivo do ator:** rodar um comando, apontar para um CSV, ver no terminal se cada linha foi criada com sucesso ou deu erro.

## 3. Fronteiras e Intersecções

- **Domínio Principal:** N/A — Fase de fundação (projeto novo, não é épico de sistema existente).
- **Impacto em Legado:** N/A — Fase de fundação. O script é uma ferramenta externa que consome a API do OpenProject (`openproject_local`, porta 8090) como dependência, mas não altera código do OpenProject em si.

## 4. Diretrizes de Estrutura

- **Arquitetura:** a definir na skill-estrutura. Recomendação a levar para aquela etapa: **separar a lógica de negócio (parsing de CSV, validação, chamadas à API) da camada de apresentação (hoje: prints no terminal)**. Isso não é obrigatório para a v1 funcionar, mas evita retrabalho quando a v2 (GUI/.exe Windows) for iniciada — a v2 poderá reaproveitar o "motor" da v1 trocando apenas a interface.
- **Integração externa:** API v3 do OpenProject (`http://localhost:8090/api/v3`), autenticação via API token (Basic Auth, `apikey:TOKEN`).
- **Dependências de dados já levantadas:** ver `doc_uso_openproject.md` — tipos, status, prioridades nativas e os 3 custom fields (Sistema=`customField1`, Módulo=`customField2`, Gravidade=`customField3`), incluindo a regra de que valores de campos-lista são referenciados por `href` de `custom_option`, não por texto puro.

## 5. Módulos e Funcionalidades

### Módulo: Importação CSV
#### Fluxo: Criar work packages em lote - [NOVO]
- João prepara um CSV com colunas: Assunto, Descrição, Tipo, Situação, Prioridade, Versão, Módulo, Sistema, Gravidade, Projeto.
- Roda o script apontando para o arquivo CSV.
- O script valida cada linha contra os valores conhecidos (tipos, status, prioridades, custom fields — ver seção 7 da doc de uso).
- Para Gravidade: obrigatório apenas se Tipo ∈ {Bug, Tech Debt}; demais tipos usam "-".
- O script resolve texto → `href` de `custom_option` para os campos de lista antes de enviar à API.
- Cada linha gera uma chamada de criação via API v3.
- O script imprime no terminal, por linha: sucesso (com ID gerado) ou erro (com motivo).

#### Fluxo: Editar work packages existentes - [NOVO — desejável, não crítico]
- Mesma lógica de CSV, mas o script identifica work packages já existentes (por ID ou outro critério a definir) e atualiza os campos informados em vez de criar novos.
- Este fluxo é valioso para a v1, mas **não bloqueia a entrega** caso a criação em lote já esteja funcionando — pode ser adicionado em uma iteração seguinte dentro da própria v1 sem exigir nova versão do produto.

## 6. Fluxo Crítico Macro

João prepara CSV → roda script → script valida e resolve custom fields → script chama API do OpenProject → script imprime resultado por linha no terminal.

## 7. Decisões de UI/UX (Macro)

- v1: sem interface gráfica. Toda interação é via terminal (linha de comando).
- Sem necessidade de log em arquivo — o feedback do terminal (sucesso/erro por linha) é suficiente para a v1.

## 8. Fora do Escopo

- GUI gráfica e `.exe` para Windows — **planejado para v2**: aplicativo local com interface visual agradável, substituindo o uso via terminal. Tecnologia (Electron, Tauri, PyInstaller+GUI, etc.) será decidida quando a v2 for iniciada, não nesta etapa.
- Dashboards de visualização (bugs, módulos, etc.) — planejado para uma versão futura, com foco em leitura/relatórios.
- Uso por múltiplos usuários/multi-usuário — fora de escopo enquanto o uso for individual (só João).
- Qualquer integração externa além da API do OpenProject.
- Migração de dados históricos (fora do que já foi tratado na migração de infraestrutura em andamento).

## 9. Próximos Passos
- [ ] **Aprovação do Cliente:** validação deste documento por João.
- [ ] **Skill Estrutura:** definir arquitetura do script (linguagem já definida: Python; definir organização de módulos/pastas para viabilizar reuso na v2).
- [ ] **Skill Spec-Driven:** extrair regras de negócio e cenários (Gherkin) — cobrindo validação de CSV, regras condicionais (Gravidade × Tipo), resolução de custom fields, e casos de erro.
- [ ] **Skill Design:** N/A para v1 (sem interface gráfica). Retomar quando a v2 for iniciada.
