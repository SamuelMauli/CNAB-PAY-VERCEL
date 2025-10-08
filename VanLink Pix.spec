# -*- mode: python ; coding: utf-8 -*-

# Lista de arquivos e pastas a serem incluídos no executável
# Formato: ('caminho/no/seu/pc', 'caminho/dentro/do/executavel')
datas = [
    ('src/static', 'src/static'), # Adiciona a pasta de arquivos da interface
    ('certs', 'certs'),           # Adiciona a pasta dos certificados
    ('.env', '.')                 # Adiciona o arquivo de variáveis de ambiente
]

a = Analysis(
    ['run_server.py'],  # Ponto de entrada correto da aplicação
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'openpyxl', # Módulo que o PyInstaller pode não encontrar sozinho
        'dotenv'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VanLink Pix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # Mude para False quando tudo estiver funcionando para esconder a janela preta
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VanLink Pix',
)