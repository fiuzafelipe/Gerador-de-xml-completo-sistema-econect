import os
import shutil
import subprocess
from tkinter import messagebox

# Responsável pela compactação.

class Compression:

    def solicitar_compactacao(self, destino):

        if messagebox.askyesno(
            "Compactar",
            "Deseja compactar a pasta gerada agora?"
        ):

            try:

                diretorio_pai = os.path.dirname(destino)

                nome_base = os.path.basename(destino)

                zip_base = os.path.join(diretorio_pai, nome_base + "_compactado")

                zip_final = shutil.make_archive(
                    zip_base,
                    'zip',
                    destino
                )

                messagebox.showinfo(
                    "OK",
                    f"Arquivo gerado:\n{zip_final}"
                )

            except Exception as e:

                messagebox.showerror(
                    "Erro",
                    f"Compactação falhou:\n{e}"
                )

def compactar_com_winrar(caminho):

    possible_paths = [
        r"C:\Program Files\WinRAR\WinRAR.exe",
        r"C:\Program Files (x86)\WinRAR\WinRAR.exe"
    ]

    winrar = None

    for path in possible_paths:

        if os.path.exists(path):
            winrar = path
            break

    if not winrar:
        raise Exception("WinRAR não encontrado.")

    diretorio_pai = os.path.dirname(caminho)

    nome_base = os.path.basename(caminho)

    rar_final = os.path.join(
        diretorio_pai,
        nome_base + ".rar"
    )

    if os.path.exists(rar_final):
        os.remove(rar_final)

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        subprocess.run(
            [
                winrar,
                "a",
                "-r",
                rar_final,
                caminho
            ],
            check=True,
            startupinfo=startupinfo
        except subprocess.CalledProcessError as e:
            raise Exception(f"WinRAR falhou: {e}")
        )

        return rar_final


def compactar_zip(destino):

    diretorio_pai = os.path.dirname(destino)

    nome_base = os.path.basename(destino)

    zip_base = os.path.join(
        diretorio_pai,
        nome_base
    )

    zip_final = shutil.make_archive(
        zip_base,
        'zip',
        destino
    )

    return zip_final
    