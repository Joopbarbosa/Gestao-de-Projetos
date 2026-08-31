"""Validações de linha do CSV (RN-002, RN-005)."""

from dataclasses import dataclass, field

PRIORIDADES_PT = {
    "Baixa": "Low",
    "Normal": "Normal",
    "Alta": "High",
    "Urgente": "Immediate",
}
PRIORIDADES_EN_PARA_PT = {ingles: pt for pt, ingles in PRIORIDADES_PT.items()}

CAMPOS_OBRIGATORIOS = [
    "assunto",
    "tipo",
    "situacao",
    "prioridade",
    "versao",
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
    if prioridade:
        prioridade_pt = PRIORIDADES_EN_PARA_PT.get(prioridade, prioridade)
        if prioridade not in ctx.prioridades_validas and prioridade_pt not in ctx.prioridades_validas:
            erros.append(f"Prioridade '{prioridade}' inválida")

    sistema = dados.get("sistema")
    if sistema and sistema not in ctx.sistemas_validos:
        erros.append(f"Sistema '{sistema}' inválido")

    projeto = dados.get("projeto")
    if projeto and projeto not in ctx.projetos_validos:
        erros.append(f"Projeto '{projeto}' inválido")

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


def resolver_prioridade(prioridade: str) -> str:
    """A API do OpenProject usa os nomes de prioridade em português (Baixa/Normal/Alta/Urgente).
    Mantém compatibilidade retroativa com CSVs legados que ainda usam os valores em inglês."""
    return PRIORIDADES_EN_PARA_PT.get(prioridade, prioridade)
