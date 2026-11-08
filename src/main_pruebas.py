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

from daos.connection import DatabaseConnection
from daos.receta_dao import RecetaDAO

from services.receta_servicio import RecetaServicio

def main():

    '''
    receta_dao = RecetaDAO(DatabaseConnection)
    receta_servicio = RecetaServicio(receta_dao=receta_dao)

    respuesta = receta_dao.obtener_ingredientes_receta(5)

    from models.receta import Receta
    from models.ingrediente import Ingrediente

    #receta:Receta
    #for receta in respuesta:
    #    print(f'{receta.num} | {receta.nombre} | {receta.num_porciones}')
    #    print('---Instrucciones--')
    #    print(receta.instrucciones)
    #    print('')'''
    

    _width, _height = shutil.get_terminal_size()

    consola = Console()
    consola.size = (_width - 1, _height - 3)

    vista_principal = VistaMenuPrincipal(consola)
    ControladorMenuPrincipal(vista=vista_principal)

if __name__ == "__main__":
    main()
