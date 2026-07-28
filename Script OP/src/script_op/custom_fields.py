"""Resolução de custom fields (texto -> href de custom_option)."""

from pathlib import Path

import yaml

from script_op.validators import TIPOS_COM_GRAVIDADE

CUSTOM_FIELD_IDS = {
    "sistema": "customField1",
    "modulo": "customField2",
    "gravidade": "customField3",
}

_DEFAULT_MAP_PATH = Path(__file__).resolve().parents[2] / "config" / "custom_fields_map.yaml"


def load_map(caminho: Path | str | None = None) -> dict:
    caminho = Path(caminho) if caminho else _DEFAULT_MAP_PATH
    with caminho.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_href(mapa: dict, categoria: str, texto: str) -> str:
    href = mapa.get(categoria, {}).get(texto)
    if not href:
        raise ValueError(
            f"Href não configurado para {categoria}='{texto}' em config/custom_fields_map.yaml"
        )
    return href


def resolve_custom_fields(mapa: dict, tipo: str, sistema: str, modulo: str, gravidade: str) -> dict:
    """Monta o trecho de `_links` do payload de criação para os custom fields da linha."""
    links = {
        CUSTOM_FIELD_IDS["sistema"]: {"href": resolve_href(mapa, "sistema", sistema)},
        CUSTOM_FIELD_IDS["modulo"]: {"href": resolve_href(mapa, "modulo", modulo)},
    }
    if tipo in TIPOS_COM_GRAVIDADE:
        links[CUSTOM_FIELD_IDS["gravidade"]] = {"href": resolve_href(mapa, "gravidade", gravidade)}
    return links
