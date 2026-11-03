import shutil


from daos.fake_insumo_dao import FakeInsumoDAO
from daos.fake_receta_dao import FakeRecetaDAO
from services.inventario_servicio import InventarioServicio
from controllers.inventario_controller import InventarioController

from rich.console import Console

from views.VistaMenuPrincipal import VistaMenuPrincipal
from controllers.ControladorMenuPrincipal import ControladorMenuPrincipal


def main():

    insumo_dao = FakeInsumoDAO()
    receta_dao = FakeRecetaDAO()
    inventario_service = InventarioServicio(insumo_dao=insumo_dao,receta_dao=receta_dao)
    inventario_controller = InventarioController(inventario_service=inventario_service)


    #print(inventario_service.get_insumo(2).nombre,': ',inventario_service.evaluar_stock_insumo(2))
    #print('Stock: ', inventario_service.get_insumo(2).stock, 'Umbral: ', inventario_service.get_insumo(2).umbral)
    #print(inventario_service.abastecer_insumo(2,10))
    #print(inventario_service.usar_insumo(2,3))
    #print('......')
    #print('Stock: ', inventario_service.get_insumo(2).stock, ': ',inventario_service.evaluar_stock_insumo(2))

    import utils.datos_simulados
    ingrediente = inventario_service.get_ingrediente(8)
    print(ingrediente.receta)

    for ingrediente_receta in ingrediente.receta.lista_ingredientes:
        print(ingrediente_receta.ingrediente.nombre)

    print('-----------------')

    for insumo in inventario_service.get_todos_los_insumos():
        print(f'Insumo: {insumo.nombre} | Stock: {insumo.stock} {insumo.unidad_medida}')
    inventario_service.preparar_receta(1)

    print('Haciendo...')
    for insumo in inventario_service.get_todos_los_insumos():
            print(f'Insumo: {insumo.nombre} | Stock: {insumo.stock} {insumo.unidad_medida}')


    #print(inventario_service.get_insumo(2).nombre,': ',inventario_service.evaluar_stock_insumo(2))
    #print('Stock: ', inventario_service.get_insumo(2).stock, 'Umbral: ', inventario_service.get_insumo(2).umbral)
    #print(inventario_service.abastecer_insumo(2,10))
    #print(inventario_service.usar_insumo(2,3))
    #print('......')
    #print('Stock: ', inventario_service.get_insumo(2).stock, ': ',inventario_service.evaluar_stock_insumo(2))
    

    #for receta in utils.datos_simulados.generar_recetas():
    #    if receta.num == 3:
    #        for ingrediente_receta in receta.lista_ingredientes:
    #            print(ingrediente_receta.ingrediente.nombre)
    

if __name__ == "__main__":
    main()


