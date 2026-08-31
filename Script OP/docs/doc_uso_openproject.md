# Documentação de Uso do OpenProject — Pense Software

> Base de referência para uso diário do OpenProject e para o script de criação em lote de work packages via CSV.
> Instância: `http://localhost:8090` (container `openproject_local`)

---

## 1. Projetos ativos

Workspace: **Pense Software**

| Projeto |
|---|
| Pense e Precifique |
| Processos Operacionais |
| Pense Software |

> Campo variável por tarefa — sempre indicado manualmente no CSV.

---

## 2. Tipos de work package

| Tipo | É marco? |
|---|---|
| Task | não |
| Epic | sim |
| Feature | não |
| Refactor | não |
| Doc | não |
| Bug | não |
| Tech Debt | não |
| Infra | não |

---

## 3. Situação (Status)

| Situação | % conclusão | Fechado? |
|---|---|---|
| BackLog *(padrão)* | 0 | não |
| Viavel | 10 | não |
| Prioridade | 25 | não |
| Em desenvolvimento | 30 | não |
| Com Pendência | 0 | não |
| Em teste | 65 | não |
| Correção | 0 | não |
| Pronto para commitar | 90 | não |
| Finalizado | 100 | **sim** |
| Resolvido anteriormente | 100 | **sim** |
| Cancelado | 0 | **sim** |

---

## 4. Prioridade × Gravidade

Dois conceitos distintos, não redundantes:

- **Prioridade** (campo nativo do OpenProject) → **urgência de fazer** a tarefa. Aplica-se a todos os tipos.
- **Gravidade** (campo customizado) → **impacto do bug**. Aplica-se apenas a **Bug** e **Tech Debt**.

---

## 4.1 Prioridade — valores nativos

> A UI do OpenProject exibe as prioridades em português. O CSV deve usar os valores em português abaixo — o script converte automaticamente para o valor em inglês esperado pela API. Valores em inglês no CSV continuam funcionando (compatibilidade retroativa).

| Valor no CSV (português) | Valor na API (inglês) |
|---|---|
| Baixa *(padrão)* | Low |
| Normal | Normal |
| Alta | High |
| Urgente | Immediate |

---

## 5. Campos personalizados (custom fields)

### 5.1 Gravidade
- Formato: Lista (seleção única)
- Obrigatório: sim
- **Habilitado apenas para**: Bug, Tech Debt
- Para os demais tipos (Task, Epic, Feature, Refactor, Doc, Infra): usar valor **"-"**

| Valor |
|---|
| Critico |
| Grave |
| Medio |
| Baixo |
| - *(usar quando o tipo não for Bug/Tech Debt)* |

### 5.2 Sistema
- Formato: Lista (seleção única)
- Obrigatório: sim
- Habilitado para: todos os tipos, todos os projetos
- Padrão: **Back/Front**

| Valor |
|---|
| Back/Front *(padrão)* |
| BackEnd |
| FrontEnd |
| Processual |
| Banco de Dados |
| Mobile |

---

## 6. Versão

Campo nativo do OpenProject (entidade "Versions" do projeto). **Varia por tarefa** — sempre indicado manualmente, sem valor padrão fixo.

Exemplos de versões existentes no projeto Pense e Precifique: Backlog, Pendências, v0.5, v0.6, v0.6.1, v0.6.2, v0.6.3, v0.7.

---

## 7. Regras de validação (para o script de import)

Ao processar uma linha do CSV, o script deve validar:

1. **Tipo** deve ser um dos 8 valores válidos (seção 2).
2. **Situação** deve ser um dos 12 valores válidos (seção 3).
3. **Prioridade** deve ser um dos valores em português: Baixa *(padrão)*, Normal, Alta, Urgente (valores em inglês também são aceitos por compatibilidade — ver seção 4.1).
4. **Gravidade**:
   - Se Tipo ∈ {Bug, Tech Debt} → obrigatório, valor ∈ {Critico, Grave, Medio, Baixo}.
   - Se Tipo ∉ {Bug, Tech Debt} → usar "-".
5. **Sistema** obrigatório, valor deve pertencer à lista da seção 5.2.
6. **Projeto** obrigatório, deve ser um dos projetos ativos (seção 1).
7. **Versão** obrigatório apenas se aplicável ao fluxo da tarefa — validar contra as versões existentes do projeto informado (via API, já que a lista muda com o tempo).

> Custom fields usam sintaxe própria na API v3 (`customField<ID>`), diferente dos campos nativos. IDs **confirmados via API** (`GET /api/v3/work_packages/{id}`, campo `_links`):
> - Sistema → `customField1` — ex: `{"title": "Back/Front", "href": "/api/v3/custom_options/1"}`
> - Módulo (`customField2`) foi removido do OpenProject — confirmado via API em 2026-08-30, não usar mais no script.
> - Gravidade → `customField3` — ex: `{"title": "Medio", "href": "/api/v3/custom_options/21"}`; retorna `{"href": null, "title": null}` quando o tipo não usa o campo (ex: Epic)
>
> Valores de campos de lista vêm em `_links.customFieldN`, não em `attributes` direto — importante pro script: ao **criar** um work package via API, o payload de escrita usa `_links.customFieldN.href` apontando pro `custom_option` desejado (ex: `/api/v3/custom_options/21`), não o texto puro.

---

## 8. Campos do CSV (v1)

```
Assunto, Descrição, Tipo, Situação, Prioridade, Versão, Sistema, Gravidade, Projeto
```

---

## 9. Próximos passos

- [ ] Puxar `/api/v3/custom_options` completo para mapear texto → ID de todos os valores de Sistema e Gravidade — necessário pro script converter texto do CSV → href da API
- [ ] Escrever script Python (CSV → OpenProject API v3)
- [ ] v2: dashboards de bugs (somente leitura)
- [ ] Futuro: GUI/.exe para Windows
