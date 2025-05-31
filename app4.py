import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from banco4 import (
    conectar,
    validar_login,
    cadastrar_usuario,
    adicionar_produto,
    obter_produtos,
    registrar_saida,
    obter_saidas,
    produtos_estoque_baixo,
    exportar_saidas_csv,
    remover_produto
)
import csv

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de controle de estoque")
        self.root.geometry("750x500")
        self.root.configure(bg="#2c3e50")
        conectar()
        self.usuario_logado = None
        self.tela_login()

    def tela_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Login", font=("Arial", 24), bg="#2c3e50", fg="white").pack(pady=20)
        tk.Label(self.root, text="Usuário:", bg="#2c3e50", fg="white").pack()
        username = tk.Entry(self.root)
        username.pack()
        tk.Label(self.root, text="Senha:", bg="#2c3e50", fg="white").pack()
        senha = tk.Entry(self.root, show="*")
        senha.pack()

        def tentar_login():
            usuario = validar_login(username.get(), senha.get())
            if usuario:
                self.usuario_logado = usuario
                self.menu_principal()
            else:
                messagebox.showerror("Erro", "Usuário ou senha inválidos.")

        tk.Button(self.root, text="Entrar", command=tentar_login).pack(pady=10)

    def menu_principal(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text=f"Bem-vindo, {self.usuario_logado[1]}!", font=("Arial", 16), bg="#2c3e50", fg="white").pack(pady=20)

        if produtos_estoque_baixo():
            tk.Label(self.root, text="⚠️ Atenção: há itens com estoque baixo!", bg="#2c3e50", fg="yellow", font=("Arial", 12)).pack(pady=5)

        botoes = [
            ("Cadastrar Produto", self.tela_cadastro_produto),
            ("Consultar Produtos", self.tela_consulta_produtos),
            ("Registrar Saída", self.tela_registrar_saida),
            ("Histórico de Saída", self.tela_historico_saida),
            ("Relatório Estoque Baixo", self.tela_estoque_baixo),
            ("Exportar CSV", self.exportar_dados),
        ]

        if self.usuario_logado[3] == "admin":
            botoes.insert(0, ("Cadastrar Usuário", self.tela_cadastro_usuario))
            botoes.insert(1, ("Remover Produto", self.tela_remover_produto))  

        for texto, comando in botoes:
            tk.Button(self.root, text=texto, width=30, command=comando).pack(pady=5)

        tk.Button(self.root, text="Sair", command=self.tela_login).pack(pady=20)

    def tela_cadastro_usuario(self):
        self.janela_popup("Cadastro de Usuário", self.frame_cadastro_usuario)

    def frame_cadastro_usuario(self, frame):
        tk.Label(frame, text="Usuário:").grid(row=0, column=0)
        e_user = tk.Entry(frame)
        e_user.grid(row=0, column=1)
        tk.Label(frame, text="Senha:").grid(row=1, column=0)
        e_senha = tk.Entry(frame, show="*")
        e_senha.grid(row=1, column=1)
        tk.Label(frame, text="Tipo:").grid(row=2, column=0)
        tipo = ttk.Combobox(frame, values=["admin", "vendedor", "usuario"])
        tipo.grid(row=2, column=1)
        def cadastrar():
            if not e_user.get() or not e_senha.get() or not tipo.get():
                messagebox.showwarning("Aviso", "Preencha todos os campos.")
                return
            if cadastrar_usuario(e_user.get(), e_senha.get(), tipo.get()):
                messagebox.showinfo("Sucesso", "Usuário cadastrado.")
            else:
                messagebox.showerror("Erro", "Nome de usuário já existe.")
        tk.Button(frame, text="Cadastrar", command=cadastrar).grid(row=3, columnspan=2)

    def tela_cadastro_produto(self):
        self.janela_popup("Cadastro de Produto", self.frame_cadastro_produto)

    def frame_cadastro_produto(self, frame):
        tk.Label(frame, text="Nome:").grid(row=0, column=0)
        e_nome = tk.Entry(frame)
        e_nome.grid(row=0, column=1)
        tk.Label(frame, text="Descrição:").grid(row=1, column=0)
        e_desc = tk.Entry(frame)
        e_desc.grid(row=1, column=1)
        tk.Label(frame, text="Quantidade:").grid(row=2, column=0)
        e_quant = tk.Entry(frame)
        e_quant.grid(row=2, column=1)

        def cadastrar():
            if not e_nome.get() or not e_desc.get() or not e_quant.get():
                messagebox.showwarning("Aviso", "Preencha todos os campos.")
                return
            try:
                quantidade = int(e_quant.get())
                adicionar_produto(e_nome.get(), e_desc.get(), quantidade)
                messagebox.showinfo("Sucesso", "Produto cadastrado.")
            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser número.")

        def importar_csv():
            caminho = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv")], 
                title="Selecione o arquivo CSV"
            )
            if not caminho:
                return
            try:
                with open(caminho, newline='', encoding='utf-8') as arquivo_csv:
                    leitor = csv.reader(arquivo_csv)
                    next(leitor)  # Pula o cabeçalho
                    count = 0
                    for linha in leitor:
                        if len(linha) >= 3:
                            nome_csv = linha[0].strip()
                            desc_csv = linha[1].strip()
                            try:
                                quant_csv = int(linha[2])
                                adicionar_produto(nome_csv, desc_csv, quant_csv)
                                count += 1
                            except ValueError:
                                continue
                    messagebox.showinfo("Importação concluída", f"{count} produtos importados com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao importar CSV:\n{e}")

        tk.Button(frame, text="Cadastrar", command=cadastrar).grid(row=3, columnspan=2, pady=(10, 0))
        tk.Button(frame, text="Importar CSV", command=importar_csv).grid(row=4, columnspan=2, pady=(10, 0))

    def tela_consulta_produtos(self):
        self.janela_popup("Produtos", self.frame_lista_produtos)

    def frame_lista_produtos(self, frame):
        produtos = obter_produtos()
        tree = ttk.Treeview(frame, columns=("Nome", "Descrição", "Quantidade"), show="headings")
        tree.heading("Nome", text="Nome")
        tree.heading("Descrição", text="Descrição")
        tree.heading("Quantidade", text="Quantidade")
        for p in produtos:
            tree.insert("", "end", values=(p[1], p[2], p[3]))
        tree.pack(expand=True, fill="both")

    def tela_registrar_saida(self):
        self.janela_popup("Registrar Saída", self.frame_registrar_saida)

    def frame_registrar_saida(self, frame):
        produtos = obter_produtos()
        tk.Label(frame, text="Produto:").grid(row=0, column=0)
        cb = ttk.Combobox(frame, values=[f"{p[0]} - {p[1]}" for p in produtos])
        cb.grid(row=0, column=1)
        tk.Label(frame, text="Quantidade:").grid(row=1, column=0)
        e_quant = tk.Entry(frame)
        e_quant.grid(row=1, column=1)

        def registrar():
            if not cb.get() or not e_quant.get():
                messagebox.showwarning("Aviso", "Preencha todos os campos.")
                return
            try:
                id_produto = int(cb.get().split(" - ")[0])
                quantidade = int(e_quant.get())
                if registrar_saida(id_produto, quantidade):
                    messagebox.showinfo("Sucesso", "Saída registrada.")
                else:
                    messagebox.showerror("Erro", "Estoque insuficiente.")
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida.")

        tk.Button(frame, text="Registrar", command=registrar).grid(row=2, columnspan=2)

    def tela_historico_saida(self):
        self.janela_popup("Histórico de Saídas", self.frame_historico)

    def frame_historico(self, frame):
        vendas = obter_saidas()
        tree = ttk.Treeview(frame, columns=("Produto", "Quantidade", "Data"), show="headings")
        tree.heading("Produto", text="Produto")
        tree.heading("Quantidade", text="Quantidade")
        tree.heading("Data", text="Data")
        for v in vendas:
            tree.insert("", "end", values=(v[1], v[2], v[3]))
        tree.pack(expand=True, fill="both")

    def tela_estoque_baixo(self):
        self.janela_popup("Estoque Baixo", self.frame_estoque_baixo)

    def frame_estoque_baixo(self, frame):
        produtos = produtos_estoque_baixo()
        tree = ttk.Treeview(frame, columns=("Nome", "Descrição", "Quantidade"), show="headings")
        tree.heading("Nome", text="Nome")
        tree.heading("Descrição", text="Descrição")
        tree.heading("Quantidade", text="Quantidade")
        for p in produtos:
            tree.insert("", "end", values=(p[1], p[2], p[3]))
        tree.pack(expand=True, fill="both")

    def exportar_dados(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if caminho:
            exportar_saidas_csv(caminho)
            messagebox.showinfo("Sucesso", "Arquivo CSV exportado.")

    def tela_remover_produto(self):
        self.janela_popup("Remover Produto", self.frame_remover_produto)

    def frame_remover_produto(self, frame):
        produtos = obter_produtos()
        tk.Label(frame, text="Selecione o produto para remover:").pack()
        cb = ttk.Combobox(frame, values=[f"{p[0]} - {p[1]}" for p in produtos])
        cb.pack()

        def remover():
            if not cb.get():
                messagebox.showwarning("Aviso", "Selecione um produto.")
                return
            id_produto = int(cb.get().split(" - ")[0])
            remover_produto(id_produto)
            messagebox.showinfo("Sucesso", "Produto removido.")

        tk.Button(frame, text="Remover", command=remover).pack(pady=10)

    def janela_popup(self, titulo, func_frame):
        popup = tk.Toplevel()
        popup.title(titulo)
        frame = tk.Frame(popup)
        frame.pack(padx=10, pady=10)
        func_frame(frame)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
