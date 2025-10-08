import pandas as pd
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Processador de arquivos Excel para dados de pagamento PIX"""
    
    COLUMN_MAPPING = {
        "name": ["NOME", "BENEFICIARIO", "FAVORECIDO", "NOME COMPLETO", "CLIENTE", "MOTORISTA", "Nome"],
        "pix_key": ["PIX", "CHAVE PIX", "CHAVE PIX/EMAIL", "CHAVE", "TELEFONE", "CELULAR", "E-MAIL", "Chave PIX", "Chave Pix"],
        "document": ["CPF", "CNPJ", "CPF/CNPJ", "DOCUMENTO", "DOCUMENTO FAVORECIDO", "CPF/CNPJ FAV"],
        "amount": ["VALOR", "VALOR PAGAMENTO", "VLR", "QUANTIA", "MONTANTE", "Valor", "Valor "],
        "campaign": ["CAMPANHA", "NOME CAMPANHA", "LOTE", "GRUPO"]
    }
    
    def __init__(self):
        self.df = None
        self.mapped_columns = {}
    
    def load_excel(self, file_path: str) -> bool:
        try:
            self.df = pd.read_excel(file_path)
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar Excel: {str(e)}")
            return False
    
    def detect_columns(self):
        if self.df is None: return
        
        detected = {}
        available_columns = {col.strip().upper(): col for col in self.df.columns}
        
        for field, possible_names in self.COLUMN_MAPPING.items():
            for name in possible_names:
                if name.upper() in available_columns:
                    detected[field] = available_columns[name.upper()]
                    break
        self.mapped_columns = detected

    def validate_data(self) -> Tuple[bool, List[str]]:
        if self.df is None: return False, ["Nenhum arquivo carregado"]
        
        errors = []
        for field in ["name", "pix_key", "amount"]:
            if field not in self.mapped_columns:
                errors.append(f"Coluna obrigatória não encontrada: {field}")
        if errors: return False, errors
        
        for idx, row in self.df.iterrows():
            if pd.isna(row.get(self.mapped_columns["amount"])):
                errors.append(f"Linha {idx+2}: Valor vazio")
        
        return not errors, errors
    
    def process_data(self) -> List[Dict[str, Any]]:
        if self.df is None: return []
        
        recipients = []
        for idx, row in self.df.iterrows():
            recipient = {}
            try:
                recipient["name"] = str(row.get(self.mapped_columns.get("name"), "")).strip()
                recipient["pix_key"] = str(row.get(self.mapped_columns.get("pix_key"), "")).strip()
                recipient["amount"] = float(row.get(self.mapped_columns.get("amount"), 0))
                
                doc = ""
                if "document" in self.mapped_columns and pd.notna(row.get(self.mapped_columns["document"])):
                    doc = "".join(filter(str.isdigit, str(row.get(self.mapped_columns["document"]))))
                
                if not doc:
                    pix_digits = "".join(filter(str.isdigit, recipient["pix_key"]))
                    if len(pix_digits) in [11, 14]:
                        doc = pix_digits
                
                recipient["document"] = doc
                recipients.append(recipient)
            except Exception as e:
                logger.error(f"Erro ao processar linha {idx+2}: {e}")
        return recipients