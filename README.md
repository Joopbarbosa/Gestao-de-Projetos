# Infraestrutura

Infraestrutura local com OpenProject + Nextcloud, integrados via sincronização
automática de anexos/documentos.

## Como subir

```bash
docker compose up -d
```

## Como parar

```bash
docker compose down
```

## Como ver logs

```bash
docker compose logs -f
```

(Também é possível usar `./start.sh {up|down|logs}`.)

## URLs

| Serviço     | URL                     |
|-------------|--------------------------|
| OpenProject | http://localhost:8090    |
| Nextcloud   | http://localhost:8091    |

## Onde ficam os dados

Todos os dados persistentes ficam em `./data/`:

- `data/pgdata` — banco Postgres do OpenProject
- `data/assets` / `data/files` — assets e arquivos do OpenProject
- `data/nextcloud` — instalação/dados do Nextcloud
- `data/nextcloud_pgdata` — banco Postgres do Nextcloud

## Como funciona o sync

O script `sync_files.py` consulta a API do OpenProject, identifica anexos de
work packages e documentos, e copia os arquivos para dentro do container do
Nextcloud (via `docker cp`), disparando um reindex (`occ files:scan`) em
seguida.

Ele roda automaticamente a cada 5 minutos via cron:

```
*/5 * * * * /home/joaobarbosa/Documentos/Projetos/Infraestrutura/sync_files.sh
```

Também pode ser executado manualmente:

```bash
./sync_files.sh
```

Logs da sincronização ficam em `logs/`.

## Estrutura de pastas no Nextcloud

Dentro de `OpenProject Files/`, os arquivos são organizados por projeto:

```
<Projeto>/
├── <Versão>/                  # anexos de work packages, por versão
└── Documentos/
    └── <Categoria>/           # documentos, por categoria
```

Quando a versão de um work package ou a categoria de um documento muda no
OpenProject, o sync move o arquivo correspondente para a nova pasta.
