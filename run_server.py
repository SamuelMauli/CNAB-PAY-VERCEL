import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório 'src' ao path para encontrar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def create_app():
    """Cria e configura a instância da aplicação Flask."""
    app = Flask(__name__, static_folder='src/static')

    # Importa as configurações do src/config.py
    import config
    
    # --- CONFIGURAÇÕES DE SEGURANÇA ---
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    CORS(app)

    # --- ROTAS (BLUEPRINTS) ---
    from routes.pix_routes import pix_bp
    app.register_blueprint(pix_bp, url_prefix='/api/pix')
    
    # Rota para servir o frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder = app.static_folder
        if path != "" and os.path.exists(os.path.join(static_folder, path)):
            return send_from_directory(static_folder, path)
        else:
            return send_from_directory(static_folder, 'index.html')

    return app

app = create_app()

if __name__ == '__main__':
    # O modo debug NUNCA deve ser True em produção
    is_debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=is_debug)