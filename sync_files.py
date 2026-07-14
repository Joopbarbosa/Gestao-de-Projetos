#!/usr/bin/env python3
"""Sincroniza anexos do OpenProject para o Nextcloud.

Dois fluxos independentes:

1. Work packages: para cada projeto, percorre as work packages via API v3,
   identifica os anexos e a versão associada, e copia o arquivo
   correspondente de ./data/assets/files/attachment/file/<id>/<nome> para
   ./data/nextcloud/data/admin/files/OpenProject Files/<Projeto>/<Versão>/<nome>.

2. Documentos de projeto: a API v3 desta instalação do OpenProject não expõe
   um recurso de "documents" (não está listado no discovery de /api/v3, e a
   única rota existente é a HTML clássica /projects/:id/documents, que exige
   sessão de login e não aceita autenticação por API key). Por isso, os
   documentos e seus anexos são obtidos consultando diretamente o Postgres
   embutido no container do OpenProject via `docker exec ... psql`. Os
   arquivos são copiados para
   .../OpenProject Files/<Projeto>/Documentos/<Categoria>/<nome>.

Em ambos os fluxos, a cópia é feita via `docker cp` (e não escrita direta no
host) porque o diretório de dados do Nextcloud pertence a www-data:www-data e
o usuário que roda este script não tem permissão de escrita nele. Depois de
copiar, os arquivos são ajustados para www-data:www-data e o Nextcloud é
instruído a reindexar a pasta via `occ files:scan`. Quando a versão (work
package) ou a categoria (documento) de um anexo já sincronizado muda, o
arquivo é movido dentro do container em vez de recopiado.
"""
from __future__ import annotations

import json
import logging
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
STATE_FILE = BASE_DIR / "data" / "sync_state.json"
LOG_FILE = BASE_DIR / "logs" / "sync.log"
SOURCE_DIR = BASE_DIR / "data" / "assets" / "files" / "attachment" / "file"

OPENPROJECT_API = "http://localhost:8090/api/v3"
NEXTCLOUD_CONTAINER = "nextcloud_app"
NEXTCLOUD_DEST_BASE = "/var/www/html/data/admin/files/OpenProject Files"
NEXTCLOUD_SCAN_PATH = "/admin/files/OpenProject Files"

# Postgres embutido na imagem all-in-one do OpenProject (não exposto fora do
# container). Usado só para ler documentos/anexos, que a API v3 não expõe.
OPENPROJECT_CONTAINER = "openproject_local"
OPENPROJECT_DB_HOST = "127.0.0.1"
OPENPROJECT_DB_USER = "openproject"
OPENPROJECT_DB_NAME = "openproject"
OPENPROJECT_DB_PASSWORD = "openproject"

PAGE_SIZE = 100

DOCUMENTS_QUERY = """
SELECT json_agg(row_to_json(sub)) FROM (
    SELECT d.id AS document_id, d.project_id, d.title,
           ec.name AS category, a.id AS attachment_id, a.filename AS file_name
    FROM documents d
    JOIN enumerations ec ON ec.id = d.category_id
    JOIN attachments a ON a.container_id = d.id AND a.container_type = 'Document'
) sub;
"""


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def setup_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def sanitize(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r'[\/\\\0]', "-", name)
    name = re.sub(r"\s+", " ", name)
    return name or "Sem-nome"


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            logging.warning("Arquivo de estado corrompido, recriando: %s", STATE_FILE)
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True))
    tmp.replace(STATE_FILE)


