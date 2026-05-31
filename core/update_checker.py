import os
import requests
import subprocess
from tkinter import messagebox
from version import APP_VERSION
from core.logs import registrar_evento

URL_VERSION = (
    "https://raw.githubusercontent.com/"
    "fiuzafelipe/"
    "Gerador-de-xml-completo-sistema-econect/"
    "main/version.json"
)

def verificar_atualizacao(auto=False):
    try:
        response = requests.get(URL_VERSION, timeout=5)
        if response.status_code != 200:
            return

        dados = response.json()
        versao_online = dados.get("version")
        download_url = dados.get("download_url")

        # =====================================
        # TEM UPDATE
        # =====================================
        if versao_online != APP_VERSION:
            registrar_evento(f"Atualização encontrada: {versao_online}")

            resposta = messagebox.askyesno(
                "Atualização disponível",
                f"Há atualizações disponíveis!\n\n"
                f"Versão atual: {APP_VERSION}\n"
                f"Nova versão: {versao_online}\n\n"
                f"Deseja atualizar agora?"
            )

            if resposta:
                registrar_evento("Iniciando updater...")

                # Exemplo de como deve ficar a chamada no sistema principal:
                # Passamos o executável, a URL de download (sys.argv[1]) e a versão online (sys.argv[2])
                subprocess.Popen(["updater.exe", url_download_zip, versao_online])

                # Fecha o programa principal imediatamente e libera o arquivo no Windows
                os._exit(0)

        else:
            if not auto:
                messagebox.showinfo(
                    "Sistema atualizado",
                    "Não há atualizações disponíveis!\n\nBom uso."
                )

    except Exception as erro:
        registrar_evento(f"Erro ao verificar atualização: {erro}")