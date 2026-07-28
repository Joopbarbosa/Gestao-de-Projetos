"""Formatação de saída no terminal — única camada de apresentação do Script OP."""


def print_line_success(linha: int, wp_id: int) -> None:
    print(f"[OK]   Linha {linha}: work package #{wp_id} criado com sucesso")


def print_line_error(linha: int, motivo: str) -> None:
    print(f"[ERRO] Linha {linha}: {motivo}")


def print_erro_conexao(motivo: str) -> None:
    print(f"[ERRO] Falha ao conectar com a API do OpenProject: {motivo}")
    print("Nenhuma linha foi processada.")


def print_erro_configuracao(motivo: str) -> None:
    print(f"[ERRO] Configuração inválida: {motivo}")


def print_summary(total: int, sucesso: int, erro: int) -> None:
    print("")
    print("Resumo:")
    print(f"  Total de linhas: {total}")
    print(f"  Sucesso: {sucesso}")
    print(f"  Erro: {erro}")
