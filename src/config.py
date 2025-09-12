import os
from dotenv import load_dotenv

# Load variables from the .env file into the environment
load_dotenv()

def _only_digits(s: str) -> str:
    """A helper function to extract only digits from a string."""
    return "".join(ch for ch in str(s or "") if ch.isdigit())

# --- API Configuration ---
CLIENT_ID = os.getenv("BANCO_INTER_CLIENT_ID")
CLIENT_SECRET = os.getenv("BANCO_INTER_CLIENT_SECRET")
CERT_PATH = os.getenv("BANCO_INTER_CERT_PATH")
KEY_PATH = os.getenv("BANCO_INTER_KEY_PATH")

# --- Company Information ---
COMPANY_NAME = os.getenv("COMPANY_NAME")
COMPANY_CNPJ = _only_digits(os.getenv("COMPANY_CNPJ"))

# --- Bank Account Details ---
BANK_CODE = os.getenv("BANK_CODE", "077") # Default to "077" if not set
AGENCY = os.getenv("BANK_AGENCY")
AGENCY_DV = os.getenv("BANK_AGENCY_DV")
ACCOUNT = os.getenv("BANK_ACCOUNT")
ACCOUNT_DV = os.getenv("BANK_ACCOUNT_DV")

# --- CNAB Layout Constants ---
# These are less likely to change, but can also be in the .env file
LAYOUT_FILE = "107"
LAYOUT_LOTE = "046"
VERSION = "001"