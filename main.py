import os
import sys

# ==========================================
# ADICIONA DIRETÓRIO RAIZ AO PYTHONPATH 
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ==========================================
# IMPORTS
# ==========================================

import customtkinter as ctk

from ui.login import FiuzaEnterpriseApp

# ==========================================
# CUSTOMTKINTER
# ==========================================

ctk.set_appearance_mode("Light")

ctk.set_widget_scaling(1.0)
ctk.set_window_scaling(1.0)

# ==========================================
# START APP
# ==========================================

if __name__ == "__main__":
    app = FiuzaEnterpriseApp()
    app.mainloop()