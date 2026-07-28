"""Validações de linha do CSV (RN-001, RN-002, RN-005)."""

from dataclasses import dataclass, field

TIPOS_COM_GRAVIDADE = {"Bug", "Tech Debt"}

CAMPOS_OBRIGATORIOS = [
    "assunto",
    "tipo",
    "situacao",
    "prioridade",
    "versao",
    "modulo",
    "sistema",
    "projeto",
]


@dataclass
class ContextoValidacao:
    """Valores válidos no momento da execução, obtidos da API do OpenProject e do
    config/custom_fields_map.yaml — nunca hardcoded, para não divergir da instância real."""

    tipos_validos: set
    situacoes_validas: set
    prioridades_validas: set
    projetos_validos: set
    sistemas_validos: set
    modulos_validos: set
    gravidades_validas: set
    versoes_por_projeto: dict = field(default_factory=dict)


def validar_linha(dados: dict, ctx: ContextoValidacao) -> list[str]:
    """Retorna lista de erros da linha (vazia se válida). RN-003: o chamador decide
    o que fazer com a linha inválida, aqui só reportamos os motivos."""
    erros = []

    for campo in CAMPOS_OBRIGATORIOS:
        if not dados.get(campo):
            erros.append(f"Campo '{campo}' é obrigatório")

    tipo = dados.get("tipo")
    if tipo and tipo not in ctx.tipos_validos:
        erros.append(f"Tipo '{tipo}' inválido")

    situacao = dados.get("situacao")
    if situacao and situacao not in ctx.situacoes_validas:
        erros.append(f"Situação '{situacao}' inválida")

    prioridade = dados.get("prioridade")
    if prioridade and prioridade not in ctx.prioridades_validas:
        erros.append(f"Prioridade '{prioridade}' inválida")

    modulo = dados.get("modulo")
    if modulo and modulo not in ctx.modulos_validos:
        erros.append(f"Módulo '{modulo}' inválido")

    sistema = dados.get("sistema")
    if sistema and sistema not in ctx.sistemas_validos:
        erros.append(f"Sistema '{sistema}' inválido")

    projeto = dados.get("projeto")
    if projeto and projeto not in ctx.projetos_validos:
        erros.append(f"Projeto '{projeto}' inválido")

    gravidade = dados.get("gravidade", "")
    if tipo in TIPOS_COM_GRAVIDADE:
        if gravidade not in ctx.gravidades_validas:
            erros.append(
                f"Gravidade obrigatória para tipo '{tipo}' "
                f"(valores válidos: {', '.join(sorted(ctx.gravidades_validas))})"
            )
    elif tipo:
        if gravidade not in ("", "-"):
            erros.append(f"Gravidade deve ser '-' para tipo '{tipo}'")

    versao = dados.get("versao")
    if versao and projeto in ctx.projetos_validos:
        versoes_do_projeto = ctx.versoes_por_projeto.get(projeto)
        if versoes_do_projeto is None:
            erros.append(
                f"Não foi possível validar a Versão '{versao}' — "
                f"falha ao consultar versões do projeto '{projeto}'"
            )
        elif versao not in versoes_do_projeto:
            erros.append(f"Versão '{versao}' não existe no projeto '{projeto}'")

    return erros
