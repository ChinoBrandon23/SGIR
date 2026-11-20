import os
import shutil
import sys
import time

from rich.console import Console
from rich.panel import Panel
from daos.connection import DatabaseConnection
from views.VistaMenuPrincipal import VistaMenuPrincipal
from controllers.ControladorMenuPrincipal import ControladorMenuPrincipal


def verificar_conexion_bd(consola: Console) -> bool:
    """Verifica que el servidor de base de datos este disponible antes de iniciar el sistema."""
    with consola.status("[bold yellow]Comprobando conexión con la base de datos...[/bold yellow]", spinner="dots"):
        time.sleep(0.3)  # breve pausa visual
        try:
            conexion = DatabaseConnection.get_connection()
            if conexion.is_connected():
                conexion.close()
                return True
            return False
        except Exception as e:
            consola.print(Panel(
                f"[bold red]Error fatal: No se pudo conectar a la base de datos.[/bold red]\n\n"
                f"[white]Detalle del error:[/white] {e}\n\n"
                f"[yellow]Sugerencias de solución:[/yellow]\n"
                f" 1. Verifica que tu servidor MySQL esté activo (XAMPP, LAMP o systemctl).\n"
                f" 2. Revisa las variables de entorno o DB_CONFIG en [italic]daos/connection.py[/italic].\n"
                f" 3. Comprueba el usuario, contraseña y nombre de la base de datos.",
                title="[bold red]Fallo de Conexión[/bold red]",
                border_style="red"
            ))
            return False

def main():
    _width, _height = shutil.get_terminal_size()
    consola = Console()
    consola.size = (_width - 1, _height - 3)

    # validar conexcion con la BD
    if not verificar_conexion_bd(consola):
        sys.exit(1)

    vista_principal = VistaMenuPrincipal(consola)
    ControladorMenuPrincipal(vista=vista_principal)

if __name__ == "__main__":
    #try:
        main()
    #except Exception as err:
    #    print(f"\n[bold red]Error inesperado no controlado:[/bold red] {err}")
    #    sys.exit(1)
