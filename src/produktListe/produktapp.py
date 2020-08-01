
from typing import Dict, Optional, Tuple, Union

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

        self.display_settings.btn_height = BUTTON_HEIGHT
        self.display_settings.btn_width = BUTTON_WIDTH
        self.display_settings.font_size = FONT_SIZE
        self.display_settings.wx_font = wx.Font(self.display_settings.font_size, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.display_settings.off_set = OFFSET
        self._products_file = PRODUCTS_FILE

        self.shown_columns = [{'column': 'nr', 'text': '#', 'width': 50},
                              {'column': 'code', 'text': 'code', 'width': 250},
                              {'column': 'desc', 'text': 'description', 'width': 250},
                              {'column': 'price', 'text': 'price', 'width': 70}]

        self.list_frame = None

    def run(self) -> None:
        """
        Implementation of the abstract run method

        :return:
        """
        self.show_list_frame()
        self.app.MainLoop()

    @property
    def products_file(self) -> str:
        """
        Implementation of the abstract property to return the products file

        :return:
        """
        return self._products_file

    def show_edit_frame(self, number: int, old_values: Optional[Tuple[str, str, str]] = None) -> None:
        """
        Show the edit frame
        Mode: 'add' for old_values = None, 'edit' otherwise

        :param number: product number
        :param old_values: tuple with old code, desc, price of the item
        :return:
        """
        src.produktListe.editframe.EditFrame(self, number=number, old_values=old_values)

    def show_list_frame(self) -> None:
        """
        Show the list frame

        :return:
        """
        self.list_frame = src.produktListe.listframe.ListFrame(self, columns=self.shown_columns)

    def update_product_listctrl(self) -> None:
        """
        Update the products ListCtrl on ListFrame

        :return:
        """
        columns = [entry['column'] for entry in self.shown_columns]
        self.list_frame.update_prod_list(products_df=self.file_contents.products[columns])

    def get_new_number(self) -> int:
        """
        Get a product number for a new item

        :return: product number
        """
        if self.file_contents.products is None:
            return 1
        number = self.file_contents.products['nr'].max() + 1
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
        if self.file_contents.products is None:
            return True
        # look up the code
        prd_code = self.file_contents.products[self.file_contents.products['code'] == code]
        if prd_code.empty and mode == 'add':
            # new code, add mode
            return True
        if (not prd_code[prd_code['nr'] == number].empty) and mode == 'edit':
            # old code, edit mode
            return True
        return False

    def add_item(self, values: Dict[str, Union[str, int]]) -> bool:
        """
        Add item to the products dataframe, input sanity is checked by create_new_product()

        :param values: dict with nr, code, desc, price
        :return: True: item successfully created, False: an exception occurred (error dialog by create_new_product())
        """
        new_item_df = self.create_new_product(values=values)
        if new_item_df is None:
            return False
        if self.file_contents.products is None:
            self.file_contents.products = new_item_df
        else:
            self.file_contents.products = pd.concat([self.file_contents.products, new_item_df])
        return True

    def edit_item(self, values: Dict[str, Union[str, int]]) -> bool:
        """
        Edit item in the products dataframe

        :param values: dict with nr, code, desc, price
        :return: True: item successfully edited, False: an exception occurred (error dialog by create_new_product())
        """
        new_item_df = self.create_new_product(values=values)
        if new_item_df is None:
            return False
        self.file_contents.products = self.file_contents.products[self.file_contents.products['nr'] != values['nr']]

        self.file_contents.products = pd.concat([self.file_contents.products, new_item_df])
        self.file_contents.products = self.file_contents.products.sort_values(by='nr')
        self.file_contents.products = self.file_contents.products.reset_index(drop=True)
        return True

    def delete_item(self, values: Dict[str, int]) -> None:
        """
        Delete item in the products dataframe

        :param values: dict with nr as product number
        :return:
        """
        self.file_contents.products = self.file_contents.products[self.file_contents.products['nr'] != values['nr']]
        self.file_contents.products = self.file_contents.products.reset_index(drop=True)
        for index in range(values['nr'], len(self.file_contents.products) + 1):
            self.file_contents.products.at[index - 1, 'nr'] = index

    def save_products(self) -> None:
        """
        Wrapper for inherited _save_products() method

        :return:
        """
        self.file_contents.products.sort_values(by='nr', inplace=True)
        self._save_products()
