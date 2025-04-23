from app import app, db, Produto

# Ativa o contexto da aplicação para acessar o banco corretamente
with app.app_context():
    db.session.query(Produto).delete()
    db.session.commit()
    print("✅ Todos os produtos foram apagados do banco de dados.")
