# src/utils.py
import sys
import os

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando em dev e no PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Se não estiver rodando via PyInstaller, usa o caminho do arquivo principal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)