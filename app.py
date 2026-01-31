import sqlite3
import os
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mb_chave_mestra_71')

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# Define o caminho para o banco de dados no servidor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mb_digital.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Cria as tabelas se não existirem
    cursor.execute('''CREATE TABLE IF NOT EXISTS tecnicos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT UNIQUE, senha TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS servicos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, zap TEXT, info TEXT, valor REAL, status TEXT)''')
    # Insere um usuário padrão para você não ficar trancado fora
    cursor.execute("INSERT OR IGNORE INTO tecnicos (id, nome, email, senha) VALUES (1, 'Mateus', 'admin@admin.com', '1234')")
    conn.commit()
    conn.close()

init_db()

# --- TEMPLATE VISUAL (HTML/CSS) ---
HTML_BASE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MB Circuito Digital</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f6f9; text-align: center; padding: 20px; }
        .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: inline-block; width: 90%; max-width: 400px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        .btn { background: #1e3c72; color: white; padding: 12px; width: 100%; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; }
        a { color: #1e3c72; text-decoration: none; display: block; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container"> {{ content | safe }} </div>
</body>
</html>
"""

# --- ROTAS DO SISTEMA ---

@app.route('/')
def home():
    if not session.get('user'): return redirect(url_for('login'))
    content = f"<h1>Painel MB Circuito</h1><p>Olá, {session['user']}!</p><div class='card'><h3>Sistema Online</h3><p>Seus orçamentos estão seguros na nuvem.</p><a href='/sair' style='color:red;'>SAIR DO SISTEMA</a></div>"
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
            session['user'] = user[1]
            return redirect(url_for('home'))
        return "Erro: Login inválido. <a href='/login'>Tente admin@admin.com / 1234</a>"
    
    content = """<div class='card'><h2>Login Profissional</h2><form method='POST'><input name='email' placeholder='E-mail (ex: admin@admin.com)' required><input name='senha' type='password' placeholder='Senha (ex: 1234)' required><button class='btn'>ENTRAR</button></form></div>"""
    return render_template_string(HTML_BASE, content=content)

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # O Render usa a porta definida na variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
