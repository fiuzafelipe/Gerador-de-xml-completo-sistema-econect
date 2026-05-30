import time
import subprocess

from updater import baixar_atualizacao

time.sleep(3)

baixar_atualizacao()

subprocess.Popen(
    ["Gerador_XML.exe"]
)