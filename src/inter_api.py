import requests
import base64
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, Any
import logging
import certifi

logger = logging.getLogger(__name__)

class InterAPIClient:
    """Cliente para integração com a API PIX AUTOMÁTICO do Banco Inter"""

    def __init__(self, client_id: str, client_secret: str, cert_path: str, key_path: str, base_url: str, scopes: str, conta_corrente: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.cert_path = cert_path
        self.key_path = key_path
        self.base_url = base_url
        self.scopes = scopes
        self.conta_corrente = conta_corrente.replace('-', '')
        self.token_url = f"{base_url}/oauth/v2/token"
        # Endpoint para a API Pix, não a de Pix Automático
        self.pix_url = f"{base_url}/pix/v2/pix" 
        # Endpoint CORRETO para criar recorrências do Pix Automático
        self.recorrencia_url = f"{base_url}/pix/v2/rec"
        self.access_token = None
        self.token_expires_at = None

    def _get_auth_header(self) -> str:
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _is_token_valid(self) -> bool:
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at

    def authenticate(self) -> bool:
        """Autentica na API do Banco Inter usando mTLS"""
        try:
            headers = { "Content-Type": "application/x-www-form-urlencoded" }
            data = { "grant_type": "client_credentials", "scope": self.scopes }

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
                verify=certifi.where(),
                timeout=30
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                logger.info("Autenticação com a API do Inter realizada com sucesso.")
                return True
            else:
                logger.error(f"Erro na autenticação: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exceção durante autenticação: {str(e)}")
            return False

    def _ensure_authenticated(self) -> bool:
        if not self._is_token_valid():
            return self.authenticate()
        return True

    def create_recorrencia(self, recipient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma RECORRÊNCIA de pagamento, não um pagamento direto."""
        if not self._ensure_authenticated():
            return {"success": False, "error": "Falha na autenticação"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            # Adiciona o x-conta-corrente se necessário
            if self.conta_corrente:
                 headers["x-conta-corrente"] = self.conta_corrente

            # --- ESTRUTURA DO JSON CONFORME A NOVA DOCUMENTAÇÃO ---
            # Este é um exemplo para criar uma recorrência mensal simples.
            today = date.today()
            data_final = today.replace(year=today.year + 1) # Validade de 1 ano

            payload = {
                "calendario": {
                    "dataInicial": today.strftime("%Y-%m-%d"),
                    "dataFinal": data_final.strftime("%Y-%m-%d"),
                    "periodicidade": "MENSAL" 
                },
                "valor": {
                    "valorRec": f"{recipient_data['amount']:.2f}"
                },
                "vinculo": {
                    "contrato": f"PAGAMENTO-{recipient_data.get('document', 'NA')}",
                    "objeto": f"Pagamento para {recipient_data.get('name', 'N/A')}"
                },
                 "politicaRetentativa": "NAO_PERMITE"
            }
            
            response = requests.post(
                self.recorrencia_url,
                headers=headers,
                json=payload,
                cert=(self.cert_path, self.key_path),
                verify=certifi.where(),
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Recorrência criada com sucesso: {result.get('idRec', 'N/A')}")
                return {"success": True, "data": result}
            else:
                logger.error(f"Erro ao criar recorrência: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            logger.error(f"Exceção durante criação da recorrência: {str(e)}")
            return {"success": False, "error": str(e)}