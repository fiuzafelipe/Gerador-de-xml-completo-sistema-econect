import os
import sys  # Importado para usar o encerramento limpo via sys.exit(0)
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
        download_url = dados.get("download_url")  # Var oficial capturada do JSON

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

                try:
                    # 🚀 PASSO 1: Salva o arquivo local temporário como Plano B de redundância
                    with open("ultima_versao.txt", "w", encoding="utf-8") as f:
                        f.write(str(versao_online))
                    
                    caminho_updater = "updater.exe"

                    if os.path.exists(caminho_updater):
                        # 🚀 PASSO 2: Correção da variável antiga 'url_download_zip' para 'download_url'
                        # Passando os dois argumentos que o novo updater_launcher.py precisa
                        subprocess.Popen([caminho_updater, download_url, str(versao_online)], shell=True)
                        
                        # 🚀 PASSO 3: Encerramento limpo liberando o handle do executável pai
                        sys.exit(0)
                    else:
                        messagebox.showerror(
                            "Erro de Atualização", 
                            "O arquivo executável 'updater.exe' não foi localizado na raiz do sistema."
                        )
                
                except Exception as erro_disparo:
                    registrar_evento(f"Falha ao invocar o processo do atualizador: {erro_disparo}")
                    messagebox.showerror(
                        "Erro Crítico", 
                        f"Não foi possível iniciar o atualizador de pacotes:\n{str(erro_disparo)}"
                    )

        else:
            if not auto:
                messagebox.showinfo(
                    "Sistema atualizado",
                    "Não há atualizações disponíveis!\n\nBom uso."
                )

    except Exception as erro:
        registrar_evento(f"Erro ao verificar atualização: {erro}")