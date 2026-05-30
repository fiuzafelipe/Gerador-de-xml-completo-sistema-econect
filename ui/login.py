import os
import json
import threading
import customtkinter as ctk
import sys
import requests
import subprocess

from PIL import Image
from tkinter import messagebox
from version import VERSION
from updater import verificar_atualizacao

from core.auth import validar_usuario
from core.database import conectar_mysql
from core.logs import registrar_evento


# =========================================================
# CONFIGURAÇÃO APPDATA
# =========================================================

APPDATA_DIR = os.path.join(
    os.getenv("APPDATA"),
    "XML"
)

os.makedirs(APPDATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(
    APPDATA_DIR,
    "config.json"
)

# =========================================================
# RESOURCE PATH
# =========================================================

def resource_path(relative_path):

    if getattr(sys, "frozen", False):

        base_path = os.path.dirname(
            sys.executable
        )

    else:

        base_path = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        base_path,
        "assets",
        relative_path
    )


# =========================================================
# APP
# =========================================================

class FiuzaEnterpriseApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # =====================================================
        # APPEARANCE
        # =====================================================

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        # =====================================================
        # WINDOW
        # =====================================================

        self.title("Fiuza Tecnology - Gerador de XML Completo")

        self.width_app = 1100
        self.height_app = 720

        self.geometry(
            f"{self.width_app}x{self.height_app}"
        )
        
        # Cor de fundo inicial
        self.configure(fg_color="#EDEDED")

        # Habilita maximizar
        self.resizable(True, True)

        # Alinhado acima
        self.after(100, self.posicionar_janela)
        
        # Ícone do sistema (opcional)
        try:
            self.iconbitmap(
                resource_path("icon.ico")
            )
        except:
            pass

        # =====================================================
        # FONTES
        # =====================================================

        self.fonte_subtitulo = ("Segoe UI", 20, "bold")
        self.fonte_bold = ("Segoe UI", 14, "bold")

        # =====================================================
        # CONFIG
        # =====================================================

        self.usuario_atual = ""

        self.config_app = {
            "tema_cor": "padrao",
            "modo_brilho": "Light",
            "auto_update": True
        }
        
        # Carrega configuração salva
        self.carregar_config()

        # =====================================================
        # TEMAS
        # =====================================================

        self.temas = {

            "blue": {
                "janela": "#E9EEF5",
                "card": "#F5F7FA",
                "destaque": "#3b8ed0",
                "btn_login": "#FFFFFF",
                "txt_login": "#3b8ed0",
                "header": "#101010",
                "texto": "#222222"
            },

            "red": {
                "janela": "#F5EEEE",
                "card": "#FAF7F7",
                "destaque": "#c84a4a",
                "btn_login": "#FFFFFF",
                "txt_login": "#c84a4a",
                "header": "#101010",
                "texto": "#222222"
            },

            "white": {
                "janela": "#FFFFFF",
                "card": "#F8F8F8",
                "destaque": "#D6D6D6",
                "btn_login": "#FFFFFF",
                "txt_login": "#444444",
                "header": "#F5F5F5",
                "texto": "#222222"
            },

            "dark": {
                "janela": "#1B1B1B",
                "card": "#252525",
                "destaque": "#3b8ed0",
                "btn_login": "#2D2D2D",
                "txt_login": "#FFFFFF",
                "header": "#101010",
                "texto": "#FFFFFF"
            },

            "padrao": {
                "janela": "#EDEDED",
                "card": "#F7F7F7",
                "destaque": "#3b8ed0",
                "btn_login": "#FFFFFF",
                "txt_login": "#3b8ed0",
                "header": "#101010",
                "texto": "#222222"
            }
        }
        

        # =====================================================
        # START
        # =====================================================
        
        if self.config_app["tema_cor"] == "dark":
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

        self.setup_login_ui()
        
        # =====================================================
        # AUTO UPDATE
        # =====================================================

        if self.config_app.get("auto_update", True):

            self.after(
                2000,
                lambda: verificar_atualizacao(auto=True)
            )

        # =========================================================
        # POSICIONAR JANELA
        # =========================================================

    def posicionar_janela(self):

        self.update_idletasks()

        largura = 1100
        altura = 720

        x = int(
            (self.winfo_screenwidth() / 2) - (largura / 2)
        )

        # MAIS PARA CIMA
        y = 0

        self.geometry(f"{largura}x{altura}+{x}+{y}")

    # =========================================================
    # SALVAR CONFIG
    # =========================================================

    def salvar_config(self):

        try:

            with open(
                CONFIG_FILE,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    self.config_app,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

        except Exception as erro:

            print(
                f"Erro ao salvar config: {erro}"
            )

    # =========================================================
    # CARREGAR CONFIG
    # =========================================================

    def carregar_config(self):

        try:

            if os.path.exists(CONFIG_FILE):

                with open(
                    CONFIG_FILE,
                    "r",
                    encoding="utf-8"
                ) as arquivo:

                    config = json.load(arquivo)

                    self.config_app.update(config)

        except Exception as erro:

            print(
                f"Erro ao carregar config: {erro}"
            )

    # =========================================================
    # MUDAR ESTILO
    # =========================================================

    def mudar_estilo(self, tema=None, brilho=None):

        if brilho:
            ctk.set_appearance_mode(brilho)
            self.config_app["modo_brilho"] = brilho

        if tema:
            self.config_app["tema_cor"] = tema

        self.setup_login_ui()

    # =========================================================
    # CABEÇALHO
    # =========================================================

    def criar_cabecalho(self):

        tema = self.temas[self.config_app["tema_cor"]]

        header = ctk.CTkFrame(
            self,
            height=70,
            fg_color="transparent",
            corner_radius=0
        )

        header.pack(fill="x")

        # =====================================
        # FRAME DOS TEMAS
        # =====================================

        self.frame_temas = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        self.frame_temas.place(
            relx=0.72,
            rely=0.5,
            anchor="center"
        )

        # =====================================
        # BOTÕES DOS TEMAS
        # =====================================

        self.criar_botao_tema(
            self.frame_temas,
            "☀ Light",
            "padrao"
        ).pack(side="left", padx=4)

        self.criar_botao_tema(
            self.frame_temas,
            "🌙 Dark",
            "dark"
        ).pack(side="left", padx=4)

        self.criar_botao_tema(
            self.frame_temas,
            "🔵 Blue",
            "blue"
        ).pack(side="left", padx=4)

        self.criar_botao_tema(
            self.frame_temas,
            "🔴 Red",
            "red"
        ).pack(side="left", padx=4)

        self.criar_botao_tema(
            self.frame_temas,
            "⚪ White",
            "white"
        ).pack(side="left", padx=4)
        
        self.criar_botao_settings(
            self.frame_temas
        ).pack(side="left", padx=8)

    # =========================================================
    # BOTÃO DE TEMA
    # =========================================================

    def criar_botao_tema(self, master, texto, tema_nome):

        tema = self.temas[tema_nome]

        return ctk.CTkButton(
            master,
            text=texto,
            width=95,
            height=34,
            corner_radius=18,
            fg_color=tema["destaque"],

            # =====================================
            # COR AO PASSAR MOUSE
            # =====================================

            hover_color=(
                "#2f6fa5" if tema_nome == "blue"
                else "#9e3838" if tema_nome == "red"
                else "#2b2b2b" if tema_nome == "dark"
                else "#CFCFCF"
            ),

            text_color=(
                "#FFFFFF"
                if tema_nome != "white"
                else "#333333"
            ),

            font=("Segoe UI", 12, "bold"),

            command=lambda: self.alterar_tema(tema_nome)
        )

    # =========================================================
    # BOTÃO SETTINGS
    # =========================================================

    def criar_botao_settings(self, master):

        return ctk.CTkButton(
            master,
            text="⚙ Settings",
            width=110,
            height=34,
            corner_radius=18,
            fg_color="#444444",
            hover_color="#2E2E2E",
            text_color="#FFFFFF",
            font=("Segoe UI", 12, "bold"),
            command=self.abrir_settings
        )

    # =========================================================
    # SETTINGS
    # =========================================================

    def abrir_settings(self):

        janela = ctk.CTkToplevel(self)

        janela.title("Configurações")

        janela.geometry("350x180")

        janela.resizable(False, False)

        janela.grab_set()

        # =====================================================
        # TITULO
        # =====================================================

        ctk.CTkLabel(
            janela,
            text="Configurações do Sistema",
            font=("Segoe UI", 18, "bold"),
            justify="center"
        ).pack(
            pady=(20, 15),
            fill="x"
        )

        # =====================================================
        # CHECKBOX UPDATE
        # =====================================================

        self.var_auto_update = ctk.BooleanVar(
            value=self.config_app.get(
                "auto_update",
                True
            )
        )

        check_update = ctk.CTkCheckBox(
            janela,
            text="Atualizações automáticas",
            variable=self.var_auto_update,
            font=("Segoe UI", 14)
        )

        check_update.pack(pady=10)

        # =====================================================
        # FRAME BOTÕES
        # =====================================================

        frame_btns = ctk.CTkFrame(
            janela,
            fg_color="transparent"
        )

        frame_btns.pack(pady=20)

        # =====================================================
        # BOTÃO VERIFICAR UPDATE
        # =====================================================

        ctk.CTkButton(
            frame_btns,
            text="Verificar atualizações",
            width=170,
            height=40,
            corner_radius=12,
            fg_color="#3b8ed0",
            hover_color="#2f6fa5",
            command=verificar_atualizacao
        ).pack(
            side="left",
            padx=5
        )

        # =====================================================
        # BOTÃO SALVAR
        # =====================================================

        ctk.CTkButton(
            frame_btns,
            text="Salvar",
            width=120,
            height=40,
            corner_radius=12,
            command=lambda: self.salvar_settings(
                janela
            )
        ).pack(
            side="left",
            padx=5
        )

    # =========================================================
    # SALVAR SETTINGS
    # =========================================================

    def salvar_settings(self, janela):

        self.config_app["auto_update"] = (
            self.var_auto_update.get()
        )

        self.salvar_config()

        messagebox.showinfo(
            "Configuração",
            "Configurações salvas com sucesso."
        )

        janela.destroy()

    # =========================================================
    # ALTERAR TEMA
    # =========================================================

    def alterar_tema(self, tema_nome):

        self.config_app["tema_cor"] = tema_nome

        # =====================================
        # DARK / LIGHT
        # =====================================

        if tema_nome == "dark":
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

        # =====================================
        # RECARREGA UI
        # =====================================

        self.setup_login_ui()

        # =====================================
        # CONFIRMA SALVAR
        # =====================================

        resposta = messagebox.askyesno(
            "Layout padrão",
            "Deseja tornar esse layout padrão?"
        )

        if resposta:

            self.salvar_config()

            messagebox.showinfo(
                "Configuração salva",
                "Tema salvo com sucesso."
            )

        # =========================================================
        # LOGIN UI
        # =========================================================

    def setup_login_ui(self):

        for w in self.winfo_children():
            w.destroy()

        tema = self.temas[
            self.config_app["tema_cor"]
        ]
        
        card_color = tema["card"]

        self.configure(
            fg_color=tema["janela"]
        )

        self.bind(
            "<Return>",
            lambda e: self.validar_login()
        )

        # =====================================================
        # HEADER
        # =====================================================

        self.criar_cabecalho()

        # =====================================================
        # CARD
        # =====================================================

        card = ctk.CTkFrame(
            self,
            corner_radius=28,
            border_width=1,
            border_color=tema["destaque"],
            fg_color=card_color
        )

        card.pack(
            expand=True,
            padx=35,
            pady=(10, 18),
            fill="both"
        )
        
        card.pack_propagate(False)

        # =====================================================
        # TITULO
        # =====================================================

        ctk.CTkLabel(
            card,
            text="Gerador de XML - Econect",
            font=("Segoe UI", 30, "bold")
        ).pack(pady=(25, 10))

        # =====================================================
        # GRID
        # =====================================================

        grid = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        grid.pack(
            fill="both",
            expand=True,
            padx=70,
            pady=10
        )

        grid.grid_columnconfigure(0, minsize=400)
        grid.grid_columnconfigure(1, minsize=400)
        grid.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # =====================================================
        # LEFT
        # =====================================================

        f_user_container = ctk.CTkFrame(
            grid,
            fg_color="transparent"
        )

        f_user_container.grid(
            row=0,
            column=0,
            rowspan=5,
            sticky="n"
        )

        ctk.CTkLabel(
            f_user_container,
            text="Painel de usuário",
            font=self.fonte_subtitulo
        ).pack(pady=(10, 8))

        self.f_img_border = ctk.CTkFrame(
            f_user_container,
            width=165,
            height=165,
            fg_color="black",
            border_width=2,
            border_color="black",
            corner_radius=5
        )

        self.f_img_border.pack(pady=5)
        self.f_img_border.pack_propagate(False)

        self.lbl_img = ctk.CTkLabel(
            self.f_img_border,
            text=""
        )

        self.lbl_img.pack(
            fill="both",
            expand=True
        )

        self.lbl_nome_v = ctk.CTkLabel(
            f_user_container,
            text="Cliente",
            text_color="#27ae60",
            font=("Segoe UI", 18, "bold")
        )

        self.lbl_nome_v.pack(
            pady=(5, 8)
        )

        self.ent_user = self.criar_campo_login_fixed(
            f_user_container,
            "Cliente",
            tema["destaque"]
        )

        self.ent_user.bind(
            "<KeyRelease>",
            self.trocar_img_dinamica
        )

        # SENHA

        self.f_pass_row = ctk.CTkFrame(
            f_user_container,
            fg_color="transparent"
        )

        self.f_pass_row.pack(pady=5)

        self.ent_pass = self.criar_campo_login_fixed(
            self.f_pass_row,
            "123456",
            tema["destaque"],
            secret=True
        )

        ctk.CTkButton(
            self.f_pass_row,
            text="👁",
            width=28,
            height=28,
            fg_color="transparent",
            text_color="gray",
            hover=False,
            command=self.toggle_senha
        ).place(
            relx=0.92,
            rely=0.5,
            anchor="center"
        )

        # =====================================================
        # RIGHT MYSQL
        # =====================================================

        ctk.CTkLabel(
            grid,
            text="Parâmetros do Banco MySQL",
            font=self.fonte_subtitulo
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=20,
            pady=(10, 10)
        )

        f_mysql_line = ctk.CTkFrame(
            grid,
            fg_color="transparent"
        )

        f_mysql_line.grid(
            row=1,
            column=1,
            sticky="w",
            padx=20
        )

        self.db_host = self.criar_campo_especial(
            f_mysql_line,
            "localhost",
            220,
            "left",
            tema["destaque"]
        )

        self.db_port = self.criar_campo_especial(
            f_mysql_line,
            "3306",
            90,
            "left",
            tema["destaque"],
            10
        )

        self.db_user = self.criar_campo_login(
            grid,
            "root",
            2,
            1,
            tema["destaque"]
        )

        self.db_pass = self.criar_campo_login(
            grid,
            "123456",
            3,
            1,
            tema["destaque"],
            secret=True
        )

        self.db_schema = self.criar_campo_login(
            grid,
            "concentrador",
            4,
            1,
            tema["destaque"]
        )

        # =====================================================
        # BOTÃO LOGIN
        # =====================================================

        self.btn_entrar = ctk.CTkButton(
            card,
            text="AUTENTICAR E CONECTAR",
            font=("Segoe UI", 16, "bold"),
            width=400,
            height=50,
            corner_radius=15,
            fg_color=tema["btn_login"],
            hover_color=(
                "#2f6fa5"
                if self.config_app["tema_cor"] == "blue"
                else "#9e3838"
                if self.config_app["tema_cor"] == "red"
                else "#2b2b2b"
                if self.config_app["tema_cor"] == "dark"
                else "#CFCFCF"
            ),
            text_color=tema["txt_login"],
            border_color=tema["destaque"],
            border_width=2,
            command=self.validar_login
        )

        self.btn_entrar.pack(
            pady=(15, 10)
        )

        # =====================================================
        # PROGRESS
        # =====================================================

        self.prog_login = ctk.CTkProgressBar(
            card,
            width=760,
            height=10,
            progress_color=tema["destaque"]
        )

        self.prog_login.pack(pady=(5, 0))

        self.prog_login.set(0)

        self.lbl_status = ctk.CTkLabel(
            card,
            text="Aguardando ação...",
            font=("Segoe UI", 11),
            text_color="gray"
        )

        self.lbl_status.pack(
            pady=(6, 18)
        )

        self.trocar_img_dinamica()

    # =========================================================
    # PLACEHOLDER INTELIGENTE
    # =========================================================

    def configurar_placeholder(
        self,
        entry,
        texto_placeholder,
        senha=False
    ):

        # =====================================
        # TEXTO INICIAL
        # =====================================

        entry.insert(0, texto_placeholder)

        # Campo senha inicia SEM máscara
        if senha:
            entry.configure(show="*")

        # =====================================
        # AO CLICAR
        # =====================================

        def ao_entrar(event):

            if entry.get() == texto_placeholder:

                entry.delete(0, "end")

                # Ativa máscara
                if senha:
                    entry.configure(show="*")

        # =====================================
        # AO SAIR
        # =====================================

        def ao_sair(event):

            # Se vazio → restaura placeholder
            if entry.get().strip() == "":

                entry.delete(0, "end")

                entry.insert(0, texto_placeholder)

                # Remove máscara para mostrar placeholder
                if senha:
                    entry.configure(show="*")

            else:

                # Se digitou algo → mantém máscara
                if senha:
                    entry.configure(show="*")

        # =====================================
        # EVENTOS
        # =====================================

        entry.bind("<FocusIn>", ao_entrar)

        entry.bind("<FocusOut>", ao_sair)

    # =========================================================
    # CAMPOS
    # =========================================================

    def criar_campo_login_fixed(
        self,
        master,
        placeholder,
        cor,
        secret=False
    ):

        e = ctk.CTkEntry(
            master,
            width=320,
            height=42,
            corner_radius=12,
            border_color=cor,
            border_width=2,
            fg_color="#FFFFFF" if self.config_app["tema_cor"] != "dark" else "#2B2B2B",
            text_color="#000000" if self.config_app["tema_cor"] != "dark" else "#FFFFFF",
        )

        e.pack(pady=5)

        self.configurar_placeholder(
            e,
            placeholder,
            senha=secret
        )

        return e

    def criar_campo_login(
        self,
        master,
        placeholder,
        row,
        col,
        cor,
        secret=False
    ):

        e = ctk.CTkEntry(
            master,
            width=320,
            height=42,
            corner_radius=10,
            border_color=cor,
            border_width=2,
            fg_color="#FFFFFF" if self.config_app["tema_cor"] != "dark" else "#2B2B2B",
            text_color="#000000" if self.config_app["tema_cor"] != "dark" else "#FFFFFF",
        )

        e.grid(
            row=row,
            column=col,
            sticky="w",
            padx=20,
            pady=6
        )

        self.configurar_placeholder(
            e,
            placeholder,
            senha=secret
        )

        return e

    def criar_campo_especial(
        self,
        master,
        placeholder,
        width,
        side,
        cor,
        padx=0
    ):

        e = ctk.CTkEntry(
            master,
            width=width,
            height=42,
            corner_radius=10,
            border_color=cor,
            border_width=2,
            fg_color="#FFFFFF" if self.config_app["tema_cor"] != "dark" else "#2B2B2B",
            text_color="#000000" if self.config_app["tema_cor"] != "dark" else "#FFFFFF",
        )

        e.pack(
            side=side,
            padx=padx
        )

        self.configurar_placeholder(
            e,
            placeholder
        )

        return e

    # =========================================================
    # TROCAR IMAGEM
    # =========================================================

    def trocar_img_dinamica(self, event=None):

        nome = self.ent_user.get().strip()

        caminho_img = resource_path(
            f"{nome}.png"
        )

        if not os.path.exists(caminho_img):

            caminho_img = resource_path(
                "Cliente.png"
            )

        try:

            img = Image.open(caminho_img)

            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(160, 160)
            )

            self.lbl_img.configure(
                image=ctk_img,
                text=""
            )

            self.lbl_img.image = ctk_img

            self.lbl_nome_v.configure(
                text=nome if nome else "Cliente",
                text_color="#3b8ed0"
                if nome == "Felipe Fiuza"
                else "#27ae60"
            )

        except Exception:

            self.lbl_img.configure(
                image=None,
                text="IMG"
            )

    # =========================================================
    # TOGGLE SENHA
    # =========================================================

    def toggle_senha(self):

        atual = self.ent_pass.cget("show")

        self.ent_pass.configure(
            show="" if atual == "*" else "*"
        )

    # =========================================================
    # LOGIN MYSQL
    # =========================================================

    def validar_login(self):

        usuario = self.ent_user.get().strip()
        senha = self.ent_pass.get().strip()

        # =========================================
        # RESET VISUAL
        # =========================================

        self.prog_login.set(0)

        self.lbl_status.configure(
            text="Validando credenciais...",
            text_color="#d6d6d6"
        )

        self.update()

        # =========================================
        # VALIDA CAMPOS
        # =========================================

        if not usuario or not senha:

            self.lbl_status.configure(
                text="Informe usuário e senha.",
                text_color="red"
            )

            return

        try:

            # =========================================
            # VALIDA LOGIN
            # =========================================

            self.prog_login.set(0.3)

            valido = validar_usuario(
                usuario,
                senha
            )

            if not valido:

                self.lbl_status.configure(
                    text="Usuário ou senha inválidos.",
                    text_color="red"
                )

                self.prog_login.set(0)

                registrar_evento(
                    f"Falha no login: {usuario}"
                )

                return

            # =========================================
            # LOGIN OK
            # =========================================

            registrar_evento(
                f"Login efetuado: {usuario}"
            )

            self.lbl_status.configure(
                text="Conectando ao MySQL...",
                text_color="#d6d6d6"
            )

            self.prog_login.set(0.6)

            self.update()

            # =========================================
            # TESTA MYSQL
            # =========================================

            conexao = conectar_mysql(
                host=self.db_host.get(),
                port=self.db_port.get(),
                user=self.db_user.get(),
                password=self.db_pass.get(),
                database=self.db_schema.get()
            )

            # =========================================
            # ERRO MYSQL
            # =========================================

            if conexao is None:

                self.lbl_status.configure(
                    text="Erro ao conectar no MySQL.",
                    text_color="red"
                )

                self.prog_login.set(0)

                registrar_evento(
                    "Falha ao conectar no MySQL."
                )

                messagebox.showerror(
                    "Erro MySQL",
                    "Não foi possível conectar ao banco MySQL.\n\n"
                    "Verifique:\n"
                    "• Host\n"
                    "• Porta\n"
                    "• Usuário\n"
                    "• Senha\n"
                    "• Serviço MySQL iniciado"
                )

                return

            # =========================================
            # MYSQL OK
            # =========================================

            self.prog_login.set(1)

            self.lbl_status.configure(
                text="Login realizado com sucesso.",
                text_color="#27ae60"
            )

            registrar_evento(
                "Conexão MySQL realizada com sucesso."
            )

            messagebox.showinfo(
                "Sucesso",
                "Login realizado com sucesso!"
            )
            
            # =========================================
            # ABRIR DASHBOARD
            # =========================================

            from ui.dashboard import DashboardApp

            self.withdraw()

            dashboard = DashboardApp(
                self,
                usuario,
                conexao
            )

            dashboard.mainloop()

        except Exception as erro:

            self.prog_login.set(0)

            self.lbl_status.configure(
                text=f"Erro: {erro}",
                text_color="red"
            )

            registrar_evento(
                f"Erro inesperado: {erro}"
            )

            messagebox.showerror(
                "Erro",
                str(erro)
            )
