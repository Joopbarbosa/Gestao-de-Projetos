# Infraestrutura

Cada serviço vive isolado na sua própria pasta, com `docker-compose.yml`,
`.env` e dados independentes. Não há mais rede, banco ou cache compartilhado
entre eles — a única ponte entre OpenProject e Nextcloud é o script de sync.

```
Infraestrutura/
├── NextCloud/       # Nextcloud + Postgres + Redis dedicados
├── OpenProject/     # OpenProject (repo git próprio, aninhado)
├── Sync/            # ponte de sincronização OpenProject -> Nextcloud
├── Script OP/       # ferramenta separada, não faz parte desta stack
└── logs/            # apenas logs históricos avulsos (ver nota no fim)
```

## NextCloud/

```bash
cd NextCloud
docker compose up -d      # ou ./start.sh up
docker compose down       # ou ./start.sh down
docker compose logs -f    # ou ./start.sh logs
```

- URL: http://localhost:8091
- Dados em `NextCloud/data/`:
  - `data/nextcloud` — instalação/arquivos do Nextcloud
  - `data/nextcloud_pgdata` — banco Postgres do Nextcloud
- Credenciais/config em `NextCloud/.env` (não versionado)

## OpenProject/

```bash
cd OpenProject
docker compose up -d      # ou ./start.sh up
docker compose down       # ou ./start.sh down
docker compose logs -f    # ou ./start.sh logs
```

- URL: http://localhost:8090
- Dados em `OpenProject/data/`:
  - `data/pgdata` — banco Postgres embutido no OpenProject
  - `data/assets`, `data/files` — assets e anexos
- Config em `OpenProject/.env` (não versionado)
- Backups manuais em `OpenProject/backups/`
- **Esta pasta é um repositório git próprio** (remote separado), por isso não
  é versionada dentro do repositório `Infraestrutura` — só o diretório em si
  aparece como referência.

## Sync/

Sincroniza anexos e documentos do OpenProject para dentro do Nextcloud.

- `Sync/sync_files.py` consulta a API do OpenProject (`Sync/.env` define
  `OPENPROJECT_BASE_URL` e `OPENPROJECT_API_TOKEN`), lê os anexos brutos em
  `../OpenProject/data/assets/files/attachment/file/`, e copia (via
  `docker cp`) para dentro do container `nextcloud_app`, disparando
  `occ files:scan` em seguida.
- Documentos de projeto (sem API v3 disponível) são obtidos via
  `docker exec ... psql` diretamente no Postgres do container
  `openproject_local`.
- Estado da sincronização: `Sync/sync_state.json`.
- Logs: `Sync/logs/sync.log` (execução) e `Sync/logs/sync_cron.log` (cron).
- Roda automaticamente a cada 5 minutos via cron:
  ```
  */5 * * * * /home/joaobarbosa/Documentos/Projetos/Infraestrutura/Sync/sync_files.sh >> /home/joaobarbosa/Documentos/Projetos/Infraestrutura/Sync/logs/sync_cron.log 2>&1
  ```
- Também pode ser executado manualmente: `./Sync/sync_files.sh`
- Requer que ambas as stacks (`NextCloud/` e `OpenProject/`) estejam de pé.

### Estrutura de pastas geradas no Nextcloud

Dentro de `OpenProject Files/`, os arquivos são organizados por projeto:

```
<Projeto>/
├── <Versão>/                  # anexos de work packages, por versão
└── Documentos/
    └── <Categoria>/           # documentos, por categoria
```

Quando a versão de um work package ou a categoria de um documento muda no
OpenProject, o sync move o arquivo correspondente para a nova pasta.

## Subir tudo de uma vez

Não há mais um compose único. Para subir as duas stacks:

```bash
(cd NextCloud && docker compose up -d)
(cd OpenProject && docker compose up -d)
```

## logs/gestao-projetos.log

Log histórico de uma subida antiga da stack unificada (antes da separação),
mantido apenas como registro — não é lido por nenhum script e não pertence
a nenhum serviço isoladamente.
