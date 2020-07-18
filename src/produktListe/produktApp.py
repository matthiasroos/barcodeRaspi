
from typing import Dict, Optional, Tuple

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

        self.shown_columns = [{'column': 'nr', 'text': '#', 'width': 50},
                              {'column': 'code', 'text': 'code', 'width': 250},
                              {'column': 'desc', 'text': 'description', 'width': 250},
                              {'column': 'price', 'text': 'price', 'width': 70}]

        self.listFrame = None

    def run(self) -> None:
        """
        Implementation of the abstract run method

        :return:
        """
        self.show_list_frame()
        self.app.MainLoop()

    @property
    def productsFile(self) -> str:
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
        self.listFrame = src.produktListe.listframe.ListFrame(self, columns=self.shown_columns)

    def update_product_listctrl(self) -> None:
        """
        Update the products ListCtrl on ListFrame

        :return:
        """
        columns = [entry['column'] for entry in self.shown_columns]
        self.listFrame.update_prodList(products_df=self.fileContents.products[columns])

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

    def add_item(self, values: Dict[str, str]) -> bool:
        """
        Add item to the products dataframe

        :param values: number, code, desc, price
        :return: True: item successfully created, False: an exception occurred
                                                            (error dialog shown by create_new_product()
        """
        new_item_df = self.create_new_product(values=values)
        if new_item_df is None:
            return False
        if self.fileContents.products is None:
            self.fileContents.products = new_item_df
        else:
            self.fileContents.products = pd.concat([self.fileContents.products, new_item_df])
        return True

    def edit_item(self, values: Dict[str, str]) -> bool:
        """
        Edit item in the products dataframe

        :param values: number, code, desc, price
        :return:
        # TODO Bug: no type checking is done here
        """
        for key, value in values.items():
            if key != 'nr':
                self.fileContents.products.loc[self.fileContents.products['nr'] == values['nr'], key] = value
        return True

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
