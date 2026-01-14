import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import sqlite3
import qrcode
import os
import pandas as pd
import re
from datetime import datetime
import math
import gc 
import sys
import shutil 

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "inventario.db")
QR_DIR = os.path.join(BASE_DIR, "qrcodes")

def limpar_nome_arquivo(nome):
    return re.sub(r'[^\w\s-]', '', nome).strip()

def formatar_moeda(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

def converter_valor_seguro(valor):
    if pd.isna(valor) or valor == "": return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    v_str = str(valor).replace("R$", "").replace("r$", "").strip()
    if not v_str: return 0.0
    try:
        if "," in v_str and "." in v_str:
            if v_str.rfind(",") > v_str.rfind("."): v_str = v_str.replace(".", "").replace(",", ".")
            else: v_str = v_str.replace(",", "")
        elif "," in v_str: v_str = v_str.replace(",", ".")
        return float(v_str)
    except: return 0.0

def inicializar_banco():
    if not os.path.exists(QR_DIR): os.makedirs(QR_DIR)
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, 
            tag_qr TEXT UNIQUE NOT NULL, local TEXT, valor REAL, data_criacao TEXT)""")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_nome ON equipamentos(nome)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tag ON equipamentos(tag_qr)")
        conn.commit(); conn.close()
    except Exception as e: print(f"Erro BD: {e}")

def db_execute(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute(query, params); conn.commit()
        res = cur.fetchall(); conn.close(); return res
    except: inicializar_banco(); return db_execute(query, params)

class JanelaMapeamento(ctk.CTkToplevel):
    def __init__(self, parent, colunas_do_excel, sugestoes):
        super().__init__(parent)
        self.title("Vincular Colunas")
        self.geometry("400x480")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        
        self.mapa_escolhido = None
        ctk.CTkLabel(self, text="Combine as colunas do Excel:", font=("Arial", 16, "bold")).pack(pady=(20, 10))
        
        def criar_seletor(label, variavel_inicial, obrigatorio=False):
            txt = f"{label} {'*' if obrigatorio else ''}"
            cor = "#1976D2" if obrigatorio else "gray"
            ctk.CTkLabel(self, text=txt, text_color=cor, font=("Arial", 12, "bold")).pack(pady=(5,0))
            opt = ctk.CTkOptionMenu(self, values=colunas_do_excel)
            if variavel_inicial in colunas_do_excel: opt.set(variavel_inicial)
            elif not obrigatorio: opt.configure(values=["(Ignorar)"] + colunas_do_excel); opt.set("(Ignorar)")
            elif obrigatorio and len(colunas_do_excel) > 0: opt.set(colunas_do_excel[0])
            opt.pack(pady=5)
            return opt

        self.opt_nome = criar_seletor("Campo NOME", sugestoes.get('nome'), True)
        self.opt_tag = criar_seletor("Campo TAG", sugestoes.get('tag'), True)
        self.opt_local = criar_seletor("Campo LOCALIZAÇÃO", sugestoes.get('local'))
        self.opt_valor = criar_seletor("Campo VALOR (R$)", sugestoes.get('valor'))

        ctk.CTkButton(self, text="CONFIRMAR", fg_color="green", height=45, command=self.confirmar).pack(pady=30)

    def confirmar(self):
        self.mapa_escolhido = {"nome": self.opt_nome.get(), "tag": self.opt_tag.get(), "local": self.opt_local.get(), "valor": self.opt_valor.get()}
        self.destroy()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nexus")
        self.geometry("900x700")
        
        self.itens_por_pagina = 30 
        self.pagina_atual = 1
        self.total_paginas = 1
        self.delay_busca = None
        
        inicializar_banco()
        
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_c = self.tabview.add("Cadastro")
        self.tab_l = self.tabview.add("Lista")
        
        self.switch_tema = ctk.CTkSwitch(self, text="Modo Escuro", command=self.mudar_tema)
        self.switch_tema.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="e")
        self.switch_tema.select() if ctk.get_appearance_mode() == "Dark" else self.switch_tema.deselect()

        self.montar_cadastro()
        self.montar_lista()

    def mudar_tema(self):
        ctk.set_appearance_mode("Dark") if self.switch_tema.get() == 1 else ctk.set_appearance_mode("Light")

    def montar_cadastro(self):
        center = ctk.CTkFrame(self.tab_c, fg_color="transparent"); center.pack(expand=True)
        ctk.CTkLabel(center, text="Novo Item", font=("Arial", 26, "bold")).pack(pady=(0, 25))
        self.e_nome = ctk.CTkEntry(center, placeholder_text="Nome do Equipamento", width=600, height=45, font=("Arial", 14)); self.e_nome.pack(pady=10)
        fr1 = ctk.CTkFrame(center, fg_color="transparent"); fr1.pack(pady=5)
        self.e_tag = ctk.CTkEntry(fr1, placeholder_text="TAG", width=290, height=45); self.e_tag.pack(side="left", padx=(0, 20))
        self.e_loc = ctk.CTkEntry(fr1, placeholder_text="Local", width=290, height=45); self.e_loc.pack(side="left")
        fr2 = ctk.CTkFrame(center, fg_color="transparent"); fr2.pack(pady=15)
        self.e_val = ctk.CTkEntry(fr2, placeholder_text="Valor", width=200, height=50); self.e_val.pack(side="left", padx=(0, 20))
        ctk.CTkButton(fr2, text="REGISTRAR", command=self.salvar, width=380, height=50, font=("bold", 14)).pack(side="left")
        self.lbl_st = ctk.CTkLabel(center, text="", font=("Arial", 12)); self.lbl_st.pack(pady=10)

    def montar_lista(self):
        top = ctk.CTkFrame(self.tab_l, fg_color="transparent"); top.pack(fill="x", pady=5)
        self.e_busca = ctk.CTkEntry(top, placeholder_text="🔍 Nome, TAG ou Local...", height=35, width=270)
        self.e_busca.pack(side="left", padx=5)
        self.e_busca.bind("<KeyRelease>", self.agendar_busca)
        
        self.combo_sort = ctk.CTkOptionMenu(top, width=140, height=35, anchor="center", values=[
            "📅 Recentes", "🔤 Nome(A-Z)", "🏷️ TAG(A-Z)", "📍 Local(A-Z)", "💰 Valor(Maior)", "💰 Valor(Menor)"
        ], command=self.atualizar_ordem)
        self.combo_sort.pack(side="left", padx=5)
        
        ctk.CTkButton(top, text="Excel", command=self.exportar, width=70, fg_color="#388E3C").pack(side="right", padx=2)
        ctk.CTkButton(top, text="Importar", command=self.importar, width=80, fg_color="#F57C00").pack(side="right", padx=2)
        ctk.CTkButton(top, text="Limpar", command=self.limpar, width=70, fg_color="#D32F2F").pack(side="right", padx=2)

        dash = ctk.CTkFrame(self.tab_l, height=50, corner_radius=10); dash.pack(fill="x", padx=5, pady=5)
        self.l_tot = ctk.CTkLabel(dash, text="ITENS: 0", font=("Arial", 14, "bold")); self.l_tot.pack(side="left", padx=30)
        ctk.CTkFrame(dash, width=2, height=30, fg_color="gray").pack(side="left")
        self.l_val = ctk.CTkLabel(dash, text="PATRIMÔNIO: R$ 0,00", font=("Arial", 14, "bold"), text_color="#2196F3"); self.l_val.pack(side="left", padx=30)

        self.scroll = ctk.CTkScrollableFrame(self.tab_l, width=800, height=350); self.scroll.pack(pady=5, fill="both", expand=True)
        
        pag = ctk.CTkFrame(self.tab_l, height=40, fg_color="transparent"); pag.pack(fill="x", pady=5)
        c_pag = ctk.CTkFrame(pag, fg_color="transparent"); c_pag.pack(expand=True)
        ctk.CTkButton(c_pag, text="⏮", width=30, command=lambda: self.mudar_pagina("inicio")).pack(side="left", padx=2)
        ctk.CTkButton(c_pag, text="◀", width=30, command=lambda: self.mudar_pagina("ant")).pack(side="left", padx=2)
        self.lbl_pag = ctk.CTkLabel(c_pag, text="1/1", font=("bold", 12), width=60); self.lbl_pag.pack(side="left", padx=5)
        ctk.CTkButton(c_pag, text="▶", width=30, command=lambda: self.mudar_pagina("prox")).pack(side="left", padx=2)
        ctk.CTkButton(c_pag, text="⏭", width=30, command=lambda: self.mudar_pagina("fim")).pack(side="left", padx=2)
        self.carregar()

    def agendar_busca(self, e):
        if self.delay_busca: self.after_cancel(self.delay_busca)
        self.pagina_atual = 1; self.delay_busca = self.after(500, lambda: self.carregar())

    def atualizar_ordem(self, escolha):
        self.pagina_atual = 1; self.carregar()

    def mudar_pagina(self, acao):
        if acao == "ant" and self.pagina_atual > 1: self.pagina_atual -= 1
        elif acao == "prox" and self.pagina_atual < self.total_paginas: self.pagina_atual += 1
        elif acao == "inicio": self.pagina_atual = 1
        elif acao == "fim": self.pagina_atual = self.total_paginas
        self.carregar()

    def carregar(self):
        for w in self.scroll.winfo_children(): w.destroy()
        gc.collect()
        
        filtro = self.e_busca.get()
        sql_c = "SELECT count(*), sum(valor) FROM equipamentos"
        if filtro: sql_c += f" WHERE nome LIKE '%{filtro}%' OR tag_qr LIKE '%{filtro}%' OR local LIKE '%{filtro}%'"
        st = db_execute(sql_c)[0]
        self.total_paginas = math.ceil(st[0] / self.itens_por_pagina) or 1
        
        ordem_escolhida = self.combo_sort.get()
        sql_order = "ORDER BY id DESC"
        if "Nome" in ordem_escolhida: sql_order = "ORDER BY nome ASC"
        elif "TAG" in ordem_escolhida: sql_order = "ORDER BY tag_qr ASC"
        elif "Local" in ordem_escolhida: sql_order = "ORDER BY local ASC"
        elif "Valor(Maior)" in ordem_escolhida: sql_order = "ORDER BY valor DESC"
        elif "Valor(Menor)" in ordem_escolhida: sql_order = "ORDER BY valor ASC"

        offset = (self.pagina_atual - 1) * self.itens_por_pagina
        sql = f"SELECT id, nome, tag_qr, local, valor FROM equipamentos {sql_order} LIMIT {self.itens_por_pagina} OFFSET {offset}"
        if filtro: sql = f"SELECT id, nome, tag_qr, local, valor FROM equipamentos WHERE nome LIKE '%{filtro}%' OR tag_qr LIKE '%{filtro}%' OR local LIKE '%{filtro}%' {sql_order} LIMIT {self.itens_por_pagina} OFFSET {offset}"

        self.lbl_pag.configure(text=f"{self.pagina_atual}/{self.total_paginas}")
        self.l_tot.configure(text=f"ITENS: {st[0]}")
        self.l_val.configure(text=f"PATRIMÔNIO: {formatar_moeda(st[1] or 0)}")

        for i, n, t, l, v in db_execute(sql) or []:
            c = ctk.CTkFrame(self.scroll, fg_color=("white", "#333333"), height=50); c.pack(fill="x", pady=3, padx=5)
            ctk.CTkLabel(c, text=n[:30], width=220, anchor="w", font=("Arial", 13, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(c, text=f"📍 {l or '-'}", font=("Arial", 12), width=130, anchor="w", text_color="gray").pack(side="left", padx=5)
            ctk.CTkLabel(c, text=f"🏷 {t}", width=100, anchor="w", text_color="gray").pack(side="left")
            ctk.CTkLabel(c, text=formatar_moeda(v), width=100, anchor="e", text_color=("#1976D2", "#64B5F6"), font=("bold", 12)).pack(side="left", padx=10)
            
            b = ctk.CTkFrame(c, fg_color="transparent"); b.pack(side="right", padx=5)
            ctk.CTkButton(b, text="QR", width=35, fg_color="green", command=lambda t=t,n=n: self.ver_qr(t,n)).pack(side="left", padx=2)
            ctk.CTkButton(b, text="✏️", width=35, fg_color="orange", command=lambda i=i,n=n,t=t,l=l,v=v: self.abrir_editor(i,n,t,l,v)).pack(side="left", padx=2)
            ctk.CTkButton(b, text="✖", width=35, fg_color="red", command=lambda i=i: self.deletar(i)).pack(side="left", padx=2)

    def importar(self):
        f = filedialog.askopenfilename(filetypes=[("Excel/CSV", "*.xlsx *.csv")])
        if not f: return
        try:
            df = pd.read_excel(f) if f.endswith(".xlsx") else pd.read_csv(f)
            colunas = list(df.columns)
            colunas_lower = [str(c).strip().lower() for c in colunas]
            sugestoes = {}
            for orig, low in zip(colunas, colunas_lower):
                if any(x in low for x in ["nome", "item"]): sugestoes['nome'] = orig
                elif any(x in low for x in ["tag", "id", "cod"]): sugestoes['tag'] = orig
                elif any(x in low for x in ["local", "sala"]): sugestoes['local'] = orig
                elif any(x in low for x in ["valor", "preço"]): sugestoes['valor'] = orig
            
            janela_map = JanelaMapeamento(self, colunas, sugestoes)
            self.wait_window(janela_map)
            escolhas = janela_map.mapa_escolhido
            if not escolhas: return

            sucessos = 0
            for _, row in df.iterrows():
                try:
                    n = str(row[escolhas['nome']]).strip()
                    t = str(row[escolhas['tag']]).strip()
                    if not n or n=="nan" or not t or t=="nan": continue
                    l = str(row[escolhas['local']]).strip() if escolhas['local'] != "(Ignorar)" else ""
                    v = converter_valor_seguro(row[escolhas['valor']]) if escolhas['valor'] != "(Ignorar)" else 0.0
                    db_execute("INSERT INTO equipamentos (nome, tag_qr, local, valor, data_criacao) VALUES (?,?,?,?,?)", (n, t, l, v, datetime.now().strftime("%d/%m/%Y %H:%M")))
                    self.gerar_qr(t); sucessos += 1
                except: continue
            self.carregar(); messagebox.showinfo("Sucesso", f"{sucessos} itens importados!")
        except Exception as e: messagebox.showerror("Erro", str(e))

    def exportar(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * FROM equipamentos", conn); conn.close()
            if df.empty: return messagebox.showwarning("Aviso", "Vazio")
            f = filedialog.asksaveasfilename(defaultextension=".xlsx")
            if f:
                with pd.ExcelWriter(f, engine='xlsxwriter') as w:
                    df = df.rename(columns={"nome":"Item","tag_qr":"TAG","local":"Local","valor":"Valor R$"})
                    df.to_excel(w, sheet_name='Patrimonio', index=False)
                    ws = w.sheets['Patrimonio']
                    fmt = w.book.add_format({'num_format': 'R$ #,##0.00'})
                    cols = [{'header': c, 'format': fmt if "Valor" in c else None} for c in df.columns]
                    ws.add_table(0, 0, df.shape[0], df.shape[1]-1, {'columns': cols, 'style': 'Table Style Medium 9', 'name': 'TabPatrimonio'})
                    for i, c in enumerate(df.columns): ws.set_column(i,i, max(df[c].astype(str).map(len).max(), len(c))+4)
                os.startfile(f)
        except Exception as e: messagebox.showerror("Erro", str(e))

    def salvar(self):
        n, t, l, v = self.e_nome.get(), self.e_tag.get(), self.e_loc.get(), converter_valor_seguro(self.e_val.get())
        if n and t:
            db_execute("INSERT INTO equipamentos (nome, tag_qr, local, valor, data_criacao) VALUES (?,?,?,?,?)", (n,t,l,v, datetime.now().strftime("%d/%m/%Y %H:%M")))
            self.gerar_qr(t); self.e_nome.delete(0,"end"); self.e_tag.delete(0,"end"); self.e_val.delete(0,"end"); self.carregar()
            self.lbl_st.configure(text="✅ Item registrado!", text_color="green"); self.after(3000, lambda: self.lbl_st.configure(text=""))
        else: self.lbl_st.configure(text="❌ Nome e TAG obrigatórios", text_color="red")

    def ver_qr(self, t, n):
        w = ctk.CTkToplevel(self); w.geometry("340x520"); w.title("QR Code")
        fr = ctk.CTkFrame(w, fg_color="white"); fr.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(fr, text=n, font=("bold", 20), wraplength=250, text_color="black").pack(pady=20)
        
        path = os.path.join(QR_DIR, f"{limpar_nome_arquivo(t)}.png")
        if not os.path.exists(path): self.gerar_qr(t)
        
        img = ctk.CTkImage(Image.open(path), size=(220,220))
        l = ctk.CTkLabel(fr, text="", image=img); l.pack(); l.image=img
        ctk.CTkLabel(w, text=t, font=("bold", 24), fg_color="#1976D2", text_color="white").pack(side="bottom", fill="x", pady=0)

        def baixar():
            dest = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")], initialfile=f"QR_{t}.png")
            if dest: shutil.copy(path, dest); messagebox.showinfo("Sucesso", "QR Code salvo!")
            
        ctk.CTkButton(fr, text="⬇ Baixar PNG", fg_color="#F57C00", command=baixar).pack(pady=10)

    def gerar_qr(self, t): qrcode.make(t).save(os.path.join(QR_DIR, f"{limpar_nome_arquivo(t)}.png"))
    def limpar(self): 
        if messagebox.askyesno("Apagar", "TUDO?"): db_execute("DELETE FROM equipamentos"); self.carregar()
    def deletar(self, i): 
        if messagebox.askyesno("Apagar", "Confirma?"): db_execute("DELETE FROM equipamentos WHERE id=?", (i,)); self.carregar()
    def abrir_editor(self, id_db, n, t, l, v):
        w = ctk.CTkToplevel(self); w.title("Editar"); w.geometry("350x400"); w.attributes("-topmost", True)
        en = ctk.CTkEntry(w); en.insert(0,n); en.pack(pady=5)
        et = ctk.CTkEntry(w); et.insert(0,t); et.pack(pady=5)
        el = ctk.CTkEntry(w); el.insert(0,l or ""); el.pack(pady=5)
        ev = ctk.CTkEntry(w); ev.insert(0,str(v)); ev.pack(pady=5)
        def save(): db_execute("UPDATE equipamentos SET nome=?, tag_qr=?, local=?, valor=? WHERE id=?",(en.get(),et.get(),el.get(),converter_valor_seguro(ev.get()),id_db)); w.destroy(); self.carregar()
        ctk.CTkButton(w, text="Salvar", command=save).pack(pady=20)

if __name__ == "__main__": App().mainloop()