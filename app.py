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
    cursor.execute('CREATE TABLE IF NOT EXISTS servicos (id INTEGER PRIMARY KEY AUTOINCREMENT, tecnico_id INTEGER, cliente TEXT, zap TEXT, descricao TEXT, mao_de_obra REAL, materiais REAL, total REAL, data TEXT)')
    conn.commit()
    conn.close()

init_db()

HTML_BASE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MB Orçamentos</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 15px; }
        .container { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-top: 8px solid #1e3c72; }
        h2 { color: #1e3c72; text-align: center; margin-bottom: 20px; }
        label { font-weight: bold; color: #333; display: block; margin-top: 10px; }
        input, textarea { width: 100%; padding: 12px; margin: 5px 0 15px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 16px; }
        .total-box { background: #1e3c72; color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; }
        .total-box span { font-size: 28px; font-weight: bold; display: block; }
        .btn { background: #28a745; color: white; padding: 15px; width: 100%; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 18px; text-decoration: none; display: block; text-align: center; }
        .card-job { border-left: 5px solid #1e3c72; background: #fff; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); position: relative; }
        .btn-pdf { background: #dc3545; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; font-size: 12px; float: right; }
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
    <h2>MB Orçamentos</h2>
    <p style='text-align:center;'>Bem-vindo, <strong>{session['empresa']}</strong></p>
    <a href='/novo' class='btn' style='background:#1e3c72'>+ GERAR ORÇAMENTO</a>
    <a href='/trabalhos' class='btn' style='margin-top:10px;'>HISTÓRICO DE SERVIÇOS</a>
    <a href='/sair' style='display:block; text-align:center; color:gray; margin-top:30px; text-decoration:none;'>Sair do Sistema</a>
    """
    return render_template_string(HTML_BASE, content=content)

@app.route('/novo', methods=['GET', 'POST'])
def novo():
    if not session.get('user_id'): return redirect(url_for('login'))
    if request.method == 'POST':
        cliente = request.form.get('cliente'); zap = request.form.get('zap')
        desc = request.form.get('descricao'); m_obra = float(request.form.get('mao_de_obra') or 0)
        mat = float(request.form.get('materiais') or 0); total = m_obra + mat
        data = datetime.now().strftime("%d/%m/%Y")
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO servicos (tecnico_id, cliente, zap, descricao, mao_de_obra, materiais, total, data) VALUES (?,?,?,?,?,?,?,?)",
                     (session['user_id'], cliente, zap, desc, m_obra, mat, total, data))
        conn.commit(); conn.close()
        return redirect(url_for('trabalhos'))
    
    content = """
    <h2>Novo Orçamento</h2>
    <form method='POST' id='orcForm'>
        <label>Cliente</label>
        <input name='cliente' placeholder='Nome do cliente' required>
        <label>WhatsApp</label>
        <input name='zap' placeholder='(71) 9....'>
        <label>Descrição dos Serviços</label>
        <textarea name='descricao' placeholder='Ex: Troca de fiação, 3 câmeras wi-fi...' rows='3' required></textarea>
        
        <label>Mão de Obra (R$)</label>
        <input type='number' name='mao_de_obra' id='m_obra' step='0.01' value='0.00' oninput='calcular()'>
        
        <label>Materiais (R$)</label>
        <input type='number' name='materiais' id='mat' step='0.01' value='0.00' oninput='calcular()'>

        <div class="total-box">
            VALOR TOTAL
            <span id="displayTotal">R$ 0,00</span>
        </div>

        <button class='btn'>SALVAR E GERAR PDF</button>
    </form>
    <script>
        function calcular() {
            let m = parseFloat(document.getElementById('m_obra').value) || 0;
            let mat = parseFloat(document.getElementById('mat').value) || 0;
            let total = m + mat;
            document.getElementById('displayTotal').innerText = "R$ " + total.toLocaleString('pt-BR', {minimumFractionDigits: 2});
        }
    </script>
    <a href='/' style='display:block; text-align:center; margin-top:15px; color:gray;'>Cancelar</a>
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
        lista += f"<div class='card-job'><a href='/pdf/{j[0]}' class='btn-pdf'>PDF</a><strong>{j[2]}</strong><br><small>{j[8]}</small><br>Total: <b>R$ {j[7]:.2f}</b></div>"
    content = f"<h2>Trabalhos Realizados</h2>{lista or '<p>Nenhum serviço salvo.</p>'}<a href='/' class='btn' style='background:gray; margin-top:20px;'>VOLTAR</a>"
    return render_template_string(HTML_BASE, content=content)

@app.route('/pdf/<int:id>')
def gerar_pdf(id):
    if not session.get('user_id'): return redirect(url_for('login'))
    conn = sqlite3.connect(DB_PATH)
    s = conn.execute("SELECT * FROM servicos WHERE id=?", (id,)).fetchone()
    conn.close()
    return f"""
    <div style='font-family:sans-serif; padding:30px; border:1px solid #eee; max-width:700px; margin:auto;'>
        <h1 style='color:#1e3c72;'>ORÇAMENTO #00{s[0]}</h1>
        <p><strong>Empresa:</strong> {session['empresa']}</p>
        <p><strong>Cliente:</strong> {s[2]} | <strong>Data:</strong> {s[8]}</p>
        <hr>
        <h3>Descrição dos Serviços:</h3>
        <p>{s[4]}</p>
        <table style='width:100%; border-collapse: collapse;'>
            <tr><td style='padding:10px; border-bottom:1px solid #eee;'>Mão de Obra</td><td style='text-align:right;'>R$ {s[5]:.2f}</td></tr>
            <tr><td style='padding:10px; border-bottom:1px solid #eee;'>Materiais</td><td style='text-align:right;'>R$ {s[6]:.2f}</td></tr>
            <tr style='font-size:20px; font-weight:bold;'><td style='padding:10px;'>TOTAL</td><td style='text-align:right; color:#28a745;'>R$ {s[7]:.2f}</td></tr>
        </table>
        <p style='margin-top:50px; text-align:center; font-size:12px;'>Obrigado pela preferência!</p>
        <button onclick='window.print()' style='display:block; margin:20px auto; padding:10px 20px;'>BAIXAR / IMPRIMIR PDF</button>
    </div>
    """

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
    content = "<h2>Acesso MB</h2><form method='POST'><input name='email' placeholder='E-mail' required><input name='senha' type='password' placeholder='Senha' required><button class='btn' style='background:#1e3c72'>ENTRAR</button></form><a href='/cadastro' style='display:block; text-align:center; margin-top:15px; color:gray; text-decoration:none;'>Criar Conta de Técnico</a>"
    return render_template_string(HTML_BASE, content=content)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome'); email = request.form.get('email'); senha = request.form.get('senha')
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO tecnicos (nome_empresa, email, senha) VALUES (?,?,?)", (nome, email, senha))
        conn.commit(); conn.close()
        return redirect(url_for('login'))
    content = "<h2>Cadastro MB</h2><form method='POST'><input name='nome' placeholder='Nome da Empresa' required><input name='email' placeholder='E-mail' required><input name='senha' type='password' placeholder='Senha' required><button class='btn' style='background:#1e3c72'>CADASTRAR</button></form>"
    return render_template_string(HTML_BASE, content=content)

@app.route('/sair')
def sair():
    session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
