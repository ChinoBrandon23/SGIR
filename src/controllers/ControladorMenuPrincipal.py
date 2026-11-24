import os
import subprocess
from datetime import date, datetime

from Validaciones.validadorInventario import validadorInventario
from Validaciones.validadorMerma import validadorMerma
from Validaciones.validadorVentas import ValidadorVentas
from controllers.ControladorCompras import ControladorCompras
from controllers.ControladorInventario import ControladorInventario
from controllers.ControladorMenus import ControladorMenus
from controllers.ControladorMerma import ControladorMerma
from controllers.ControladorPlatillos import ControladorPlatillos
from controllers.ControladorRecetas import ControladorRecetas
from controllers.ControladorVentas import ControladorVentas
from daos.platillos_dao import PlatillosDAO
from services.merma_servicio import MermaServicio
#from daos.venta_dao import VentaDAO
from services.platillos_servicio import PlatillosServicio
#from services.venta_servicio import VentaServicio
from daos.venta_dao import VentaDAO
from services.venta_servicio import VentaServicio
from views.VistaCompras import VistaCompras
from views.VistaInventario import VistaInventario
from views.VistaMenuPrincipal import VistaMenuPrincipal
from views.VistaMenus import VistaMenus
from views.VistaMerma import VistaMerma
from views.VistaPlatillos import VistaPlatillos
from views.VistaRecetas import VistaRecetas
from views.VistaVentas import VistaVentas
from Validaciones.validadorReceta import validadorReceta
from Validaciones.validadorPlatillos import validadorPlatillos
from Validaciones.validadorMenus import validadorMenu
from Validaciones.validadorCompras import validadorCompras

from daos.connection import DatabaseConnection
from daos.receta_dao import RecetaDAO
from daos.menu_dao import MenuDAO
from daos.insumo_dao import InsumoDAO
from daos.compra_dao import CompraDAO
from daos.merma_dao import MermaDAO

from services.receta_servicio import RecetaServicio
from services.menu_servicio import MenuServicio
from services.inventario_servicio import InventarioServicio
from services.compras_servicio import CompraServicio

class ControladorMenuPrincipal:
    def __init__(self, vista: VistaMenuPrincipal, servicio=None):
        self.vista = vista
        self.servicio = servicio
        self.vista.input_menu.agregar_escuchante(self.evaluar_input_menu)
        self.db = DatabaseConnection()

        self.abrir_menu_principal()

    def evaluar_input_menu(self, seleccion):
        match seleccion:
            case "1":
                self.abrir_vista_receta()
            case "2":
                self.abrir_vista_platillos()
            case "3":
                self.abrir_vista_menus()
            case "4":
                self.abrir_vista_compras()
            case "5":
                self.abrir_vista_inventario()
            case "6":
                self.abrir_vista_merma()
            case "7":
                self.abrir_vista_ventas()
            case "8":
                try:
                    subprocess.run('cls' if os.name == 'nt' else 'clear')
                except FileNotFoundError:
                    print(chr(27) + "[2J")
                finally:
                    os._exit(0)

    def evaluar_redirigir_menu_principal(self, seleccion:str):
        if seleccion == "m" or seleccion == "M":
            self.abrir_menu_principal()

    def abrir_menu_principal(self):
        self.vista.mostrar_layout()
        self.vista.mostrar_prompt_menu()

    def abrir_vista_receta(self):
        vista = VistaRecetas(self.vista.console)

        vista.input_menu_recetas.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_receta.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        receta_dao = RecetaDAO(DatabaseConnection)
        receta_servicio = RecetaServicio(receta_dao=receta_dao)
        validador_receta = validadorReceta()

        ControladorRecetas(vista, servicio_receta=receta_servicio, validador=validador_receta)

    def abrir_vista_platillos(self):
        vista = VistaPlatillos(self.vista.console)

        vista.input_menu_platillos.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_platillo.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        receta_dao = RecetaDAO(DatabaseConnection)
        receta_servicio = RecetaServicio(receta_dao=receta_dao)

        menu_dao = PlatillosDAO(DatabaseConnection)
        platillos_servicio = PlatillosServicio(platillos_dao=menu_dao, receta_dao=receta_dao, insumo_dao=InsumoDAO(DatabaseConnection))
        platillo_validador = validadorPlatillos()

        ControladorPlatillos(vista, servicio_recetas=receta_servicio, servicio_platillos=platillos_servicio, validador=platillo_validador)

    def abrir_vista_menus(self):
        vista = VistaMenus(self.vista.console)

        vista.input_menu_menus.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_menu.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        validador_menu = validadorMenu()
        menu_dao = MenuDAO(DatabaseConnection)
        menu_servicio = MenuServicio(menu_dao)
        ControladorMenus(vista,menu_servicio, validador_menu)

    @staticmethod
    def _formatear_fecha(fecha: str | date | datetime) -> str:
        if isinstance(fecha, (date, datetime)):
            return fecha.strftime("%Y-%m-%d")

        fecha_limpia = fecha.strip()
        for formato in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(fecha_limpia, formato).strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError(
            f"Formato de fecha no válido: {fecha!r}. Use DD-MM-AAAA o AAAA-MM-DD."
        )

    def abrir_vista_compras(self):
    
        vista = VistaCompras(self.vista.console)

        vista.input_menu_compras.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_compra.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        compra_servicio = CompraServicio(compra_dao=CompraDAO(DatabaseConnection),insumo_dao=InsumoDAO(DatabaseConnection))
        inventario_servicio = InventarioServicio(insumo_dao=InsumoDAO(DatabaseConnection),compra_dao=CompraDAO(DatabaseConnection))
        validador_compras = validadorCompras()

        ControladorCompras(vista,compra_servicio=compra_servicio,inventario_servicio=inventario_servicio, validador=validador_compras)

    def abrir_vista_inventario(self):
        vista = VistaInventario(self.vista.console)

        vista.input_menu_inventario.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_inventario.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        insumo_dao = InsumoDAO(self.db)
        compra_dao = CompraDAO(self.db)
        inventario_servicio = InventarioServicio(insumo_dao=insumo_dao, compra_dao=compra_dao)
        validador_inventario = validadorInventario()

        ControladorInventario(vista, inventario_servicio, validador_inventario)

    def abrir_vista_merma(self):
        vista = VistaMerma(self.vista.console)

        vista.input_menu_merma.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_merma.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        dao_merma = MermaDAO(self.db)
        dao_insumo = InsumoDAO(self.db)
        compra_dao = CompraDAO(self.db)

        servicio_merma = MermaServicio(dao_merma, dao_insumo)
        validador = validadorMerma()
        receta_dao = RecetaDAO(DatabaseConnection)
        platillo_dao = PlatillosDAO(DatabaseConnection)
        insumo_dao = InsumoDAO(self.db)
        servicio_platillos = PlatillosServicio(platillo_dao, receta_dao, insumo_dao)

        servicio_insumo = InventarioServicio(dao_insumo, compra_dao)

        ControladorMerma(vista, servicio_merma, servicio_platillos, servicio_insumo, validador)

    def abrir_vista_ventas(self):
        vista = VistaVentas(self.vista.console)

        vista.input_menu_ventas.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        dao_venta = VentaDAO(self.db)
        insumo_dao = InsumoDAO(self.db)
        receta_dao = RecetaDAO(DatabaseConnection)
        platillo_dao = PlatillosDAO(DatabaseConnection)
        servicio_venta = VentaServicio(dao_venta, insumo_dao, receta_dao, platillo_dao)

        validador_ventas = ValidadorVentas()

        ControladorVentas(vista=vista, servicio=servicio_venta, validador=validador_ventas)
