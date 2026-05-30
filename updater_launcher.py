import sys
import os
import subprocess
import time

from tkinter import Tk
from tkinter import messagebox

from updater import baixar_atualizacao

def main():
    if len(sys.argv) < 2:
        messagebox.showerror(
            "Erro",
            "URL de atualização não informada."
        )
        return

    download_url = sys.argv[1]

    # ==========================================
    # FECHA O SISTEMA PRINCIPAL DE FORMA SEGURA
    # ==========================================
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "Gerador_XML.exe"],
            capture_output=True
        )
    except:
        pass

    # Aguarda o encerramento completo do processo pai
    time.sleep(3)

    # ==========================================
    # EXECUTA A ATUALIZAÇÃO REAL
    # ==========================================
    # Essa função já exibe a mensagem de sucesso integrada caso conclua!
    baixar_atualizacao(download_url)

    # Limpa o arquivo de controle temporário se existir
    if os.path.exists("ultima_versao.txt"):
        try:
            os.remove("ultima_versao.txt")
        except:
            pass

    # Identifica o diretório atual do sistema
    if getattr(sys, "frozen", False):
        pasta_app = os.path.dirname(sys.executable)
    else:
        pasta_app = os.path.dirname(os.path.abspath(__file__))

    exe_principal = os.path.join(pasta_app, "Gerador_XML.exe")

    # ==========================================
    # REINICIALIZA O SISTEMA SEM HERANÇA DE ADMIN
    # ==========================================
    if os.path.exists(exe_principal):
        # 🚀 TRUQUE DE ENGENHARIA: Chamar via explorer.exe faz o Windows abrir 
        # o aplicativo de volta no modo de usuário comum, desvinculando o UAC de Administrador do Updater
        subprocess.Popen(["explorer.exe", exe_principal], shell=True)

if __name__ == "__main__":
    # Inicializa uma janela fantasma oculta apenas para herdar o motor de caixas de alerta
    root = Tk()
    root.withdraw()
    main()