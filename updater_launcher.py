import sys
import os
import subprocess
import time
import threading
from tkinter import Tk, Frame, Label, Button, ttk, messagebox

from updater import baixar_atualizacao

class UpdaterGUI:
    def __init__(self, root, download_url):
        self.root = root
        self.download_url = download_url
        self.versao_online = "Nova Versão"
        
        # Carrega o número da versão salva pelo sistema principal se existir
        if os.path.exists("ultima_versao.txt"):
            try:
                with open("ultima_versao.txt", "r", encoding="utf-8") as f:
                    self.versao_online = f.read().strip()
            except:
                pass

        # Configurações da Janela (Estilo Janela de Setup Moderna)
        self.root.title("Fiuza Technology - Atualizador")
        self.largura, self.altura = 450, 240
        px = (self.root.winfo_screenwidth() // 2) - (self.largura // 2)
        py = (self.root.winfo_screenheight() // 2) - (self.altura // 2)
        self.root.geometry(f"{self.largura}x{self.altura}+{px}+{py}")
        self.root.resizable(False, False)
        self.root.configure(bg="#F5F7FA")
        
        # Garante foco total na tela de update
        self.root.attributes("-topmost", True)

        # Estilo Flat para a Barra de Progresso Nativa
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(
            "Flat.Horizontal.TProgressbar", 
            thickness=14, 
            background="#3b8ed0", 
            troughcolor="#E9EEF5", 
            bordercolor="#F5F7FA", 
            lightcolor="#3b8ed0", 
            darkcolor="#3b8ed0"
        )

        # Montagem dos Elementos de Interface
        self.f_card = Frame(self.root, bg="#FFFFFF", bd=1, relief="flat", highlightbackground="#3b8ed0", highlightthickness=1)
        self.f_card.pack(fill="both", expand=True, padx=15, pady=15)

        self.lbl_titulo = Label(self.f_card, text="Atualizando Sistema", font=("Segoe UI", 18, "bold"), fg="#222222", bg="#FFFFFF")
        self.lbl_titulo.pack(pady=(20, 5))

        self.lbl_versao = Label(self.f_card, text=f"Download da versão {self.versao_online}", font=("Segoe UI", 12), fg="#555555", bg="#FFFFFF")
        self.lbl_versao.pack(pady=2)

        self.progress = ttk.Progressbar(self.f_card, style="Flat.Horizontal.TProgressbar", length=340, mode="determinate")
        self.progress.pack(pady=15)

        self.lbl_status = Label(self.f_card, text="Aguardando encerramento do sistema principal...", font=("Segoe UI", 10, "italic"), fg="#777777", bg="#FFFFFF")
        self.lbl_status.pack(pady=5)

        # Botão de OK (Inicia desativado/escondido)
        self.btn_ok = Button(
            self.f_card, text="OK", font=("Segoe UI", 12, "bold"), width=12, height=1,
            bg="#2d8a4e", fg="#FFFFFF", activebackground="#216f3e", activeforeground="#FFFFFF",
            bd=0, relief="flat", cursor="hand2", command=self.concluir_e_reabrir
        )

        # Dispara o gatilho assíncrono do download para não travar a janela gráfica
        threading.Thread(target=self.processar_atualizacao, daemon=True).start()

    def atualizar_barra(self, valor):
        """ Atualiza a preenchimento da barra de progresso (0.0 a 1.0) """
        self.progress['value'] = valor * 100
        porcentagem = int(valor * 100)
        self.lbl_versao.config(text=f"Download da versão {self.versao_online} ({porcentagem}%)")
        self.root.update_idletasks()

    def atualizar_status(self, texto):
        """ Altera o rótulo de rodapé do atualizador """
        self.lbl_status.config(text=texto)
        self.root.update_idletasks()

    def processar_atualizacao(self):
        # 1. Derruba o processo pai por garantia
        try:
            subprocess.run(["taskkill", "/F", "/IM", "Gerador_XML.exe"], capture_output=True)
        except:
            pass
        time.sleep(2.5)

        # 2. Inicia o download interativo passando as funções de atualização da tela
        self.atualizar_status("Conectando ao repositório...")
        sucesso = baixar_atualizacao(
            self.download_url, 
            callback_progresso=self.atualizar_barra, 
            callback_status=self.atualizar_status
        )

        if sucesso:
            # Layout pós-atualização solicitado
            self.progress.pack_forget()
            self.lbl_titulo.config(text="Atualização concluída", fg="#2d8a4e")
            self.lbl_versao.config(text=f"Sistema atualizado com sucesso para\na versão {self.versao_online}!")
            self.lbl_status.pack_forget()
            
            # Exibe o botão de OK centralizado
            self.btn_ok.pack(pady=(10, 15))
        else:
            self.atualizar_status("Falha na atualização. Feche o atualizador.")

    def concluir_e_reabrir(self):
        # Remove o arquivo texto residual
        if os.path.exists("ultima_versao.txt"):
            try: os.remove("ultima_versao.txt")
            except: pass

        # Identifica a pasta e reabre o sistema limpo de herança Admin via Explorer
        if getattr(sys, "frozen", False):
            pasta_app = os.path.dirname(sys.executable)
        else:
            pasta_app = os.path.dirname(os.path.abspath(__file__))

        exe_principal = os.path.join(pasta_app, "Gerador_XML.exe")
        if os.path.exists(exe_principal):
            subprocess.Popen(["explorer.exe", exe_principal], shell=True)
        
        self.root.destroy()
        sys.exit(0)

def main():
    if len(sys.argv) < 2:
        messagebox.showerror("Erro", "URL de atualização não informada.")
        return

    download_url = sys.argv[1]
    
    root = Tk()
    app = UpdaterGUI(root, download_url)
    root.mainloop()

if __name__ == "__main__":
    main()