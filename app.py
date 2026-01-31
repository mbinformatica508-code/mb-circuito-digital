import sqlite3
import os
from flask import Flask, render_template_string, request, redirect, url_for, session, make_response
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mb_premium_2026')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mb_sistema.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS tecnicos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome_empresa TEXT, email TEXT UNIQUE, senha TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS servicos (id INTEGER PRIMARY KEY AUTOINCREMENT, tecnico_id INTEGER, cliente TEXT, zap TEXT, descricao TEXT, valor REAL, data TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- ESTILO E INTERFACE ---
HTML_BASE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MB Orçamentos</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7f6; margin: 0; padding: 15px; }
        .container { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-top: 8px solid #1e3c72; }
        h2 { color: #1e3c72; text-align: center; }
        input, textarea { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 16px; }
        .btn { background: #1e3c72; color: white; padding: 15px; width: 100%; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; text-decoration: none; display: block; text-align: center; margin-top: 10px; }
        .card-job { border-left: 5px solid #28a745; background: #f9f9f9; padding: 10px; margin: 10px 0; border-radius: 5px; text-align: left; }
        .total-box { background: #eef2f3; padding: 15px; border-radius: 8px; font-size: 20px; font-weight: bold; color: #1e3c72; margin: 10px 0; text-align: center; }
    </style>
</head>
<body>
    <div class="container"> {{ content | safe }} </div>
</body>
</html>
"""

@app.route('/')
def home():
    if not session.get('user_id'): return redirect(url_for('login'))
    content = f"""
    <h2>Painel MB</h2>
    <p style='text-align:center;'>Empresa: <strong>{session['empresa']}</strong></p>
    <a href='/novo' class='btn'>+ NOVO ORÇAMENTO</a>
    <a href='/trabalhos' class='btn' style='background:#28a745'>TRABALHOS REALIZADOS</a>
    <a href='/sair' style='display:block; text-align:center; color:red; margin-top:20px; text-decoration:none;'>Sair</a>
    """
    return render_template_string(HTML_BASE, content=content)

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if not session.get('user_id'): return redirect(url_for('login'))
    if request.method == 'POST':
        cliente = request.form.get('cliente')
        zap = request.form.get('zap')
        descricao = request.form.get('descricao')
        valor = request.form.get('valor')
        data = datetime.now().strftime("%d/%m/%Y")
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO servicos (tecnico_id, cliente, zap, descricao, valor, data) VALUES (?,?,?,?,?,?)",
                     (session['user_id'], cliente, zap, descricao, valor, data))
        conn.commit()
        conn.close()
        return redirect(url_for('trabalhos'))
    
    content = """
    <h2>Gerar Orçamento</h2>
    <form method='POST'>
        <input name='cliente' placeholder='Nome do Cliente' required>
        <input name='zap' placeholder='WhatsApp'>
        <textarea name='descricao' placeholder='Descrição dos serviços...' rows='4' required></textarea>
        <p style='margin-bottom:0;'>Valor do Serviço (R$):</p>
        <input name='valor' id='valorInput' type='number' step='0.01' placeholder='0,00' oninput='updateTotal()' required>
        <div class='total-box'>TOTAL: R$ <span id='totalDisplay'>0,00</span></div>
        <button class='btn'>SALVAR E GERAR</button>
    </form>
    <script>
        function updateTotal() {
            let val = document.getElementById('valorInput').value;
            document.getElementById('totalDisplay').innerText = val ? parseFloat(val).toFixed(2).replace('.', ',') : '0,00';
        }
    </script>
    <a href='/' style='text-decoration:none; color:gray; display:block; text-align:center; margin-top:10px;'>Voltar</a>
    """
    return render_template_string(HTML_BASE, content=content)

@app.route('/trabalhos')
def trabalhos():
    if not session.get('user_id'): return redirect(url_for('login'))
    conn = sqlite3.connect(DB_PATH)
    jobs = conn.execute("SELECT * FROM servicos WHERE tecnico_id=? ORDER BY id DESC", (session['user_id'],)).fetchall()
    conn.close()
    
    lista = ""
    for j in jobs:
        lista += f"""
        <div class='card-job'>
            <strong>{j[2]}</strong> - {j[6]}<br>
            <small>{j[4]}</small><br>
            <strong>R$ {j[5]:.2f}</strong>
            <a href='/pdf/{j[0]}' style='float:right; color:#1e3c72; font-weight:bold; text-decoration:none;'>📄 PDF</a>
        </div>"""
    
    content = f"<h2>Trabalhos Realizados</h2>{lista or '<p>Nenhum trabalho salvo.</p>'}<a href='/' class='btn'>VOLTAR</a>"
    return render_template_string(HTML_BASE, content=content)

@app.route('/pdf/<int:id>')
def gerar_pdf(id):
    if not session.get('user_id'): return redirect(url_for('login'))
    conn = sqlite3.connect(DB_PATH)
    s = conn.execute("SELECT * FROM servicos WHERE id=?", (id,)).fetchone()
    conn.close()
    
    # Simulação de PDF em HTML formatado para impressão/compartilhamento
    pdf_html = f"""
    <div style='font-family:sans-serif; border:2px solid #333; padding:20px; width:100%; max-width:600px;'>
        <h1 style='text-align:center; color:#1e3c72;'>ORÇAMENTO PROFISSIONAL</h1>
        <hr>
        <p><strong>Empresa:</strong> {session['empresa']}</p>
        <p><strong>Cliente:</strong> {s[2]}</p>
        <p><strong>Data:</strong> {s[6]}</p>
        <hr>
        <h3>Descrição do Serviço:</h3>
        <p style='min-height:100px;'>{s[4]}</p>
        <hr>
        <h2 style='text-align:right;'>VALOR TOTAL: R$ {s[5]:.2f}</h2>
        <p style='text-align:center; font-size:12px; margin-top:50px;'>Orçamento válido por 7 dias.</p>
    </div>
    <script>window.print();</script>
    """
    return pdf_html

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email'); senha = request.form.get('senha')
        conn = sqlite3.connect(DB_PATH)
        user = conn.execute("SELECT * FROM tecnicos WHERE email=? AND senha=?", (email, senha)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]; session['empresa'] = user[1]
            return redirect(url_for('home'))
    content = "<h2>Acesso MB</h2><form method='POST'><input name='email' placeholder='E-mail' required><input name='senha' type='password' placeholder='Senha' required><button class='btn'>ENTRAR</button></form><a href='/cadastro' class='btn' style='background:gray'>CRIAR CONTA</a>"
    return render_template_string(HTML_BASE, content=content)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome'); email = request.form.get('email'); senha = request.form.get('senha')
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO tecnicos (nome_empresa, email, senha) VALUES (?,?,?)", (nome, email, senha))
        conn.commit(); conn.close()
        return redirect(url_for('login'))
    content = "<h2>Cadastro</h2><form method='POST'><input name='nome' placeholder='Nome da sua Empresa' required><input name='email' placeholder='E-mail' required><input name='senha' type='password' placeholder='Senha' required><button class='btn'>CADASTRAR</button></form>"
    return render_template_string(HTML_BASE, content=content)

@app.route('/sair')
def sair():
    session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
