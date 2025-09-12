# src/config.py

import os
from dotenv import load_dotenv

load_dotenv()

def _only_digits(s: str) -> str:
    """Remove todos os caracteres não numéricos de uma string."""
    return "".join(ch for ch in str(s or "") if ch.isdigit())

# ADICIONE ESTA LINHA:
BASE_URL = os.getenv("BASE_URL")

# Chave secreta da aplicação Flask
SECRET_KEY = os.getenv("SECRET_KEY")

# Credenciais da API do Banco Inter
CLIENT_ID = os.getenv("BANCO_INTER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BANCO_INTER_CLIENT_SECRET")
CERT_PATH = os.getenv("BANCO_INTER_CERT_PATH")
KEY_PATH = os.getenv("BANCO_INTER_KEY_PATH")
SCOPES = os.getenv("BANCO_INTER_SCOPES")

# Informações da Empresa
COMPANY_NAME = os.getenv("COMPANY_NAME")
COMPANY_CNPJ = _only_digits(os.getenv("COMPANY_CNPJ"))

# Dados Bancários
BANK_CODE = os.getenv("BANK_CODE", "077")
AGENCY = os.getenv("BANK_AGENCY")
AGENCY_DV = os.getenv("BANK_AGENCY_DV")
ACCOUNT = os.getenv("BANK_ACCOUNT")
ACCOUNT_DV = os.getenv("BANK_ACCOUNT_DV")

# Configurações do CNAB
LAYOUT_FILE = "107"
LAYOUT_LOTE = "046"
VERSION = "001"