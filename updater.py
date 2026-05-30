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
def baixar_atualizacao(url_zip):
    temp_dir = None
    try:
        registrar_evento("Iniciando download da atualização...")

        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "update.zip")

        response = requests.get(url_zip, stream=True, timeout=15)
        if response.status_code != 200:
            raise Exception("Falha ao baixar atualização.")

        with open(zip_path, "wb") as arquivo:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    arquivo.write(chunk)

        registrar_evento("Download concluído. Extraindo arquivos...")

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        pasta_extraida = temp_dir
        registrar_evento(f"Conteúdo extraído: {os.listdir(pasta_extraida)}")

        # Validação de integridade do pacote baixado
        arquivos_necessarios = ["Gerador_XML.exe", "_internal", "assets"]
        for item in arquivos_necessarios:
            if not os.path.exists(os.path.join(pasta_extraida, item)):
                raise Exception(f"Arquivo obrigatório não encontrado no pacote de atualização: {item}")

        # Identifica a pasta onde o sistema principal está instalado
        if getattr(sys, "frozen", False):
            pasta_atual = os.path.dirname(sys.executable)
        else:
            pasta_atual = os.path.dirname(os.path.abspath(__file__))

        registrar_evento(f"Pasta de instalação alvo: {pasta_atual}")

        # 🚀 DELAY DE SEGURANÇA: Dá tempo para o processo pai (Gerador_XML.exe) morrer completamente
        time.sleep(2)

        # =====================================================
        # SUBSTITUI ARQUIVOS COM TRATAMENTO DE PERMISSÃO
        # =====================================================
        for item in os.listdir(pasta_extraida):
            if item in IGNORAR_UPDATE:
                registrar_evento(f"Ignorado (Item protegido): {item}")
                continue

            origem = os.path.join(pasta_extraida, item)
            destino = os.path.join(pasta_atual, item)

            # --- REMOVE VERSÃO ANTIGA COM RETENTATIVAS ---
            if os.path.exists(destino):
                removido = False
                for tentativa in range(3):  # Tenta até 3 vezes se o Windows travar o arquivo
                    try:
                        if os.path.isdir(destino):
                            shutil.rmtree(destino)
                        else:
                            os.remove(destino)
                        removido = True
                        break
                    except Exception as erro_perm:
                        registrar_evento(f"[Tentativa {tentativa+1}] Arquivo {item} travado pelo Windows, aguardando... Erro: {erro_perm}")
                        time.sleep(1.5)  # Aguarda um pouco antes de tentar novamente

                if not removido:
                    raise PermissionError(f"O Windows negou acesso para substituir o item '{item}'. Feche o sistema por completo e tente novamente.")

            # --- COPIA VERSÃO NOVA ---
            try:
                if os.path.isdir(origem):
                    shutil.copytree(origem, destino)
                else:
                    shutil.copy2(origem, destino)
                registrar_evento(f"Sucesso ao atualizar: {item}")
            except Exception as erro:
                registrar_evento(f"ERRO CRÍTICO ao copiar {item}: {erro}")
                raise

        registrar_evento("Atualização concluída com sucesso.")
        messagebox.showinfo("Sucesso", "O sistema foi atualizado com sucesso!\n\nInicie o Gerador de XML novamente.")

    except Exception as erro:
        registrar_evento(f"Erro no processo de update: {erro}")
        messagebox.showerror("Erro no Update", f"Não foi possível concluir a atualização automática:\n\n{str(erro)}")
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