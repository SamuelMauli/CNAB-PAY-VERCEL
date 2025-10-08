from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Adiciona o diretório 'src' ao path para importações corretas
sys.path.append(str(Path(__file__).parent.parent))

import config
from excel_processor import ExcelProcessor
from cnab_generator import CNAB240Generator, Company

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

pix_bp = Blueprint('pix', __name__)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

UPLOAD_FOLDER = Path(resource_path("uploads"))
OUTPUT_FOLDER = Path(resource_path("output"))

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@pix_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Arquivo inválido ou não selecionado'}), 400

    try:
        filename = secure_filename(file.filename)
        new_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        filepath = UPLOAD_FOLDER / new_filename
        file.save(filepath)

        processor = ExcelProcessor()
        if not processor.load_excel(filepath):
            return jsonify({'success': False, 'error': 'Erro ao carregar o arquivo Excel.'}), 500
        
        processor.detect_columns()
        is_valid, errors = processor.validate_data()
        if not is_valid:
            return jsonify({'success': False, 'error': 'Dados inválidos na planilha.', 'details': errors}), 400

        recipients = processor.process_data()
        total_amount = sum(r.get("amount", 0) for r in recipients)
        
        summary = {
            "total_recipients": len(recipients),
            "total_amount": total_amount,
            "columns_detected": processor.mapped_columns
        }

        # MODIFICAÇÃO: Retornar TODOS os 'recipients', não apenas uma amostra.
        return jsonify({
            'success': True,
            'filename': new_filename,
            'summary': summary,
            'recipients': recipients, # Retorna a lista completa
            'total_recipients': len(recipients)
        })

    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return jsonify({'success': False, 'error': f"Ocorreu um erro interno: {e}"}), 500

# NOVA ROTA: Para buscar e exibir o conteúdo de um arquivo já enviado.
@pix_bp.route('/details/<filename>', methods=['GET'])
def get_file_details(filename):
    try:
        filepath = UPLOAD_FOLDER / secure_filename(filename)
        if not filepath.exists():
            return jsonify({'success': False, 'error': 'Arquivo não encontrado.'}), 404

        processor = ExcelProcessor()
        if not processor.load_excel(filepath):
            return jsonify({'success': False, 'error': 'Erro ao ler o arquivo Excel.'}), 500
        
        processor.detect_columns()
        recipients = processor.process_data()

        return jsonify({'success': True, 'filename': filename, 'recipients': recipients})

    except Exception as e:
        logger.error(f"Erro ao obter detalhes do arquivo: {e}")
        return jsonify({'success': False, 'error': "Ocorreu um erro interno no servidor."}), 500

@pix_bp.route('/generate-cnab', methods=['POST'])
def generate_cnab():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'success': False, 'error': 'Nome do arquivo não fornecido'}), 400

    try:
        filepath = UPLOAD_FOLDER / secure_filename(filename)
        if not filepath.exists():
            return jsonify({'success': False, 'error': 'Arquivo de origem não encontrado.'}), 404

        processor = ExcelProcessor()
        processor.load_excel(filepath)
        processor.detect_columns()
        recipients = processor.process_data()

        company = Company(
            bank_code=config.BANK_CODE, agency=config.AGENCY, agency_dv=config.AGENCY_DV,
            account=config.ACCOUNT, account_dv=config.ACCOUNT_DV,
            name=config.COMPANY_NAME, cnpj=config.COMPANY_CNPJ
        )
        
        seq_num = len(list(OUTPUT_FOLDER.glob("*.rem"))) + 1
        generator = CNAB240Generator(company)
        cnab_content = generator.generate_pix_file(recipients, seq_num)
        
        cnab_filename = f"CI240_001_{str(seq_num).zfill(6)}.rem"
        (OUTPUT_FOLDER / cnab_filename).write_text(cnab_content, encoding='ascii')

        total_amount = sum(r.get('amount', 0) for r in recipients)
        return jsonify({
            'success': True, 'cnab_filename': cnab_filename,
            'total_recipients': len(recipients), 'total_amount': total_amount,
            'download_url': f'/api/pix/download/{cnab_filename}'
        })
    except Exception as e:
        logger.error(f"Erro ao gerar CNAB: {e}")
        return jsonify({'success': False, 'error': f"Ocorreu um erro interno: {e}"}), 500

@pix_bp.route('/download/<filename>')
def download_file_route(filename):
    try:
        return send_file(OUTPUT_FOLDER / secure_filename(filename), as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'Arquivo não encontrado'}), 404

@pix_bp.route('/files', methods=['GET'])
def list_files():
    def get_file_info(folder, pattern):
        return sorted(
            ({'filename': f.name, 'size': f.stat().st_size, 'modified': f.stat().st_mtime} for f in folder.glob(pattern)),
            key=lambda x: x['modified'], reverse=True
        )
    return jsonify({
        'uploads': get_file_info(UPLOAD_FOLDER, "*.xls*"),
        'outputs': get_file_info(OUTPUT_FOLDER, "*.rem")
    })