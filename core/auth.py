# core/auth.py 

# Lista de usuários autorizados
USUARIOS = {
    "Cliente": {"senha": "123456", "nivel": "user"},
    "Felipe Fiuza": {"senha": "ABC,123@", "nivel": "admin"},
    "Leandro": {"senha": "738495", "nivel": "admin"},
    "Italo": {"senha": "naosei123@", "nivel": "admin"},
    "Julio": {"senha": "062725@Jl", "nivel": "admin"},
    "Raphael": {"senha": "38845331", "nivel": "admin"},
    "Gabriel": {"senha": "290819", "nivel": "admin"},
    "Micael": {"senha": "2546", "nivel": "admin"},
    "Francis": {"senha": "xml@#2026", "nivel": "admin"},
    "Bruno": {"senha": "abc,123", "nivel": "admin"}
}


def validar_usuario(usuario, senha):
    """
    Valida usuário e senha.
    Retorna True se estiver correto.
    """
    if usuario in USUARIOS:
        return USUARIOS[usuario]["senha"] == senha

    return False


def obter_nivel(usuario):
    """
    Retorna o nível do usuário.
    """
    return USUARIOS.get(usuario, {}).get("nivel", "user")