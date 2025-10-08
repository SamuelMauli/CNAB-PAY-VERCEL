from datetime import datetime, date
from typing import List, Dict, Any
from dataclasses import dataclass
import logging
import unicodedata

logger = logging.getLogger(__name__)

def only_digits(s: str) -> str:
    return "".join(ch for ch in str(s or "") if ch.isdigit())

def pad_alfa(text: str, length: int) -> str:
    t = (text or "")
    t = "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    t = t.encode("ascii", "ignore").decode("ascii").upper()
    return t[:length].ljust(length, " ")

def pad_num(num: Any, length: int) -> str:
    return only_digits(str(num or "0")).zfill(length)

@dataclass
class Company:
    bank_code: str; agency: str; agency_dv: str; account: str
    account_dv: str; name: str; cnpj: str
    layout_file: str = "107"; layout_lote: str = "046"

class CNAB240Generator:
    def __init__(self, company: Company):
        self.company = company; self.records: List[str] = []
        self.lote_seq = 0; self.reg_count = 0
    
    def _add_record(self, line: str, func_name: str):
        if len(line) != 240:
            raise ValueError(f"[{func_name}] Registro deve ter 240, mas tem {len(line)}")
        self.records.append(line); self.reg_count += 1
    
    def header_arquivo(self, seq_num: int):
        c = self.company
        line = (pad_num(c.bank_code, 3) + pad_num(0, 4) + pad_num(0, 1) +
                pad_alfa("", 9) + pad_num(2, 1) + pad_num(c.cnpj, 14) +
                pad_alfa("", 20) + pad_num(c.agency, 5) + pad_alfa(c.agency_dv, 1) +
                pad_num(c.account, 12) + pad_num(c.account_dv, 1) + pad_alfa("", 1) +
                pad_alfa(c.name, 30) + pad_alfa("BANCO INTER", 30) +
                pad_alfa("", 10) + pad_num(1, 1) + datetime.now().strftime("%d%m%Y") +
                datetime.now().strftime("%H%M%S") + pad_num(seq_num, 6) +
                pad_num(c.layout_file, 3) + pad_num(0, 5) + pad_alfa("", 20) +
                pad_alfa("", 20) + pad_alfa("", 29))
        self._add_record(line, "header_arquivo")
    
    def trailer_arquivo(self):
        line = (pad_num(self.company.bank_code, 3) + pad_num(9999, 4) +
                pad_num(9, 1) + pad_alfa("", 9) + pad_num(1, 6) +
                pad_num(self.reg_count + 1, 6) + pad_num(0, 6) + pad_alfa("", 205))
        self._add_record(line, "trailer_arquivo")

    def header_lote_pix(self):
        self.lote_seq += 1; c = self.company
        line = (pad_num(c.bank_code, 3) + pad_num(self.lote_seq, 4) + pad_num(1, 1) +
                pad_alfa("C", 1) + pad_num(20, 2) + pad_num(45, 2) +
                pad_num(c.layout_lote, 3) + pad_alfa("", 1) + pad_num(2, 1) +
                pad_num(c.cnpj, 14) + pad_alfa("", 20) + pad_num(c.agency, 5) +
                pad_alfa(c.agency_dv, 1) + pad_num(c.account, 12) +
                pad_num(c.account_dv, 1) + pad_alfa("", 1) + pad_alfa(c.name, 30) +
                pad_alfa("", 40) + pad_alfa("", 40) + pad_num(0, 8) +
                pad_alfa("", 15) + pad_alfa("", 20) + pad_num(0, 8) +
                pad_alfa("", 2) + pad_alfa("", 5))
        self._add_record(line, "header_lote_pix")

    def trailer_lote(self, soma_cents: int, qtd_regs: int):
        line = (pad_num(self.company.bank_code, 3) + pad_num(self.lote_seq, 4) +
                pad_num(5, 1) + pad_alfa("", 9) + pad_num(qtd_regs, 6) +
                pad_num(soma_cents, 18) + pad_num(0, 18) + pad_alfa("", 171) +
                pad_alfa("", 10))
        self._add_record(line, "trailer_lote")
    
    def segmento_a_pix(self, idx: int, r: Dict[str, Any], v_cents: int, dt: date):
        line = (pad_num(self.company.bank_code, 3) + pad_num(self.lote_seq, 4) +
                pad_num(3, 1) + pad_num(idx, 5) + pad_alfa("A", 1) + pad_num(3, 1) +
                pad_num("00", 2) + pad_num(self.company.bank_code, 3) +
                pad_num(0, 3) + pad_alfa("", 20) + pad_alfa(r.get("name", ""), 30) +
                pad_alfa("PAG PIX", 20) + dt.strftime("%d%m%Y") + pad_alfa("BRL", 3) +
                pad_num(0, 15) + pad_num(v_cents, 15) + pad_alfa("", 20) +
                dt.strftime("%d%m%Y") + pad_num(v_cents, 15) + pad_alfa("", 40) +
                pad_num(0, 2) + pad_num(0, 2) + pad_alfa("", 1) +
                pad_num(0, 1) + pad_alfa("", 17))
        self._add_record(line, "segmento_a_pix")

    def segmento_b_pix(self, idx: int, r: Dict[str, Any]):
        doc = only_digits(r.get("document", "")); t_doc = "1" if len(doc) == 11 else "2"
        line = (pad_num(self.company.bank_code, 3) + pad_num(self.lote_seq, 4) +
                pad_num(3, 1) + pad_num(idx, 5) + pad_alfa("B", 1) +
                pad_alfa("", 3) + pad_num(t_doc, 1) + pad_num(doc, 14) +
                pad_alfa(r.get("pix_key", ""), 77) + pad_alfa("", 131))
        self._add_record(line, "segmento_b_pix")

    def generate_pix_file(self, recipients: List[Dict[str, Any]], seq_num: int=1) -> str:
        self.records, self.lote_seq, self.reg_count = [], 0, 0
        self.header_arquivo(seq_num); self.header_lote_pix()
        total_valor, pay_date, seq_in_lote = 0, date.today(), 0
        for r in recipients:
            valor_cents = int(float(r["amount"]) * 100); total_valor += valor_cents
            seq_in_lote += 1; self.segmento_a_pix(seq_in_lote, r, valor_cents, pay_date)
            seq_in_lote += 1; self.segmento_b_pix(seq_in_lote, r)
        self.trailer_lote(total_valor, seq_in_lote + 2); self.trailer_arquivo()
        return "\n".join(self.records)