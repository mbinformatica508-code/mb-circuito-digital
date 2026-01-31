import sqlite3
import os
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mb_infor_2026_sucesso')

# Banco de Dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mb_orcamentos.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tabela de profissionais (Seus futuros clientes)
    cursor.execute('''CREATE TABLE IF NOT EXISTS tecnicos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, nome_empresa TEXT, email TEXT UNIQUE, senha TEXT)''')
    # Tabela de orçamentos vinculada ao técnico
    cursor.execute('''CREATE TABLE IF NOT EXISTS servicos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, tecnico_id INTEGER, cliente TEXT, zap TEXT, info TEXT, valor REAL)''')
    conn.commit()
    conn.close()

init_db()

# Visual Profissional com a marca MB
HTML_BASE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MB Orçamentos</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; color: #1c1e21; margin: 0; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .card { background: #ffffff; padding: 30px; border-radius: 12px; width: 90%; max-width: 400px; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.1); border-top: 6px solid #1e3c72; }
        h2 { color: #1e3c72; margin-bottom: 10px; font-weight: 800; }
        .btn { background: #1e3c72; color: #ffffff; padding: 12px; width: 100%; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 15px; text-decoration: none; display: block; transition: background 0.3s; }
        .btn:hover { background: #2c5364; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; background: #fff; color: #333; box-sizing: border-box; }
        .link-alt { color: #606770; font-size: 14px; text-decoration: none; margin-top: 20px; display: block; }
        .link-alt:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card"> {{ content | safe }} </div>
</body>
</html>
"""

@app.route('/')
def home():
    if not session.get('user_id'): return redirect(url_for('login'))
    content = f"""
    <h2>Painel MB</h2>
    <p>Bem-vindo, <strong>{session['empresa']}</strong></p>
    <hr style='border: 0.5px solid #eee; margin: 20px 0;'>
    <a href='/novo' class='btn'>CRIAR NOVO ORÇAMENTO</a>
    <a href='/meus_orcamentos' class='btn' style='background:#28a745'>LISTAR MEUS SERVIÇOS</a>
    <a href='/sair' class='link-alt'>Sair do Sistema</a>
    """
    return render_template_string(HTML_BASE, content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        conn = sqlite3.connect(DB_PATH)
        user = conn.execute("SELECT * FROM tecnicos WHERE email=? AND senha=?", (email, senha)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['empresa'] = user[1]
            return redirect(url_for('home'))
        return "Erro: Acesso Negado! <a href='/login'>Tentar novamente</a>"
    
    content = """
    <h2 style='color:#1e3c72;'>MB Orçamentos</h2>
    <p>Acesse sua conta profissional</p>
    <form method='POST'>
        <input name='email' type='email' placeholder='E-mail' required>
        <input name='senha' type='password' placeholder='Senha' required>
        <button class='btn'>ENTRAR</button>
    </form>
    <a href='/cadastro' class='link-alt'>Ainda não tem conta? Cadastre-se</a>
    """
    return render_template_string(HTML_BASE, content=content)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO tecnicos (nome_empresa, email, senha) VALUES (?,?,?)", (nome, email, senha))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except: return "E-mail já cadastrado! <a href='/cadastro'>Voltar</a>"
    
    content = """
    <h2>Nova Conta MB</h2>
    <p>Cadastre sua empresa e comece agora.</p>
    <form method='POST'>
        <input name='nome' placeholder='Nome da sua Empresa' required>
        <input name='email' type='email' placeholder='Seu E-mail' required>
        <input name='senha' type='password' placeholder='Crie uma Senha' required>
        <button class='btn'>CADASTRAR GRATUITAMENTE</button>
    </form>
    <a href='/login' class='link-alt'>Já possuo uma conta</a>
    """
    return render_template_string(HTML_BASE, content=content)

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
