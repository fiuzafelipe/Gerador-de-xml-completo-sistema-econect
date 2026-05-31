import sys
import os
import subprocess
import time
import threading
from tkinter import Tk, Frame, Label, Button, ttk, messagebox

from updater import baixar_atualizacao

class UpdaterGUI:
    def __init__(self, root, download_url, versao_online):
        self.root = root
        self.download_url = download_url
        
        # 🚀 AGORA É DINÂMICO: Recebe diretamente o argumento real do sistema principal
        self.versao_online = versao_online
        
        if os.path.exists("ultima_versao.txt"):
            try:
                with open("ultima_versao.txt", "r", encoding="utf-8") as f:
                    self.versao_online = f.read().strip()
            except:
                pass

        # ---------------------------------------------------------
        # CONFIGURAÇÕES DA JANELA (FORÇAR NASCIMENTO E RENDERIZAÇÃO)
        # ---------------------------------------------------------
        self.root.title("Fiuza Technology - Atualizador")
        self.largura, self.altura = 450, 240
        
        px = (self.root.winfo_screenwidth() // 2) - (self.largura // 2)
        py = (self.root.winfo_screenheight() // 2) - (self.altura // 2)
        self.root.geometry(f"{self.largura}x{self.altura}+{px}+{py}")
        self.root.resizable(False, False)
        self.root.configure(bg="#F5F7FA")
        
        # Garante foco e visibilidade máxima na inicialização
        self.root.attributes("-topmost", True)
        
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(
            "Flat.Horizontal.TProgressbar", 
            thickness=16, 
            background="#3b8ed0", 
            troughcolor="#E9EEF5", 
            bordercolor="#F5F7FA", 
            lightcolor="#3b8ed0", 
            darkcolor="#3b8ed0"
        )

        # ---------------------------------------------------------
        # INTERFACE GRÁFICA (DURANTE A ATUALIZAÇÃO)
        # ---------------------------------------------------------
        self.f_card = Frame(self.root, bg="#FFFFFF", bd=1, relief="flat", highlightbackground="#3b8ed0", highlightthickness=1)
        self.f_card.pack(fill="both", expand=True, padx=15, pady=15)

        self.lbl_titulo = Label(self.f_card, text="Atualizando Sistema", font=("Segoe UI", 18, "bold"), fg="#1A202C", bg="#FFFFFF")
        self.lbl_titulo.pack(pady=(20, 5))

        self.lbl_versao = Label(self.f_card, text=f"Download da versão {self.versao_online}", font=("Segoe UI", 12), fg="#4A5568", bg="#FFFFFF")
        self.lbl_versao.pack(pady=2)

        self.progress = ttk.Progressbar(self.f_card, style="Flat.Horizontal.TProgressbar", length=340, mode="determinate")
        self.progress.pack(pady=15)

        self.lbl_status = Label(self.f_card, text="Preparando ambiente...", font=("Segoe UI", 11, "italic"), fg="#718096", bg="#FFFFFF")
        self.lbl_status.pack(pady=5)

        self.btn_ok = Button(
            self.f_card, text="OK", font=("Segoe UI", 11, "bold"), width=14, height=1,
            bg="#2d8a4e", fg="#FFFFFF", activebackground="#216f3e", activeforeground="#FFFFFF",
            bd=0, relief="flat", cursor="hand2", command=self.concluir_e_reabrir
        )

        # 🚀 O SEGREDO: Força o Windows a desenhar os componentes na tela ANTES de rodar qualquer código pesado
        self.root.update()
        self.root.update_idletasks()

        # Dispara a thread secundária de processamento
        threading.Thread(target=self.executar_fluxo_update, daemon=True).start()

    def atualizar_progresso_ui(self, valor):
        """ Atualiza a barra de progresso forçando a liberação da interface do Windows """
        self.progress['value'] = valor * 100
        porcentagem = int(valor * 100)
        self.lbl_versao.config(text=f"Download da versão {self.versao_online} - {porcentagem}%")
        
        # 🚀 Força o loop gráfico a bombear a atualização visual imediatamente
        self.root.update_idletasks()

    def atualizar_status_ui(self, texto):
        self.lbl_status.config(text=texto)
        self.root.update_idletasks()

    def executar_fluxo_update(self):
        # 🚀 AJUSTE DE ESTABILIDADE: Dá um respiro de 1.5 segundos para a janela aparecer na tela
        # antes de cometer o "assassinato" do processo pai. Isso previne o congelamento inicial!
        time.sleep(1.5)
        self.atualizar_status_ui("Encerrando aplicação principal...")

        try:
            subprocess.run(["taskkill", "/F", "/IM", "Gerador_XML.exe"], capture_output=True)
        except:
            pass
        time.sleep(1.5)

        # Inicia o download repassando os gatilhos visuais
        self.atualizar_status_ui("Baixando pacotes...")
        sucesso = baixar_atualizacao(
            self.download_url, 
            callback_progresso=self.atualizar_progresso_ui, 
            callback_status=self.atualizar_status_ui
        )

        if sucesso:
            # Transiciona perfeitamente para o layout de conclusão solicitado
            self.progress.pack_forget()
            self.lbl_status.pack_forget()
            
            self.lbl_titulo.config(text="Atualização concluída", fg="#2d8a4e")
            self.lbl_versao.config(
                text=f"Sistema updated para\nversão {self.versao_online}", 
                font=("Segoe UI", 13, "bold"),
                fg="#1A202C"
            )
            self.btn_ok.pack(pady=(15, 10))
            
            # Traz a tela para o foco final com som de aviso nativo do Windows
            self.root.bell()
            self.root.attributes("-topmost", True)
        else:
            self.atualizar_status_ui("Erro crítico na atualização.")

    def concluir_e_reabrir(self):
        if os.path.exists("ultima_versao.txt"):
            try: os.remove("ultima_versao.txt")
            except: pass

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
    # Verifica se os argumentos mínimos foram passados (Nome do script, URL e Versão)
    if len(sys.argv) < 3:
        # Fallback de segurança caso seja aberto manualmente sem argumentos
        download_url = sys.argv[1] if len(sys.argv) > 1 else ""
        versao_online = "Nova Versão"
    else:
        download_url = sys.argv[1]
        versao_online = sys.argv[2] # 🚀 Captura o segundo argumento enviado
    
    root = Tk()
    app = UpdaterGUI(root, download_url, versao_online)
    root.mainloop()

if __name__ == "__main__":
    main()