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

    pasta_app = os.path.dirname(
        sys.executable
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