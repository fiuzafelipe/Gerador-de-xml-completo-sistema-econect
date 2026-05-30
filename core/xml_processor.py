import os
import threading
import traceback
import logging
import pymysql
from datetime import datetime
from tkinter import messagebox

# Centraliza o log do motor também na pasta segura do APPDATA
APPDATA_DIR = os.path.join(os.getenv("APPDATA") or os.getcwd(), "XML")
os.makedirs(APPDATA_DIR, exist_ok=True)
LOG_PATH = os.path.join(APPDATA_DIR, "xml_processor.log")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

from core.xml_utils import montar_xml_processado
from core.reports import salvar_relatorio_numeracao

class XMLProcessor:
    
    def __init__(self, app):
        self.app = app
        self.processando = False

    def ui(self, callback):
        self.app.after(0, callback)
        
    def executar_processamento_xml(self):
        if self.processando:
            return

        self.processando = True
        
        loja_s = self.app.loja_cb.get()
        if " - " not in loja_s:
            self.processando = False  # Destrava o estado antes de retornar
            self.ui(lambda: messagebox.showwarning("Aviso", "Selecione uma loja!"))
            self.ui(lambda: self.app.btn_gerar_final.configure(state="normal", text="GERAR XML AGORA"))
            return
        
        num_loj = loja_s.split(" - ")[0].strip()
        num_loj = int(num_loj)
        status_ui = self.app.status_cb.get()

        status_codigo = status_ui.split(" - ")[0] if status_ui != "Todos" else None
        pdv_ui = self.app.pdv_cb.get()
        d_ini = self.app.ent_d_ini.get()
        d_fim = self.app.ent_d_fim.get()
        seq_ini, seq_fim = self.app.ent_s_ini.get() or "0", self.app.ent_s_fim.get() or "0"
        destino = self.app.ent_path.get()
        
        if not destino or not os.path.exists(destino):
            self.processando = False
            self.ui(lambda: messagebox.showwarning("Aviso", "Selecione uma pasta de destino válida!"))
            self.ui(lambda: self.app.btn_gerar_final.configure(state="normal", text="GERAR XML AGORA"))
            return

        try:
            dt_ini_sql = datetime.strptime(d_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
            dt_fim_sql = datetime.strptime(d_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            self.processando = False
            self.ui(lambda: messagebox.showwarning("Erro", "Data inválida!"))
            self.ui(lambda: self.app.btn_gerar_final.configure(state="normal", text="GERAR XML AGORA"))
            return

        self.ui(lambda: self.app.gerenciar_botoes_operacionais("disabled"))
        self.ui(lambda: self.app.btn_gerar_final.configure(state="disabled", text="GERANDO..."))

        # --- O MOTOR INTERNO DA THREAD ---
        def r_process():
            conn = None
            try:
                conn = pymysql.connect(
                    host=self.app.db_host,
                    user=self.app.db_user,
                    password=self.app.db_password,
                    database=self.app.db_name,
                    charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True,
                    connect_timeout=15,
                    read_timeout=60,
                    write_timeout=60
                )

                # =========================
                # PASSO 1 - PENDENTES
                # =========================
                with conn.cursor() as cursor:
                    sql_p = """
                        SELECT COUNT(*) as total
                        FROM mov_nfc 
                        WHERE num_loj = %s
                        AND dat_hor_ems >= %s
                        AND dat_hor_ems <= %s 
                        AND sit_env_nfc <> 2
                        AND ope IN (102, 103, 105)
                    """
                    cursor.execute(sql_p, (num_loj, dt_ini_sql + " 00:00:00", dt_fim_sql + " 23:59:59"))
                    resultado = cursor.fetchone()
                    pendentes = resultado['total'] if resultado else 0

                # =========================
                # PASSO 2 - STATS
                # =========================
                stats = {
                    "bruto": 0, "ign_vazio": 0, "ign_integridade": 0, "ign_serie": 0,
                    "ign_ui": 0, "sucesso": 0, "inut": 0, "vend": 0, "canc": 0
                }

                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT numero_pdv FROM pdv WHERE codigo_loja = %s AND situacao_pdv IN (2, 3)",
                        (num_loj,)
                    )
                    rows = cursor.fetchall()
                    pdvs_validos = {int(r['numero_pdv']) for r in rows if r.get('numero_pdv') is not None}

                    query_where = """
                        WHERE m.num_loj = %s AND m.dat_hor_ems >= %s AND m.dat_hor_ems <= %s
                        AND m.amb = 1 AND m.sit_env_nfc = 2
                    """
                    query_params = [num_loj, dt_ini_sql + " 00:00:00", dt_fim_sql + " 23:59:59"]

                    if status_ui != "Todos":
                        query_where += " AND m.ope = %s"
                        query_params.append(status_codigo)
                    else:
                        query_where += " AND m.ope IN (102, 103, 105)"

                    if pdv_ui != "Todos":
                        query_where += " AND m.num_pdv = %s"
                        query_params.append(pdv_ui)

                    query_count = f"SELECT COUNT(*) as total FROM mov_nfc m {query_where}"
                    cursor.execute(query_count, tuple(query_params))
                    resultado_total = cursor.fetchone()
                    total_registros = int(resultado_total['total']) if resultado_total else 0

                    query_total = f"""
                        SELECT m.*, l.cnpj as cnpj_loja FROM mov_nfc m
                        LEFT JOIN loja l ON m.num_loj = l.codigo_loja
                        {query_where} ORDER BY m.num_loj, m.num_nfc
                    """
                    cursor.execute(query_total, tuple(query_params))

                    pasta_loja = os.path.join(destino, f"loja{int(num_loj):03d}")
                    os.makedirs(pasta_loja, exist_ok=True)

                    self.ui(lambda: self.app.prog_xml.set(0))
                    processados = 0

                    while True:
                        lote = cursor.fetchmany(500)
                        if not lote:
                            break

                        stats["bruto"] += len(lote)

                        for row in lote:
                            try:
                                base_ser = str(row.get('sre_nfc') or "001").zfill(3)
                                n_pdv = int(row['num_pdv'])
                                n_nfc = int(row['num_nfc'])
                                
                                if n_pdv not in pdvs_validos:
                                    stats["ign_integridade"] += 1
                                    continue

                                if base_ser in ("011", "000", "999"):
                                    stats["ign_serie"] += 1
                                    continue

                                if num_loj == 1 and base_ser == "005":
                                    stats["ign_serie"] += 1
                                    continue

                                env_raw = str(row['xml_env'] or "")
                                ret_raw = str(row['xml_ret'] or "")

                                if not (env_raw.strip().startswith("<") and ret_raw.strip().startswith("<")):
                                    stats["ign_vazio"] += 1
                                    continue

                                env = env_raw if not isinstance(row['xml_env'], bytes) else row['xml_env'].decode('utf-8', errors='ignore')
                                ret = ret_raw if not isinstance(row['xml_ret'], bytes) else row['xml_ret'].decode('utf-8', errors='ignore')

                                xml_f = montar_xml_processado(env, ret)

                                if not xml_f or "<" not in xml_f or "</" not in xml_f:
                                    stats["ign_integridade"] += 1
                                    continue

                                env_ope = int(row['ope'])
                                suf = "vend" if env_ope == 102 else "canc" if env_ope == 103 else "inut"

                                if suf == "vend": stats["vend"] += 1
                                elif suf == "canc": stats["canc"] += 1
                                else: stats["inut"] += 1

                                data_mov = row['dat_hor_ems']
                                if isinstance(data_mov, str):
                                    try:
                                        data_mov = datetime.strptime(data_mov, "%Y-%m-%d %H:%M:%S")
                                    except Exception:
                                        try:
                                            data_mov = datetime.fromisoformat(data_mov)
                                        except Exception:
                                            stats["ign_integridade"] += 1
                                            continue

                                if not isinstance(data_mov, datetime):
                                    stats["ign_integridade"] += 1
                                    continue

                                path_dia = os.path.join(pasta_loja, data_mov.strftime("%d%m%Y"))
                                os.makedirs(path_dia, exist_ok=True)

                                n_chave = "".join(c for c in str(row['chv_acs']) if c.isalnum()) if row['chv_acs'] and len(str(row['chv_acs'])) >= 40 else f"manual-{n_nfc}-{n_pdv}"
                                nome_arq = f"nfce-{n_chave}-{suf}-{n_pdv}.xml"

                                with open(os.path.join(path_dia, nome_arq), "w", encoding="utf-8") as f:
                                    f.write(xml_f)

                                stats["sucesso"] += 1
                                processados += 1

                                if processados % 50 == 0:
                                    progresso = processados / max(total_registros, 1)
                                    self.ui(lambda v=round(progresso, 4): self.app.prog_xml.set(v))

                                if processados % 30 == 0:
                                    self.ui(lambda n=n_nfc: self.app.lbl_gerando.configure(text=f"Gerando NFC-e {n}"))

                            except Exception:
                                logging.exception(f"ERRO PROCESSANDO NFC {row}")
                                stats["ign_integridade"] += 1
                                continue

                # FINALIZAÇÃO DE SUCESSO DA UI
                self.ui(lambda: self.app.prog_xml.set(1))
                self.ui(lambda: self.app.lbl_gerando.configure(text="Processo finalizado."))
                self.ui(lambda: self.app.gerenciar_botoes_operacionais("normal"))
                self.ui(lambda: self.app.btn_gerar_final.configure(state="normal", text="GERAR XML AGORA"))

                msg = (
                    f"Geração Concluída!\n\n"
                    f"XMLs gerados: {stats['sucesso']}\n"
                    f"Pendentes encontrados: {pendentes}\n"
                    f"Falhas ignoradas: {stats['ign_integridade']}"
                )
                self.ui(lambda m=msg: messagebox.showinfo("Sucesso", m))

            except Exception as e:
                logging.exception("ERRO FATAL NO PROCESSAMENTO XML")
                traceback.print_exc()
                self.ui(lambda err=e: messagebox.showerror("Erro Fatal", f"Falha no processamento: {str(err)}"))
                self.ui(lambda: self.app.gerenciar_botoes_operacionais("normal"))
                self.ui(lambda: self.app.btn_gerar_final.configure(state="normal", text="GERAR XML AGORA"))
                self.ui(lambda: self.app.lbl_gerando.configure(text="Processo finalizado com erro."))
            finally:
                self.processando = False
                if conn:
                    try: conn.close()
                    except Exception: pass

        # 🚀 A THREAD AGORA É DISPARADA DA MANEIRA CORRETA: NO ESCOPO DE EXECUÇÃO DO PROCESSO
        threading.Thread(target=r_process, daemon=True).start()