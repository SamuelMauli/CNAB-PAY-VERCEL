import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

static_dir = resource_path('src/static')
app = Flask(__name__, static_folder=static_dir)
app.config['SECRET_KEY'] = 'vanlink-pix-system-2024'
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

