# =================================================================
# DIÁLOGOS CUSTOMIZADOS - ui/dialogs.py
# =================================================================
import customtkinter as ctk

class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, text):
        super().__init__(parent)
        self.title(title)
        self.largura, self.altura = 400, 200
        
        # Centraliza o diálogo com base na janela pai
        px = parent.winfo_x() + (parent.winfo_width() // 2) - (self.largura // 2)
        py = parent.winfo_y() + (parent.winfo_height() // 2) - (self.altura // 2)
        self.geometry(f"{self.largura}x{self.altura}+{px}+{py}")
        self.resizable(False, False)
        
        # Propriedades Modais essenciais para travar a janela de trás
        self.transient(parent)
        self.grab_set()
        self.attributes("-topmost", True)
        
        self.result = None
        
        ctk.CTkLabel(self, text=text, font=("Segoe UI", 14)).pack(pady=(30, 10))
        
        self.entry = ctk.CTkEntry(self, width=250, height=35)
        self.entry.pack(pady=10)
        self.entry.focus_set()
        
        btn_f = ctk.CTkFrame(self, fg_color="transparent")
        btn_f.pack(pady=15)
        
        ctk.CTkButton(btn_f, text="Ok", width=100, command=self.on_ok).pack(side="left", padx=5)
        ctk.CTkButton(btn_f, text="Cancelar", width=100, fg_color="gray", command=self.on_cancel).pack(side="left", padx=5)
        
        # Atalho para o teclado
        self.bind("<Return>", lambda e: self.on_ok())
        
    def on_ok(self): 
        self.result = self.entry.get()
        self.destroy()
        
    def on_cancel(self): 
        self.result = None
        self.destroy()
        
    def get_input(self): 
        self.master.wait_window(self)
        return self.result