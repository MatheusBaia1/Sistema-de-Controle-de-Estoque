import sqlite3
from datetime import datetime
import csv

# Conexão e configuração inicial
def conectar():
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('admin', 'vendedor', 'usuario'))
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT NOT NULL,
        quantidade INTEGER NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        quantidade INTEGER,
        data TEXT,
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )''')
    cur.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO usuarios (username, senha, tipo) VALUES (?, ?, ?)", ("admin", "admin", "admin"))
    con.commit()
    con.close()

def validar_login(username, senha):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE username=? AND senha=?", (username, senha))
    usuario = cur.fetchone()
    con.close()
    return usuario

def cadastrar_usuario(username, senha, tipo):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO usuarios (username, senha, tipo) VALUES (?, ?, ?)", (username, senha, tipo))
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        con.close()

def adicionar_produto(nome, descricao, quantidade):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("INSERT INTO produtos (nome, descricao, quantidade) VALUES (?, ?, ?)", (nome, descricao, quantidade))
    con.commit()
    con.close()

def obter_produtos():
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM produtos")
    produtos = cur.fetchall()
    con.close()
    return produtos

def registrar_saida(produto_id, quantidade):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("SELECT quantidade FROM produtos WHERE id=?", (produto_id,))
    estoque = cur.fetchone()
    if estoque and estoque[0] >= quantidade:
        nova_quantidade = estoque[0] - quantidade
        cur.execute("UPDATE produtos SET quantidade=? WHERE id=?", (nova_quantidade, produto_id))
        cur.execute("INSERT INTO vendas (produto_id, quantidade, data) VALUES (?, ?, ?)",
                    (produto_id, quantidade, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        con.commit()
        sucesso = True
    else:
        sucesso = False
    con.close()
    return sucesso

def obter_saidas():
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute('''
        SELECT v.id, 
               COALESCE(p.nome, 'Produto removido'), 
               v.quantidade, 
               v.data
        FROM vendas v
        LEFT JOIN produtos p ON v.produto_id = p.id
    ''')
    vendas = cur.fetchall()
    con.close()
    return vendas

def excluir_saidas(venda_id):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("SELECT produto_id, quantidade FROM vendas WHERE id=?", (venda_id,))
    dados = cur.fetchone()
    if dados:
        produto_id, quantidade = dados
        cur.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE id=?", (quantidade, produto_id))
        cur.execute("DELETE FROM vendas WHERE id=?", (venda_id,))
        con.commit()
    con.close()

def editar_saida(venda_id, nova_quantidade):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("SELECT produto_id, quantidade FROM vendas WHERE id=?", (venda_id,))
    venda = cur.fetchone()
    if venda:
        produto_id, antiga_quantidade = venda
        cur.execute("SELECT quantidade FROM produtos WHERE id=?", (produto_id,))
        estoque_atual = cur.fetchone()[0]
        diferenca = nova_quantidade - antiga_quantidade
        if estoque_atual >= diferenca:
            cur.execute("UPDATE vendas SET quantidade=? WHERE id=?", (nova_quantidade, venda_id))
            cur.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id=?", (diferenca, produto_id))
            con.commit()
            sucesso = True
        else:
            sucesso = False
    else:
        sucesso = False
    con.close()
    return sucesso

def produtos_estoque_baixo(limite=5):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM produtos WHERE quantidade <= ?", (limite,))
    produtos = cur.fetchall()
    con.close()
    return produtos

def exportar_saidas_csv(caminho):
    vendas = obter_saidas()
    with open(caminho, 'w', newline='') as f:
        escritor = csv.writer(f)
        escritor.writerow(['ID', 'Produto', 'Quantidade', 'Data'])
        escritor.writerows(vendas)

def remover_produto(produto_id):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    # Não verifica vendas associadas, apenas apaga o produto
    cur.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
    con.commit()
    con.close()
    return True

def importar_produtos_csv(caminho):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    with open(caminho, newline='', encoding='utf-8') as f:
        leitor = csv.reader(f)
        next(leitor, None)  # Pula o cabeçalho
        for linha in leitor:
            if len(linha) != 3:
                continue  # Ignora linhas malformadas
            nome, descricao, quantidade = linha
            try:
                quantidade = int(quantidade)
                cur.execute("INSERT INTO produtos (nome, descricao, quantidade) VALUES (?, ?, ?)", (nome, descricao, quantidade))
            except ValueError:
                continue  # Ignora se a quantidade não for número
    con.commit()
    con.close()
