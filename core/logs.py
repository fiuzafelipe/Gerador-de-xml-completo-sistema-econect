# Salvar e carregar Logs - core/logs.py

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

# Cria pasta automaticamente
os.makedirs(APPDATA_DIR, exist_ok=True)


def carregar_logs():
    """
    Carrega logs do sistema.
    """

    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    except Exception as erro:
        print(f"Erro ao carregar logs: {erro}")
        return []


def registrar_evento(mensagem):
    """
    Registra evento no sistema.
    """
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    print(f"[{data}] {mensagem}")

    try:

        logs_historico = carregar_logs()

        novo_log = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "evento": mensagem
        }

        logs_historico.append(novo_log)

        with open(LOG_FILE, "w", encoding="utf-8") as arquivo:

            json.dump(
                logs_historico,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    except Exception as erro:
        print(f"Erro ao registrar log: {erro}")