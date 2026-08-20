# SCENARIOS_EP-01_ScriptOP.md (Versão Mínima)
> Baseado em: BUSINESS_RULES_ScriptOP.md | Épico: Criação de Work Packages em lote via CSV
> **Status:** Reduzido para v0 — sem Cenários 007 e 008 (hierarquia Pai/Filho)

---

## Cenário 001 — Criar work package simples com sucesso ✅
*Dado* que João preparou um CSV com uma linha válida, Tipo = "Task", todos os campos obrigatórios preenchidos corretamente
*Quando* ele roda o script apontando para esse CSV
*Então* o script deve criar o Work Package no OpenProject e imprimir no terminal o ID gerado com sucesso

## Cenário 005 — Campo obrigatório vazio ❌ (BLOQUEIO)
*Dado* que João preparou um CSV com uma linha sem o campo Assunto preenchido
*Quando* ele roda o script
*Então* essa linha deve ser bloqueada com mensagem de erro indicando o campo faltante, e as demais linhas do CSV devem continuar sendo processadas

## Cenário 006 — Versão inexistente no Projeto ❌ (BLOQUEIO)
*Dado* que João preparou um CSV com uma linha cujo campo Versão não corresponde a nenhuma versão cadastrada no Projeto informado
*Quando* ele roda o script
*Então* essa linha deve ser bloqueada com mensagem de erro indicando que a Versão não existe, e as demais linhas do CSV devem continuar sendo processadas

## Cenário 009 — Falha de conexão com a API ❌ (BLOQUEIO total)
*Dado* que a API do OpenProject está inacessível ou o token de autenticação é inválido
*Quando* João roda o script apontando para um CSV válido
*Então* nenhuma linha deve ser processada, e o script deve informar claramente o erro de conexão/autenticação antes de encerrar

## Cenário 010 — CSV com múltiplas linhas válidas e inválidas misturadas 🔀
*Dado* que João preparou um CSV com 5 linhas, sendo 3 válidas e 2 inválidas (sem relação entre si)
*Quando* ele roda o script
*Então* as 3 linhas válidas devem ser criadas com sucesso e as 2 inválidas devem ser reportadas como erro, sem que uma afete a outra

---

## Índice de Rastreabilidade

| Cenário | Regra de Negócio | Caso de Uso |
|---|---|---|
| 001 | RN-002 | UC-001 (Fluxo Principal) |
| 005 | RN-002, RN-003 | UC-001 (Fluxo Alternativo — Linha inválida) |
| 006 | RN-005, RN-003 | UC-001 (Fluxo Alternativo — Linha inválida) |
| 009 | RN-007 | UC-001 (Fluxo de Exceção — Falha de conexão) |
| 010 | RN-003 | UC-001 (Fluxo Alternativo — Linha inválida) |

---

## Checklist de Aceite

- [ ] Work package simples é criado com sucesso e ID reportado no terminal (Cen. 001)
- [ ] Campos obrigatórios ausentes bloqueiam apenas a linha afetada (Cen. 005)
- [ ] Versão inexistente no projeto bloqueia a linha (Cen. 006)
- [ ] Falha de conexão/autenticação bloqueia o processamento inteiro antes de qualquer criação (Cen. 009)
- [ ] Arquivo misto (válidas + inválidas) processa corretamente cada linha de forma independente (Cen. 010)
