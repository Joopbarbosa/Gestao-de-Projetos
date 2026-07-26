# DECISOES_GLOBAIS.md

> Registro de decisões arquiteturais e de padrões que se aplicam a todos os projetos/subprojetos dentro do repositório `Gestao-de-Projetos`.

---

## Arquitetura

- O repositório `Gestao-de-Projetos` hospeda tanto a infraestrutura base (OpenProject, Nextcloud, PostgreSQL, Redis via `docker-compose.yml` na raiz) quanto ferramentas auxiliares independentes (ex: `Script OP/`), organizadas em pastas próprias na raiz do repositório.
- Ferramentas auxiliares que não são serviços de longa duração (scripts, utilitários de linha de comando) **não entram no `docker-compose.yml` principal** — rodam à parte, com seu próprio ambiente isolado (venv Python, por exemplo), para não acoplar o ciclo de vida delas ao stack de infraestrutura.

## Padrões de Interface

- CLIs Python usam **Typer** (ou Click) para experiência de linha de comando mais robusta que `argparse` puro.

## Contratos de API

- Integrações com a API v3 do OpenProject devem tratar valores de campos-lista (custom fields) via `href` de `custom_option`, nunca por texto puro — conforme descoberto na integração do Script OP.

## OpenProject

- Instância local: `http://localhost:8090`, container `openproject_local`.
- Autenticação via API token (Basic Auth, `apikey:TOKEN`), nunca hardcoded — sempre via variável de ambiente.

---

## Tabela de Registro

| Data | Decisão | Projeto/Subprojeto de origem |
|---|---|---|
| 26/07/2026 | Ferramentas auxiliares (scripts) vivem em pastas próprias na raiz do repo, fora do docker-compose principal | Script OP |
| 26/07/2026 | CLIs Python usam Typer | Script OP |
| 26/07/2026 | Custom fields do OpenProject são resolvidos via mapa estático texto→href, em arquivo de configuração separado do código | Script OP |
