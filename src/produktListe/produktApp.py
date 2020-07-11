
import wx
from typing import Optional, Tuple

import pandas as pd

import src.app
import src.produktListe.editframe
import src.produktListe.listframe

PRODUCTS_FILE = 'produkt.txt'
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 150
FONT_SIZE = 14
OFFSET = 5


class ProduktApp(src.app.App):

    def __init__(self):
        super().__init__()

        self.displaySettings.btnHeight = BUTTON_HEIGHT
        self.displaySettings.btnWidth = BUTTON_WIDTH
        self.displaySettings.fontSize = FONT_SIZE
        self.displaySettings.wxFont = wx.Font(self.displaySettings.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.displaySettings.offSet = OFFSET
        self._productsFile = PRODUCTS_FILE

        self.listFrame = None

    def run(self) -> None:
        self.show_list_frame()
        self.app.MainLoop()

    @property
    def productsFile(self):
        return self._productsFile

    def show_edit_frame(self, number: int, old_values: Optional[Tuple[str, str, str]] = None) -> None:
        src.produktListe.editframe.EditFrame(self, number=number, old_values=old_values)

    def show_list_frame(self) -> None:
        self.listFrame = src.produktListe.listframe.ListFrame(self)

    def check_item(self, number: int, code: str, mode: str) -> bool:
        prd_code = self.fileContents.products[self.fileContents.products['code'] == code]
        if prd_code.empty and mode == 'add':
            # new code, add mode
            return True
        else:
            if (not prd_code[prd_code['nr'] == number].empty) and mode == 'edit':
                # old code, edit mode
                return True
        return False

    def add_item(self, number: int, code: str, desc: str, price: str):
        new_item = pd.DataFrame([[number, code, desc, price, 0]], columns=['nr', 'code', 'desc', 'price', 'stock'])
        self.fileContents.products = pd.concat([self.fileContents.products, new_item])
        self.listFrame.update_prodList()

    def edit_item(self, number: int, code: str, desc: str, price: str):
        self.fileContents.products.loc[self.fileContents.products['nr'] == number, 'code'] = code
        self.fileContents.products.loc[self.fileContents.products['nr'] == number, 'desc'] = desc
        self.fileContents.products.loc[self.fileContents.products['nr'] == number, 'price'] = price
        self.listFrame.update_prodList()

    def delete_item(self, product_nr: int):
        self.fileContents.products = self.fileContents.products[self.fileContents.products['nr'] != product_nr]
        self.fileContents.products = self.fileContents.products.reset_index(drop=True)
        for index in range(product_nr, len(self.fileContents.products)+1):
            self.fileContents.products.at[index-1, 'nr'] = index

    def save_products(self):
        self.fileContents.products.sort_values(by='nr', inplace=True)
        self._save_products()

