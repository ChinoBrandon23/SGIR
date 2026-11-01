'''from models.Insumo import Insumo

insumos = []

insumo1 = Insumo(1,'Aceite','30-12-2026',5,'litros',1,30.0,'2-10-2026')
insumos.append(insumo1)

for insumo in insumos:
    print(insumo.unidad_medida)
    print(insumo.fecha_caducidad)

'''
import shutil

from rich.console import Console

from views.VistaMenuPrincipal import VistaMenuPrincipal
from controllers.ControladorMenuPrincipal import ControladorMenuPrincipal

print('iniciando app...')

#dao's imports

# main.py
import sys
from PySide6.QtWidgets import QApplication

from daos.insumo_dao import InsumoDAO


def main():
    app = QApplication(sys.argv)
    
    #Capa de DAO
    db_connection = "Conexión MySQL"
    dao = InsumoDAO(db_connection)
    #
    # #Capa Servicios
    # service = InventarioServicio(dao)
    #
    # #Capa Vista
    # view = InventarioView()
    #
    # #Capa Controladora
    # controller = InventarioController(view, service)
    #
    # # Mostrar la aplicación
    # view.resize(400, 200)
    # view.show()
    # sys.exit(app.exec())

    _width, _height = shutil.get_terminal_size()

    consola = Console()
    consola.size = (_width - 1, _height - 3)

    vista_principal = VistaMenuPrincipal(consola)
    ControladorMenuPrincipal(vista=vista_principal)

if __name__ == "__main__":
    main()
