
from typing import Optional, Tuple

import pandas as pd
import wx

import src.app
import src.produktListe.editframe
import src.produktListe.listframe

PRODUCTS_FILE = 'produkt.txt'
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 150
FONT_SIZE = 14
OFFSET = 5


class ProduktApp(src.app.App):
    """
    App for the creation and editing of a product list
    """

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
        """
        Implementation of the abstract run method

        :return:
        """
        self.show_list_frame()
        self.app.MainLoop()

    @property
    def productsFile(self):
        """
        Implementation of the abstract property to return the products file

        :return:
        """
        return self._productsFile

    def show_edit_frame(self, number: int, old_values: Optional[Tuple[str, str, str]] = None) -> None:
        """
        Show the edit frame
        If old_values is None

        :param number: product number
        :param old_values: tuple with old code, desc, price of the item
        :return:
        """
        src.produktListe.editframe.EditFrame(self, number=number, old_values=old_values)

    def show_list_frame(self) -> None:
        self.listFrame = src.produktListe.listframe.ListFrame(self)

    def update_product_listctrl(self) -> None:
        """
        Update the products ListCtrl on ListFrame

        :return:
        """
        self.listFrame.update_prodList()

    def get_new_number(self) -> int:
        """
        Get a product number for a new item

        :return: product number
        """
        if self.fileContents.products is None:
            return 1
        number = self.fileContents.products['nr'].max() + 1
        return number

    def check_item(self, number: int, code: str, mode: str) -> bool:
        """
        Check if the entered code is already in the product list

        :param number: product number of the item
        :param code: entered barcode of the item
        :param mode: process mode 'add' or 'edit'
        :return: True: code is unique, False: already existent code
        """
        # check if there are already entries
        if self.fileContents.products is None:
            return True
        # look up the code
        prd_code = self.fileContents.products[self.fileContents.products['code'] == code]
        if prd_code.empty and mode == 'add':
            # new code, add mode
            return True
        else:
            if (not prd_code[prd_code['nr'] == number].empty) and mode == 'edit':
                # old code, edit mode
                return True
        return False

    def add_item(self, number: int, code: str, desc: str, price: str) -> None:
        """
        Add item to the products dataframe

        :param number: product number
        :param code: product code
        :param desc: product description
        :param price: product price
        :return:
        """
        new_item = pd.DataFrame([[number, code, desc, price, 0]], columns=['nr', 'code', 'desc', 'price', 'stock'])
        if self.fileContents.products is None:
            self.fileContents.products = new_item
        else:
            self.fileContents.products = pd.concat([self.fileContents.products, new_item])

    def edit_item(self, number: int, code: str, desc: str, price: str) -> None:
        """
        Edit item in the products dataframe

        :param number: product number
        :param code: product code
        :param desc: product description
        :param price: product price
        :return:
        """
        self.fileContents.products.loc[self.fileContents.products['nr'] == number, 'code'] = code
        self.fileContents.products.loc[self.fileContents.products['nr'] == number, 'desc'] = desc
        self.fileContents.products.loc[self.fileContents.products['nr'] == number, 'price'] = price

    def delete_item(self, number: int) -> None:
        """
        Delete item in the products dataframe

        :param number: product number
        :return:
        """
        self.fileContents.products = self.fileContents.products[self.fileContents.products['nr'] != number]
        self.fileContents.products = self.fileContents.products.reset_index(drop=True)
        for index in range(number, len(self.fileContents.products) + 1):
            self.fileContents.products.at[index-1, 'nr'] = index

    def save_products(self) -> None:
        """
        Wrapper for inherited _save_products() method

        :return:
        """
        self.fileContents.products.sort_values(by='nr', inplace=True)
        self._save_products()
