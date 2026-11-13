import shutil
import sys

from rich.console import Console
from views.VistaMenuPrincipal import VistaMenuPrincipal
from controllers.ControladorMenuPrincipal import ControladorMenuPrincipal

print('iniciando app...')


from daos.connection import DatabaseConnection
from daos.receta_dao import RecetaDAO
from daos.menu_dao import MenuDAO

from datetime import date

from services.receta_servicio import RecetaServicio
from services.menu_servicio import MenuServicio

def main():
    '''
    _width, _height = shutil.get_terminal_size()
    consola = Console()
    consola.size = (_width - 1, _height - 3)
    vista_principal = VistaMenuPrincipal(consola)
    ControladorMenuPrincipal(vista=vista_principal)
    '''
    testeando_crud_menus()

def testeando_crud_menus():
    connection:DatabaseConnection = DatabaseConnection()
    menu_dao = MenuDAO(connection)
    menu_servicio = MenuServicio(menu_dao=menu_dao)

    try: 
        respuesta = menu_servicio.obtener_menus_disponibles(date(2026,5,12))
        for menu in respuesta:
            print(f'Menu: {menu.nombre} | Cantidad Platillos: {menu_servicio.calcular_num_platillos(menu)}')
            for detalleMenu in menu.detalles:
                print(f'        Platillo: {detalleMenu.platillo.nombre} | Precio: {detalleMenu.precio}')
    except IndexError as ie:
        print(f'No hay menus disponible para la fecha. {ie}')
if __name__ == "__main__":
    main()