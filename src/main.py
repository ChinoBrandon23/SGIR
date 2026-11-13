import shutil

from rich.console import Console

from views.VistaMenuPrincipal import VistaMenuPrincipal
from controllers.ControladorMenuPrincipal import ControladorMenuPrincipal

import sys
import mysql.connector
from PySide6.QtWidgets import QApplication
from daos.connection import DatabaseConnection
from daos.receta_dao import RecetaDAO
from models.receta import Receta
from models.ingrediente import Ingrediente
from services.receta_servicio import RecetaServicio

print('iniciando app...')

def main():


    _width, _height = shutil.get_terminal_size()

    consola = Console()
    consola.size = (_width - 1, _height - 3)

    vista_principal = VistaMenuPrincipal(consola)
    ControladorMenuPrincipal(vista=vista_principal)

if __name__ == "__main__":
    main()
