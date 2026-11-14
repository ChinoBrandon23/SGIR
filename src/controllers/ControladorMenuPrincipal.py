import os
import subprocess

from controllers.ControladorCompras import ControladorCompras
from controllers.ControladorInventario import ControladorInventario
from controllers.ControladorMenus import ControladorMenus
from controllers.ControladorMerma import ControladorMerma
from controllers.ControladorPlatillos import ControladorPlatillos
from controllers.ControladorRecetas import ControladorRecetas
from controllers.ControladorVentas import ControladorVentas
from views.VistaCompras import VistaCompras
from views.VistaInventario import VistaInventario
from views.VistaMenuPrincipal import VistaMenuPrincipal
from views.VistaMenus import VistaMenus
from views.VistaMerma import VistaMerma
from views.VistaPlatillos import VistaPlatillos
from views.VistaRecetas import VistaRecetas
from views.VistaVentas import VistaVentas


from daos.connection import DatabaseConnection
from daos.receta_dao import RecetaDAO
from daos.menu_dao import MenuDAO

from services.receta_servicio import RecetaServicio
from services.menu_servicio import MenuServicio

class ControladorMenuPrincipal:
    def __init__(self, vista: VistaMenuPrincipal, servicio=None):
        self.vista = vista
        self.servicio = servicio
        self.vista.input_menu.agregar_escuchante(self.evaluar_input_menu)

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
        ControladorRecetas(vista,servicio=receta_servicio)

    def abrir_vista_platillos(self):
        vista = VistaPlatillos(self.vista.console)

        vista.input_menu_platillos.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_platillo.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        ControladorPlatillos(vista)

    def abrir_vista_menus(self):
        vista = VistaMenus(self.vista.console)

        vista.input_menu_menus.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_menu.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        menu_dao = MenuDAO(DatabaseConnection)
        menu_servicio = MenuServicio(menu_dao)
        ControladorMenus(vista,menu_servicio)

    def abrir_vista_compras(self):
        vista = VistaCompras(self.vista.console)

        vista.input_menu_compras.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_compra.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        ControladorCompras(vista)

    def abrir_vista_inventario(self):
        vista = VistaInventario(self.vista.console)

        vista.input_menu_inventario.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_inventario.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        ControladorInventario(vista)

    def abrir_vista_merma(self):
        vista = VistaMerma(self.vista.console)

        vista.input_menu_merma.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar_merma.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        ControladorMerma(vista)

    def abrir_vista_ventas(self):
        vista = VistaVentas(self.vista.console)

        vista.input_menu_ventas.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_detalles.agregar_escuchante(self.evaluar_redirigir_menu_principal)
        vista.input_menu_editar.agregar_escuchante(self.evaluar_redirigir_menu_principal)

        ControladorVentas(vista)
