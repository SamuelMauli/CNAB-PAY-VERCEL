# Sistema de Pagamentos PIX - VANLINK LTDA

Sistema completo para processamento de pagamentos PIX para motoristas, com geração de arquivos CNAB240 e integração com API do Banco Inter.

## 🚀 Funcionalidades

- ✅ **Upload de Planilhas Excel**: Interface drag-and-drop para upload de arquivos .xlsx/.xls
- ✅ **Processamento Automático**: Detecção automática de colunas e validação de dados
- ✅ **Geração CNAB240**: Criação de arquivos de remessa no padrão Banco Inter
- ✅ **Integração PIX**: Processamento direto via API do Banco Inter
- ✅ **Interface Moderna**: Design responsivo com tema VANLINK
- ✅ **Logs e Auditoria**: Sistema completo de rastreamento

## 📋 Dados da Empresa

- **Razão Social**: VANLINK LTDA
- **CNPJ**: 60.413.854/0001-21
- **Banco**: Inter (077)
- **Agência**: 0001
- **Conta**: 44810271-4

## 🛠️ Instalação

### Pré-requisitos
- Python 3.11+
- pip

### Passos de Instalação

1. **Extrair o projeto**:
```bash
unzip vanlink_pix_system.zip
cd vanlink_pix_app
```

2. **Criar ambiente virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

4. **Configurar certificados**:
   - Coloque os certificados do Banco Inter na pasta `certs/`
   - `inter.crt` - Certificado público
   - `inter.key` - Chave privada

5. **Executar aplicação**:
```bash
python app.py
```

6. **Acessar sistema**:
   - Abra o navegador em: http://localhost:5000

## 📁 Estrutura do Projeto

```
vanlink_pix_app/
├── app.py                 # Arquivo principal da aplicação
├── requirements.txt       # Dependências Python
├── README.md             # Esta documentação
├── .env                  # Configurações de ambiente
├── src/
│   ├── static/
│   │   └── index.html    # Interface web
│   ├── routes/
│   │   └── pix_routes.py # Rotas da API
│   ├── excel_processor.py # Processador de Excel
│   ├── cnab_generator.py  # Gerador CNAB240
│   └── inter_api.py      # Cliente API Banco Inter
├── certs/                # Certificados do Banco Inter
├── uploads/              # Arquivos Excel enviados
└── output/               # Arquivos CNAB240 gerados
```

## 📊 Formato da Planilha Excel

A planilha deve conter as seguintes colunas (nomes flexíveis):

| Coluna | Nomes Aceitos | Obrigatório | Exemplo |
|--------|---------------|-------------|---------|
| Nome | Nome, Motorista, Beneficiário | ✅ | João Silva |
| Chave PIX | Chave PIX, PIX, Telefone, E-mail | ✅ | 11999999999 |
| CPF/CNPJ | CPF/CNPJ, CPF, CNPJ, Documento | ⚠️ | 12345678901 |
| Valor | Valor, Quantia, VLR | ✅ | 250.00 |

## 🔧 Configurações

### Variáveis de Ambiente (.env)

```env
# Banco Inter - Produção
BANCO_INTER_CLIENT_ID=77435113-d0ff-4dc5-ad5a-98d739b84ffe
BANCO_INTER_CLIENT_SECRET=7017f530-599a-4033-826a-55cabeda3910
BANCO_INTER_CERT_PATH=certs/inter.crt
BANCO_INTER_KEY_PATH=certs/inter.key

# Dados da Conta
BANCO_INTER_CONTA_CORRENTE=44810271-4
BANCO_INTER_AGENCIA=0001
BANCO_INTER_CNPJ=60.413.854/0001-21

# Sistema
SECRET_KEY=sua_chave_secreta_muito_segura_para_producao
PORT=5000
```

## 🚦 Como Usar

### 1. Upload de Planilha
1. Acesse a aba "Upload & Processamento"
2. Arraste sua planilha Excel ou clique para selecionar
3. Aguarde o processamento automático

### 2. Gerar Arquivo CNAB240
1. Após o upload, clique em "Gerar Arquivo CNAB240"
2. O arquivo será gerado e baixado automaticamente
3. Use este arquivo para envio ao Banco Inter

### 3. Processar Pagamentos PIX
1. Clique em "Processar Pagamentos PIX"
2. Confirme a operação (irreversível)
3. Acompanhe o status de cada pagamento

### 4. Gerenciar Arquivos
1. Acesse a aba "Arquivos"
2. Visualize histórico de uploads e downloads
3. Baixe arquivos CNAB240 anteriores

## 🔒 Segurança

- ✅ Certificados mTLS para autenticação no Banco Inter
- ✅ Validação rigorosa de dados de entrada
- ✅ Logs de auditoria para todas as operações
- ✅ Configurações sensíveis em variáveis de ambiente

## 🆘 Solução de Problemas

### Erro de Autenticação API
- Verifique se os certificados estão na pasta `certs/`
- Confirme as credenciais no arquivo `.env`
- Teste a conectividade na aba "Configurações"

### Erro no Processamento Excel
- Verifique se a planilha tem as colunas obrigatórias
- Confirme se os valores estão no formato correto
- Veja os detalhes do erro na interface

### Servidor não Inicia
- Verifique se todas as dependências estão instaladas
- Confirme se a porta 5000 está disponível
- Execute: `python -m pip install -r requirements.txt`

## 📞 Suporte

Para suporte técnico, entre em contato com a equipe de desenvolvimento.

## 📄 Licença

Sistema proprietário da VANLINK LTDA. Todos os direitos reservados.

---

**VANLINK LTDA** - Sistema de Pagamentos PIX  
Versão 1.0 - Setembro 2024

