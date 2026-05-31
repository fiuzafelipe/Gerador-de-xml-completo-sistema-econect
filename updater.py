import os
import sys
import subprocess
import shutil
import zipfile
import tempfile
import requests
import time  # <-- Adicionado para gerenciar os delays de segurança

from tkinter import messagebox

from core.logs import registrar_evento
from version import APP_VERSION  # Ajustado para o nome correto da variável

# =========================================================
# CONFIGURAÇÕES
# =========================================================
VERSAO_ATUAL = APP_VERSION

REPOSITORIO = "fiuzafelipe/Gerador-de-xml-completo-sistema-econect"
URL_VERSION = f"https://raw.githubusercontent.com/{REPOSITORIO}/main/version.json"

# Itens protegidos que nunca serão apagados ou alterados no update
IGNORAR_UPDATE = [
    "XML", "logs_sistema.json", "config.json",
    ".git", ".vscode", "__pycache__",
    "build", "dist", "releases", "installer",
    "venv", ".venv", "update.zip", "updater.exe"  # Protege o próprio updater de se auto-deletar no meio da extração
]

# =========================================================
# BAIXAR UPDATE
# =========================================================
def baixar_atualizacao(url_zip, callback_progresso=None, callback_status=None):
    temp_dir = None
    try:
        if callback_status: callback_status("Conectando ao servidor...")
        registrar_evento("Iniciando download da atualização...")

        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "update.zip")

        response = requests.get(url_zip, stream=True, timeout=15)
        if response.status_code != 200:
            raise Exception("Falha ao baixar atualização.")

        # Coleta o tamanho total do arquivo para calcular a porcentagem
        total_size = int(response.headers.get('content-length', 0))
        bytes_baixados = 0

        with open(zip_path, "wb") as arquivo:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    arquivo.write(chunk)
                    bytes_baixados += len(chunk)
                    if total_size > 0 and callback_progresso:
                        # Calcula a porcentagem real e empurra para a UI do atualizador
                        porcentagem = bytes_baixados / total_size
                        callback_progresso(porcentagem)

        if callback_status: callback_status("Extraindo arquivos...")
        registrar_evento("Download concluído. Extraindo arquivos...")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        pasta_extraida = temp_dir

        # Validação de integridade do pacote baixado
        arquivos_necessarios = ["Gerador_XML.exe", "_internal", "assets"]
        for item in arquivos_necessarios:
            if not os.path.exists(os.path.join(pasta_extraida, item)):
                raise Exception(f"Arquivo obrigatório não encontrado no pacote: {item}")

        if getattr(sys, "frozen", False):
            pasta_atual = os.path.dirname(sys.executable)
        else:
            pasta_atual = os.path.dirname(os.path.abspath(__file__))

        if callback_status: callback_status("Substituindo binários...")
        time.sleep(2)

        # Substituição atômica de arquivos
        for item in os.listdir(pasta_extraida):
            if item in IGNORAR_UPDATE:
                continue

            origem = os.path.join(pasta_extraida, item)
            destino = os.path.join(pasta_atual, item)

            if os.path.exists(destino):
                removido = False
                for tentativa in range(3):
                    try:
                        if os.path.isdir(destino):
                            shutil.rmtree(destino)
                        else:
                            os.remove(destino)
                        removido = True
                        break
                    except:
                        time.sleep(1.5)

                if not removido:
                    raise PermissionError(f"Acesso negado pelo Windows ao substituir o item '{item}'.")

            if os.path.isdir(origem):
                shutil.copytree(origem, destino)
            else:
                shutil.copy2(origem, destino)

        registrar_evento("Atualização concluída com sucesso.")
        return True

    except Exception as erro:
        registrar_evento(f"Erro no processo de update: {erro}")
        messagebox.showerror("Erro no Update", f"Não foi possível concluir a atualização automática:\n\n{str(erro)}")
        return False
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


# =========================================================
# VERIFICAR UPDATE (USADO NO MODO DESENVOLVIMENTO)
# =========================================================
def verificar_atualizacao(auto=False):
    try:
        registrar_evento("Verificando atualizações...")
        response = requests.get(URL_VERSION, timeout=10)
        
        if response.status_code != 200:
            registrar_evento("Falha ao acessar version.json online.")
            return

        dados = response.json()
        versao_online = dados.get("version", "0.0.0")
        download_url = dados.get("download_url")

        if versao_online != VERSAO_ATUAL:
            registrar_evento(f"Nova versão encontrada: {versao_online}")

            resposta = messagebox.askyesno(
                "Atualização disponível",
                f"Há atualizações disponíveis!\n\nVersão atual: {VERSAO_ATUAL}\nNova versão: {versao_online}\n\nDeseja atualizar agora?"
            )

            if resposta:
                with open("ultima_versao.txt", "w", encoding="utf-8") as arquivo:
                    arquivo.write(versao_online)

                # Correção do caminho absoluto e do nome da variável
                updater_exe = os.path.join(os.path.dirname(sys.executable), "updater.exe")

                # Dispara o processo independente e desvincula da árvore pai
                subprocess.Popen([updater_exe, download_url], shell=True, start_new_session=True)
                os._exit(0)
        else:
            registrar_evento("O sistema já está rodando a última versão.")
            if not auto:
                messagebox.showinfo("Sistema atualizado", "Não há atualizações disponíveis.\n\nBom uso.")
    except Exception as erro:
        registrar_evento(f"Erro ao verificar atualização: {erro}")
        if not auto:
            messagebox.showerror("Erro", f"Falha ao checar atualizações: {erro}")