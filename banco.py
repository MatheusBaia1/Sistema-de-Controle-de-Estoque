import sqlite3
from datetime import datetime
import csv

# Conexão com banco
def conectar():
    import sqlite3
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()

    # Tabelas
    cur.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('Gerente', 'Funcionário'))
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

    # Usuário admin padrão
    cur.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO usuarios (username, senha, tipo) VALUES (?, ?, ?)", ("admin", "admin", "Gerente"))

    con.commit()
    con.close()

# Login
def validar_login(username, senha):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE username=? AND senha=?", (username, senha))
    usuario = cur.fetchone()
    con.close()
    return usuario

# Cadastro de usuário
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

# Produtos
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

def remover_produto(produto_id):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
    con.commit()
    con.close()
    return True

def produtos_estoque_baixo(limite=5):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM produtos WHERE quantidade <= ?", (limite,))
    produtos = cur.fetchall()
    con.close()
    return produtos

# importar produtos via CSV
def importar_produtos_csv(caminho_csv):
    try:
        with open(caminho_csv, newline='', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            con = sqlite3.connect("sistema.db")
            cur = con.cursor()
            for linha in leitor:
                nome = linha.get('nome')
                descricao = linha.get('descricao')
                quantidade = linha.get('quantidade')
                if nome and descricao and quantidade and quantidade.isdigit():
                    # Verifica se produto já existe pelo nome
                    cur.execute("SELECT id FROM produtos WHERE nome=?", (nome,))
                    produto_existente = cur.fetchone()
                    if produto_existente:
                        # Atualiza a quantidade do produto existente somando a nova
                        cur.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE id=?", (int(quantidade), produto_existente[0]))
                    else:
                        # Insere novo produto
                        cur.execute("INSERT INTO produtos (nome, descricao, quantidade) VALUES (?, ?, ?)", (nome, descricao, int(quantidade)))
                else:
                    con.close()
                    return False, f"Erro no arquivo CSV: linha com dados inválidos ({linha})"
            con.commit()
            con.close()
        return True, "Produtos importados com sucesso."
    except Exception as e:
        return False, f"Erro ao importar CSV: {e}"

# Saídas
def registrar_saida(produto_id, quantidade):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    cur.execute("SELECT quantidade FROM produtos WHERE id=?", (produto_id,))
    estoque = cur.fetchone()

    if estoque and estoque[0] >= quantidade:
        nova_qtd = estoque[0] - quantidade
        cur.execute("UPDATE produtos SET quantidade=? WHERE id=?", (nova_qtd, produto_id))
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

def excluir_saida(venda_id):
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

def editar_quantidade_produto(produto_id, nova_quantidade):
    con = sqlite3.connect("sistema.db")
    cur = con.cursor()
    try:
        cur.execute("UPDATE produtos SET quantidade=? WHERE id=?", (nova_quantidade, produto_id))
        con.commit()
        sucesso = cur.rowcount > 0
    except Exception as e:
        print(f"Erro ao editar quantidade do produto: {e}")
        sucesso = False
    finally:
        con.close()
    return sucesso

def exportar_saidas_csv(caminho):
    vendas = obter_saidas()
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Produto', 'Quantidade', 'Data'])
        writer.writerows(vendas)
