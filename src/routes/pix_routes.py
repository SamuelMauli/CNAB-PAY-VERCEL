# src/routes/pix_routes.py

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Importa as configurações corrigidas
import config

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from excel_processor import ExcelProcessor
from cnab_generator import CNAB240Generator, Company
from inter_api import InterAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pix_bp = Blueprint('pix', __name__)

BASE_DIR = Path(__file__).parent.parent.parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "output"
CERTS_FOLDER = BASE_DIR / "certs"

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@pix_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload e processamento de arquivo Excel"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = UPLOAD_FOLDER / filename
            
            file.save(str(filepath))
            
            processor = ExcelProcessor()
            if not processor.load_excel(str(filepath)):
                return jsonify({'success': False, 'error': 'Erro ao carregar arquivo Excel'}), 400
            
            columns = processor.detect_columns()
            
            is_valid, errors = processor.validate_data()
            if not is_valid:
                return jsonify({
                    'success': False, 
                    'error': 'Dados inválidos no arquivo',
                    'details': errors[:10]
                }), 400
            
            recipients = processor.process_data()
            summary = processor.get_summary()
            
            return jsonify({
                'success': True,
                'filename': filename,
                'summary': summary,
                'recipients': recipients[:10],
                'total_recipients': len(recipients)
            })
        
        return jsonify({'success': False, 'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@pix_bp.route('/generate-cnab', methods=['POST'])
def generate_cnab():
    """Gera arquivo CNAB240"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': 'Nome do arquivo não fornecido'}), 400
        
        filepath = UPLOAD_FOLDER / filename
        if not filepath.exists():
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'}), 404
        
        processor = ExcelProcessor()
        processor.load_excel(str(filepath))
        processor.detect_columns()
        recipients = processor.process_data()
        
        company = Company( 
            bank_code=config.BANK_CODE,
            agency=config.AGENCY,
            agency_dv=config.AGENCY_DV,
            account=config.ACCOUNT,
            account_dv=config.ACCOUNT_DV,
            name=config.COMPANY_NAME,
            cnpj=config.COMPANY_CNPJ
        ) 

        existing_files = list(OUTPUT_FOLDER.glob("*.rem"))
        sequential_number = len(existing_files) + 1
        
        formatted_sequential = str(sequential_number).zfill(7)
        
        generator = CNAB240Generator(company)
        cnab_content = generator.generate_pix_file(recipients, sequential_number)
        
        cnab_filename = f"CI240_001_{formatted_sequential}.rem"
        cnab_filepath = OUTPUT_FOLDER / cnab_filename
        
        with open(cnab_filepath, 'w', encoding='ascii') as f:
            f.write(cnab_content)
        
        total_amount = sum(float(r['amount']) for r in recipients)
        
        return jsonify({
            'success': True,
            'cnab_filename': cnab_filename,
            'total_recipients': len(recipients),
            'total_amount': total_amount,
            'download_url': f'/api/pix/download/{cnab_filename}'
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar CNAB: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
@pix_bp.route('/download/<filename>')
def download_file(filename):
    """Download de arquivo gerado"""
    try:
        filepath = OUTPUT_FOLDER / filename
        if not filepath.exists():
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(str(filepath), as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@pix_bp.route('/test-api', methods=['GET'])
def test_api():
    """Testa conectividade com API do Banco Inter"""
    try:
        cert_path = str(CERTS_FOLDER / config.CERT_PATH)
        client = InterAPIClient(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            cert_path=cert_path,
            key_path=str(CERTS_FOLDER / config.KEY_PATH),
            base_url=config.BASE_URL,
            scopes=config.SCOPES
        )
        result = client.test_connection()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro no teste da API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@pix_bp.route('/process-payments', methods=['POST'])
def process_payments():
    """Processa pagamentos PIX via API do Banco Inter"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': 'Nome do arquivo não fornecido'}), 400
        
        filepath = UPLOAD_FOLDER / filename
        if not filepath.exists():
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'}), 404
        
        processor = ExcelProcessor()
        processor.load_excel(str(filepath))
        processor.detect_columns()
        recipients = processor.process_data()
        
        cert_path = str(CERTS_FOLDER / config.CERT_PATH)
        client = InterAPIClient(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            cert_path=cert_path,
            key_path=str(CERTS_FOLDER / config.KEY_PATH),
            base_url=config.BASE_URL,
            scopes=config.SCOPES
        )
        
        results = []
        for recipient in recipients:
            payment_data = {
                "name": recipient["name"],
                "document": recipient["document"],
                "pix_key": recipient["pix_key"],
                "amount": recipient["amount"]
            }
            
            result = client.create_pix_payment(payment_data)
            results.append({
                "recipient": recipient["name"],
                "amount": recipient["amount"],
                "success": result["success"],
                "error": result.get("error", ""),
                "payment_id": result.get("data", {}).get("id", "")
            })
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        return jsonify({
            'success': True,
            'total_processed': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar pagamentos: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@pix_bp.route('/files', methods=['GET'])
def list_files():
    """Lista arquivos disponíveis"""
    try:
        uploads = []
        if UPLOAD_FOLDER.exists():
            for file in UPLOAD_FOLDER.glob("*.xlsx"):
                stat = file.stat()
                uploads.append({
                    'filename': file.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        outputs = []
        if OUTPUT_FOLDER.exists():
            for file in OUTPUT_FOLDER.glob("*.rem"):
                stat = file.stat()
                outputs.append({
                    'filename': file.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return jsonify({
            'uploads': uploads,
            'outputs': outputs
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar arquivos: {str(e)}")
        return jsonify({'error': str(e)}), 500