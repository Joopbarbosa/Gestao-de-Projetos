"""Comunicação com a API v3 do OpenProject."""

import requests


def _mensagem_erro(resp: requests.Response) -> str:
    try:
        corpo = resp.json()
    except ValueError:
        return f"HTTP {resp.status_code}: {resp.text[:200]}"
    mensagem = corpo.get("message")
    if mensagem:
        return f"HTTP {resp.status_code}: {mensagem}"
    return f"HTTP {resp.status_code}: {resp.text[:200]}"


class OpenProjectClient:
    """Cliente HTTP fino para a API v3 do OpenProject. Não decide regra de negócio —
    apenas busca dados (cacheados em memória durante a execução) e cria work packages."""

    def __init__(self, base_url: str, api_token: str, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = ("apikey", api_token)
        self.session.headers.update({"Content-Type": "application/json"})

        self._projetos = None
        self._tipos = None
        self._situacoes = None
        self._prioridades = None
        self._versoes_cache: dict[str, set | None] = {}

    def _get(self, path: str) -> requests.Response:
        return self.session.get(f"{self.base_url}{path}", timeout=self.timeout)

    def test_connection(self) -> tuple[bool, str]:
        try:
            resp = self._get("/api/v3/users/me")
        except requests.RequestException as exc:
            return False, str(exc)
        if resp.status_code == 200:
            return True, ""
        return False, _mensagem_erro(resp)

    def _mapa_nome_href(self, path: str) -> dict:
        resp = self._get(path)
        resp.raise_for_status()
        elementos = resp.json().get("_embedded", {}).get("elements", [])
        return {el["name"]: el["_links"]["self"]["href"] for el in elementos}

    def get_projects(self) -> dict:
        if self._projetos is None:
            self._projetos = self._mapa_nome_href("/api/v3/projects")
        return self._projetos

    def get_types(self) -> dict:
        if self._tipos is None:
            self._tipos = self._mapa_nome_href("/api/v3/types")
        return self._tipos

    def get_statuses(self) -> dict:
        if self._situacoes is None:
            self._situacoes = self._mapa_nome_href("/api/v3/statuses")
        return self._situacoes

    def get_priorities(self) -> dict:
        if self._prioridades is None:
            self._prioridades = self._mapa_nome_href("/api/v3/priorities")
        return self._prioridades

    def get_project_versions(self, projeto_nome: str) -> dict | None:
        """Retorna um mapa nome -> href das versões do projeto, ou None se o projeto não
        existir ou a consulta falhar. Resultado cacheado por nome de projeto."""
        if projeto_nome in self._versoes_cache:
            return self._versoes_cache[projeto_nome]

        projeto_href = self.get_projects().get(projeto_nome)
        if not projeto_href:
            self._versoes_cache[projeto_nome] = None
            return None

        try:
            resp = self._get(f"{projeto_href}/versions")
        except requests.RequestException:
            self._versoes_cache[projeto_nome] = None
            return None

        if resp.status_code != 200:
            self._versoes_cache[projeto_nome] = None
            return None

        elementos = resp.json().get("_embedded", {}).get("elements", [])
        versoes = {el["name"]: el["_links"]["self"]["href"] for el in elementos}
        self._versoes_cache[projeto_nome] = versoes
        return versoes

    def create_work_package(self, payload: dict) -> tuple[bool, dict | str]:
        resp = self.session.post(
            f"{self.base_url}/api/v3/work_packages", json=payload, timeout=self.timeout
        )
        if resp.status_code == 201:
            return True, resp.json()
        return False, _mensagem_erro(resp)