def api_get(session: requests.Session, path: str, params: dict | None = None) -> dict:
    resp = session.get(f"{OPENPROJECT_API}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def iter_collection(session: requests.Session, path: str):
    offset = 1
    while True:
        data = api_get(session, path, params={"pageSize": PAGE_SIZE, "offset": offset})
        elements = data.get("_embedded", {}).get("elements", [])
        yield from elements
        total = data.get("total", 0)
        if not elements or offset * PAGE_SIZE >= total:
            break
        offset += 1


def docker_mkdir_p(container_path: str) -> bool:
    result = subprocess.run(
        ["docker", "exec", NEXTCLOUD_CONTAINER, "mkdir", "-p", container_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        logging.error("Falha ao criar diretório %s no container: %s", container_path, result.stderr.strip())
        return False
    return True


def docker_cp(src: Path, container_dest: str) -> bool:
    result = subprocess.run(
        ["docker", "cp", str(src), f"{NEXTCLOUD_CONTAINER}:{container_dest}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        logging.error("Falha ao copiar %s -> %s: %s", src, container_dest, result.stderr.strip())
        return False
    return True


def docker_mv(container_src: str, container_dest: str) -> bool:
    result = subprocess.run(
        ["docker", "exec", NEXTCLOUD_CONTAINER, "mv", container_src, container_dest],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        logging.error("Falha ao mover %s -> %s: %s", container_src, container_dest, result.stderr.strip())
        return False
    return True


def fetch_documents_with_attachments() -> list[dict]:
    """Busca documentos de projeto e seus anexos direto no Postgres do OpenProject.

    Necessário porque a API v3 não expõe um recurso de documentos (ver
    docstring do módulo).
    """
    result = subprocess.run(
        [
            "docker", "exec", "-e", f"PGPASSWORD={OPENPROJECT_DB_PASSWORD}",
            OPENPROJECT_CONTAINER, "psql",
            "-h", OPENPROJECT_DB_HOST, "-U", OPENPROJECT_DB_USER, "-d", OPENPROJECT_DB_NAME,
            "-t", "-A", "-c", DOCUMENTS_QUERY,
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        logging.error("Falha ao consultar documentos no banco do OpenProject: %s", result.stderr.strip())
        return []

    raw = result.stdout.strip()
    if not raw:
        return []

    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        logging.error("Resposta inesperada do psql ao buscar documentos: %s (saída: %r)", exc, raw[:200])
        return []

    return rows or []


def main() -> int:
    setup_logging()
    env = load_env(ENV_FILE)
    token = env.get("OPENPROJECT_API_TOKEN")
    if not token:
        logging.error(
            "OPENPROJECT_API_TOKEN não encontrado em %s. "
            "A API v3 do OpenProject não aceita usuário/senha via Basic Auth, "
            "apenas 'apikey:<token>'. Gere um token e adicione essa linha ao .env.",
            ENV_FILE,
        )
        return 1

    session = requests.Session()
    session.auth = HTTPBasicAuth("apikey", token)

    state = load_state()
    copied: list[str] = []
    moved: list[str] = []
    errors: list[str] = []

    try:
        projects = list(iter_collection(session, "/projects"))
    except requests.RequestException as exc:
        logging.error("Falha ao conectar na API do OpenProject: %s", exc)
        return 1

    for project in projects:
        project_id = project["id"]
        project_name = sanitize(project.get("name") or f"project-{project_id}")

        try:
            work_packages = iter_collection(session, f"/projects/{project_id}/work_packages")
        except requests.RequestException as exc:
            logging.error("Falha ao listar work packages do projeto %s: %s", project_name, exc)
            errors.append(f"project:{project_id}")
            continue

        for wp in work_packages:
            wp_id = wp["id"]
            version_link = (wp.get("_links") or {}).get("version") or {}
            version_name = sanitize(version_link.get("title") or "Sem Versao")

            try:
                attachments = api_get(session, f"/work_packages/{wp_id}/attachments")
            except requests.RequestException as exc:
                logging.error("Falha ao buscar anexos da work package %s: %s", wp_id, exc)
                errors.append(f"wp:{wp_id}")
                continue

            for att in attachments.get("_embedded", {}).get("elements", []):
                att_id = str(att["id"])
                file_name = att["fileName"]

                if att_id in state:
                    entry = state[att_id]
                    old_version = entry.get("version")
                    if old_version == version_name:
                        continue  # já sincronizado e sem mudança de versão

                    old_dest_path = entry.get("dest_path")
                    if not old_dest_path:
                        logging.warning(
                            "Anexo %s sem dest_path salvo no state, não é possível mover; pulando.",
                            att_id,
                        )
                        continue

                    new_dest_dir = f"{NEXTCLOUD_DEST_BASE}/{project_name}/{version_name}"
                    new_dest_path = f"{new_dest_dir}/{file_name}"

                    if not docker_mkdir_p(new_dest_dir):
                        errors.append(att_id)
                        continue
                    if not docker_mv(old_dest_path, new_dest_path):
                        errors.append(att_id)
                        continue

                    logging.info(
                        "Anexo %s movido: versão '%s' -> '%s' (%s -> %s)",
                        att_id, old_version, version_name, old_dest_path, new_dest_path,
                    )
                    moved.append(att_id)
                    entry["version"] = version_name
                    entry["project"] = project_name
                    entry["dest_path"] = new_dest_path
                    entry["moved_at"] = datetime.now(timezone.utc).isoformat()
                    continue

                src = SOURCE_DIR / att_id / file_name
                if not src.exists():
                    logging.warning(
                        "Anexo %s (%s) referenciado na API mas ausente em disco: %s",
                        att_id, file_name, src,
                    )
                    continue

                dest_dir = f"{NEXTCLOUD_DEST_BASE}/{project_name}/{version_name}"
                dest_path = f"{dest_dir}/{file_name}"

                if not docker_mkdir_p(dest_dir):
                    errors.append(att_id)
                    continue
                if not docker_cp(src, dest_path):
                    errors.append(att_id)
                    continue

                logging.info(
                    "Anexo %s copiado: %s -> %s / %s / %s",
                    att_id, file_name, project_name, version_name, file_name,
                )
                copied.append(att_id)
                state[att_id] = {
                    "file_name": file_name,
                    "project": project_name,
                    "version": version_name,
                    "work_package_id": wp_id,
                    "dest_path": dest_path,
                    "synced_at": datetime.now(timezone.utc).isoformat(),
                }

    # --- Documentos de projeto (não vinculados a work packages) ---
    project_names = {p["id"]: sanitize(p.get("name") or f"project-{p['id']}") for p in projects}
    documents = fetch_documents_with_attachments()

    for doc in documents:
        project_id = doc.get("project_id")
        project_name = project_names.get(project_id)
        if project_name is None:
            logging.warning(
                "Documento %s pertence ao projeto id=%s, que não está na lista de projetos da API; pulando.",
                doc.get("document_id"), project_id,
            )
            continue

        category_name = sanitize(doc.get("category") or "Other")
        doc_id = doc.get("document_id")
        att_id = str(doc.get("attachment_id"))
        file_name = doc.get("file_name")
        state_key = f"doc_{att_id}"

        if state_key in state:
            entry = state[state_key]
            old_category = entry.get("category")
            if old_category == category_name:
                continue  # já sincronizado e sem mudança de categoria

            old_dest_path = entry.get("dest_path")
            if not old_dest_path:
                logging.warning(
                    "Documento (anexo %s) sem dest_path salvo no state, não é possível mover; pulando.",
                    att_id,
                )
                continue

            new_dest_dir = f"{NEXTCLOUD_DEST_BASE}/{project_name}/Documentos/{category_name}"
            new_dest_path = f"{new_dest_dir}/{file_name}"

            if not docker_mkdir_p(new_dest_dir):
                errors.append(state_key)
                continue
            if not docker_mv(old_dest_path, new_dest_path):
                errors.append(state_key)
                continue

            logging.info(
                "Documento %s (anexo %s) movido: categoria '%s' -> '%s' (%s -> %s)",
                doc_id, att_id, old_category, category_name, old_dest_path, new_dest_path,
            )
            moved.append(state_key)
            entry["category"] = category_name
            entry["project"] = project_name
            entry["dest_path"] = new_dest_path
            entry["moved_at"] = datetime.now(timezone.utc).isoformat()
            continue

        src = SOURCE_DIR / att_id / file_name
        if not src.exists():
            logging.warning(
                "Anexo de documento %s (%s) referenciado no banco mas ausente em disco: %s",
                att_id, file_name, src,
            )
            continue

        dest_dir = f"{NEXTCLOUD_DEST_BASE}/{project_name}/Documentos/{category_name}"
        dest_path = f"{dest_dir}/{file_name}"

        if not docker_mkdir_p(dest_dir):
            errors.append(state_key)
            continue
        if not docker_cp(src, dest_path):
            errors.append(state_key)
            continue

        logging.info(
            "Documento %s (anexo %s) copiado: %s -> %s / Documentos / %s / %s",
            doc_id, att_id, file_name, project_name, category_name, file_name,
        )
        copied.append(state_key)
        state[state_key] = {
            "file_name": file_name,
            "project": project_name,
            "category": category_name,
            "document_id": doc_id,
            "dest_path": dest_path,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }

    if copied or moved:
        save_state(state)
        if copied:
            logging.info("%d arquivo(s) novo(s) sincronizado(s).", len(copied))
        if moved:
            logging.info("%d arquivo(s) movido(s) por mudança de versão/categoria.", len(moved))

        logging.info("Ajustando permissões...")
        chown = subprocess.run(
            ["docker", "exec", NEXTCLOUD_CONTAINER, "chown", "-R", "www-data:www-data", NEXTCLOUD_DEST_BASE],
            capture_output=True, text=True,
        )
        if chown.returncode != 0:
            logging.error("Falha ao ajustar permissões (chown): %s", chown.stderr.strip())

        logging.info("Rodando occ files:scan...")
        scan = subprocess.run(
            ["docker", "exec", NEXTCLOUD_CONTAINER, "php", "occ", "files:scan", f"--path={NEXTCLOUD_SCAN_PATH}"],
            capture_output=True, text=True,
        )
        if scan.returncode != 0:
            logging.error("Falha no occ files:scan: %s", scan.stderr.strip())
        else:
            logging.info("occ files:scan concluído com sucesso.")
    else:
        logging.info("Nenhum arquivo novo ou movido para sincronizar.")

    if errors:
        logging.warning("Execução concluída com %d erro(s): %s", len(errors), ", ".join(errors))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
