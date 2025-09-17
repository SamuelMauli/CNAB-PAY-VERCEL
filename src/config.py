# src/config.py

import os
from dotenv import load_dotenv

load_dotenv()

def _only_digits(s: str) -> str:
    """Remove todos os caracteres não numéricos de uma string."""
    return "".join(ch for ch in str(s or "") if ch.isdigit())

# --- CONFIGURAÇÕES DO SERVIDOR ---
# Chave secreta da aplicação Flask
SECRET_KEY = os.getenv("SECRET_KEY")
# Nível de log (INFO, DEBUG, ERROR)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


# --- CONFIGURAÇÕES DA API DO BANCO INTER ---
BASE_URL = os.getenv("BASE_URL")
CLIENT_ID = os.getenv("BANCO_INTER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BANCO_INTER_CLIENT_SECRET")
CERT_PATH = os.getenv("BANCO_INTER_CERT_PATH")
KEY_PATH = os.getenv("BANCO_INTER_KEY_PATH")
SCOPES = os.getenv("BANCO_INTER_SCOPES")


# --- DADOS DA EMPRESA E CONTA ---
COMPANY_NAME = os.getenv("COMPANY_NAME")
COMPANY_CNPJ = _only_digits(os.getenv("COMPANY_CNPJ"))
BANK_CODE = os.getenv("BANK_CODE", "077")
AGENCY = os.getenv("BANK_AGENCY")
AGENCY_DV = os.getenv("BANK_AGENCY_DV")
# A conta corrente para a API não deve ter o dígito verificador
ACCOUNT = _only_digits(os.getenv("BANK_ACCOUNT"))
ACCOUNT_DV = os.getenv("BANK_ACCOUNT_DV")


# --- CONFIGURAÇÕES DO CNAB (se necessário) ---
LAYOUT_FILE = "107"
LAYOUT_LOTE = "046"
VERSION = "001"