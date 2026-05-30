import os
import shutil
import time
import socket
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog

from core.logs import registrar_evento
# Importamos o motor real de processamento de XML
from core.xml_processor import XMLProcessor

MESES = [
    "JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

class DashboardApp(ctk.CTkToplevel):

    def __init__(self, master, usuario, conexao):
        super().__init__(master)

        # =====================================================
        # DADOS E SEGURANÇA DE CONEXÃO
        # =====================================================
        self.usuario_atual = usuario
        self.db_conexao = conexao
        
        # Correção segura para extrair o host do objeto Connection do PyMySQL
        self.host_conectado = conexao.kwargs.get('host', 'Desconhecido')
        
        # Mapeia as credenciais para o motor assíncrono ler quando rodar a Thread
        self.db_host = conexao.kwargs.get('host')
        self.db_user = conexao.kwargs.get('user')
        self.db_password = conexao.kwargs.get('password')
        self.db_name = conexao.kwargs.get('database')

        self.nivel_acesso = "admin"

        # Instancia o motor real de processamento passando esta interface como alvo
        self.motor_xml = XMLProcessor(self)

        # =====================================================
        # CONFIG
        # =====================================================
        self.title("Fiuza Technology - Gerador de XML Completo")
        self.geometry("1100x720")
        self.resizable(True, True)
        self.after(100, self.posicionar_janela)

        # =====================================================
        # FONTES
        # =====================================================
        self.fonte_titulo_dash = ("Segoe UI", 34, "bold")
        self.fonte_bold = ("Segoe UI", 14, "bold")

        # =====================================================
        # TEMA
        # =====================================================
        self.config = {"tema_cor": "padrao"}
        self.temas = {
            "padrao": {"janela": "#EDEDED", "card": "#F7F7F7", "destaque": "#3b8ed0"},
            "blue": {"janela": "#E9EEF5", "card": "#F5F7FA", "destaque": "#3b8ed0"},
            "red": {"janela": "#F5EEEE", "card": "#FAF7F7", "destaque": "#c84a4a"},
            "dark": {"janela": "#1B1B1B", "card": "#252525", "destaque": "#3b8ed0"},
            "white": {"janela": "#FFFFFF", "card": "#F8F8F8", "destaque": "#D6D6D6"}
        }

        # =====================================================
        # START
        # =====================================================
        self.setup_dashboard()
        registrar_evento(f"Dashboard iniciada: {usuario}")

    def posicionar_janela(self):
        self.update_idletasks()
        largura = 1100
        altura = 720
        x = int((self.winfo_screenwidth() / 2) - (largura / 2))
        y = 0
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def add_lbl(self, master, texto, fonte):
        lbl = ctk.CTkLabel(master, text=texto, font=fonte)
        lbl.pack(anchor="w", padx=10, pady=(4, 2))
        return lbl

    def criar_campo_dash_placeholder(self, master, placeholder, largura, cor):
        ent = ctk.CTkEntry(master, width=largura, height=32, border_color=cor)
        ent.insert(0, placeholder)
        ent.pack(side="left", padx=2)
        return ent

    def criar_cabecalho(self):
        tema = self.temas[self.config.get("tema_cor", "padrao")]
        header = ctk.CTkFrame(self, height=60, fg_color="transparent")
        header.pack(fill="x", pady=5)

        btn_sair = ctk.CTkButton(header, text="⇢ Sair", width=90, fg_color="#c84a4a", command=self.fechar_dashboard)
        btn_sair.pack(side="right", padx=15)

        btn_log = ctk.CTkButton(header, text="🧾 Log", width=90, fg_color=tema["destaque"])
        btn_log.pack(side="right")

    def fechar_dashboard(self):
        try: self.db_conexao.close()
        except: pass
        try: self.master.deiconify()
        except: pass
        self.destroy()

    # Método obrigatório exigido pelo core/xml_processor para congelar/liberar o painel
    def gerenciar_botoes_operacionais(self, estado):
        self.loja_cb.configure(state=estado)
        self.tipo_cb.configure(state=estado)
        self.status_cb.configure(state=estado)
        self.pdv_cb.configure(state=estado)
        self.ent_d_ini.configure(state=estado)
        self.ent_path.configure(state=estado)
        self.btn_procurar.configure(state=estado)
        self.btn_xml_mes.configure(state=estado)
        self.btn_xml_falt.configure(state=estado)
        self.btn_pasta.configure(state=estado)
        self.btn_compactar.configure(state=estado)

    def setup_dashboard(self):
        for w in self.winfo_children():
            w.destroy()

        tema = self.temas[self.config.get("tema_cor", "padrao")]
        self.configure(fg_color=tema["janela"])
        self.criar_cabecalho()

        ctk.CTkLabel(self, text=f"Bem vindo {self.usuario_atual}!", font=self.fonte_titulo_dash, text_color=tema["destaque"]).pack(pady=(2, 0))
        ctk.CTkLabel(self, text=f"Banco: {self.host_conectado}", font=("Segoe UI", 14, "italic"), text_color="gray").pack(pady=(0, 2))

        card_dash = ctk.CTkFrame(self, corner_radius=20, border_width=1, border_color=tema["destaque"], fg_color=tema["card"])
        card_dash.pack(expand=True, padx=40, pady=(0, 5), fill="both")

        self.tabs = ctk.CTkTabview(card_dash, corner_radius=15, segmented_button_selected_color=tema["destaque"], fg_color=tema["card"])
        self.tabs.pack(fill="both", expand=True, padx=15, pady=5)

        t_xml = self.tabs.add("Gerador de XML")
        self.tabs.add("Monitor de XML")

        if self.nivel_acesso == "admin":
            self.tabs.add("MySQL Query")

        f_main = ctk.CTkFrame(t_xml, fg_color="transparent")
        f_main.pack(fill="x", padx=30, pady=5)

        f_top = ctk.CTkFrame(f_main, fg_color="transparent")
        f_top.pack(fill="x")

        f_left = ctk.CTkFrame(f_top, fg_color="transparent")
        f_left.pack(side="left", fill="both", expand=True)

        self.add_lbl(f_left, "Razão Social (Base MySQL):", self.fonte_bold)
        self.lbl_razao = ctk.CTkLabel(f_left, text="Selecione uma Loja", text_color="gray", font=("Segoe UI", 12, "italic"))
        self.lbl_razao.pack(anchor="w", padx=10)

        self.add_lbl(f_left, "Selecionar Loja:", self.fonte_bold)

        # --- CARGA DINÂMICA DE LOJAS ---
        lojas = []
        ips_locais = ["127.0.0.1", "localhost"]
        try:
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None):
                ip_encontrado = info[4][0]
                if "." in ip_encontrado and ip_encontrado not in ips_locais:
                    ips_locais.append(ip_encontrado)
        except Exception as erro:
            print(erro)

        try:
            with self.db_conexao.cursor() as cursor:
                self.db_conexao.ping(reconnect=True)
                placeholders = ", ".join(["%s"] * len(ips_locais))
                query = f"""
                    SELECT l.codigo_loja, l.razao, c.matriz FROM loja l
                    INNER JOIN configuracao_loja c ON l.codigo_loja = c.codigo_loja
                    WHERE c.ip_loja IN ({placeholders})
                """
                cursor.execute(query, tuple(ips_locais))
                config_local = cursor.fetchone()

                if config_local and int(config_local["matriz"]) == 0:
                    lojas = [f"{config_local['codigo_loja']} - {config_local['razao']}"]
                else:
                    cursor.execute("""
                        SELECT DISTINCT l.codigo_loja, l.razao FROM loja l
                        INNER JOIN pdv p ON l.codigo_loja = p.codigo_loja
                        WHERE p.situacao_pdv IN (2, 3) ORDER BY l.codigo_loja
                    """)
                    lojas = [f"{r['codigo_loja']} - {r['razao']}" for r in cursor.fetchall()]
        except Exception as erro:
            print(erro)
            lojas = ["Erro ao carregar lojas"]

        self.loja_cb = ctk.CTkComboBox(f_left, values=lojas, width=400, border_color=tema["destaque"], command=self.atualizar_dados_loja)
        self.loja_cb.pack(anchor="w", padx=10)

        if len(lojas) == 1:
            self.loja_cb.set(lojas[0])
            self.after(100, lambda: self.atualizar_dados_loja(lojas[0]))
        else:
            self.loja_cb.set("Selecione uma Loja")

        f_right = ctk.CTkFrame(f_top, fg_color="transparent")
        f_right.pack(side="right", padx=10)

        card_cnpj = ctk.CTkFrame(f_right, width=310, height=80, corner_radius=15, border_width=1, border_color=tema["destaque"], fg_color="transparent")
        card_cnpj.pack()
        card_cnpj.pack_propagate(False)

        ctk.CTkLabel(card_cnpj, text="CNPJ da Loja Selecionada:", font=self.fonte_bold).pack(pady=(2, 0))
        self.lbl_cnpj = ctk.CTkLabel(card_cnpj, text="00.000.000/0000-00", font=("Segoe UI", 20, "bold"), text_color=tema["destaque"])
        self.lbl_cnpj.pack(expand=True)

        f_row1 = ctk.CTkFrame(f_main, fg_color="transparent")
        f_row1.pack(fill="x")

        f_tipo = ctk.CTkFrame(f_row1, fg_color="transparent")
        f_tipo.pack(side="left")
        self.add_lbl(f_tipo, "Tipo:", self.fonte_bold)
        self.tipo_cb = ctk.CTkComboBox(f_tipo, values=["1 - NFC-e", "2 - SAT-CF-e"], width=180, border_color=tema["destaque"])
        self.tipo_cb.pack(padx=10)

        f_stat = ctk.CTkFrame(f_row1, fg_color="transparent")
        f_stat.pack(side="left", padx=20)
        self.add_lbl(f_stat, "Status:", self.fonte_bold)
        self.status_cb = ctk.CTkComboBox(f_stat, values=["Todos", "102 - Venda NFCe", "103 - Cancelamento", "105 - Inutilização"], width=280, border_color=tema["destaque"])
        self.status_cb.set("Todos")
        self.status_cb.pack(padx=10)

        f_row2 = ctk.CTkFrame(f_main, fg_color="transparent")
        f_row2.pack(fill="x")

        f_pdv = ctk.CTkFrame(f_row2, fg_color="transparent")
        f_pdv.pack(side="left")
        self.add_lbl(f_pdv, "PDV:", self.fonte_bold)
        self.pdv_cb = ctk.CTkComboBox(f_pdv, values=["Todos"], width=180, border_color=tema["destaque"])
        self.pdv_cb.pack(padx=10)

        f_per = ctk.CTkFrame(f_row2, fg_color="transparent")
        f_per.pack(side="left", padx=20)
        self.add_lbl(f_per, "Período (Inicial / Final):", self.fonte_bold)

        f_datas = ctk.CTkFrame(f_per, fg_color="transparent")
        f_datas.pack(padx=10)
        self.ent_d_ini = self.criar_campo_dash_placeholder(f_datas, "00/00/0000", 120, tema["destaque"])
        ctk.CTkLabel(f_datas, text="até").pack(side="left", padx=5)
        self.ent_d_fim = self.criar_campo_dash_placeholder(f_datas, "00/00/0000", 120, tema["destaque"])

        self.add_lbl(f_main, "Sequência (Inicial / Final):", self.fonte_bold)
        f_seq = ctk.CTkFrame(f_main, fg_color="transparent")
        f_seq.pack(anchor="w", padx=10)
        self.ent_s_ini = self.criar_campo_dash_placeholder(f_seq, "0", 100, tema["destaque"])
        self.ent_s_ini.bind("<KeyRelease>", self.trava_sequencia)

        ctk.CTkLabel(f_seq, text=" a ").pack(side="left")
        self.ent_s_fim = ctk.CTkEntry(f_seq, width=100, border_color=tema["destaque"], state="disabled")
        self.ent_s_fim.insert(0, "0")
        self.ent_s_fim.pack(side="left")

        self.add_lbl(f_main, "Caminho de Destino:", self.fonte_bold)
        f_path = ctk.CTkFrame(f_main, fg_color="transparent")
        f_path.pack(fill="x", padx=10)
        self.ent_path = self.criar_campo_dash_placeholder(f_path, "", 340, tema["destaque"])

        self.btn_procurar = ctk.CTkButton(f_path, text="Procurar", width=80, command=self.escolher_pasta)
        self.btn_procurar.pack(side="left", padx=2)

        self.btn_xml_mes = ctk.CTkButton(f_path, text="XML Mes", width=80, fg_color="#c84a4a", command=lambda: self.automacao_pastas("XML"))
        self.btn_xml_mes.pack(side="left", padx=2)

        self.btn_xml_falt = ctk.CTkButton(f_path, text="XML Faltantes", width=120, fg_color="#d4ac0d", text_color="black", command=lambda: self.automacao_pastas("XML FALTANTES"))
        self.btn_xml_falt.pack(side="left", padx=2)

        self.btn_pasta = ctk.CTkButton(f_path, text="Pasta", width=70, fg_color="#e67e22", command=self.criar_pasta_avulsa)
        self.btn_pasta.pack(side="left", padx=2)

        self.btn_compactar = ctk.CTkButton(f_path, text="Compactar", width=90, fg_color="#8e44ad", command=self.compactar_manual)
        self.btn_compactar.pack(side="left", padx=2)

        self.lbl_gerando = ctk.CTkLabel(t_xml, text="Aguardando ação...", font=("Segoe UI", 11, "italic"), text_color="gray")
        self.lbl_gerando.pack(pady=(2, 0))

        self.prog_xml = ctk.CTkProgressBar(t_xml, height=14, progress_color=tema["destaque"])
        self.prog_xml.set(0)
        self.prog_xml.pack(fill="x", padx=40, pady=(1, 5))

        # Atribui o método unificado para disparar a thread real de geração
        self.btn_gerar_final = ctk.CTkButton(t_xml, text="GERAR XML AGORA", font=("Segoe UI", 20, "bold"), fg_color="#2d8a4e", height=55, width=480, corner_radius=15, command=self.gerar_xml_final)
        self.btn_gerar_final.pack(pady=(0, 10))

    def atualizar_dados_loja(self, escolha):
        try:
            cod = escolha.split(" - ")[0]
            razao = escolha.split(" - ")[1]
            self.lbl_razao.configure(text=razao)

            with self.db_conexao.cursor() as cursor:
                cursor.execute("SELECT numero_pdv FROM pdv WHERE codigo_loja=%s AND situacao_pdv IN (2, 3) ORDER BY numero_pdv", (cod,))
                pdvs = [str(r["numero_pdv"]) for r in cursor.fetchall()]
                self.pdv_cb.configure(values=["Todos"] + pdvs)
                self.pdv_cb.set("Todos")

                cursor.execute("SELECT cnpj FROM loja WHERE codigo_loja=%s", (cod,))
                res = cursor.fetchone()
                if res:
                    p = "".join(filter(str.isdigit, str(res["cnpj"]))).zfill(14)
                    self.lbl_cnpj.configure(text=f"{p[:2]}.{p[2:5]}.{p[5:8]}/{p[8:12]}-{p[12:]}")
        except Exception:
            self.lbl_cnpj.configure(text="Erro ao carregar")

    def trava_sequencia(self, event=None):
        valor = self.ent_s_ini.get().strip()
        if not valor: valor = "0"
        valor = "".join(filter(str.isdigit, valor))
        self.ent_s_ini.delete(0, "end")
        self.ent_s_ini.insert(0, valor)

        self.ent_s_fim.configure(state="normal")
        self.ent_s_fim.delete(0, "end")
        self.ent_s_fim.insert(0, valor)
        self.ent_s_fim.configure(state="disabled")

    def escolher_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.ent_path.delete(0, "end")
            self.ent_path.insert(0, pasta)
            self.lbl_gerando.configure(text="Pasta selecionada.", text_color="#27ae60")

    def automacao_pastas(self, prefixo):
        loja = self.loja_cb.get()
        if " - " not in loja:
            return messagebox.showwarning("Aviso", "Selecione a loja.")

        cod = loja.split(" - ")[0]
        h = datetime.now()
        mes = h.month - 1
        ano = h.year
        nome_pasta = f"{prefixo} LJ{cod} {MESES[mes]} {ano}"
        caminho = os.path.join(os.getcwd(), nome_pasta)

        if os.path.exists(caminho):
            resposta = messagebox.askyesno("Substituir", "A pasta já existe.\nDeseja substituir?")
            if not resposta: return
            shutil.rmtree(caminho)

        os.makedirs(caminho)
        self.ent_path.delete(0, "end")
        self.ent_path.insert(0, caminho)
        messagebox.showinfo("Sucesso", "Pasta criada com sucesso.")

        while True:
            resposta = messagebox.askyesno("PDV", "Deseja adicionar pasta PDV?")
            if not resposta: break
            num = ctk.CTkInputDialog(text="Digite o número do PDV:", title="Novo PDV").get_input()
            if not num: break
            pdv_path = os.path.join(caminho, f"PDV {num}")
            os.makedirs(pdv_path, exist_ok=True)

    def criar_pasta_avulsa(self):
        pasta = filedialog.askdirectory()
        if not pasta: return
        nome = ctk.CTkInputDialog(text="Digite o nome da pasta:", title="Nova Pasta").get_input()
        if not nome: return
        caminho = os.path.join(pasta, nome)
        os.makedirs(caminho, exist_ok=True)

        self.ent_path.delete(0, "end")
        self.ent_path.insert(0, caminho)
        self.lbl_gerando.configure(text="Pasta criada com sucesso.", text_color="#27ae60")
        registrar_evento(f"Pasta criada: {caminho}")

    def compactar_manual(self):
        caminho = self.ent_path.get().strip()
        if not caminho: return messagebox.showwarning("Aviso", "Selecione uma pasta.")
        if not os.path.exists(caminho): return messagebox.showerror("Erro", "Pasta não encontrada.")

        try:
            arquivo_zip = shutil.make_archive(caminho, "zip", caminho)
            self.lbl_gerando.configure(text="Compactação concluída.", text_color="#27ae60")
            registrar_evento(f"Pasta compactada: {arquivo_zip}")
            messagebox.showinfo("Sucesso", "Compactação concluída.")
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    # Conecta o clique do botão diretamente ao motor assíncrono real do core
    def gerar_xml_final(self):
        # Dispara o processamento com as queries reais e a atualização segura da barra de progresso
        self.motor_xml.executar_processamento_xml()