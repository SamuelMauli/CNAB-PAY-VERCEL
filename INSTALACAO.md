# 🚀 Guia de Instalação - Sistema PIX VANLINK

## Pré-requisitos

### Windows
1. **Python 3.11+**
   - Baixe em: https://www.python.org/downloads/
   - ✅ Marque "Add Python to PATH" durante instalação

2. **Git** (opcional)
   - Baixe em: https://git-scm.com/download/win

### Linux/Ubuntu
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### macOS
```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python
brew install python
```

## 📦 Instalação Passo a Passo

### 1. Extrair o Projeto
```bash
# Extrair o arquivo ZIP
unzip vanlink_pix_system.zip
cd vanlink_pix_app
```

### 2. Criar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configurar Certificados

1. **Obter Certificados do Banco Inter**:
   - Acesse o Portal PJ do Banco Inter
   - Vá em "Aplicações" → "Nova Aplicação"
   - Baixe o pacote de certificados (.zip)

2. **Instalar Certificados**:
   ```bash
   # Criar pasta de certificados (se não existir)
   mkdir -p certs
   
   # Copiar certificados para a pasta
   cp /caminho/para/certificado.crt certs/inter.crt
   cp /caminho/para/chave.key certs/inter.key
   ```

### 5. Configurar Variáveis de Ambiente

Edite o arquivo `.env` com suas credenciais:

```env
# Banco Inter - PRODUÇÃO
BANCO_INTER_CLIENT_ID=77435113-d0ff-4dc5-ad5a-98d739b84ffe
BANCO_INTER_CLIENT_SECRET=7017f530-599a-4033-826a-55cabeda3910

# Caminhos dos Certificados
BANCO_INTER_CERT_PATH=certs/inter.crt
BANCO_INTER_KEY_PATH=certs/inter.key

# Dados da Conta VANLINK
BANCO_INTER_CONTA_CORRENTE=44810271-4
BANCO_INTER_AGENCIA=0001
BANCO_INTER_CNPJ=60.413.854/0001-21

# Configurações do Sistema
SECRET_KEY=vanlink_pix_system_2024_secure_key
PORT=5000
```

### 6. Testar Instalação

```bash
# Executar aplicação
python app.py
```

Você deve ver:
```
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
```

### 7. Acessar Sistema

Abra seu navegador e acesse: **http://localhost:5000**

## 🔧 Configuração Avançada

### Executar como Serviço (Linux)

1. **Criar arquivo de serviço**:
```bash
sudo nano /etc/systemd/system/vanlink-pix.service
```

2. **Conteúdo do arquivo**:
```ini
[Unit]
Description=VANLINK PIX System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/vanlink_pix_app
Environment=PATH=/home/ubuntu/vanlink_pix_app/venv/bin
ExecStart=/home/ubuntu/vanlink_pix_app/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Ativar serviço**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vanlink-pix
sudo systemctl start vanlink-pix
```

### Configurar Nginx (Produção)

1. **Instalar Nginx**:
```bash
sudo apt install nginx
```

2. **Configurar site**:
```bash
sudo nano /etc/nginx/sites-available/vanlink-pix
```

3. **Conteúdo da configuração**:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **Ativar site**:
```bash
sudo ln -s /etc/nginx/sites-available/vanlink-pix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
# Verificar se ambiente virtual está ativo
which python
# Deve mostrar: /caminho/para/venv/bin/python

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: "Permission denied" (Linux/Mac)
```bash
# Dar permissões aos certificados
chmod 600 certs/inter.key
chmod 644 certs/inter.crt
```

### Erro: "Port already in use"
```bash
# Verificar processos na porta 5000
lsof -i :5000

# Matar processo se necessário
kill -9 PID_DO_PROCESSO

# Ou usar porta diferente
export PORT=8000
python app.py
```

### Erro de Certificados SSL
```bash
# Verificar certificados
openssl x509 -in certs/inter.crt -text -noout
openssl rsa -in certs/inter.key -check
```

## 📱 Acesso Remoto

### Configurar Acesso na Rede Local

1. **Descobrir IP local**:
```bash
# Windows
ipconfig

# Linux/Mac
ip addr show
# ou
ifconfig
```

2. **Executar aplicação**:
```bash
python app.py
```

3. **Acessar de outros dispositivos**:
   - Use: `http://SEU_IP_LOCAL:5000`
   - Exemplo: `http://192.168.1.100:5000`

### Configurar Firewall (se necessário)

**Windows**:
- Painel de Controle → Sistema e Segurança → Firewall do Windows
- Permitir aplicativo → Adicionar Python

**Linux**:
```bash
sudo ufw allow 5000
```

## 🔄 Atualizações

Para atualizar o sistema:

1. **Backup dos dados**:
```bash
cp -r uploads uploads_backup
cp -r output output_backup
```

2. **Atualizar código**:
```bash
# Extrair nova versão
unzip vanlink_pix_system_v2.zip -d temp/
cp -r temp/vanlink_pix_app/* .
```

3. **Atualizar dependências**:
```bash
pip install -r requirements.txt --upgrade
```

4. **Reiniciar aplicação**:
```bash
python app.py
```

## 📞 Suporte

Em caso de problemas:

1. **Verificar logs**:
   - Logs aparecem no terminal onde executou `python app.py`

2. **Testar conectividade**:
   - Use a aba "Configurações" → "Testar Conexão"

3. **Verificar arquivos**:
   - Certificados em `certs/`
   - Configurações em `.env`
   - Uploads em `uploads/`

4. **Contato**:
   - Email: suporte@vanlink.com.br
   - Telefone: (11) 9999-9999

---

**VANLINK LTDA** - Suporte Técnico  
Atualizado em: Setembro 2024

