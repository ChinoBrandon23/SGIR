from rich.panel import Panel
from rich.layout import Layout

class VistaBase:
    def __init__(self):
        self.layout = Layout()
        self.titulo = "[bold yellow]Sistema de Gestión de Inventario para Restaurante[/bold yellow]"

        self.configurar_layout()

    def configurar_layout(self):
        self.layout.split_column(Layout(name="titulo"),
                            Layout(name="contenido"))

        self.layout["titulo"].size = 3

        self.layout["titulo"].update(Panel(self.titulo))