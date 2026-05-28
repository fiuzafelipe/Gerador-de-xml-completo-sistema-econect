import os
import shutil
import zipfile
import tempfile
import requests

from tkinter import messagebox

from core.logs import registrar_evento
from version import VERSION


# =========================================================
# CONFIGURAÇÕES
# =========================================================

VERSAO_ATUAL = VERSION

REPOSITORIO = (
    "fiuzafelipe/"
    "Gerador-de-xml-completo-sistema-econect"
)

URL_VERSION = (
    "https://raw.githubusercontent.com/"
    f"{REPOSITORIO}/main/version.json"
)

URL_ZIP = None

# =========================================================
# ITENS PROTEGIDOS
# NÃO SERÃO SUBSTITUÍDOS
# =========================================================

IGNORAR_UPDATE = [

    # Dados do usuário
    "XML",
    "logs_sistema.json",
    "config.json",

    # Pastas internas
    ".git",
    ".vscode",
    "__pycache__",

    # Build
    "build",
    "dist",

    # Releases
    "releases",
    "installer",

    # Executáveis
    "Gerador_XML.exe",

    # Ambientes
    "venv",
    ".venv"
]


# =========================================================
# BAIXAR UPDATE
# =========================================================

def baixar_atualizacao(url_zip):

    temp_dir = None

    try:

        registrar_evento(
            "Iniciando download da atualização..."
        )

        # =====================================================
        # CRIA PASTA TEMPORÁRIA
        # =====================================================

        temp_dir = tempfile.mkdtemp()

        zip_path = os.path.join(
            temp_dir,
            "update.zip"
        )

        # =====================================================
        # DOWNLOAD ZIP
        # =====================================================

        response = requests.get(
            url_zip,
            stream=True,
            timeout=15
        )

        if response.status_code != 200:

            raise Exception(
                "Falha ao baixar atualização."
            )

        with open(zip_path, "wb") as arquivo:

            for chunk in response.iter_content(
                chunk_size=8192
            ):

                if chunk:
                    arquivo.write(chunk)

        registrar_evento(
            "Download concluído."
        )

        # =====================================================
        # EXTRAI ZIP
        # =====================================================

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_ref:

            zip_ref.extractall(temp_dir)

        registrar_evento(
            "Arquivos extraídos."
        )

        # =====================================================
        # PASTA EXTRAÍDA
        # =====================================================

        pasta_extraida = os.path.join(
            temp_dir,
            "Gerador-de-xml-completo-sistema-econect-main"
        )

        if not os.path.exists(pasta_extraida):

            raise Exception(
                "Estrutura inválida do ZIP."
            )

        # =====================================================
        # PASTA DO SISTEMA
        # =====================================================

        pasta_atual = os.getcwd()

        registrar_evento(
            f"Pasta atual: {pasta_atual}"
        )

        # =====================================================
        # SUBSTITUI ARQUIVOS
        # =====================================================

        for item in os.listdir(pasta_extraida):

            # =============================================
            # IGNORA ITENS PROTEGIDOS
            # =============================================

            if item in IGNORAR_UPDATE:

                registrar_evento(
                    f"Ignorado: {item}"
                )

                continue

            origem = os.path.join(
                pasta_extraida,
                item
            )

            destino = os.path.join(
                pasta_atual,
                item
            )

            # =============================================
            # REMOVE ANTIGO
            # =============================================

            if os.path.exists(destino):

                try:

                    if os.path.isdir(destino):

                        shutil.rmtree(destino)

                    else:

                        os.remove(destino)

                except Exception as erro:

                    registrar_evento(
                        f"Erro removendo {item}: {erro}"
                    )

                    continue

            # =============================================
            # COPIA NOVO
            # =============================================

            try:

                if os.path.isdir(origem):

                    shutil.copytree(
                        origem,
                        destino
                    )

                else:

                    shutil.copy2(
                        origem,
                        destino
                    )

                registrar_evento(
                    f"Atualizado: {item}"
                )

            except Exception as erro:

                registrar_evento(
                    f"Erro copiando {item}: {erro}"
                )

        # =====================================================
        # FINALIZAÇÃO
        # =====================================================

        registrar_evento(
            "Atualização concluída com sucesso."
        )

        messagebox.showinfo(
            "Atualização",
            "Sistema atualizado com sucesso.\n\n"
            "Feche e abra novamente a aplicação."
        )

    except Exception as erro:

        registrar_evento(
            f"Erro no update: {erro}"
        )

        messagebox.showerror(
            "Erro Update",
            str(erro)
        )

    finally:

        # =====================================================
        # LIMPA TEMP
        # =====================================================

        try:

            if temp_dir and os.path.exists(temp_dir):

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )

        except:
            pass


# =========================================================
# VERIFICAR UPDATE
# =========================================================

def verificar_atualizacao(auto=False):

    try:

        registrar_evento(
            "Verificando atualizações..."
        )

        response = requests.get(
            URL_VERSION,
            timeout=10
        )

        if response.status_code != 200:

            registrar_evento(
                "Falha ao acessar version.json"
            )

            return

        dados = response.json()

        versao_online = dados.get(
            "version",
            "0.0.0"
        )

        download_url = dados.get(
            "download_url"
        )

        # =====================================================
        # TEM UPDATE
        # =====================================================

        if versao_online != VERSAO_ATUAL:

            registrar_evento(
                f"Nova versão encontrada: {versao_online}"
            )

            resposta = messagebox.askyesno(
                "Atualização disponível",
                f"Há atualizações disponíveis!\n\n"
                f"Versão atual: {VERSAO_ATUAL}\n"
                f"Nova versão: {versao_online}\n\n"
                f"Deseja atualizar agora?"
            )

            if resposta:

                baixar_atualizacao(download_url)

        else:

            registrar_evento(
                "Sistema já atualizado."
            )

            # NÃO MOSTRA SE FOR AUTO
            if not auto:

                messagebox.showinfo(
                    "Sistema atualizado",
                    "Não há atualizações disponíveis.\n\n"
                    "Bom uso."
                )

    except Exception as erro:

        registrar_evento(
            f"Erro ao verificar atualização: {erro}"
        )