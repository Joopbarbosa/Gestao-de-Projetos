# BACKLOG_POCKET_V1.0.md — Script OP
> Baseado em: BUSINESS_RULES_ScriptOP.md, SCENARIOS_EP-01_ScriptOP.md
> Fatiamento por Vertical Slicing (valor funcional, não camada de código)

---

## [Fundação] - Definir arquitetura e setup do projeto
- [ ] **Estrutura:** definir organização de pastas/módulos Python (separação lógica de negócio × apresentação, conforme PRD seção 4)
- [ ] **Estrutura:** decidir codificação técnica da referência Pai/Filho no CSV (pendente da skill-estrutura)
- [ ] **Spec:** N/A — decisão estrutural pura, sem novo delta de regra de negócio

## [Conexão] - Validar conexão com a API do OpenProject antes de processar
- [ ] **Backend:** implementar checagem de autenticação/conexão (RN-007) como pré-condição do script
- [ ] **Spec:** RN-007, Cenário 009 já cobertos

## [Validação] - Validar campos obrigatórios de uma linha do CSV
- [ ] **Backend:** implementar validação dos 8 campos-base obrigatórios (RN-002)
- [ ] **Spec:** RN-002, Cenário 005 já cobertos

## [Validação] - Validar Gravidade condicional ao Tipo
- [ ] **Backend:** implementar regra RN-001 (Gravidade obrigatória só para Bug/Tech Debt; "-" para os demais)
- [ ] **Spec:** RN-001, Cenários 002, 003, 004 já cobertos

## [Validação] - Validar Versão contra o Projeto informado
- [ ] **Backend:** implementar checagem de existência da Versão no Projeto (RN-005) — requer consulta à API por Projeto
- [ ] **Spec:** RN-005, Cenário 006 já cobertos

## [Resolução de Dados] - Mapear texto → href de Custom Option
- [ ] **Backend:** implementar mapa estático (Sistema, Módulo, Gravidade) texto → `href` de `/api/v3/custom_options/{id}`
- [ ] **Spec:** Restrição Global (mapeamento estático) já coberta em BUSINESS_RULES

## [Criação] - Criar Work Package simples via API
- [ ] **Backend:** implementar chamada de criação (POST) para uma linha válida, sem hierarquia
- [ ] **Spec:** RN-002, Cenário 001 já cobertos

## [Criação] - Criar hierarquia Pai/Filho
- [ ] **Backend:** implementar criação respeitando vínculo Pai/Filho entre linhas do mesmo CSV
- [ ] **Spec:** Relacionamento Pai/Filho, Cenário 007 já cobertos

## [Resiliência] - Isolar falhas por linha sem interromper o arquivo
- [ ] **Backend:** implementar RN-003 (linha inválida não bloqueia as demais)
- [ ] **Spec:** RN-003, Cenário 010 já cobertos

## [Resiliência] - Propagar bloqueio de Pai para Filhos
- [ ] **Backend:** implementar RN-004 (falha em linha-Pai bloqueia também as Filhas)
- [ ] **Spec:** RN-004, Cenário 008 já cobertos

## [Feedback] - Reportar resultado no terminal
- [ ] **Backend:** implementar output por linha (sucesso com ID / erro com motivo) no terminal
- [ ] **Spec:** UC-001 (Fluxo Principal, passo 6) já coberto

---

## Fora deste Pocket (v1, mas não bloqueante — considerar em iteração futura)
- Fluxo de edição/atualização de Work Packages existentes (PRD seção 5, marcado como desejável não crítico)

## Fora de escopo total da v1 (registrado no PRD)
- GUI/.exe Windows, dashboards, multi-usuário, log em arquivo — v2 ou futuro
