from rich.prompt import Prompt

class InputEmisor:
    def __init__(self):
        super().__init__()
        self.user_input = None
        self.listeners = []

    def agregar_escuchante(self, listener):
        self.listeners.append(listener)

    def remover_escuchante(self, listener):
        self.listeners.remove(listener)

    def notificar(self):
        for listener in self.listeners:
            listener(self.user_input)

    def imprimir(self, prompt: str, choices=None, show_choices=False, default=None):
        self.user_input = Prompt.ask(prompt, choices=choices, show_choices=show_choices, default=default, case_sensitive=False)
        self.notificar()
