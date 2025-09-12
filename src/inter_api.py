import requests
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any
import logging
import certifi # <--- ADICIONE ESTA LINHA

logger = logging.getLogger(__name__)

class InterAPIClient:
    """Cliente para integração com API PIX do Banco Inter"""

    def __init__(self, client_id: str, client_secret: str, cert_path: str, key_path: str, base_url: str, scopes: str): # <--- REMOVA verify_path
        self.client_id = client_id
        self.client_secret = client_secret
        self.cert_path = cert_path
        self.key_path = key_path
        self.base_url = base_url
        self.scopes = scopes
        self.token_url = f"{base_url}/oauth/v2/token"
        self.pix_url = f"{base_url}/banking/v2/pix"
        self.access_token = None
        self.token_expires_at = None

    def _get_auth_header(self) -> str:
        """Gera header de autenticação Basic"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _is_token_valid(self) -> bool:
        """Verifica se o token ainda é válido"""
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at

    def authenticate(self) -> bool:
        """Autentica na API do Banco Inter usando mTLS"""
        try:
            headers = {
                "Authorization": self._get_auth_header(),
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "grant_type": "client_credentials",
                "scope": self.scopes
            }

            if not Path(self.cert_path).exists():
                logger.error(f"Certificado não encontrado: {self.cert_path}")
                return False
            if not Path(self.key_path).exists():
                logger.error(f"Chave privada não encontrada: {self.key_path}")
                return False

            response = requests.post(
                self.token_url,
                headers=headers,
                data=data,
                cert=(self.cert_path, self.key_path),
                verify=certifi.where(), # <--- ALTERE ESTA LINHA
                timeout=30
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                logger.info("Autenticação realizada com sucesso")
                return True
            else:
                logger.error(f"Erro na autenticação: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro durante autenticação: {str(e)}")
            return False

    def _ensure_authenticated(self) -> bool:
        """Garante que temos um token válido"""
        if not self._is_token_valid():
            return self.authenticate()
        return True

    def create_pix_payment(self, recipient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um pagamento PIX"""
        if not self._ensure_authenticated():
            return {"success": False, "error": "Falha na autenticação"}
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            payment_data = {
                "valor": recipient_data["amount"],
                "destinatario": {
                    "nome": recipient_data["name"],
                    "cpfCnpj": recipient_data["document"],
                    "chave": recipient_data["pix_key"]
                },
                "descricao": f"Pagamento para {recipient_data['name']}"
            }
            response = requests.post(
                f"{self.pix_url}/pix",
                headers=headers,
                json=payment_data,
                cert=(self.cert_path, self.key_path),
                verify=certifi.where(), # <--- ALTERE ESTA LINHA
                timeout=30
            )
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Pagamento PIX criado com sucesso: {result.get('id', 'N/A')}")
                return {"success": True, "data": result}
            else:
                logger.error(f"Erro ao criar pagamento PIX: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            logger.error(f"Erro durante criação do pagamento PIX: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Consulta status de um pagamento PIX"""
        if not self._ensure_authenticated():
            return {"success": False, "error": "Falha na autenticação"}
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                f"{self.pix_url}/pagamentos/{payment_id}",
                headers=headers,
                cert=(self.cert_path, self.key_path),
                verify=certifi.where(), # <--- ALTERE ESTA LINHA
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "data": result}
            else:
                logger.error(f"Erro ao consultar pagamento: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            logger.error(f"Erro durante consulta do pagamento: {str(e)}")
            return {"success": False, "error": str(e)}

    def test_connection(self) -> Dict[str, Any]:
        """Testa a conectividade com a API"""
        try:
            if self.authenticate():
                return {"success": True, "message": "Conexão com API do Banco Inter estabelecida com sucesso"}
            else:
                return {"success": False, "error": "Falha na autenticação"}
        except Exception as e:
            return {"success": False, "error": str(e)}