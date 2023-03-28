from ui.uiElement import GlElement

class UiWrapper(GlElement):
    def __init__(self, window, constraints, dim=(0,0,0,0)):
        super().__init__(window, constraints, dim)
        self.type = 'wrapper'

    def reshape(self):
        return

    def absUpdate(self, delta):
        return

    def absRender(self):
        return
