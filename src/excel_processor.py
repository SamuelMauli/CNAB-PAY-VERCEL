import pandas as pd
from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Processador de arquivos Excel para dados de pagamento PIX"""
    
    # Mapeamento de colunas possíveis
    COLUMN_MAPPING = {
        "name": ["NOME", "BENEFICIARIO", "FAVORECIDO", "NOME COMPLETO", "CLIENTE", "MOTORISTA", "Nome"],
        "pix_key": ["PIX", "CHAVE PIX", "CHAVE PIX/EMAIL", "CHAVE", "TELEFONE", "CELULAR", "E-MAIL", "Chave PIX"],
        "document": ["CPF", "CNPJ", "CPF/CNPJ", "DOCUMENTO", "DOCUMENTO FAVORECIDO", "CPF/CNPJ FAV", "CPF/CNPJ"],
        "amount": ["VALOR", "VALOR PAGAMENTO", "VLR", "QUANTIA", "MONTANTE", "Valor"],
        "campaign": ["CAMPANHA", "NOME CAMPANHA", "LOTE", "GRUPO"]
    }
    
    def __init__(self):
        self.df = None
        self.mapped_columns = {}
    
    def load_excel(self, file_path: str) -> bool:
        """Carrega arquivo Excel"""
        try:
            self.df = pd.read_excel(file_path)
            logger.info(f"Excel carregado: {len(self.df)} linhas, {len(self.df.columns)} colunas")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar Excel: {str(e)}")
            return False
    
    def detect_columns(self) -> Dict[str, str]:
        """Detecta automaticamente as colunas baseado nos nomes"""
        if self.df is None:
            return {}
        
        detected = {}
        available_columns = [col.strip().upper() for col in self.df.columns]
        
        for field, possible_names in self.COLUMN_MAPPING.items():
            for possible_name in possible_names:
                if possible_name.upper() in available_columns:
                    # Encontrar o nome original da coluna
                    original_col = None
                    for col in self.df.columns:
                        if col.strip().upper() == possible_name.upper():
                            original_col = col
                            break
                    
                    if original_col:
                        detected[field] = original_col
                        break
        
        self.mapped_columns = detected
        logger.info(f"Colunas detectadas: {detected}")
        return detected
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        """Valida os dados carregados"""
        if self.df is None:
            return False, ["Nenhum arquivo carregado"]
        
        errors = []
        
        # Verificar colunas obrigatórias
        required_fields = ["name", "pix_key", "amount"]
        for field in required_fields:
            if field not in self.mapped_columns:
                errors.append(f"Coluna obrigatória não encontrada: {field}")
        
        if errors:
            return False, errors
        
        # Validar dados linha por linha
        for idx, row in self.df.iterrows():
            row_errors = []
            
            # Nome
            name = row.get(self.mapped_columns["name"])
            if pd.isna(name) or not str(name).strip():
                row_errors.append(f"Linha {idx+2}: Nome vazio")
            
            # Chave PIX
            pix_key = row.get(self.mapped_columns["pix_key"])
            if pd.isna(pix_key) or not str(pix_key).strip():
                row_errors.append(f"Linha {idx+2}: Chave PIX vazia")
            
            # Valor
            amount = row.get(self.mapped_columns["amount"])
            try:
                amount_float = float(amount)
                if amount_float <= 0:
                    row_errors.append(f"Linha {idx+2}: Valor deve ser maior que zero")
            except (ValueError, TypeError):
                row_errors.append(f"Linha {idx+2}: Valor inválido")
            
            errors.extend(row_errors)
        
        return len(errors) == 0, errors
    
    def process_data(self) -> List[Dict[str, Any]]:
        """Processa os dados e retorna lista de beneficiários"""
        if self.df is None:
            return []
        
        recipients = []
        
        for idx, row in self.df.iterrows():
            try:
                recipient = {}
                
                # Nome
                recipient["name"] = str(row.get(self.mapped_columns["name"], "")).strip()
                
                # Chave PIX
                pix_key = row.get(self.mapped_columns["pix_key"])
                if pd.isna(pix_key):
                    recipient["pix_key"] = ""
                else:
                    recipient["pix_key"] = str(pix_key).strip()
                
                # Documento (CPF/CNPJ) - pode estar na chave PIX ou coluna separada
                if "document" in self.mapped_columns:
                    doc = row.get(self.mapped_columns["document"])
                    if not pd.isna(doc):
                        recipient["document"] = str(doc).strip()
                    else:
                        # Tentar extrair da chave PIX se for numérica
                        pix_digits = "".join(c for c in recipient["pix_key"] if c.isdigit())
                        if len(pix_digits) in [11, 14]:  # CPF ou CNPJ
                            recipient["document"] = pix_digits
                        else:
                            recipient["document"] = ""
                else:
                    # Tentar extrair da chave PIX
                    pix_digits = "".join(c for c in recipient["pix_key"] if c.isdigit())
                    if len(pix_digits) in [11, 14]:  # CPF ou CNPJ
                        recipient["document"] = pix_digits
                    else:
                        recipient["document"] = ""
                
                # Valor
                amount = row.get(self.mapped_columns["amount"])
                try:
                    recipient["amount"] = float(amount)
                except (ValueError, TypeError):
                    recipient["amount"] = 0.0
                
                # Campanha (opcional)
                if "campaign" in self.mapped_columns:
                    campaign = row.get(self.mapped_columns["campaign"])
                    recipient["campaign"] = str(campaign).strip() if not pd.isna(campaign) else ""
                else:
                    recipient["campaign"] = ""
                
                # Adicionar índice da linha para referência
                recipient["row_index"] = idx + 2  # +2 porque Excel começa em 1 e tem header
                
                recipients.append(recipient)
                
            except Exception as e:
                logger.error(f"Erro ao processar linha {idx+2}: {str(e)}")
                continue
        
        logger.info(f"Processados {len(recipients)} beneficiários")
        return recipients
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos dados processados"""
        if self.df is None:
            return {}
        
        recipients = self.process_data()
        
        total_amount = sum(r["amount"] for r in recipients)
        total_count = len(recipients)
        
        campaigns = set(r["campaign"] for r in recipients if r["campaign"])
        
        return {
            "total_recipients": total_count,
            "total_amount": total_amount,
            "campaigns": list(campaigns),
            "columns_detected": self.mapped_columns,
            "sample_data": recipients[:5] if recipients else []
        }
    
    def export_processed_data(self, output_path: str) -> bool:
        """Exporta dados processados para Excel"""
        try:
            recipients = self.process_data()
            if not recipients:
                return False
            
            df_export = pd.DataFrame(recipients)
            df_export.to_excel(output_path, index=False)
            logger.info(f"Dados exportados para: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {str(e)}")
            return False

