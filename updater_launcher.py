import sys
import os
import subprocess

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
    # FECHA O SISTEMA PRINCIPAL
    # ==========================================

    try:

        subprocess.run(
            [
                "taskkill",
                "/F",
                "/IM",
                "Gerador_XML.exe"
            ],
            capture_output=True
        )

    except:
        pass

    # Aguarda encerramento completo

    import time

    time.sleep(3)

    # ==========================================
    # EXECUTA UPDATE
    # ==========================================

    baixar_atualizacao(download_url)

    versao = ""

    if os.path.exists("ultima_versao.txt"):

        with open(
            "ultima_versao.txt",
            "r",
            encoding="utf-8"
        ) as arquivo:

            versao = arquivo.read().strip()

        os.remove("ultima_versao.txt")

    messagebox.showinfo(
        "Atualização concluída",
        f"Sistema atualizado com sucesso!\n\nVersão: {versao}"
    )

    if getattr(sys, "frozen", False):

        pasta_app = os.path.dirname(
            sys.executable
        )

    else:

        pasta_app = os.path.dirname(
            os.path.abspath(__file__)
        )

    exe_principal = os.path.join(
        pasta_app,
        "Gerador_XML.exe"
    )

    if os.path.exists(exe_principal):

        subprocess.Popen(exe_principal)

if __name__ == "__main__":

    root = Tk()
    root.withdraw()

    main()