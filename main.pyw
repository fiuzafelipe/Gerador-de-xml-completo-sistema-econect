import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import threading
import time
import json
import os
import sys
import shutil
import subprocess
from datetime import datetime
import pymysql  # Motor de conexão estável para executáveis

# =================================================================
# FUNÇÃO ESSENCIAL PARA RECURSOS INTERNOS (EXECUTÁVEL)
# =================================================================
def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funciona no dev e no PyInstaller """
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# DPI Awareness para manter a geometria perfeita no monitor
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# =================================================================
# CONFIGURAÇÃO DE DIRETÓRIO E ARQUIVOS
# =================================================================

APPDATA_DIR = os.path.join(
    os.getenv("APPDATA") or os.getcwd(),
    "XML"
)

LOG_FILE = os.path.join(APPDATA_DIR, "logs_sistema.json")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")
os.makedirs(APPDATA_DIR, exist_ok=True)

USUARIOS = {
    "Cliente": {"senha": "123456", "nivel": "user"},
    "Felipe Fiuza": {"senha": "ABC,123@", "nivel": "admin"},
    "Leandro": {"senha": "abc,123", "nivel": "admin"},
    "Italo": {"senha": "abc,123", "nivel": "admin"},
    "Julio": {"senha": "abc,123", "nivel": "admin"},
    "Raphael": {"senha": "abc,123", "nivel": "admin"},
    "Gabriel": {"senha": "abc,123", "nivel": "admin"},
    "Micael": {"senha": "abc,123", "nivel": "admin"},
    "Francismar": {"senha": "abc,123", "nivel": "admin"},
    "Bruno": {"senha": "abc,123", "nivel": "admin"}
}

MESES = ["", "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", 
         "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]

# =================================================================
# DIÁLOGOS CUSTOMIZADOS
# =================================================================
class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, text):
        super().__init__(parent)
        self.title(title)
        self.largura, self.altura = 400, 200
        px = parent.winfo_x() + (parent.winfo_width() // 2) - (self.largura // 2)
        py = parent.winfo_y() + (parent.winfo_height() // 2) - (self.altura // 2)
        self.geometry(f"{self.largura}x{self.altura}+{px}+{py}")
        self.resizable(False, False)
        self.transient(parent); self.grab_set(); self.attributes("-topmost", True)
        self.result = None
        ctk.CTkLabel(self, text=text, font=("Segoe UI", 14)).pack(pady=(30, 10))
        self.entry = ctk.CTkEntry(self, width=250, height=35); self.entry.pack(pady=10); self.entry.focus_set()
        btn_f = ctk.CTkFrame(self, fg_color="transparent"); btn_f.pack(pady=15)
        ctk.CTkButton(btn_f, text="Ok", width=100, command=self.on_ok).pack(side="left", padx=5)
        ctk.CTkButton(btn_f, text="Cancelar", width=100, fg_color="gray", command=self.on_cancel).pack(side="left", padx=5)
        self.bind("<Return>", lambda e: self.on_ok())
    def on_ok(self): self.result = self.entry.get(); self.destroy()
    def on_cancel(self): self.result = None; self.destroy()
    def get_input(self): self.master.wait_window(self); return self.result

# =================================================================
# APLICAÇÃO PRINCIPAL - FIUZA TECNOLOGY
# =================================================================
class FiuzaEnterpriseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = self.carregar_config()
        self.largura, self.height_win = 1000, 650
        self.title("Fiuza Tecnology - Gerador de XML Completo")
        self.resizable(False, False)
        
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.largura}x{self.height_win}+{int((sw/2)-(self.largura/2))}+{int((sh/2)-(self.height_win/2)-30)}")

        self.temas = {
            "blue": {"janela": ("#E3F2FD", "#0D1B2A"), "card": ("#D0E1F9", "#1A2A40"), "destaque": "#3b8ed0", "btn_login": ("#FFFFFF", "#3b8ed0"), "txt_login": ("#3b8ed0", "#FFFFFF")},
            "red": {"janela": ("#FFEBEE", "#1A0D0D"), "card": ("#F9D0D0", "#2D1A1A"), "destaque": "#c84a4a", "btn_login": ("#FFFFFF", "#c84a4a"), "txt_login": ("#3b8ed0", "#FFFFFF")},
            "padrao": {"janela": ("#F2F2F2", "#1A1A1A"), "card": ("#ebebeb", "#242424"), "destaque": ("#3b8ed0", "#1f6aa5"), "btn_login": ("#FFFFFF", "#3b8ed0"), "txt_login": ("#3b8ed0", "#FFFFFF")}
        }
        
        self.usuario_atual, self.db_conexao = "", None
        self.host_conectado, self.nivel_acesso = "", "user"
        self.logs_historico = self.carregar_logs()
        
        self.fonte_bold = ("Segoe UI", 14, "bold")
        self.fonte_subtitulo = ("Segoe UI", 19, "bold")
        self.fonte_titulo_dash = ("Segoe UI", 32, "bold")
        
        ctk.set_appearance_mode(self.config.get("modo_brilho", "Light"))
        self.protocol("WM_DELETE_WINDOW", self.fechar_app)
        self.setup_login_ui()

    def carregar_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: return json.load(f)
            except: pass
        return {"tema_cor": "padrao", "modo_brilho": "Light"}

    def salvar_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(self.config, f, indent=4)
        except: pass

    def carregar_logs(self):
        if not os.path.exists(LOG_FILE): return []
        try:
            with open(LOG_FILE, "r", encoding='utf-8') as f: 
                data = json.load(f)
                return data.get("logs", [])
        except: return []

    def registrar_evento(self, msg):

        try:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            self.logs_historico.append(
                f"[{timestamp}] Usuário: {self.usuario_atual} | {msg}"
            )

            with open(LOG_FILE, "w", encoding='utf-8') as f:
                json.dump(
                    {"logs": self.logs_historico},
                    f,
                    ensure_ascii=False,
                    indent=4
                )

        except Exception as e:
            print(f"Erro ao salvar log: {e}")

    def mudar_estilo(self, tema=None, brilho=None):
        escolha_padrao = messagebox.askyesno("Layout", "Deseja tornar este layout o padrão?")
        if brilho: 
            ctk.set_appearance_mode(brilho)
            if escolha_padrao: self.config["modo_brilho"] = brilho
        if tema: self.config["tema_cor"] = tema
        if escolha_padrao: self.salvar_config()
        self.setup_login_ui() if self.usuario_atual == "" else self.setup_dashboard()

    def criar_cabecalho(self):
        f_head = ctk.CTkFrame(self, height=50, fg_color="transparent")
        f_head.pack(fill="x", padx=30, pady=10)
        f_right = ctk.CTkFrame(f_head, fg_color="transparent"); f_right.pack(side="right")
        if self.usuario_atual == "":
            for t, c, v in [("⚪ White", "#FFFFFF", "padrao"), ("🔴 Red", "#c84a4a", "red"), ("🔵 Blue", "#3b8ed0", "blue")]:
                ctk.CTkButton(f_right, text=t, width=80, height=28, corner_radius=15, fg_color=c, command=lambda x=v: self.mudar_estilo(tema=x)).pack(side="right", padx=2)
            ctk.CTkLabel(f_right, text="|", text_color="gray").pack(side="right", padx=8)
            ctk.CTkButton(f_right, text="🌙 Dark", width=80, height=28, corner_radius=15, fg_color="#2B2B2B", command=lambda: self.mudar_estilo(brilho="Dark")).pack(side="right", padx=2)
            ctk.CTkButton(f_right, text="☀️ Light", width=80, height=28, corner_radius=15, command=lambda: self.mudar_estilo(brilho="Light")).pack(side="right", padx=2)
        else:
            ctk.CTkButton(f_right, text="📋 Log", width=80, fg_color="#3b8ed0", command=self.abrir_logs).pack(side="right", padx=5)
            ctk.CTkButton(f_right, text="↩ Sair", width=80, fg_color="#c84a4a", command=self.logout).pack(side="right", padx=5)
            
    def logout(self):

        try:

            if self.db_conexao:
                self.db_conexao.close()

        except:
            pass

        self.db_conexao = None
        self.usuario_atual = ""
        self.host_conectado = ""
        self.nivel_acesso = "user"

        self.setup_login_ui()
         
    
    def fechar_app(self):
         try:
             if self.db_conexao:
                 self.db_conexao.close()
         except:
             pass

         self.destroy()

    def setup_login_ui(self):
        self.usuario_atual = "" 
        for w in self.winfo_children(): w.destroy()
        tema = self.temas[self.config.get("tema_cor", "padrao")]
        self.configure(fg_color=tema["janela"]); self.bind("<Return>", lambda e: self.validar_login()); self.criar_cabecalho()
        
        card = ctk.CTkFrame(self, corner_radius=20, border_width=1, border_color=tema["destaque"], fg_color=tema["card"])
        card.pack(expand=True, padx=40, pady=(10, 30), fill="both")
        ctk.CTkLabel(card, text="Gerador de XML - Econect", font=("Segoe UI", 26, "bold")).pack(pady=(20, 5))
        
        grid = ctk.CTkFrame(card, fg_color="transparent"); grid.pack(fill="both", expand=True, padx=60)
        grid.columnconfigure((0, 1), weight=1)
        
        f_user_container = ctk.CTkFrame(grid, fg_color="transparent"); f_user_container.grid(row=0, column=0, rowspan=5, sticky="n")
        ctk.CTkLabel(f_user_container, text="Painel de usuário", font=self.fonte_subtitulo).pack(pady=(10, 5))
        self.f_img_border = ctk.CTkFrame(f_user_container, width=165, height=135, fg_color="black", border_color="black", border_width=2, corner_radius=5)
        self.f_img_border.pack(pady=5); self.f_img_border.pack_propagate(False)
        self.lbl_img = ctk.CTkLabel(self.f_img_border, text="", fg_color="transparent"); self.lbl_img.pack(fill="both", expand=True)
        self.lbl_nome_v = ctk.CTkLabel(f_user_container, text="Cliente", text_color="#27ae60", font=("Segoe UI", 16, "bold")); self.lbl_nome_v.pack(pady=(0, 5))
        self.ent_user = self.criar_campo_login_fixed(f_user_container, "Cliente", tema["destaque"])
        self.ent_user.bind("<KeyRelease>", self.trocar_img_dinamica)
        self.f_pass_row = ctk.CTkFrame(f_user_container, fg_color="transparent"); self.f_pass_row.pack(pady=5)
        self.ent_pass = self.criar_campo_login_fixed(self.f_pass_row, "123456", tema["destaque"], secret=True)
        ctk.CTkButton(self.f_pass_row, text="👁️", width=30, height=30, fg_color="transparent", text_color="gray", command=self.toggle_senha).place(relx=0.9, rely=0.5, anchor="center")
        
        ctk.CTkLabel(grid, text="Parâmetros do Banco MySQL", font=self.fonte_subtitulo).grid(row=0, column=1, pady=(10, 5), sticky="w", padx=20)
        f_mysql_line = ctk.CTkFrame(grid, fg_color="transparent", width=320); f_mysql_line.grid(row=1, column=1, sticky="w", padx=20)
        self.db_host = self.criar_campo_especial(f_mysql_line, "localhost", 220, "left", tema["destaque"])
        self.db_port = self.criar_campo_especial(f_mysql_line, "3306", 90, "left", tema["destaque"], 10)
        self.db_user = self.criar_campo_login(grid, "root", 2, 1, tema["destaque"])
        self.db_pass = self.criar_campo_login(grid, "123456", 3, 1, tema["destaque"], secret=True)
        self.db_schema = self.criar_campo_login(grid, "concentrador", 4, 1, tema["destaque"])
        
        self.btn_entrar = ctk.CTkButton(card, text="AUTENTICAR E CONECTAR", font=self.fonte_bold, width=400, height=50, corner_radius=15, fg_color=tema["btn_login"], text_color=tema["txt_login"], border_color=tema["destaque"], command=self.validar_login)
        self.btn_entrar.pack(pady=(20, 10))
        self.prog_login = ctk.CTkProgressBar(card, width=700, height=10, progress_color=tema["destaque"]); self.prog_login.set(0); self.prog_login.pack()
        self.lbl_status = ctk.CTkLabel(card, text="Aguardando ação...", font=("Segoe UI", 11), text_color="gray"); self.lbl_status.pack(pady=(5, 20))
        self.trocar_img_dinamica()

    def criar_campo_login_fixed(self, master, placeholder, cor, secret=False):
        e = ctk.CTkEntry(master, width=320, height=42, corner_radius=10, border_color=cor)
        if secret: e.configure(show="*")
        e.insert(0, placeholder); e.pack(pady=5)
        e.bind("<FocusIn>", lambda ev: self.gerenciar_placeholder(e, placeholder, "in", secret))
        e.bind("<FocusOut>", lambda ev: self.gerenciar_placeholder(e, placeholder, "out", secret)); return e

    def criar_campo_login(self, master, placeholder, row, col, cor, secret=False):
        e = ctk.CTkEntry(master, width=320, height=42, corner_radius=10, border_color=cor)
        if secret: e.configure(show="*")
        e.insert(0, placeholder); e.grid(row=row, column=col, sticky="w", padx=20, pady=5)
        e.bind("<FocusIn>", lambda ev: self.gerenciar_placeholder(e, placeholder, "in", secret))
        e.bind("<FocusOut>", lambda ev: self.gerenciar_placeholder(e, placeholder, "out", secret)); return e

    def criar_campo_especial(self, master, placeholder, width, side, cor, padx=0):
        e = ctk.CTkEntry(master, width=width, height=42, corner_radius=10, border_color=cor)
        e.insert(0, placeholder); e.pack(side=side, padx=padx)
        e.bind("<FocusIn>", lambda ev: self.gerenciar_placeholder(e, placeholder, "in"))
        e.bind("<FocusOut>", lambda ev: self.gerenciar_placeholder(e, placeholder, "out")); return e

    def gerenciar_placeholder(self, entry, placeholder, acao, secret=False):
        if acao == "in" and entry.get() == placeholder:
            entry.delete(0, "end")
            if secret: entry.configure(show="*")
        elif acao == "out" and entry.get().strip() == "":
            if secret: entry.configure(show="")
            entry.insert(0, placeholder)

    def trocar_img_dinamica(self, event=None):
        nome = self.ent_user.get().strip()
        caminho_img = resource_path(f"{nome}.png")
        if not os.path.exists(caminho_img): caminho_img = resource_path("Cliente.png")
        try:
            img = Image.open(caminho_img)

            ctk_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(161, 131)
            )
            self.lbl_img.configure(image=ctk_img)
            self.lbl_img.image = ctk_img
            self.lbl_nome_v.configure(text=nome if nome != "" and nome != "Cliente" else "Cliente", text_color="#3b8ed0" if nome == "Felipe Fiuza" else "#27ae60")
        except: self.lbl_img.configure(image=None, text="IMG")

    def toggle_senha(self):

        if self.ent_pass.get() in ("", "123456"):
            return

        cur = self.ent_pass.cget("show")

        self.ent_pass.configure(
            show="" if cur == "*" else "*"
        )

    def validar_login(self):
        u = self.ent_user.get().strip()
        s = self.ent_pass.get().strip()

        self.lbl_status.configure(
        text="Validando credenciais...",
        text_color="gray"
        )

        if u in USUARIOS and USUARIOS[u]["senha"] == s:

            self.usuario_atual = u
            self.nivel_acesso = USUARIOS[u]["nivel"]

            host = self.db_host.get().strip()

            if not host or host == "localhost":
                host = "127.0.0.1"

            self.host_conectado = host

            self.registrar_evento("Login efetuado.")

            threading.Thread(
                target=self.processo_conexao,
                daemon=True
            ).start()

        else:
            self.lbl_status.configure(
                text="Falha na autenticação.",
                text_color="#c84a4a"
            )

            messagebox.showerror(
                "Erro",
                "Usuário ou senha inválido."
            )

    def processo_conexao(self):
        try:
            self.after(0, lambda: self.prog_login.set(0.2))
            self.after(0, lambda: self.lbl_status.configure(text="Estabelecendo conexão...", text_color="gray"))
            self.db_conexao = pymysql.connect(
                host=self.host_conectado, port=int(self.db_port.get()), 
                user=self.db_user.get(), password=self.db_pass.get(), 
                database=self.db_schema.get(), connect_timeout=15, charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                read_timeout=600,
                write_timeout=600,
                autocommit=True
            )
            self.after(0, lambda: self.prog_login.set(0.8))
            self.after(0, lambda: self.lbl_status.configure(text="Conexão estável!", text_color="#27ae60"))
            self.after(0, lambda: self.prog_login.set(1.0))
            self.after(500, self.setup_dashboard)
        except Exception as e:
            self.after(0, lambda: self.prog_login.set(0))
            self.after(0, lambda: self.lbl_status.configure(text="Erro ao conectar.", text_color="#c84a4a"))
            self.after(
                0,
                lambda err=str(e):
                messagebox.showerror(
                "Erro de Banco",
                f"Falha na conexão:\n{err}"
                )
            )

    def setup_dashboard(self):
        for w in self.winfo_children(): w.destroy()
        tema = self.temas[self.config.get("tema_cor", "padrao")]
        self.configure(fg_color=tema["janela"]); self.criar_cabecalho()
        ctk.CTkLabel(self, text=f"Bem vindo {self.usuario_atual}!", font=self.fonte_titulo_dash, text_color=tema["destaque"]).pack(pady=(2, 0))
        ctk.CTkLabel(self, text=f"Banco: {self.host_conectado}", font=("Segoe UI", 14, "italic"), text_color="gray").pack(pady=(0, 2))
        
        card_dash = ctk.CTkFrame(self, corner_radius=20, border_width=1, border_color=tema["destaque"], fg_color=tema["card"])
        card_dash.pack(expand=True, padx=40, pady=(0, 5), fill="both")
        
        self.tabs = ctk.CTkTabview(card_dash, corner_radius=15, segmented_button_selected_color=tema["destaque"], fg_color=tema["card"])
        self.tabs.pack(fill="both", expand=True, padx=15, pady=2)
        t_xml = self.tabs.add("Gerador de XML")
        self.tabs.add("Monitor de XML")
        if self.nivel_acesso == "admin": self.tabs.add("MySQL Query")
        
        f_main = ctk.CTkFrame(t_xml, fg_color="transparent"); f_main.pack(fill="x", padx=30, pady=0)
        f_top = ctk.CTkFrame(f_main, fg_color="transparent"); f_top.pack(fill="x", pady=0)
        f_left = ctk.CTkFrame(f_top, fg_color="transparent"); f_left.pack(side="left", fill="both", expand=True)
        
        self.add_lbl(f_left, "Razão Social (Base MySQL):", self.fonte_bold)
        self.lbl_razao = ctk.CTkLabel(f_left, text="Selecione uma Loja", text_color="gray", font=("Segoe UI", 12, "italic")); self.lbl_razao.pack(anchor="w", padx=10)
        self.add_lbl(f_left, "Selecionar Loja:", self.fonte_bold)

        # --- Lógica de Identificação Offline/Contexto ---
        lojas = []
        import socket
        ips_locais = ["127.0.0.1", "localhost"]
        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None):
                ip_encontrado = info[4][0]
                if "." in ip_encontrado and ip_encontrado not in ips_locais: ips_locais.append(ip_encontrado)
        except Exception as e:
            print(e)

        try:
            with self.db_conexao.cursor() as cursor:
                
                self.db_conexao.ping(reconnect=True)

                placeholders = ', '.join(['%s'] * len(ips_locais))

                query = f"""
                SELECT
                    l.codigo_loja,
                    l.razao,
                    c.matriz
                FROM loja l
                INNER JOIN configuracao_loja c
                    ON l.codigo_loja = c.codigo_loja
                WHERE c.ip_loja IN ({placeholders})
                """

                cursor.execute(query, tuple(ips_locais))

                config_local = cursor.fetchone()

                if config_local and int(config_local['matriz']) == 0:

                    lojas = [
                        f"{config_local['codigo_loja']} - {config_local['razao']}"
                    ]

                else:

                    cursor.execute(
                        """
                        SELECT DISTINCT
                            l.codigo_loja,
                            l.razao
                        FROM loja l
                        INNER JOIN pdv p
                            ON l.codigo_loja = p.codigo_loja
                        WHERE p.situacao_pdv IN (2, 3)
                        ORDER BY l.codigo_loja
                        """
                    )

                    lojas = [
                        f"{r['codigo_loja']} - {r['razao']}"
                        for r in cursor.fetchall()
                    ]

        except Exception as e:
            print(e)
            lojas = ["Erro ao carregar lojas"]

        self.loja_cb = ctk.CTkComboBox(f_left, values=lojas, width=400, border_color=tema["destaque"], command=self.atualizar_dados_loja)
        self.loja_cb.pack(anchor="w", padx=10)
        if len(lojas) == 1:
            self.loja_cb.set(lojas[0]); self.after(100, lambda: self.atualizar_dados_loja(lojas[0]))
        else: self.loja_cb.set("Selecione uma Loja")

        # --- Painel Lateral CNPJ ---
        f_right = ctk.CTkFrame(f_top, fg_color="transparent"); f_right.pack(side="right", padx=10)
        card_cnpj = ctk.CTkFrame(f_right, width=310, height=80, corner_radius=15, border_width=1, border_color=tema["destaque"], fg_color="transparent")
        card_cnpj.pack(); card_cnpj.pack_propagate(False)
        ctk.CTkLabel(card_cnpj, text="CNPJ da Loja Selecionada:", font=self.fonte_bold).pack(pady=(2, 0))
        self.lbl_cnpj = ctk.CTkLabel(card_cnpj, text="00.000.000/0000-00", font=("Segoe UI", 20, "bold"), text_color=tema["destaque"]); self.lbl_cnpj.pack(expand=True)
        
        # --- Filtros de Tipo e Status ---
        f_row1 = ctk.CTkFrame(f_main, fg_color="transparent"); f_row1.pack(fill="x", pady=0)
        f_tipo = ctk.CTkFrame(f_row1, fg_color="transparent"); f_tipo.pack(side="left")
        self.add_lbl(f_tipo, "Tipo:", self.fonte_bold); self.tipo_cb = ctk.CTkComboBox(f_tipo, values=["1 - NFC-e", "2 - SAT-CF-e"], width=180, border_color=tema["destaque"]); self.tipo_cb.pack(padx=10)
        f_stat = ctk.CTkFrame(f_row1, fg_color="transparent"); f_stat.pack(side="left", padx=20)
        self.add_lbl(f_stat, "Status:", self.fonte_bold)
        self.status_cb = ctk.CTkComboBox(f_stat, values=["Todos", "102 - Venda de NFCe", "103 - Cancelamento de NFCe", "105 - Inutilizacao Numeracao de NFCe"], width=280, border_color=tema["destaque"]); self.status_cb.set("Todos"); self.status_cb.pack(padx=10)
        
        # --- PDV e Datas ---
        f_row2 = ctk.CTkFrame(f_main, fg_color="transparent"); f_row2.pack(fill="x", pady=0)
        f_pdv = ctk.CTkFrame(f_row2, fg_color="transparent"); f_pdv.pack(side="left")
        self.add_lbl(f_pdv, "PDV:", self.fonte_bold); self.pdv_cb = ctk.CTkComboBox(f_pdv, values=["Todos"], width=180, border_color=tema["destaque"]); self.pdv_cb.pack(padx=10)
        f_per = ctk.CTkFrame(f_row2, fg_color="transparent"); f_per.pack(side="left", padx=20)
        self.add_lbl(f_per, "Período (Data Inicial / Final):", self.fonte_bold)
        f_datas = ctk.CTkFrame(f_per, fg_color="transparent"); f_datas.pack(padx=10)
        self.ent_d_ini = self.criar_campo_dash_placeholder(f_datas, "00/00/0000", 120, tema["destaque"], data=True); self.ent_d_ini.bind("<Return>", lambda e: self.gerar_xml_final())
        ctk.CTkLabel(f_datas, text="até").pack(side="left", padx=5)
        self.ent_d_fim = self.criar_campo_dash_placeholder(f_datas, "00/00/0000", 120, tema["destaque"], data=True); self.ent_d_fim.bind("<Return>", lambda e: self.gerar_xml_final())
        
        # --- Sequência ---
        self.add_lbl(f_main, "Sequência (Inicial / Final):", self.fonte_bold); f_seq = ctk.CTkFrame(f_main, fg_color="transparent"); f_seq.pack(anchor="w", padx=10)
        self.ent_s_ini = self.criar_campo_dash_placeholder(f_seq, "0", 100, tema["destaque"]); self.ent_s_ini.bind("<KeyRelease>", self.trava_sequencia)
        ctk.CTkLabel(f_seq, text=" a ").pack(side="left")
        self.ent_s_fim = ctk.CTkEntry(f_seq, width=100, border_color=tema["destaque"], state="disabled", fg_color=("#D3D3D3", "#3D3D3D")); self.ent_s_fim.insert(0, "0"); self.ent_s_fim.pack(side="left")
        
        # --- BARRA DE BOTÕES COM CORREÇÃO ---
        self.add_lbl(f_main, "Caminho de Destino:", self.fonte_bold)
        f_path = ctk.CTkFrame(f_main, fg_color="transparent") # CORRIGIDO DE "transparent river" PARA "transparent"
        f_path.pack(fill="x", padx=10)
        self.ent_path = self.criar_campo_dash_placeholder(f_path, "", 340, tema["destaque"])
        
        # Botões com referências para trava
        self.btn_procurar = ctk.CTkButton(f_path, text="Procurar", width=80, command=self.escolher_pasta)
        self.btn_procurar.pack(side="left", padx=2)
        
        self.btn_xml_mes = ctk.CTkButton(f_path, text="XML Mes", width=80, fg_color="#c84a4a", command=lambda: self.automacao_pastas("XML"))
        self.btn_xml_mes.pack(side="left", padx=2)
        
        self.btn_xml_falt = ctk.CTkButton(f_path, text="XML Faltantes", width=100, fg_color="#d4ac0d", text_color="black", command=lambda: self.automacao_pastas("XML FALTANTES"))
        self.btn_xml_falt.pack(side="left", padx=2)
        
        self.btn_pasta = ctk.CTkButton(f_path, text="Pasta", width=65, fg_color="#e67e22", command=self.criar_pasta_avulsa)
        self.btn_pasta.pack(side="left", padx=2)
        
        self.btn_compactar = ctk.CTkButton(f_path, text="Compactar", width=90, fg_color="#8e44ad", command=self.compactar_manual)
        self.btn_compactar.pack(side="left", padx=2)
        
        # Status e Progresso
        self.lbl_gerando = ctk.CTkLabel(t_xml, text="Aguardando ação...", font=("Segoe UI", 11, "italic"), text_color="gray"); self.lbl_gerando.pack(pady=(2, 0))
        self.prog_xml = ctk.CTkProgressBar(t_xml, height=14, progress_color=tema["destaque"]); self.prog_xml.set(0); self.prog_xml.pack(fill="x", padx=40, pady=(1, 5))
        
        self.btn_gerar_final = ctk.CTkButton(t_xml, text="GERAR XML AGORA", font=("Segoe UI", 20, "bold"), fg_color="#2d8a4e", height=55, width=480, corner_radius=15, command=self.gerar_xml_final)
        self.btn_gerar_final.pack(pady=(0, 10))

    def compactar_manual(self):

        caminho = self.ent_path.get().strip()

        if not caminho or not os.path.exists(caminho):
            return messagebox.showwarning(
                "Aviso",
                "Selecione ou crie uma pasta válida primeiro!"
            )

        try:

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
                return messagebox.showerror(
                    "Erro",
                    "WinRAR não encontrado."
                )

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
            )

            messagebox.showinfo(
                "Sucesso",
                "Arquivo .rar gerado com sucesso!"
            )

        except Exception as e:

            messagebox.showerror(
                "Erro",
                f"Falha ao compactar:\n{e}"
            )

    def criar_pasta_avulsa(self):
        diretorio = filedialog.askdirectory()
        if diretorio:
            nome = CustomInputDialog(self, "Nova Pasta", "Digite o nome da pasta:").get_input()
            if nome: 
                path = os.path.join(diretorio, nome); os.makedirs(path, exist_ok=True)
                self.ent_path.delete(0, "end"); self.ent_path.insert(0, path)
                messagebox.showinfo("Sucesso", f"Pasta '{nome}' criada!"); self.registrar_evento(f"Pasta manual: {nome}")

    def criar_campo_dash_placeholder(self, master, placeholder, width, cor, data=False):
        e = ctk.CTkEntry(master, width=width, border_color=cor); e.insert(0, placeholder); e.pack(side="left", padx=2)
        e.bind("<FocusIn>", lambda ev: self.gerenciar_placeholder(e, placeholder, "in")); e.bind("<FocusOut>", lambda ev: self.gerenciar_placeholder(e, placeholder, "out"))
        if data: e.bind("<KeyRelease>", lambda ev: self.formatar_data(e, ev))
        return e

    def add_lbl(self, master, text, font): ctk.CTkLabel(master, text=text, font=font).pack(anchor="w", padx=10, pady=0)

    def atualizar_dados_loja(self, escolha):
        try:
            cod = escolha.split(" - ")[0]; self.lbl_razao.configure(text=escolha.split(" - ")[1])
            with self.db_conexao.cursor() as cursor:
                cursor.execute("SELECT numero_pdv FROM pdv WHERE codigo_loja=%s AND situacao_pdv IN (2, 3) ORDER BY numero_pdv", (cod,))
                self.pdv_cb.configure(values=["Todos"] + [str(r['numero_pdv']) for r in cursor.fetchall()]); self.pdv_cb.set("Todos")
                cursor.execute("SELECT cnpj FROM loja WHERE codigo_loja = %s", (cod,))
                res = cursor.fetchone()
                if res:
                    p = "".join(filter(str.isdigit, str(res['cnpj']))).zfill(14)
                    self.lbl_cnpj.configure(text=f"{p[:2]}.{p[2:5]}.{p[5:8]}/{p[8:12]}-{p[12:]}")
        except: self.lbl_cnpj.configure(text="Erro ao carregar")

    def formatar_data(self, entry, event):
        if event.keysym in ("Left", "Right", "Up", "Down", "Home", "End", "BackSpace", "Delete"):
            return
        pos_cursor = entry.index("insert")
        original = entry.get()
        v = "".join(filter(str.isdigit, original))[:8]
        res = ""
        if len(v) > 0: res += v[:2]
        if len(v) > 2: res += "/" + v[2:4]
        if len(v) > 4: res += "/" + v[4:8]
        if original != res:
            entry.delete(0, "end")
            entry.insert(0, res)
            entry.icursor(pos_cursor + (1 if len(res) > len(original) else 0))

    def trava_sequencia(self, e):
        if e.keysym in ("Left", "Right", "Up", "Down", "Home", "End", "Tab"):
            return
        pos_cursor = self.ent_s_ini.index("insert")
        original = self.ent_s_ini.get()
        v = "".join(filter(str.isdigit, original))
        if original != v:
            self.ent_s_ini.delete(0, "end")
            self.ent_s_ini.insert(0, v)
            self.ent_s_ini.icursor(pos_cursor)
        if v not in ["0", ""]: 
            self.ent_s_fim.configure(state="normal", fg_color="transparent")
        else: 
            self.ent_s_fim.configure(state="normal")
            self.ent_s_fim.delete(0, "end")
            self.ent_s_fim.insert(0, "0")
            self.ent_s_fim.configure(state="disabled", fg_color=("#D3D3D3", "#3D3D3D"))

    def gerenciar_botoes_operacionais(self, estado):
        botoes = [self.btn_procurar, self.btn_xml_mes, self.btn_xml_falt, self.btn_pasta, self.btn_compactar]
        for btn in botoes:
            btn.configure(state=estado)

    def escolher_pasta(self):
        p = filedialog.askdirectory()
        if p: self.ent_path.delete(0, "end"); self.ent_path.insert(0, p)

    def automacao_pastas(self, prefixo):
        loja = self.loja_cb.get()
        if " - " not in loja: return messagebox.showwarning("Aviso", "Selecione a loja!")
        cod = loja.split(" - ")[0]; h = datetime.now(); m_idx, a = (h.month-1, h.year) if h.month > 1 else (12, h.year-1)
        nome_p = f"{prefixo} LJ{cod} {MESES[m_idx]} {a}"; caminho = os.path.join(os.getcwd(), nome_p)
        if os.path.exists(caminho):
            if not messagebox.askyesno("Substituir", f"A pasta '{nome_p}' já existe. Substituir?"): return
            shutil.rmtree(caminho)
        os.makedirs(caminho); self.ent_path.delete(0, "end"); self.ent_path.insert(0, caminho)
        messagebox.showinfo("Sucesso", f"Pasta '{nome_p}' criada com sucesso!")
        while messagebox.askyesno("Incluir PDV", "Deseja incluir um PDV nesta organização?"):
            num = CustomInputDialog(self, "Novo PDV", "Digite o número do PDV:").get_input()
            if num:
                pdv_path = os.path.join(caminho, f"PDV {num}")
                if not os.path.exists(pdv_path):
                    os.makedirs(pdv_path)
                    messagebox.showinfo("Sucesso", f"Pasta PDV {num} criada com sucesso!")
                else: messagebox.showwarning("Aviso", "A pasta já existe.")
            else: break

    def gerar_xml_final(self):
        self.btn_gerar_final.configure(state="disabled", text="PROCESSANDO...")
        self.executar_processamento_xml()

    def abrir_prompt_pendencias(self, total_pendentes):
        msg_janela = ctk.CTkToplevel(self)
        msg_janela.title("Atenção - Notas Pendentes")
        msg_janela.geometry("450x200")
        msg_janela.resizable(False, False)
        try:
            msg_janela.attributes("-toolwindow", True)
        except:
            pass
        msg_janela.attributes("-topmost", True)
        msg_janela.grab_set()
        
        msg_janela.update_idletasks()
        x = (msg_janela.winfo_screenwidth() // 2) - (450 // 2)
        y = (msg_janela.winfo_screenheight() // 2) - (200 // 2)
        msg_janela.geometry(f"+{x}+{y}")

        lbl = ctk.CTkLabel(msg_janela, text=f"Existem {total_pendentes} movimentos de NFC-e pendentes\nde envio neste período. Deseja continuar?", 
                           font=("Arial", 15, "bold"), justify="center")
        lbl.pack(pady=25)

        self.resposta_pendencia = None

        def definir_resp(valor):
            self.resposta_pendencia = valor
            msg_janela.destroy()

        msg_janela.bind("<Return>", lambda e: definir_resp("Sim"))
        msg_janela.bind("<Escape>", lambda e: definir_resp("Não"))

        btn_f = ctk.CTkFrame(msg_janela, fg_color="transparent")
        btn_f.pack(pady=10)

        btn_sim = ctk.CTkButton(btn_f, text="Sim", width=90, fg_color="#28a745", command=lambda: definir_resp("Sim"))
        btn_sim.pack(side="left", padx=10)
        btn_sim.focus_set() 

        ctk.CTkButton(btn_f, text="Não", width=90, fg_color="#dc3545", command=lambda: definir_resp("Não")).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="Verificar", width=100, fg_color="#ff8c00", command=lambda: definir_resp("Verificar")).pack(side="left", padx=10)

        self.wait_window(msg_janela)
        return self.resposta_pendencia

    def executar_processamento_xml(self):
        loja_s = self.loja_cb.get()
        if " - " not in loja_s:

            self.after(
                0,
                lambda: messagebox.showwarning(
                    "Aviso",
                    "Selecione uma loja!"
                )
            )

            self.after(
                0,
                lambda: self.btn_gerar_final.configure(
                    state="normal",
                    text="GERAR XML AGORA"
            )
        )

            return
        
        num_loj = loja_s.split(" - ")[0]
        tipo_ui, status_ui, pdv_ui = self.tipo_cb.get(), self.status_cb.get(), self.pdv_cb.get()
        d_ini, d_fim = self.ent_d_ini.get(), self.ent_d_fim.get()
        seq_ini, seq_fim = self.ent_s_ini.get() or "0", self.ent_s_fim.get() or "0"
        destino = self.ent_path.get()
        
        if not destino or not os.path.exists(destino):

            self.after(
                0,
                lambda: messagebox.showwarning(
                    "Aviso",
                    "Selecione uma pasta de destino válida!"
                )
            )

            self.after(
                0,
                lambda: self.btn_gerar_final.configure(
                    state="normal",
                    text="GERAR XML AGORA"
                )
            )

            return

        try:
            dt_ini_sql = datetime.strptime(d_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
            dt_fim_sql = datetime.strptime(d_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
        except:

            self.after(
                0,
                lambda: messagebox.showwarning(
                    "Erro",
                    "Data inválida!"
                )
            )

            self.after(
                0,
                lambda: self.btn_gerar_final.configure(
                    state="normal",
                    text="GERAR XML AGORA"
                )
            )

            return

        self.after(0, lambda: self.gerenciar_botoes_operacionais("disabled"))
        self.after(0, lambda: self.btn_gerar_final.configure(state="disabled", text="PROCESSANDO..."))

        # --- MOTOR ASSÍNCRONO EM THREAD PARA IMPEDIR TRAVAMENTOS DA INTERFACE ---
        def r_process():
            try:
                # --- PASSO 1: PRÉ-VALIDAÇÃO DE NOTAS PENDENTES ---
                with self.db_conexao.cursor() as cursor:
                    sql_p = """
                        SELECT COUNT(*) as total FROM mov_nfc 
                        WHERE num_loj = %s AND dat_hor_ems >= %s AND dat_hor_ems <= %s 
                        AND sit_env_nfc <> 2 AND ope IN (102, 103, 105)
                    """
                    cursor.execute(sql_p, (num_loj, dt_ini_sql + " 00:00:00", dt_fim_sql + " 23:59:59"))
                    total_pendentes = cursor.fetchone()['total']

                # --- PASSO 2: FILTRO EM TELA PARA GRAVAÇÃO DOS XMLs FISCAIS ---
                stats = {
                    "bruto": 0, "ign_112": 0, "ign_vazio": 0, "ign_integridade": 0, 
                    "ign_serie": 0, "ign_ui": 0, "sucesso": 0, "inut": 0, "vend": 0, "canc": 0
                }

                with self.db_conexao.cursor() as cursor:
                    cursor.execute("SELECT numero_pdv FROM pdv WHERE codigo_loja = %s AND situacao_pdv IN (2, 3)", (num_loj,))
                    pdvs_validos = [int(r['numero_pdv']) for r in cursor.fetchall()]

                    query_where = "WHERE m.num_loj = %s AND m.dat_hor_ems >= %s AND m.dat_hor_ems <= %s AND m.amb = 1 AND m.sit_env_nfc = 2"
                    query_params = [num_loj, dt_ini_sql + " 00:00:00", dt_fim_sql + " 23:59:59"]

                    if status_ui != "Todos":
                        query_where += " AND m.ope = %s"
                        query_params.append(status_ui.split(" - ")[0])
                    else:
                        query_where += " AND m.ope IN (102, 103, 105)"

                    if pdv_ui != "Todos":
                        query_where += " AND m.num_pdv = %s"
                        query_params.append(pdv_ui)

                    query_total = f"""
                        SELECT m.*, l.cnpj as cnpj_loja FROM mov_nfc m 
                        LEFT JOIN loja l ON m.num_loj = l.codigo_loja
                        {query_where}
                        ORDER BY m.num_loj, m.num_nfc
                        """
                    cursor.execute(query_total, tuple(query_params))

                    dados_crus = []

                    while True:
                        lote = cursor.fetchmany(500)

                        if not lote:
                            break

                        dados_crus.extend(lote)
                    stats["bruto"] = len(dados_crus)

                mapa_final = {}
                import re
                
                for r in dados_crus:
                    base_ser = str(r.get('sre_nfc') or "001").zfill(3)
                    n_pdv, n_nfc, ope_atual = int(r['num_pdv']), int(r['num_nfc']), int(r['ope'])

                    if n_pdv not in pdvs_validos:
                        stats["ign_integridade"] += 1; continue
                        
                    if base_ser in ("011", "000", "999"): stats["ign_serie"] += 1; continue
                    if num_loj == "1" and base_ser == "005": stats["ign_serie"] += 1; continue

                    if pdv_ui != "Todos" and str(n_pdv) != pdv_ui: stats["ign_ui"] += 1; continue
                    if status_ui != "Todos" and str(ope_atual) != status_ui.split(" - ")[0]: stats["ign_ui"] += 1; continue

                    env_raw, ret_raw = str(r['xml_env'] or ""), str(r['xml_ret'] or "")
                    if "<" in env_raw or "<" in ret_raw:
                        mapa_final[(base_ser, n_pdv, n_nfc)] = r
                    else:
                        stats["ign_vazio"] += 1

                # Gravação estável dos XMLs físicos em disco
                total_lista = len(mapa_final)
                pasta_loja = os.path.join(destino, f"loja{int(num_loj):03d}")
                os.makedirs(pasta_loja, exist_ok=True)

                for idx, ((serie, pdv, n_nfc), row) in enumerate(mapa_final.items()):
                    env, ret = row['xml_env'] or "", row['xml_ret'] or ""
                    if isinstance(env, bytes): env = env.decode('utf-8', errors='ignore')
                    if isinstance(ret, bytes): ret = ret.decode('utf-8', errors='ignore')
                    
                    if "<nfeProc" in env or "<procInut" in env: xml_f = env
                    elif "<NFe" in env and "<infProt" in ret:
                        m = re.search(r'(<protNFe.*?</protNFe>)', ret, re.DOTALL); p_xml = m.group(1) if m else ""
                        n_corpo = env.replace('<?xml version="1.0" encoding="UTF-8"?>', '').strip()
                        xml_f = f'<?xml version="1.0" encoding="UTF-8"?><nfeProc versao="4.00" xmlns="http://www.portalfiscal.inf.br/nfe">{n_corpo}{p_xml}</nfeProc>'
                    else: xml_f = ret if len(ret) > len(env) else env

                    env_ope = int(row['ope'])
                    suf = "vend" if env_ope == 102 else "canc" if env_ope == 103 else "inut"
                    if suf == "vend": stats["vend"] += 1
                    elif suf == "canc": stats["canc"] += 1
                    else: stats["inut"] += 1


                    data_mov = row['dat_hor_ems']

                    if isinstance(data_mov, str):

                        try:
                            data_mov = datetime.strptime(
                                data_mov,
                                "%Y-%m-%d %H:%M:%S"
                            )

                        except:
                            data_mov = datetime.fromisoformat(data_mov)

                    path_dia = os.path.join(
                        pasta_loja,
                        data_mov.strftime("%d%m%Y")
                    )

                    os.makedirs(path_dia, exist_ok=True)

                    n_chave = row['chv_acs'] if row['chv_acs'] and len(row['chv_acs']) >= 40 else f"manual-{n_nfc}"
                    nome_arq = f"nfce-{n_chave}-{suf}.xml"
                    
                    if idx % 30 == 0:
                        self.after(
                            0,
                            lambda n=n_nfc:
                            self.lbl_gerando.configure(
                            text=f"Processando NFC-e {n}"
                        )
                    )
                    with open(os.path.join(path_dia, nome_arq), "w", encoding="utf-8") as f: f.write(xml_f)
                    stats["sucesso"] += 1
                    if total_lista > 0 and idx % 50 == 0:
                        progresso = (idx + 1) / total_lista

                        self.after(
                           0,
                           lambda v=progresso:
                           self.prog_xml.set(v)
                        )

                # --- PASSO 5 OTIMIZADO - RELATÓRIO DE NUMERAÇÃO FALTANTE ---
                possui_quebras = False
                relatorio_final = []

                try:
                     s_ini_val = int(seq_ini)
                except:
                     s_ini_val = 0

                try:
                     s_fim_val = int(seq_fim)
                except:
                     s_fim_val = 0

                with self.db_conexao.cursor() as cursor:

                    cursor.execute("""
                        SELECT DISTINCT COALESCE(sre_nfc, '001') as sre_nfc
                        FROM mov_nfc
                        WHERE num_loj = %s
                        AND amb = 1
                        AND sit_env_nfc = 2
                    """, (num_loj,))

                    series_ativas = [
                         str(r['sre_nfc']).strip().zfill(3)
                         for r in cursor.fetchall()
                    ]

                for serie in sorted(series_ativas):

                    if not serie:
                        continue

                    if serie in ("000", "011", "999"):
                        continue

                    if num_loj == "1" and serie == "005":
                        continue

                    self.after(
                        0,
                        lambda s=serie:
                        self.lbl_gerando.configure(
                            text=f"Verificando sequência Série {s}"
                        )
                    )

                    query_seq = """
                        SELECT DISTINCT num_nfc
                        FROM mov_nfc
                        WHERE num_loj = %s
                        AND sre_nfc = %s
                        AND amb = 1
                        AND sit_env_nfc = 2
                    """

                    params_seq = [num_loj, serie]

                    if pdv_ui != "Todos":

                        query_seq += " AND num_pdv = %s"
                        params_seq.append(pdv_ui)

                    if status_ui != "Todos":

                        query_seq += " AND ope = %s"

                        params_seq.append(
                            status_ui.split(" - ")[0]
                        )

                    else:

                        query_seq += " AND ope IN (102,103,105)"

                    query_seq += """
                        AND dat_hor_ems >= %s
                        AND dat_hor_ems <= %s
                        ORDER BY num_nfc
                    """

                    params_seq.append(
                        dt_ini_sql + " 00:00:00"
                    )

                    params_seq.append(
                        dt_fim_sql + " 23:59:59"
                    )

                    with self.db_conexao.cursor() as cursor:

                        cursor.execute(
                            query_seq,
                            tuple(params_seq)
                        )

                        resultado_notas = cursor.fetchall()

                    notas = []

                    for row_nota in resultado_notas:

                        try:

                            n = int(row_nota['num_nfc'])

                            if s_ini_val > 0 and n < s_ini_val:
                                continue

                            if s_fim_val > 0 and n > s_fim_val:
                                continue

                            notas.append(n)

                        except:
                            pass

                    if not notas:
                        continue

                    notas = sorted(set(notas))

                    relatorio_serie = []

                    ultimo = notas[0]

                    for atual in notas[1:]:

                        if atual > ultimo + 1:

                            possui_quebras = True

                            inicio_gap = ultimo + 1
                            fim_gap = atual - 1

                            tamanho_gap = fim_gap - inicio_gap

                            # GAP PEQUENO → LISTA INDIVIDUAL
                            if tamanho_gap <= 15:

                                for nf in range(
                                    inicio_gap,
                                    fim_gap + 1
                                ):

                                    relatorio_serie.append(
                                        f"         {nf} - NUMERAÇÃO NÃO CONSTA NA MOV_NFC"
                                    )

                            # GAP GRANDE → COMPACTADO
                            else:

                                relatorio_serie.append(
                                    f"         {inicio_gap} até {fim_gap} - NUMERAÇÃO NÃO CONSTA NA MOV_NFC"
                                )

                        ultimo = atual

                    if relatorio_serie:

                        bloco = (
                            f"----SERIE NFCe: {serie}----\n"
                            + "\n".join(relatorio_serie)
                            + "\n"
                        )

                        relatorio_final.append(bloco)

                    if possui_quebras:

                        ext = f".{int(num_loj):03d}"

                        caminho_relatorio = os.path.join(
                            destino,
                            f"Numeracao_Faltante{ext}"
                        )

                        with open(
                            caminho_relatorio,
                            "w",
                            encoding="utf-8"
                        ) as f:

                            f.write(
                                "\n".join(relatorio_final)
                            )

                # Finaliza e limpa o status operacional da UI de forma síncrona estável
                self.after(0, lambda: self.lbl_gerando.configure(text="Processo finalizado."))
                self.after(0, lambda: self.gerenciar_botoes_operacionais("normal"))
                self.after(0, lambda: self.btn_gerar_final.configure(state="normal", text="GERAR XML AGORA"))
                self.after(0, lambda: messagebox.showinfo("Sucesso","Geração Concluída!"))

            except Exception as e:
                self.after(0, lambda err=e: messagebox.showerror("Erro Fatal", f"Falha no processamento: {str(err)}"))
                self.after(0, lambda: self.gerenciar_botoes_operacionais("normal"))
                self.after(0, lambda: self.btn_gerar_final.configure(state="normal", text="GERAR XML AGORA"))
                self.after(0, lambda: self.lbl_gerando.configure(text="Processo finalizado com erro."))

        # Executa o r_process em background absoluto livrando a Thread principal do Tkinter
        threading.Thread(
            target=r_process,
            daemon=True
        ).start()

    def solicitar_compactacao(self, destino):

        if messagebox.askyesno(
            "Compactar",
            "Deseja compactar a pasta gerada agora?"
        ):

            try:

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

                messagebox.showinfo(
                    "OK",
                    f"Arquivo gerado:\n{zip_final}"
                )

            except Exception as e:

                messagebox.showerror(
                    "Erro",
                    f"Compactação falhou:\n{e}"
                )

    def abrir_logs(self):
        log_win = ctk.CTkToplevel(self); log_win.title("Logs")
        log_win.attributes("-topmost", True); log_win.attributes("-toolwindow", 1); log_win.resizable(False, False)
        lx, ly = self.winfo_x() + (self.winfo_width() // 2) - 300, self.winfo_y() + (self.winfo_height() // 2) - 200
        log_win.geometry(f"600x400+{lx}+{ly}")
        txt = ctk.CTkTextbox(log_win, width=580, height=380, font=("Segoe UI", 12))
        txt.pack(padx=10, pady=10); txt.insert("0.0", "\n".join(self.logs_historico) if self.logs_historico else "Vazio.")
        txt.configure(state="disabled")

if __name__ == "__main__":
    app = FiuzaEnterpriseApp(); app.mainloop()