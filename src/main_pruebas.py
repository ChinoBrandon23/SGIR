import shutil
import sys

from rich.console import Console
from views.VistaMenuPrincipal import VistaMenuPrincipal
from controllers.ControladorMenuPrincipal import ControladorMenuPrincipal

print('iniciando app...')


from daos.connection import DatabaseConnection
from daos.receta_dao import RecetaDAO
from daos.menu_dao import MenuDAO
from daos.insumo_dao import InsumoDAO

from datetime import date

from services.receta_servicio import RecetaServicio
from services.menu_servicio import MenuServicio
from services.insumo_servicio import InsumoServicio

def main():
    '''
    _width, _height = shutil.get_terminal_size()
    consola = Console()
    consola.size = (_width - 1, _height - 3)
    vista_principal = VistaMenuPrincipal(consola)
    ControladorMenuPrincipal(vista=vista_principal)
    '''
    #testeando_crud_menus()
    testeando_crud_insumos()

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

def testeando_crud_insumos():
    connection:DatabaseConnection = DatabaseConnection()
    insumo_dao = InsumoDAO(connection)
    insumo_servicio = InsumoServicio(insumo_dao=insumo_dao)

    for compra in insumo_servicio.obtener_insumos():
        print(f'Compra: {compra.num} - Fecha Compra: {compra.fecha_creacion}')
        for detalle in compra.lista_compras:
            print(f'    - Insumo: {detalle.insumo.nombre} - Stock: {detalle.insumo.stock} {detalle.unidad_medida} Caducidad: {detalle.fecha_caducidad} Marca: {detalle.insumo.marca.nombre}') # type: ignore
            print()


if __name__ == "__main__":
    main()