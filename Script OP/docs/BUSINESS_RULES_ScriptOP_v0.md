# BUSINESS_RULES_ScriptOP.md (Versão Mínima)
> Baseado em: PRD_ScriptOP_V0.D0.md | Data: 26/07/2026
> **Status:** Reduzido para v0 — sem RN-004 (hierarquia Pai/Filho)

---

## Entidades

### Linha CSV
Representa uma linha do arquivo de entrada, candidata a se tornar um Work Package.

| Atributo | Obrigatório | Observação |
|---|---|---|
| Assunto | Sim | |
| Descrição | Não | |
| Tipo | Sim | Um dos 8 valores válidos (Task, Epic, Feature, Refactor, Doc, Bug, Tech Debt, Infra) |
| Situação | Sim | Um dos 12 valores válidos (ver doc de uso) |
| Prioridade | Sim | Low, Normal, High, Immediate |
| Versão | Sim | Deve existir no Projeto informado |
| Módulo | Sim | Um dos valores válidos do custom field Módulo |
| Sistema | Sim | Um dos valores válidos do custom field Sistema |
| Gravidade | **Condicional** | Obrigatório e válido apenas se Tipo ∈ {Bug, Tech Debt}. Nos demais tipos, usar "-" |
| Projeto | Sim | Um dos projetos existentes no OpenProject |

### Work Package
Entidade criada no OpenProject a partir de uma Linha CSV validada com sucesso.

**Estados:** não modelados nesta v0 (a v0 não gerencia transição de estado pós-criação).

### Custom Option
Valor possível de um Custom Field (Sistema, Módulo, Gravidade) no OpenProject, identificado por um `href` (ex: `/api/v3/custom_options/21`). Mapeamento texto → `href` é **fixo/estático na v0** — atualizado manualmente quando novos valores forem cadastrados no OpenProject (fora do escopo do script detectar automaticamente).

---

## Relacionamentos

- Um **Work Package** pertence a exatamente um **Projeto**.
- Um **Work Package** do tipo Bug ou Tech Debt possui exatamente uma **Gravidade** válida (não "-").

---

## Regras de Negócio

**RN-001 — Gravidade condicional ao Tipo**
Gravidade é obrigatória e deve ser um dos valores {Critico, Grave, Medio, Baixo} quando o Tipo da linha for Bug ou Tech Debt. Para os demais tipos, o valor deve ser "-".

**RN-002 — Todos os campos-base são obrigatórios**
Assunto, Tipo, Situação, Prioridade, Versão, Módulo, Sistema, Projeto são obrigatórios em toda Linha CSV. Descrição é opcional. Gravidade segue RN-001.

**RN-003 — Erro de linha não interrompe o arquivo**
Se uma Linha CSV falhar em qualquer validação (BLOQUEIO), o script pula apenas essa linha e continua processando as demais linhas independentes.

**RN-005 — Versão deve existir no Projeto**
O valor informado em Versão deve corresponder a uma versão já cadastrada no Projeto informado na mesma linha. Se não existir, a linha é bloqueada (BLOQUEIO) — não é permitido criar o Work Package sem Versão.

**RN-006 — Sem limite de volume**
O script não impõe limite de quantidade de linhas processadas por execução.

**RN-007 — Pré-condição de conexão**
Antes de processar qualquer linha do CSV, o script deve validar a conexão e autenticação com a API do OpenProject. Se a validação falhar, nenhuma linha é processada (o arquivo inteiro é bloqueado nesse caso específico — falha de infraestrutura, não de dado).

---

## Casos de Uso

**UC-001 — Criar Work Packages em lote via CSV**
- **Ator:** João
- **Pré-condição:** CSV preparado no formato definido (seção "Linha CSV"); conexão com a API do OpenProject validada com sucesso (RN-007).
- **Fluxo Principal:**
  1. João roda o script apontando para o arquivo CSV.
  2. O script valida a conexão com a API (RN-007).
  3. Para cada Linha CSV, o script valida os campos (RN-001, RN-002, RN-005).
  4. Para linhas válidas, o script resolve os valores de Sistema/Módulo/Gravidade para `href` de Custom Option.
  5. O script cria o Work Package via API v3.
  6. O script imprime no terminal o resultado de cada linha: sucesso (com ID gerado) ou erro (com motivo).
- **Fluxo Alternativo — Linha inválida:** linha é pulada (RN-003), processamento continua.
- **Fluxo de Exceção — Falha de conexão:** nenhuma linha é processada; script informa erro de conexão e encerra (RN-007).

---

## Restrições Globais

- Mapeamento de Custom Options (texto → `href`) é estático na v0; requer atualização manual quando novos valores forem cadastrados no OpenProject.
- v0 não trata: hierarquia Pai/Filho entre work packages, edição de Work Packages existentes, ou integração com múltiplos projetos em cascata. Esses recursos ficam para versões futuras.
