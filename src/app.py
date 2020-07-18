
import abc
import dataclasses
import os
import sys
from typing import Dict, List, Optional

import pandas as pd
import wx

import functions


@dataclasses.dataclass()
class FileContents:
    products: pd.DataFrame = None
    purchases: pd.DataFrame = None
    users: pd.DataFrame = None


@dataclasses.dataclass()
class DisplaySettings:
    btnHeight: int = None
    btnWidth: int = None
    fontSize: int = None
    offSet: int = None
    wxFont: wx.Font = None
    screen_width: int = None
    screen_height: int = None


class App:

    def __init__(self):
        self.displaySettings = DisplaySettings()
        self.fileContents = FileContents()
        self._productsFile: Optional[str] = None
        self.product_columns = ['nr', 'code', 'desc', 'price', 'stock']
        self.product_columns_type = {'nr': int, 'code': str, 'desc': str, 'price': float, 'stock': int}

        self.app = wx.App(False)
        if 'BARCODE_DEV' in os.environ:
            self.displaySettings.screen_width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X) / 2
        else:
            self.displaySettings.screen_width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self.displaySettings.screen_height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

    # The magic methods __enter__ and __exit__ are necessary for using the class in context managers
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    @abc.abstractmethod
    def run(self) -> None:
        """
        Abstract method to run the app (load data if necessary, show the first frame and start the main loop)

        :return:
        """
        pass

    @staticmethod
    def exit() -> None:
        sys.exit()

    @staticmethod
    def restart() -> None:
        os.execl(sys.executable, sys.executable, *sys.argv)
        sys.exit()

    # dialogs
    @staticmethod
    def show_error_dialog(error_message: str) -> None:
        dlg = wx.MessageDialog(None, message=error_message, caption='ERROR',
                               style=wx.OK | wx.ICON_WARNING | wx.STAY_ON_TOP)
        # dlg.SetFont(self.displaySettings.wxFont)
        dlg.ShowModal()

    @staticmethod
    def show_info_dialog(info_message: str) -> None:
        dlg = wx.MessageDialog(None, message=info_message, caption='INFO',
                               style=wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
        # dlg.SetFont(self.displaySettings.wxFont)
        dlg.ShowModal()

    @staticmethod
    def show_confirm_dialog(confirm_message: str) -> bool:
        dlg = wx.MessageDialog(None, message=confirm_message, caption='CONFIRM',
                               style=wx.OK | wx.CANCEL | wx.ICON_QUESTION | wx.STAY_ON_TOP)
        # dlg.SetFont(self.displaySettings.wxFont)
        choice = dlg.ShowModal()
        if choice == wx.ID_OK:
            return True
        else:
            return False

    @staticmethod
    def show_password_dialog(password_message: str) -> bool:
        dlg = wx.PasswordEntryDialog(parent=None, message=password_message,
                                     defaultValue='', style=wx.OK | wx.CANCEL)
        # dlg.SetFont(self.displaySettings.wxFont)
        dlg.ShowModal()
        if dlg.GetValue() == os.getenv('ADMIN_PASSWORD'):
            return True
        return False

    # handling of products
    @property
    @abc.abstractmethod
    def productsFile(self) -> str:
        """
        Abstract property to return the products file
        """
        raise NotImplementedError

    @productsFile.setter
    def productsFile(self, value) -> None:
        self._productsFile = value

    def load_products(self) -> None:
        self.fileContents.products = functions.read_csv_file(file=self.productsFile,
                                                             columns=self.product_columns,
                                                             column_types=self.product_columns_type)

    def create_new_product(self, values: Dict[str, str]) -> Optional[pd.DataFrame]:
        """

        :param number: product number of the new product
        :param values: code, desc, price, stock
        :return: dataframe containing the new product
        """
        new_item_list = [values[column] if values.get(column) else 0 for column in self.product_columns]
        new_item_df = pd.DataFrame([new_item_list], columns=self.product_columns)
        try:
            new_item_df = functions.format_dataframe(data_df=new_item_df, types=self.product_columns_type)
        except ValueError as exc:
            self.show_error_dialog(error_message=f'Error: {str(exc)}')
            return None
        return new_item_df

    def _save_products(self) -> None:
        functions.write_csv_file(file=self.productsFile, df=self.fileContents.products)
