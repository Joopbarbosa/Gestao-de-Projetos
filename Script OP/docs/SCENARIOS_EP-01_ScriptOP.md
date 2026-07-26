# SCENARIOS_EP-01_ScriptOP.md
> Baseado em: BUSINESS_RULES_ScriptOP.md | Épico: Criação de Work Packages em lote via CSV

---

## Cenário 001 — Criar work package simples com sucesso ✅
*Dado* que João preparou um CSV com uma linha válida, Tipo = "Task", todos os campos obrigatórios preenchidos corretamente
*Quando* ele roda o script apontando para esse CSV
*Então* o script deve criar o Work Package no OpenProject e imprimir no terminal o ID gerado com sucesso

## Cenário 002 — Criar Bug com Gravidade válida ✅
*Dado* que João preparou um CSV com uma linha de Tipo = "Bug" e Gravidade = "Critico"
*Quando* ele roda o script
*Então* o Work Package deve ser criado com o Custom Field Gravidade preenchido com "Critico"

## Cenário 003 — Criar Task com Gravidade "-" ✅
*Dado* que João preparou um CSV com uma linha de Tipo = "Task" e Gravidade = "-"
*Quando* ele roda o script
*Então* o Work Package deve ser criado sem erro, sem valor de Gravidade sendo enviado à API

## Cenário 004 — Bug sem Gravidade preenchida ❌ (BLOQUEIO)
*Dado* que João preparou um CSV com uma linha de Tipo = "Bug" e Gravidade vazia ou "-"
*Quando* ele roda o script
*Então* essa linha deve ser bloqueada com mensagem de erro indicando que Gravidade é obrigatória para o tipo Bug, e as demais linhas do CSV devem continuar sendo processadas

## Cenário 005 — Campo obrigatório vazio ❌ (BLOQUEIO)
*Dado* que João preparou um CSV com uma linha sem o campo Assunto preenchido
*Quando* ele roda o script
*Então* essa linha deve ser bloqueada com mensagem de erro indicando o campo faltante, e as demais linhas do CSV devem continuar sendo processadas

## Cenário 006 — Versão inexistente no Projeto ❌ (BLOQUEIO)
*Dado* que João preparou um CSV com uma linha cujo campo Versão não corresponde a nenhuma versão cadastrada no Projeto informado
*Quando* ele roda o script
*Então* essa linha deve ser bloqueada com mensagem de erro indicando que a Versão não existe, e as demais linhas do CSV devem continuar sendo processadas

## Cenário 007 — Hierarquia Pai/Filho criada com sucesso ✅
*Dado* que João preparou um CSV com uma linha Pai válida e uma linha Filha que a referencia
*Quando* ele roda o script
*Então* ambos os Work Packages devem ser criados no OpenProject, com o Filho vinculado ao Pai na hierarquia

## Cenário 008 — Falha na linha Pai propaga para Filhos 🔀 (BLOQUEIO em cascata)
*Dado* que João preparou um CSV com uma linha Pai inválida (ex: Tipo incorreto) e uma ou mais linhas Filhas que a referenciam
*Quando* ele roda o script
*Então* a linha Pai deve ser bloqueada, todas as linhas Filhas dela também devem ser bloqueadas (sem tentativa de criação), e as demais linhas do CSV sem relação com esse Pai devem continuar sendo processadas normalmente

## Cenário 009 — Falha de conexão com a API ❌ (BLOQUEIO total)
*Dado* que a API do OpenProject está inacessível ou o token de autenticação é inválido
*Quando* João roda o script apontando para um CSV válido
*Então* nenhuma linha deve ser processada, e o script deve informar claramente o erro de conexão/autenticação antes de encerrar

## Cenário 010 — CSV com múltiplas linhas válidas e inválidas misturadas 🔀
*Dado* que João preparou um CSV com 5 linhas, sendo 3 válidas e 2 inválidas (sem relação de hierarquia entre si)
*Quando* ele roda o script
*Então* as 3 linhas válidas devem ser criadas com sucesso e as 2 inválidas devem ser reportadas como erro, sem que uma afete a outra

---

## Índice de Rastreabilidade

| Cenário | Regra de Negócio | Caso de Uso |
|---|---|---|
| 001 | RN-002 | UC-001 (Fluxo Principal) |
| 002 | RN-001 | UC-001 (Fluxo Principal) |
| 003 | RN-001 | UC-001 (Fluxo Principal) |
| 004 | RN-001, RN-003 | UC-001 (Fluxo Alternativo — Linha inválida) |
| 005 | RN-002, RN-003 | UC-001 (Fluxo Alternativo — Linha inválida) |
| 006 | RN-005, RN-003 | UC-001 (Fluxo Alternativo — Linha inválida) |
| 007 | Relacionamento Pai/Filho | UC-001 (Fluxo Principal) |
| 008 | RN-004 | UC-001 (Fluxo Alternativo — Pai inválido) |
| 009 | RN-007 | UC-001 (Fluxo de Exceção — Falha de conexão) |
| 010 | RN-003 | UC-001 (Fluxo Alternativo — Linha inválida) |

---

## Checklist de Aceite

- [ ] Work package simples é criado com sucesso e ID reportado no terminal (Cen. 001)
- [ ] Gravidade é corretamente exigida para Bug/Tech Debt e aceita "-" para os demais tipos (Cen. 002, 003, 004)
- [ ] Campos obrigatórios ausentes bloqueiam apenas a linha afetada (Cen. 005)
- [ ] Versão inexistente no projeto bloqueia a linha (Cen. 006)
- [ ] Hierarquia Pai/Filho é criada corretamente no OpenProject (Cen. 007)
- [ ] Falha em linha-Pai propaga bloqueio para todas as Filhas, sem afetar linhas não relacionadas (Cen. 008)
- [ ] Falha de conexão/autenticação bloqueia o processamento inteiro antes de qualquer criação (Cen. 009)
- [ ] Arquivo misto (válidas + inválidas, sem hierarquia) processa corretamente cada linha de forma independente (Cen. 010)
