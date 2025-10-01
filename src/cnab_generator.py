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
            pad_num(c.agency, 5) + pad_alfa(c.agency_dv, 1) + pad_num(c.account, 12) + pad_num(c.account_dv, 1) + 
            pad_alfa("", 1) + 
            pad_alfa(c.name, 30) + pad_alfa("BANCO INTER", 30) + pad_alfa("", 10) + 
            pad_num(1, 1) + self._now().strftime("%d%m%Y") + self._now().strftime("%H%M%S") + 
            pad_num(seq_num, 7) + pad_num(c.layout_file, 3) + pad_num(0, 5) + 
            pad_alfa("", 20) + pad_alfa("", 20) + pad_alfa("", 28)
        
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
            pad_num(c.bank_code, 3) +                      # 001-003: Código do banco
            pad_num(self.lote_seq, 4) +                    # 004-007: Lote de serviço
            pad_num(1, 1) +                                # 008-008: Tipo de registro
            pad_alfa("C", 1) +                             # 009-009: Tipo de operação
            pad_num(20, 2) +                               # 010-011: Tipo de serviço
            pad_num(45, 2) +                               # 012-013: Forma de lançamento
            pad_num(c.layout_lote, 3) +                    # 014-016: Layout do lote
            pad_alfa("", 1) +                              # 017-017: Brancos
            pad_num(2, 1) +                                # 018-018: Tipo de inscrição
            pad_num(c.cnpj, 14) +                          # 019-032: CNPJ
            pad_alfa("", 20) +                             # 033-052: Brancos
            pad_num(c.agency, 5) +                         # 053-057: Agência
            pad_alfa(c.agency_dv, 1) +                     # 058-058: DV agência
            pad_num(c.account, 12) +                       # 059-070: Conta
            pad_num(c.account_dv, 1) +                     # 071-071: DV conta
            pad_alfa(c.name, 30) +                         # 072-101: Nome da empresa
            pad_alfa("", 40) +                             # 102-141: Brancos
            pad_alfa("", 30) +                             # 142-171: Brancos
            pad_num(0, 5) +                                # 172-176: Zeros
            pad_alfa("", 15) +                             # 177-191: Brancos
            pad_alfa("", 20) +                             # 192-211: Brancos
            pad_num(0, 5) +                                # 212-216: Zeros
            pad_num(0, 3) +                                # 217-219: Zeros
            pad_alfa("", 2) +                              # 220-221: Brancos
            pad_alfa("", 8) +                              # 222-229: Brancos
            pad_alfa("", 11)                               # 230-240: Brancos (corrigido para 11)
        )
        
        # Verificar se tem exatamente 240 posições
        assert len(line) == 240, f"Header lote deve ter 240 posições, got {len(line)}"
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
            pad_num(self.company.bank_code, 3) +           # 001-003: Código do banco
            pad_num(self.lote_seq, 4) +                    # 004-007: Lote de serviço
            pad_num(3, 1) +                                # 008-008: Tipo de registro
            pad_num(idx, 5) +                              # 009-013: Número sequencial
            pad_alfa("A", 1) +                             # 014-014: Código segmento
            pad_num(0, 1) +                                # 015-015: Tipo de movimento
            pad_num("00", 2) +                             # 016-017: Código de movimento
            pad_num("000", 3) +                            # 018-020: Banco favorecido
            pad_num("000", 3) +                            # 021-023: Agência favorecida
            pad_num("00000", 5) +                          # 024-028: Conta favorecida
            pad_num("0", 1) +                              # 029-029: DV conta favorecida
            pad_num("000000000000", 12) +                  # 030-041: Conta complementar
            pad_num("0", 1) +                              # 042-042: DV conta complementar
            pad_alfa("", 1) +                              # 043-043: Brancos
            pad_alfa(recipient.get("name", ""), 30) +      # 044-073: Nome favorecido
            pad_alfa(recipient.get("document", ""), 20) +  # 074-093: Número documento favorecido
            data_pag.strftime("%d%m%Y") +                  # 094-101: Data pagamento
            pad_alfa("BRL", 3) +                           # 102-104: Tipo moeda
            pad_num(0, 15) +                               # 105-119: Quantidade moeda
            pad_num(valor_cents, 15) +                     # 120-134: Valor pagamento
            pad_alfa("", 20) +                             # 135-154: Número documento empresa
            data_efetivacao +                              # 155-162: Data real efetivação
            pad_num(only_digits(recipient.get("document", "")), 14) + # 163-176: Valor real efetivação
            pad_alfa("", 8) +                              # 177-184: Brancos
            pad_num("01", 2) +                             # 185-186: Finalidade
            pad_alfa("", 29) +                             # 187-215: Complemento finalidade
            pad_alfa("", 3) +                              # 216-218: Brancos
            pad_alfa("", 6) +                              # 219-224: Aviso favorecido
            pad_alfa("", 16)                               # 225-240: Código ISPB
        )
        
        # Verificar se tem exatamente 240 posições
        assert len(line) == 240, f"Registro deve ter 240 posições, got {len(line)}"
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
            pad_alfa(chave, 77) + pad_alfa("", 36)
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
        
        return "\n".join(self.records)
    
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

