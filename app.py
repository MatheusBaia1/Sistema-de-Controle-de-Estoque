import customtkinter as ctk 
from PIL import Image, ImageTk
from tkinter import ttk, filedialog, messagebox
import csv
import os
from banco import (
    conectar,
    validar_login,
    cadastrar_usuario,
    adicionar_produto,
    obter_produtos,
    registrar_saida,
    obter_saidas,
    produtos_estoque_baixo,
    exportar_saidas_csv,
    remover_produto,
    editar_quantidade_produto
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de controle de estoque")
        self.root.geometry("800x600")
        conectar()
        self.usuario_logado = None
        self.tela_login()

    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def tela_login(self):
        self.limpar_tela()
        frame = ctk.CTkFrame(self.root, corner_radius=20)
        frame.pack(expand=True, padx=40, pady=45)
        # Adiciona imagem ao frame de login
        caminho_imagem = os.path.join("imagens/logo.png")
        imagem_pil = Image.open(caminho_imagem)
        imagem_pil = imagem_pil.resize((150, 150))
        imagem_tk = ImageTk.PhotoImage(imagem_pil)

        label_imagem = ctk.CTkLabel(frame, image=imagem_tk, text="")
        label_imagem.image = imagem_tk
        label_imagem.pack(pady=10)


        ctk.CTkLabel(frame, text="Login", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(0, 20))
        ctk.CTkLabel(frame, text="Usuário:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10)
        username = ctk.CTkEntry(frame, width=300, height=40, corner_radius=15)
        username.pack(pady=10)

        ctk.CTkLabel(frame, text="Senha:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10)
        senha = ctk.CTkEntry(frame, show="*", width=300, height=40, corner_radius=15)
        senha.pack(pady=10)

        def tentar_login():
            usuario = validar_login(username.get(), senha.get())
            if usuario:
                self.usuario_logado = usuario
                self.menu_principal()
            else:
                messagebox.showerror("Erro", "Usuário ou senha inválidos.")

        ctk.CTkButton(frame, text="Entrar", command=tentar_login, width=200, height=45, corner_radius=15).pack(pady=20)

    def menu_principal(self):
        self.limpar_tela()
        frame = ctk.CTkFrame(self.root, corner_radius=20)
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(frame, text=f"Bem-vindo, {self.usuario_logado[1]}!", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(10, 10))

        if produtos_estoque_baixo():
            ctk.CTkLabel(frame, text="Atenção: há itens com estoque baixo!", text_color="orange", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 15))

        botoes = [
            ("Cadastrar Produto", self.tela_cadastro_produto),
            ("Consultar Produtos", self.tela_consulta_produtos),
            ("Registrar Saída", self.tela_registrar_saida),
            ("Histórico de Saída", self.tela_historico_saida),
            ("Relatório Estoque Baixo", self.tela_estoque_baixo),
            ("Exportar CSV", self.exportar_dados),
            ("Importar Produtos CSV", self.importar_produtos_csv),
        ]

        if self.usuario_logado[3] in ("Gerente", "admin"):
            botoes.insert(0, ("Cadastrar Usuário", self.tela_cadastro_usuario))
            botoes.insert(1, ("Remover Produto", self.tela_remover_produto))

        grid_frame = ctk.CTkFrame(frame)
        grid_frame.pack(expand=True)

        colunas = [[], [], []]
        for i, (texto, comando) in enumerate(botoes):
            colunas[i % 3].append((texto, comando))

        for col_idx, col_botoes in enumerate(colunas):
            col_frame = ctk.CTkFrame(grid_frame)
            col_frame.grid(row=0, column=col_idx, padx=15, pady=10)
            for texto, comando in col_botoes:
                ctk.CTkButton(col_frame, text=texto, command=comando, width=220, height=45, corner_radius=15).pack(pady=8)

        ctk.CTkButton(frame, text="Sair", command=self.tela_login, width=250, height=45, corner_radius=15).pack(pady=(10, 5))

    def popup_janela(self, titulo, conteudo_func):
        popup = ctk.CTkToplevel(self.root)
        popup.title(titulo)
        popup.geometry("600x400")
        popup.transient(self.root)
        popup.grab_set()
        popup.focus()

        frame = ctk.CTkFrame(popup, corner_radius=20)
        frame.pack(padx=25, pady=25, expand=True)
        conteudo_func(frame, popup)

    def tela_cadastro_usuario(self):
        self.popup_janela("Cadastro de Usuário", self.frame_cadastro_usuario)

    def frame_cadastro_usuario(self, frame, popup):
        campos = {}
        for i, (label, var) in enumerate({"Usuário": "user", "Senha": "senha", "Tipo": "tipo"}.items()):
            ctk.CTkLabel(frame, text=label + ":", font=ctk.CTkFont(size=14)).grid(row=i, column=0, padx=10, pady=8, sticky="w")
            if var == "tipo":
                campos[var] = ctk.CTkComboBox(frame, values=["Gerente", "Funcionário"], width=250, height=35)
            else:
                campos[var] = ctk.CTkEntry(frame, width=250, height=35, corner_radius=10, show="*" if var == "senha" else None)
            campos[var].grid(row=i, column=1, padx=10, pady=8)

        def cadastrar():
            if not all(c.get() for c in campos.values()):
                messagebox.showwarning("Aviso", "Preencha todos os campos.")
                return
            if cadastrar_usuario(campos["user"].get(), campos["senha"].get(), campos["tipo"].get()):
                messagebox.showinfo("Sucesso", "Usuário cadastrado.")
                popup.destroy()
            else:
                messagebox.showerror("Erro", "Nome de usuário já existe.")

        ctk.CTkButton(frame, text="Cadastrar", command=cadastrar, width=200, height=40, corner_radius=15).grid(row=3, columnspan=2, pady=20)

    def tela_cadastro_produto(self):
        self.popup_janela("Cadastro de Produto", self.frame_cadastro_produto)

    def frame_cadastro_produto(self, frame, popup):
        labels = ["Nome", "Descrição", "Quantidade"]
        entradas = []
        for i, label in enumerate(labels):
            ctk.CTkLabel(frame, text=label + ":", font=ctk.CTkFont(size=14)).grid(row=i, column=0, padx=10, pady=8, sticky="w")
            entrada = ctk.CTkEntry(frame, width=250, height=35, corner_radius=10)
            entrada.grid(row=i, column=1, padx=10, pady=8)
            entradas.append(entrada)

        def cadastrar():
            nome, descricao, quant = (e.get() for e in entradas)
            if not nome or not descricao or not quant:
                messagebox.showwarning("Aviso", "Preencha todos os campos.")
                return
            try:
                adicionar_produto(nome, descricao, quantidade=int(quant))
                messagebox.showinfo("Sucesso", "Produto cadastrado.")
                popup.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser número.")

        ctk.CTkButton(frame, text="Cadastrar", command=cadastrar, width=200, height=40, corner_radius=15).grid(row=3, columnspan=2, pady=20)

    def tela_consulta_produtos(self):
        self.popup_janela("Produtos", self.frame_treeview_produtos)

    def frame_treeview_produtos(self, frame, popup=None):
        tree = ttk.Treeview(frame, columns=("ID", "Nome", "Descrição", "Quantidade"), show="headings")
        tree.heading("ID", text="ID")
        tree.column("ID", width=40, anchor="center")
        for col in ("Nome", "Descrição", "Quantidade"):
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for p in obter_produtos():
            tree.insert("", "end", values=(p[0], p[1], p[2], p[3]))
        tree.pack(expand=True, fill="both", padx=10, pady=10)

        def editar_quantidade_local():
            selecionado = tree.focus()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um produto para editar.")
                return
            dados = tree.item(selecionado, "values")
            produto_id, nome, descricao, quantidade_atual = int(dados[0]), dados[1], dados[2], dados[3]

            def salvar_edicao():
                try:
                    nova_quantidade = int(entry_quant.get())
                    if nova_quantidade < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Erro", "Quantidade deve ser um número inteiro positivo.")
                    return
                editar_quantidade_produto(produto_id, nova_quantidade)
                tree.item(selecionado, values=(produto_id, nome, descricao, nova_quantidade))
                popup_editar.destroy() 

            popup_editar = ctk.CTkToplevel(frame)
            popup_editar.title(f"Editar quantidade - {nome}")
            popup_editar.geometry("300x150")
            ctk.CTkLabel(popup_editar, text=f"Produto: {nome}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
            entry_quant = ctk.CTkEntry(popup_editar, width=100, height=35, corner_radius=10)
            entry_quant.insert(0, quantidade_atual)
            entry_quant.pack(pady=5)
            ctk.CTkButton(popup_editar, text="Salvar", command=salvar_edicao, width=120, height=40, corner_radius=15).pack(pady=15)

        def ver_descricao_completa():
            selecionado = tree.focus()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um produto para ver a descrição.")
                return
            dados = tree.item(selecionado, "values")
            nome = dados[1]
            descricao = dados[2]

            # popup para mostrar descrição completa
            popup_desc = ctk.CTkToplevel(frame)
            popup_desc.title(f"Descrição Completa - {nome}")
            popup_desc.geometry("500x300")
            popup_desc.transient(self.root)
            popup_desc.grab_set()
            popup_desc.focus()

            frame_desc = ctk.CTkFrame(popup_desc, corner_radius=20)
            frame_desc.pack(padx=20, pady=20, expand=True, fill="both")

            label_nome = ctk.CTkLabel(frame_desc, text=nome, font=ctk.CTkFont(size=18, weight="bold"))
            label_nome.pack(pady=(0,10))

            text_desc = ctk.CTkTextbox(frame_desc, width=460, height=200, corner_radius=10)
            text_desc.pack(expand=True, fill="both")
            text_desc.insert("0.0", descricao)
            text_desc.configure(state="disabled")

        frame_botoes = ctk.CTkFrame(frame, corner_radius=10)
        frame_botoes.pack(pady=10)

        btn_editar = ctk.CTkButton(frame_botoes, text="Editar Quantidade", command=editar_quantidade_local, width=150, height=40, corner_radius=15)
        btn_editar.grid(row=0, column=0, padx=10)

        btn_ver_desc = ctk.CTkButton(frame_botoes, text="Ver Descrição Completa", command=ver_descricao_completa, width=180, height=40, corner_radius=15)
        btn_ver_desc.grid(row=0, column=1, padx=10)

    def tela_registrar_saida(self):
        self.popup_janela("Registrar Saída", self.frame_registrar_saida)

    def frame_registrar_saida(self, frame, popup):
        produtos = obter_produtos()
        nomes = [p[1] for p in produtos]
        ctk.CTkLabel(frame, text="Produto:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        combo_produto = ctk.CTkComboBox(frame, values=nomes, width=250, height=35)
        combo_produto.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Quantidade:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        entry_quantidade = ctk.CTkEntry(frame, width=250, height=35, corner_radius=10)
        entry_quantidade.grid(row=1, column=1, padx=10, pady=10)

        def registrar():
            nome = combo_produto.get()
            quant = entry_quantidade.get()
            if not nome or not quant:
                messagebox.showwarning("Aviso", "Preencha todos os campos.")
                return
            try:
                quantidade = int(quant)
                if quantidade <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser um número inteiro positivo.")
                return

            produto_id = None
            for p in produtos:
                if p[1] == nome:
                    produto_id = p[0]
                    if p[3] < quantidade:
                        messagebox.showerror("Erro", "Quantidade em estoque insuficiente.")
                        return
                    break
            if produto_id is None:
                messagebox.showerror("Erro", "Produto não encontrado.")
                return

            registrar_saida(produto_id, quantidade)
            messagebox.showinfo("Sucesso", "Saída registrada.")
            popup.destroy()

        ctk.CTkButton(frame, text="Registrar", command=registrar, width=200, height=40, corner_radius=15).grid(row=2, columnspan=2, pady=20)

    def tela_historico_saida(self):
        self.popup_janela("Histórico de Saída", self.frame_historico_saida)

    def frame_historico_saida(self, frame, popup):
        tree = ttk.Treeview(frame, columns=("ID", "Produto", "Quantidade", "Data"), show="headings")
        tree.heading("ID", text="ID")
        tree.column("ID", width=40, anchor="center")
        for col in ("Produto", "Quantidade", "Data"):
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for saida in obter_saidas():
            tree.insert("", "end", values=saida)
        tree.pack(expand=True, fill="both", padx=10, pady=10)

    def tela_estoque_baixo(self):
        self.popup_janela("Estoque Baixo", self.frame_estoque_baixo)

    def frame_estoque_baixo(self, frame, popup):
        tree = ttk.Treeview(frame, columns=("ID", "Nome", "Descrição", "Quantidade"), show="headings")
        tree.heading("ID", text="ID")
        tree.column("ID", width=40, anchor="center")
        for col in ("Nome", "Descrição", "Quantidade"):
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for p in produtos_estoque_baixo():
            tree.insert("", "end", values=(p[0], p[1], p[2], p[3]))
        tree.pack(expand=True, fill="both", padx=10, pady=10)

    def exportar_dados(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
        if filename:
            exportar_saidas_csv(filename)
            messagebox.showinfo("Sucesso", "Dados exportados para CSV.")

    def importar_produtos_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            with open(filename, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    nome = row.get("Nome") or row.get("nome")
                    descricao = row.get("Descrição") or row.get("descricao") or ""
                    quantidade = row.get("Quantidade") or row.get("quantidade") or "0"
                    if nome and descricao and quantidade:
                        try:
                            adicionar_produto(nome, descricao, int(quantidade))
                        except Exception:
                            pass
            messagebox.showinfo("Sucesso", "Produtos importados com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar CSV.\n{e}")

    def tela_remover_produto(self):
        self.popup_janela("Remover Produto", self.frame_remover_produto)

    def frame_remover_produto(self, frame, popup):
        produtos = obter_produtos()
        nomes = [p[1] for p in produtos]
        ctk.CTkLabel(frame, text="Produto:", font=ctk.CTkFont(size=14)).pack(pady=10)
        combo = ctk.CTkComboBox(frame, values=nomes, width=250, height=35)
        combo.pack(pady=10)

        def remover():
            nome = combo.get()
            if not nome:
                messagebox.showwarning("Aviso", "Selecione um produto.")
                return
            for p in produtos:
                if p[1] == nome:
                    remover_produto(p[0])
                    messagebox.showinfo("Sucesso", "Produto removido.")
                    popup.destroy()
                    return
            messagebox.showerror("Erro", "Produto não encontrado.")

        ctk.CTkButton(frame, text="Remover", command=remover, width=200, height=40, corner_radius=15).pack(pady=20)


if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()