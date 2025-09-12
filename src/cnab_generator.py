from datetime import datetime, date
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

def only_digits(s: str) -> str:
    """Extrai apenas dígitos de uma string"""
    return "".join(ch for ch in str(s or "") if ch.isdigit())

def pad_alfa(text: str, length: int) -> str:
    """Preenche string alfanumérica com espaços à direita"""
    t = (text or "")
    import unicodedata
    t = unicodedata.normalize("NFKD", t)
    t = t.encode("ascii", "ignore").decode("ascii")
    t = t.upper()
    return t[:length].ljust(length, " ")

def pad_num(num: Any, length: int) -> str:
    """Preenche string numérica com zeros à esquerda"""
    if num is None or num == "":
        s = ""
    else:
        s = only_digits(str(num))
    return s[-length:].rjust(length, "0")

@dataclass
class Company:
    """Dados da empresa para CNAB240"""
    bank_code: str
    agency: str
    agency_dv: str
    account: str
    account_dv: str
    name: str
    cnpj: str
    layout_file: str = "107"
    layout_lote: str = "046"
    version: str = "001"

class CNAB240Generator:
    """Gerador de arquivos CNAB240 para Banco Inter"""
    
    def __init__(self, company: Company):
        self.company = company
        self.records: List[str] = []
        self.lote_seq = 0
        self.reg_count = 0
    
    def _now(self):
        return datetime.now()
    
    def _add_record(self, line: str):
        """Adiciona um registro ao arquivo"""
        assert len(line) == 240, f"Registro deve ter 240 posições, got {len(line)}"
        self.records.append(line)
        self.reg_count += 1
    
    def header_arquivo(self, seq_num: int):
        """Gera header do arquivo"""
        c = self.company
        line = (
            pad_num(c.bank_code, 3) + pad_num(0, 4) + pad_num(0, 1) + pad_alfa("", 9) +
            pad_num(2, 1) + pad_num(c.cnpj, 14) + pad_alfa("", 20) +
            pad_num(c.agency, 5) + pad_alfa(c.agency_dv, 1) + pad_num(c.account, 13) + 
            pad_alfa("", 1) +
            pad_alfa(c.name, 30) + pad_alfa("BANCO INTER", 30) + pad_alfa("", 10) +
            pad_num(1, 1) + self._now().strftime("%d%m%Y") + self._now().strftime("%H%M%S") +
            pad_num(seq_num, 6) + pad_num(c.layout_file, 3) + pad_num(1600, 5) + 
            pad_alfa("", 20) + pad_alfa("", 20) + pad_alfa("", 29)
        )
        self._add_record(line)
    
    def trailer_arquivo(self, total_lotes: int):
        """Gera trailer do arquivo"""
        line = (
            pad_num(self.company.bank_code, 3) + pad_num(9999, 4) + pad_num(9, 1) + 
            pad_alfa("", 9) + pad_num(total_lotes, 6) + pad_num(self.reg_count + 1, 6) + 
            pad_alfa("", 211)
        )
        self._add_record(line)
    
    def header_lote_pix(self):
        """Gera header do lote PIX"""
        self.lote_seq += 1
        c = self.company
        line = (
            pad_num(c.bank_code, 3) + pad_num(self.lote_seq, 4) + pad_num(1, 1) + 
            pad_alfa("C", 1) + pad_num(20, 2) + pad_num(45, 2) + pad_num(c.layout_lote, 3) + 
            pad_alfa("", 1) + pad_num(2, 1) + pad_num(c.cnpj, 14) + pad_alfa("", 20) +
            pad_num(c.agency, 5) + pad_num(c.agency_dv, 1) + pad_num(c.account, 13) + 
            pad_alfa("", 1) + pad_alfa(c.name, 30) +
            pad_alfa("", 40) + pad_alfa("", 30) + pad_num(0, 5) + pad_alfa("", 15) + 
            pad_alfa("", 20) + pad_num(0, 5) + pad_num(0, 3) + pad_alfa("", 2) + 
            pad_alfa("", 8) + pad_alfa("", 10)
        )
        self._add_record(line)
    
    def trailer_lote(self, soma_valores_cents: int, qtd_registros_detalhe: int):
        """Gera trailer do lote"""
        line = (
            pad_num(self.company.bank_code, 3) + pad_num(self.lote_seq, 4) + pad_num(5, 1) + 
            pad_alfa("", 9) + pad_num(qtd_registros_detalhe + 2, 6) + 
            pad_num(soma_valores_cents, 18) + pad_num(0, 18) + pad_alfa("", 6) + 
            pad_alfa("", 165) + pad_alfa("", 10)
        )
        self._add_record(line)
    
    def segmento_a_pix(self, idx: int, recipient: Dict[str, str], valor_cents: int, data_pag: date):
        """Gera segmento A para PIX"""
        # Data de hoje para efetivação do pagamento (posições 155-162)
        data_efetivacao = date.today().strftime("%d%m%Y")
        
        line = (
            pad_num(self.company.bank_code, 3) + pad_num(self.lote_seq, 4) + pad_num(3, 1) + 
            pad_num(idx, 5) + pad_alfa("A", 1) + pad_num(0, 1) + pad_num("00", 2) + 
            pad_num("000", 3) + pad_num("000", 3) + pad_num("00000", 5) + pad_num("0", 1) + 
            pad_num("000000000000", 12) + pad_num("0", 1) + pad_alfa("", 1) +
            pad_alfa(recipient.get("name", ""), 30) + 
            pad_alfa(recipient.get("document", ""), 20) +
            data_pag.strftime("%d%m%Y") + pad_alfa("BRL", 3) + pad_num(0, 15) + 
            pad_num(valor_cents, 15) + pad_alfa("", 20) + data_efetivacao + 
            pad_num(only_digits(recipient.get("document", "")), 14) + 
            pad_num("", 8) + pad_num("01", 2) + pad_alfa("", 29) + pad_alfa("", 10)
        )
        if len(line) < 240:
            line = line + pad_alfa("", 240 - len(line))
        elif len(line) > 240:
            line = line[:240]
        self._add_record(line)
    
    def segmento_b_pix(self, idx: int, recipient: Dict[str, str]):
        """Gera segmento B para PIX"""
        chave = recipient.get("pix_key", "") or ""
        # Determinar tipo de chave PIX
        if only_digits(chave) and len(only_digits(chave)) in (11, 14):
            forma = "03"  # CPF/CNPJ
        elif "@" in chave:
            forma = "01"  # Email
        elif only_digits(chave) and len(only_digits(chave)) >= 10:
            forma = "02"  # Telefone
        else:
            forma = "04"  # Chave aleatória
        
        tipo_doc = "1" if len(only_digits(recipient.get("document", ""))) == 11 else "2"
        
        line = (
            pad_num(self.company.bank_code, 3) + pad_num(self.lote_seq, 4) + pad_num(3, 1) + 
            pad_num(idx, 5) + pad_alfa("B", 1) + pad_alfa(forma, 3) + pad_num(tipo_doc, 1) +
            pad_num(recipient.get("document", ""), 14) + 
            pad_alfa(recipient.get("txid", ""), 35) + pad_alfa("", 60) + 
            pad_alfa(chave, 99) + pad_alfa("", 6) + pad_num("", 8)
        )
        self._add_record(line)
    
    def generate_pix_file(self, recipients: List[Dict[str, Any]], seq_num: int = 1) -> str:
        """Gera arquivo CNAB240 completo para pagamentos PIX"""
        self.records = []
        self.lote_seq = 0
        self.reg_count = 0
        
        # Header do arquivo
        self.header_arquivo(seq_num)
        
        # Header do lote PIX
        self.header_lote_pix()
        
        # Registros de detalhe
        total_valor = 0
        pay_date = date.today()
        
        for i, recipient in enumerate(recipients, 1):
            valor_cents = int(float(recipient["amount"]) * 100)
            total_valor += valor_cents
            
            # Segmento A
            self.segmento_a_pix(i, recipient, valor_cents, pay_date)
            
            # Segmento B
            self.segmento_b_pix(i, recipient)
        
        # Trailer do lote
        qtd_detalhes = len(recipients) * 2  # 2 segmentos por beneficiário
        self.trailer_lote(total_valor, qtd_detalhes)
        
        # Trailer do arquivo
        self.trailer_arquivo(1)  # 1 lote
        
        return "\n".join(self.records) + "\n"
    
    def validate_recipient(self, recipient: Dict[str, Any]) -> List[str]:
        """Valida dados do beneficiário"""
        errors = []
        
        if not recipient.get("name"):
            errors.append("Nome é obrigatório")
        
        if not recipient.get("pix_key"):
            errors.append("Chave PIX é obrigatória")
        
        if not recipient.get("document"):
            errors.append("CPF/CNPJ é obrigatório")
        
        try:
            amount = float(recipient.get("amount", 0))
            if amount <= 0:
                errors.append("Valor deve ser maior que zero")
        except (ValueError, TypeError):
            errors.append("Valor inválido")
        
        return errors

