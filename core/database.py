# =========================================================
# CONEXÃO MYSQL
# core/database.py 
# =========================================================

import pymysql


# =========================================================
# CONECTAR MYSQL
# =========================================================

def conectar_mysql(
    host,
    port,
    user,
    password,
    database
):
    """
    Cria conexão com banco MySQL.
    """

    try:

        conexao = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            connect_timeout=15,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

        print("MySQL conectado com sucesso.")

        return conexao

    except pymysql.MySQLError as erro:

        print(
            f"Erro ao conectar no MySQL: {erro}"
        )

        return None

    except Exception as erro:

        print(
            f"Erro inesperado no MySQL: {erro}"
        )

        return None