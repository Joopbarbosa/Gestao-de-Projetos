"""Entrypoint CLI (Typer) do Script OP."""

import os
from pathlib import Path

import typer
from dotenv import load_dotenv

from script_op import api_client, csv_parser, custom_fields, output
from script_op.validators import ContextoValidacao, resolver_prioridade, validar_linha

app = typer.Typer()


def _montar_contexto(client: api_client.OpenProjectClient, mapa_custom_fields: dict) -> ContextoValidacao:
    return ContextoValidacao(
        tipos_validos=set(client.get_types()),
        situacoes_validas=set(client.get_statuses()),
        prioridades_validas=set(client.get_priorities()),
        projetos_validos=set(client.get_projects()),
        sistemas_validos=set(mapa_custom_fields.get("sistema", {})),
        versoes_por_projeto={},
    )


def _montar_payload(dados: dict, client: api_client.OpenProjectClient, mapa_custom_fields: dict) -> dict:
    versoes = client.get_project_versions(dados["projeto"]) or {}
    links = {
        "type": {"href": client.get_types()[dados["tipo"]]},
        "status": {"href": client.get_statuses()[dados["situacao"]]},
        "priority": {"href": client.get_priorities()[resolver_prioridade(dados["prioridade"])]},
        "project": {"href": client.get_projects()[dados["projeto"]]},
        "version": {"href": versoes[dados["versao"]]},
    }
    links.update(custom_fields.resolve_custom_fields(mapa_custom_fields, dados["sistema"]))

    payload = {"subject": dados["assunto"], "_links": links}
    if dados.get("descricao"):
        payload["description"] = {"raw": dados["descricao"]}
    return payload


@app.command()
def importar(caminho_csv: Path = typer.Argument(..., help="Caminho do arquivo CSV a importar")):
    """Cria work packages em lote no OpenProject a partir de um CSV."""
    load_dotenv()
    base_url = os.environ.get("OPENPROJECT_BASE_URL")
    token = os.environ.get("OPENPROJECT_API_TOKEN")
    if not base_url or not token:
        output.print_erro_configuracao(
            "OPENPROJECT_BASE_URL e OPENPROJECT_API_TOKEN precisam estar definidos no .env"
        )
        raise typer.Exit(code=1)

    client = api_client.OpenProjectClient(base_url, token)

    conectado, motivo = client.test_connection()
    if not conectado:
        output.print_erro_conexao(motivo)
        raise typer.Exit(code=1)

    linhas = csv_parser.ler_csv(caminho_csv)
    mapa_custom_fields = custom_fields.load_map()
    ctx = _montar_contexto(client, mapa_custom_fields)

    sucesso = 0
    erro = 0

    for item in linhas:
        numero = item["linha"]
        dados = item["dados"]

        projeto = dados.get("projeto")
        if projeto in ctx.projetos_validos and projeto not in ctx.versoes_por_projeto:
            ctx.versoes_por_projeto[projeto] = client.get_project_versions(projeto)

        erros = validar_linha(dados, ctx)
        if erros:
            erro += 1
            output.print_line_error(numero, "; ".join(erros))
            continue

        try:
            payload = _montar_payload(dados, client, mapa_custom_fields)
        except ValueError as exc:
            erro += 1
            output.print_line_error(numero, str(exc))
            continue

        criado, resultado = client.create_work_package(payload)
        if criado:
            sucesso += 1
            output.print_line_success(numero, resultado["id"])
        else:
            erro += 1
            output.print_line_error(numero, resultado)

    output.print_summary(len(linhas), sucesso, erro)


if __name__ == "__main__":
    app()
