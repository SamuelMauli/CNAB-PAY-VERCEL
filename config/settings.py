import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
CERTS_DIR = BASE_DIR / "certs"

# Configurações do Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Configurações do Banco Inter
INTER_CLIENT_ID = os.environ.get('BANCO_INTER_CLIENT_ID', '77435113-d0ff-4dc5-ad5a-98d739b84ffe')
INTER_CLIENT_SECRET = os.environ.get('BANCO_INTER_CLIENT_SECRET', '7017f530-599a-4033-826a-55cabeda3910')
INTER_CERT_PATH = CERTS_DIR / "inter.crt"
INTER_KEY_PATH = CERTS_DIR / "inter.key"

# URLs da API do Banco Inter
INTER_BASE_URL = "https://cdpj.partners.bancointer.com.br"
INTER_TOKEN_URL = f"{INTER_BASE_URL}/oauth/v2/token"
INTER_PIX_URL = f"{INTER_BASE_URL}/banking/v2/pix"

# Configurações CNAB240 - VANLINK LTDA
COMPANY_CONFIG = {
    "bank_code": "077",
    "agency": "0001", 
    "agency_dv": "9",
    "account": "448102714",
    "account_dv": "4",
    "name": "VANLINK LTDA",
    "cnpj": "60413854000121",
    "layout_file": "107",
    "layout_lote": "046",
    "version": "001"
}

# Criar diretórios se não existirem
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

