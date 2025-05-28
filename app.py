import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from banco import (
    conectar,
    validar_login,
    cadastrar_usuario,
    adicionar_produto,
    obter_produtos,
    registrar_venda,
    obter_vendas,
    produtos_estoque_baixo,
    exportar_vendas_csv
)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Vendas")
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

        botoes = [
            ("Cadastrar Produto", self.tela_cadastro_produto),
            ("Consultar Produtos", self.tela_consulta_produtos),
            ("Registrar Venda", self.tela_registrar_venda),
            ("Histórico de Vendas", self.tela_historico_vendas),
            ("Relatório Estoque Baixo", self.tela_estoque_baixo),
            ("Exportar CSV", self.exportar_dados),
        ]

        if self.usuario_logado[3] == "admin":
            botoes.insert(0, ("Cadastrar Usuário", self.tela_cadastro_usuario))

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
        tk.Label(frame, text="Preço:").grid(row=1, column=0)
        e_preco = tk.Entry(frame)
        e_preco.grid(row=1, column=1)
        tk.Label(frame, text="Quantidade:").grid(row=2, column=0)
        e_quant = tk.Entry(frame)
        e_quant.grid(row=2, column=1)
        def cadastrar():
            adicionar_produto(e_nome.get(), float(e_preco.get()), int(e_quant.get()))
            messagebox.showinfo("Sucesso", "Produto cadastrado.")
        tk.Button(frame, text="Cadastrar", command=cadastrar).grid(row=3, columnspan=2)

    def tela_consulta_produtos(self):
        self.janela_popup("Produtos", self.frame_lista_produtos)

    def frame_lista_produtos(self, frame):
        produtos = obter_produtos()
        for i, p in enumerate(produtos):
            tk.Label(frame, text=f"{p[1]} - R${p[2]:.2f} - {p[3]} un.").grid(row=i, column=0)

    def tela_registrar_venda(self):
        self.janela_popup("Registrar Venda", self.frame_registrar_venda)

    def frame_registrar_venda(self, frame):
        produtos = obter_produtos()
        tk.Label(frame, text="Produto:").grid(row=0, column=0)
        cb = ttk.Combobox(frame, values=[f"{p[0]} - {p[1]}" for p in produtos])
        cb.grid(row=0, column=1)
        tk.Label(frame, text="Quantidade:").grid(row=1, column=0)
        e_quant = tk.Entry(frame)
        e_quant.grid(row=1, column=1)
        def registrar():
            if cb.get():
                id_produto = int(cb.get().split(" - ")[0])
                if registrar_venda(id_produto, int(e_quant.get())):
                    messagebox.showinfo("Sucesso", "Venda registrada.")
                else:
                    messagebox.showerror("Erro", "Estoque insuficiente.")
        tk.Button(frame, text="Registrar", command=registrar).grid(row=2, columnspan=2)

    def tela_historico_vendas(self):
        self.janela_popup("Histórico de Vendas", self.frame_historico)

    def frame_historico(self, frame):
        vendas = obter_vendas()
        for i, v in enumerate(vendas):
            tk.Label(frame, text=f"{v[1]} - {v[2]} un. - {v[3]}").grid(row=i, column=0)

    def tela_estoque_baixo(self):
        self.janela_popup("Estoque Baixo", self.frame_estoque)

    def frame_estoque(self, frame):
        produtos = produtos_estoque_baixo()
        for i, p in enumerate(produtos):
            tk.Label(frame, text=f"{p[1]} - {p[3]} un.").grid(row=i, column=0)

    def exportar_dados(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".csv")
        if caminho:
            exportar_vendas_csv(caminho)
            messagebox.showinfo("Sucesso", "Dados exportados para CSV.")

    def janela_popup(self, titulo, frame_func):
        popup = tk.Toplevel(self.root)
        popup.title(titulo)
        popup.geometry("400x300")
        popup.configure(bg="#ecf0f1")
        frame = tk.Frame(popup, bg="#ecf0f1")
        frame.pack(padx=10, pady=10, expand=True, fill="both")
        frame_func(frame)

# Execução do app
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
