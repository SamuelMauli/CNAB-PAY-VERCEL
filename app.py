import os
import sys
import tempfile
from pathlib import Path

# Configuração para Vercel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def resource_path(relative_path):
    """Retorna o caminho absoluto para o recurso, funcionando em dev e na Vercel"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_temp_dirs():
    """Configura diretórios temporários para uploads e outputs na Vercel"""
    temp_dir = Path(tempfile.gettempdir())
    uploads_dir = temp_dir / "cnab_uploads"
    outputs_dir = temp_dir / "cnab_outputs"
    certs_dir = temp_dir / "cnab_certs"
    
    uploads_dir.mkdir(exist_ok=True)
    outputs_dir.mkdir(exist_ok=True)
    certs_dir.mkdir(exist_ok=True)
    
    # Configurar certificados se fornecidos via variáveis de ambiente
    setup_certificates(certs_dir)
    
    return uploads_dir, outputs_dir, certs_dir

def setup_certificates(certs_dir):
    """Configura certificados do Banco Inter a partir de variáveis de ambiente"""
    import base64
    
    cert_content = os.getenv('BANCO_INTER_CERT_CONTENT')
    key_content = os.getenv('BANCO_INTER_KEY_CONTENT')
    
    if cert_content:
        try:
            cert_data = base64.b64decode(cert_content)
            with open(certs_dir / 'inter.crt', 'wb') as f:
                f.write(cert_data)
        except Exception as e:
            print(f"Erro ao configurar certificado: {e}")
    
    if key_content:
        try:
            key_data = base64.b64decode(key_content)
            with open(certs_dir / 'inter.key', 'wb') as f:
                f.write(key_data)
        except Exception as e:
            print(f"Erro ao configurar chave privada: {e}")

# Configurar diretórios temporários
uploads_dir, outputs_dir, certs_dir = setup_temp_dirs()

# Configurar variáveis de ambiente para os diretórios
os.environ['UPLOADS_DIR'] = str(uploads_dir)
os.environ['OUTPUTS_DIR'] = str(outputs_dir)
os.environ['CERTS_DIR'] = str(certs_dir)

static_dir = resource_path('src/static')
app = Flask(__name__, static_folder=static_dir)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vanlink-pix-system-2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)

# Importar rotas
sys.path.append('src')
from routes.pix_routes import pix_bp
app.register_blueprint(pix_bp, url_prefix='/api/pix')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Para Vercel - exporta a aplicação diretamente
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
