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
from daos.compra_dao import CompraDAO

from datetime import date

from services.receta_servicio import RecetaServicio
from services.menu_servicio import MenuServicio
from services.inventario_servicio import InventarioServicio
from services.compras_servicio import CompraServicio


from models.insumo import Insumo
from models.insumo import TipoInsumo
from models.insumo import Marca
from models.compra import Compra, DetalleCompra
from models.proveedor import Proveedor

def main():
    '''
    _width, _height = shutil.get_terminal_size()
    consola = Console()
    consola.size = (_width - 1, _height - 3)
    vista_principal = VistaMenuPrincipal(consola)
    ControladorMenuPrincipal(vista=vista_principal)
    '''
    #testeando_crud_menus()
    #testeando_crud_insumos()
    testeando_crud_compras()

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
    compra_dao = CompraDAO(connection)
    inventario_servicio = InventarioServicio(insumo_dao=insumo_dao,compra_dao=compra_dao)
    compras_servicio = CompraServicio(compra_dao=compra_dao,insumo_dao=insumo_dao)

    for compra in inventario_servicio.obtener_compras():
        print(f'Compra: {compra.num} - Fecha Compra: {compra.fecha_creacion}')
        for detalle in compra.lista_compras:
            print(f'    - Insumo: {detalle.insumo.nombre} - Stock: {detalle.insumo.stock} {detalle.unidad_medida} Caducidad: {detalle.fecha_caducidad} Marca: {detalle.insumo.marca.nombre}') # type: ignore
            print()

    print('---------ACTUALIZAR INSUMO')
    inventario_servicio.actualizar_insumo(Insumo(15,'Queso Mozzarella',5,12,TipoInsumo('LAC',''),Marca(0,'')))

    print('-----------')
    for insumo in inventario_servicio.obtener_insumos():
        print(f'Insumo: {insumo.nombre} Stock: {insumo.stock}')

    print('------------Tipos insumo------------')
    for ti in inventario_servicio.obtener_tipos_insumo():
        print(f'{ti.clave}-{ti.nombre}')

    print('------------Marcas------------')
    for m in inventario_servicio.obtener_marcas():
        print(f'{m.num}-{m.nombre}')
    print('------------Proveedores------------')
    for m in compra_dao.obtener_proveedores():
        print(f'{m.num}-{m.nombre}')

def testeando_crud_compras():
    compra_dao = CompraDAO(DatabaseConnection())
    insumo_dao = InsumoDAO(DatabaseConnection())

    compra_servicio = CompraServicio(compra_dao=compra_dao,insumo_dao=insumo_dao)
    proveedores = compra_servicio.obtener_proovedores()

    for proveedor in proveedores:
        print(proveedor.num,' ',proveedor.nombre)

    print('------------------------------')
    compra = Compra(0,str('11-12-2026'),0,Proveedor(10,''))
    #compra = compra_servicio.obtener_compra_por_numero(1)
    compra.agregar_insumo_compra(
        insumo=compra_servicio.obtener_insumo_por_nombre('Tomate Roma'),
        fecha_compra='20-11-2026',
        cantidad_comprada=10,
        cantidad_actual=0,
        unidad_medida='kg',
        importe=0,
        monto_unitario=10,
        fecha_caducidad='12-12-2026',
        )
    #compra_servicio.registrar_compra(compra_nueva=compra)

    #compra_servicio.registrar_compra(compra_nueva=compra)
    #compra.agregar_insumo_compra(compra_servicio.obtener_insumo_por_nombre('Cilantro Fresco'),2.5,0,'kg',0,40,'2-2-2027','19-11-2026')
    #compra.agregar_insumo_compra(compra_servicio.obtener_insumo_por_nombre('Tortillas de Maíz'),10,0,'kg',0,40,'1-12-2026','19-11-2026')

    #compra_servicio.actualizar_compra(compra_act=compra)

if __name__ == "__main__":
    main()


