from abc import ABC, ABCMeta

import wx

import src.app
import src.produktListe.editframe
import src.produktListe.listframe

PRODUCTS_FILE = 'produkt.txt'
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 150
FONT_SIZE = 14
OFFSET = 5


class ProduktApp(src.app.App, metaclass=ABCMeta):

    def __init__(self):
        super().__init__()

        self.displaySettings.btnHeight = BUTTON_HEIGHT
        self.displaySettings.btnWidth = BUTTON_WIDTH
        self.displaySettings.fontSize = FONT_SIZE
        self.displaySettings.wxFont = wx.Font(self.displaySettings.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.displaySettings.offSet = OFFSET
        self._productsFile = PRODUCTS_FILE

    def run(self) -> None:
        self.show_list_frame()
        self.app.MainLoop()

    @property
    def productsFile(self):
        return self._productsFile

    def show_edit_frame(self) -> None:
        src.produktListe.editframe.EditFrame(self)

    def show_list_frame(self) -> None:
        src.produktListe.listframe.ListFrame(self)

