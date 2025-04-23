from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os



app = Flask(__name__)

# Diretórios
ENCARTES_DIR = "encartes"
UPLOAD_FOLDER = 'static/imagens'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCARTES_DIR, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuração do banco SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///encartes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Produto
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem_url = db.Column(db.String(200), nullable=False)

# Página inicial
@app.route('/')
def home():
    return 'API de Encartes funcionando com SQLite! ✅'

# Rota para cadastrar produto com imagem
@app.route('/cadastrar-produto', methods=['POST'])
def cadastrar_produto():
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    imagem = request.files.get('imagem')

    if not nome or not preco or not imagem:
        return jsonify({'erro': 'Dados incompletos'}), 400

    # Salvar imagem com nome seguro
    nome_imagem = secure_filename(imagem.filename)
    imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_imagem))
    imagem_url = f"imagens/{nome_imagem}"  # caminho relativo para a pasta static

    produto = Produto(
        nome=nome,
        preco=float(preco.replace(',', '.')),
        imagem_url=imagem_url
    )
    db.session.add(produto)
    db.session.commit()

    # Redireciona para a vitrine após o cadastro
    return redirect(url_for('exibir_produtos'))

# Página com vitrine dos produtos
@app.route('/produtos')
def exibir_produtos():
    produtos = Produto.query.all()
    return render_template('produtos.html', produtos=produtos)

# Função para excluir produto
@app.route('/excluir/<int:id>')
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('exibir_produtos'))

@app.route('/cadastrar')
def formulario_cadastro():
    return render_template(
        'form_produto.html',
        titulo="Cadastro de Produto",
        acao=url_for('cadastrar_produto'),
        texto_botao="Cadastrar",
        icone='<i class="fas fa-plus"></i>',
        produto=None
    )

@app.route('/editar/<int:id>')
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    return render_template(
        'form_produto.html',
        titulo="Editar Produto",
        acao=url_for('atualizar_produto', id=id),
        texto_botao="Salvar Alterações",
        icone='<i class="fas fa-save"></i>',
        produto=produto
    )

# Rota para atualizar o produto
@app.route('/atualizar/<int:id>', methods=['POST'])
def atualizar_produto(id):
    produto = Produto.query.get_or_404(id)
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    imagem = request.files.get('imagem')

    if nome:
        produto.nome = nome
    if preco:
        produto.preco = float(preco.replace(',', '.'))
    if imagem:
        nome_imagem = secure_filename(imagem.filename)
        imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_imagem))
        produto.imagem_url = f"imagens/{nome_imagem}"

    db.session.commit()
    return redirect(url_for('exibir_produtos'))

if __name__ == '__main__':
    print("🚀 Iniciando o servidor Flask...")
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)
