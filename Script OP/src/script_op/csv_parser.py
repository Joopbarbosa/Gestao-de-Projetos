"""Parsing e leitura do CSV de entrada."""

import csv
from pathlib import Path

COLUNAS_ESPERADAS = [
    "assunto",
    "descricao",
    "tipo",
    "situacao",
    "prioridade",
    "versao",
    "sistema",
    "projeto",
]


def ler_csv(caminho: Path | str) -> list[dict]:
    """Lê o CSV e retorna uma lista de `{"linha": N, "dados": {...}}`, uma por linha de
    dados (N começa em 1 para a primeira linha após o cabeçalho). A coluna `pai_linha`,
    se presente, é ignorada — hierarquia Pai/Filho não é suportada nesta v0."""
    caminho = Path(caminho)
    linhas = []
    with caminho.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for numero, row in enumerate(reader, start=1):
            dados = {coluna: (row.get(coluna) or "").strip() for coluna in COLUNAS_ESPERADAS}
            linhas.append({"linha": numero, "dados": dados})
    return linhas
