## Salvar e carregar Logs - core/logs.py

import json
import os
from datetime import datetime

# Diretório da aplicação
APPDATA_DIR = os.path.join(
    os.getenv("APPDATA") or os.getcwd(),
    "XML"
)

# Arquivo de logs
LOG_FILE = os.path.join(APPDATA_DIR, "logs_sistema.json")

# Garante criação da pasta
os.makedirs(APPDATA_DIR, exist_ok=True)


def carregar_logs():
    """
    Carrega logs salvos do sistema.
    """

    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as arquivo:
            data = json.load(arquivo)

        return data.get("logs", [])

    except Exception as erro:
        print(f"Erro ao carregar logs: {erro}")
        return []


def registrar_evento(usuario, logs_historico, mensagem):
    """
    Registra evento no histórico do sistema.
    """

    try:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        logs_historico.append(
            f"[{timestamp}] Usuário: {usuario} | {mensagem}"
        )

        with open(LOG_FILE, "w", encoding="utf-8") as arquivo:

            json.dump(
                {"logs": logs_historico},
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    except Exception as erro:
        print(f"Erro ao registrar log: {erro}")