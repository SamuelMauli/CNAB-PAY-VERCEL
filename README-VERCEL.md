# Deploy do Sistema CNAB-PAY na Vercel

Este documento contém as instruções para fazer o deploy do sistema CNAB-PAY na Vercel.

## Modificações Realizadas

### 1. Configuração para Vercel
- Criado `vercel.json` com configurações específicas para Python
- Modificado `app.py` para funcionar em ambiente serverless
- Configurado uso de diretórios temporários para uploads e outputs

### 2. Gerenciamento de Certificados
- Certificados do Banco Inter agora são configurados via variáveis de ambiente
- Conteúdo dos certificados deve ser codificado em Base64
- Certificados são criados dinamicamente no diretório temporário

### 3. Armazenamento de Arquivos
- Uploads e outputs são armazenados em diretórios temporários
- Arquivos são mantidos durante a execução da função serverless
- **Importante**: Arquivos são perdidos entre execuções diferentes

## Variáveis de Ambiente Necessárias

Configure as seguintes variáveis de ambiente na Vercel:

```bash
# Sistema
SECRET_KEY=sua_chave_secreta_muito_segura_para_producao
LOG_LEVEL=INFO

# Banco Inter
BASE_URL=https://cdpj.partners.bancointer.com.br
BANCO_INTER_CLIENT_ID=77435113-d0ff-4dc5-ad5a-98d739b84ffe
BANCO_INTER_CLIENT_SECRET=7017f530-599a-4033-826a-55cabeda3910
BANCO_INTER_SCOPES=pix-write

# Certificados (Base64)
BANCO_INTER_CERT_CONTENT=LS0tLS1CRUdJTi... (conteúdo do certificado em Base64)
BANCO_INTER_KEY_CONTENT=LS0tLS1CRUdJTi... (conteúdo da chave privada em Base64)

# Empresa
COMPANY_NAME=VANLINK LTDA
COMPANY_CNPJ=60.413.854/0001-21
BANK_CODE=077
BANK_AGENCY=0001
BANK_ACCOUNT=44810271
BANK_ACCOUNT_DV=4
```

## Como Converter Certificados para Base64

```bash
# Para o certificado
base64 -i inter.crt -o cert_base64.txt

# Para a chave privada
base64 -i inter.key -o key_base64.txt
```

## Limitações do Ambiente Serverless

1. **Armazenamento Temporário**: Arquivos são perdidos entre execuções
2. **Timeout**: Funções têm limite de 30 segundos (configurado no vercel.json)
3. **Memória**: Limitada pelo plano da Vercel
4. **Certificados**: Devem ser fornecidos via variáveis de ambiente

## Estrutura de Arquivos Modificada

```
CNAB-PAY-VERCEL/
├── vercel.json              # Configuração da Vercel
├── app.py                   # Aplicação principal (modificada)
├── requirements.txt         # Dependências (otimizada)
├── .env.example            # Exemplo de variáveis de ambiente
├── src/
│   ├── config.py           # Configurações (modificada)
│   ├── routes/
│   │   └── pix_routes.py   # Rotas (modificada)
│   └── ...
└── README-VERCEL.md        # Este arquivo
```

## Deploy na Vercel

1. Faça push do código para um repositório Git
2. Conecte o repositório na Vercel
3. Configure as variáveis de ambiente
4. Deploy será automático

## Funcionalidades Mantidas

- ✅ Upload de planilhas Excel
- ✅ Processamento de dados PIX
- ✅ Geração de arquivos CNAB240
- ✅ Interface web completa
- ✅ Validação de dados
- ✅ Logs e auditoria

## Considerações de Produção

- Para uso em produção, considere usar um serviço de armazenamento persistente (AWS S3, Google Cloud Storage)
- Implemente backup dos certificados em local seguro
- Configure monitoramento e alertas
- Considere usar um banco de dados externo para logs e auditoria
