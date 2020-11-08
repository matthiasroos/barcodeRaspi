"""
Module containing the abstract base class for an app
"""
import abc
import dataclasses
import logging
import os
import sys
from typing import Dict, List, Optional

import pandas as pd
import wx

import functions


@dataclasses.dataclass()
class FileContents:
    """
    DataClass containing the contents of files
    """
    products: pd.DataFrame = None
    purchases: pd.DataFrame = None
    users: List[str] = None


@dataclasses.dataclass()
class DisplaySettings:
    """
    DataClass containing all display related settings
    """
    btn_height: int = 0
    btn_width: int = 0
    font_size: int = 0
    off_set: int = 0
    wx_font: wx.Font = None
    screen_width: int = 0
    screen_height: int = 0


class App(metaclass=abc.ABCMeta):
    """
    Abstract base class for a barcodeRaspi App
    """

    def __init__(self):
        self.display_settings = DisplaySettings()
        self.file_contents = FileContents()
        self.products_file: Optional[str] = None
        self.purchases_file: Optional[str] = None
        self.users_file: Optional[str] = None
        self.product_columns = ['nr', 'code', 'desc', 'price', 'stock']
        self.product_columns_type = {'nr': int, 'code': str, 'desc': str, 'price': float, 'stock': int}

        logging.basicConfig(filename='getraenke.log',
                            filemode='a',
                            format='%(asctime)s.%(msecs)03d %(levelname)s - %(name)s - %(funcName)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.app = wx.App(False)
        if 'BARCODE_DEV' in os.environ:
            self.display_settings.screen_width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X) / 2
        else:
            self.display_settings.screen_width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self.display_settings.screen_height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

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

    @staticmethod
    def exit() -> None:
        """
        Exit the app

        :return:
        """
        sys.exit()

    @staticmethod
    def restart() -> None:
        """
        Restart the app

        :return:
        """
        os.execl(sys.executable, sys.executable, *sys.argv)

    # dialogs
    @staticmethod
    def show_error_dialog(error_message: str) -> None:
        """
        Show an error dialog

        :param error_message: error message for the user
        :return:
        """
        dlg = wx.MessageDialog(None, message=error_message, caption='ERROR',
                               style=wx.OK | wx.ICON_WARNING | wx.STAY_ON_TOP)
        # dlg.SetFont(self.display_settings.wxFont)
        dlg.ShowModal()

    @staticmethod
    def show_info_dialog(info_message: str) -> None:
        """
        Show an info dialog

        :param info_message: info message for the user
        :return:
        """
        dlg = wx.MessageDialog(None, message=info_message, caption='INFO',
                               style=wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
        # dlg.SetFont(self.display_settings.wxFont)
        dlg.ShowModal()

    @staticmethod
    def show_confirm_dialog(confirm_message: str) -> bool:
        """
        Show an confirm dialog

        :param confirm_message: confirm message for the user
        :return: True if wx.OK was clicked, False if wx.CANCEL was clicked
        """
        dlg = wx.MessageDialog(None, message=confirm_message, caption='CONFIRM',
                               style=wx.OK | wx.CANCEL | wx.ICON_QUESTION | wx.STAY_ON_TOP)
        # dlg.SetFont(self.display_settings.wxFont)
        choice = dlg.ShowModal()
        return bool(choice == wx.ID_OK)

    @staticmethod
    def show_password_dialog(password_message: str) -> bool:
        """
        Prompt the user for a password and compare it with the environment variable 'ADMIN_PASSWORD'

        :param password_message: password message for the user
        :return: True if password
        """
        dlg = wx.PasswordEntryDialog(parent=None, message=password_message,
                                     defaultValue='', style=wx.OK | wx.CANCEL)
        # dlg.SetFont(self.display_settings.wxFont)
        dlg.ShowModal()
        return bool(dlg.GetValue() == os.getenv('ADMIN_PASSWORD'))

    # handling of products
    @property
    def products_file(self) -> str:
        """
        Abstract property to return the products file
        """
        return self._products_file

    @products_file.setter
    def products_file(self, filename) -> None:
        """
        Setter for the property products_file

        :param filename: value for the property products_file
        :return:
        """
        self._products_file = filename

    def load_products(self) -> None:
        """
        Load the products file into a dataframe

        :return:
        """
        self.logger.info('loading products')
        self.file_contents.products = functions.read_csv_file(file=self.products_file,
                                                              columns=self.product_columns,
                                                              column_types=self.product_columns_type)
        self.logger.info('loading of %s products successful', len(self.file_contents.products))

    def create_new_product(self, values: Dict[str, str]) -> Optional[pd.DataFrame]:
        """
        Create dataframe for new item, if possible (input sanity check)

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
        """
        Save the products dataframe to file

        :return:
        """
        functions.write_csv_file(file=self.products_file, df=self.file_contents.products)

    # basics purchases
    def load_purchases(self) -> None:
        """
        Load the purchases file into a dataframe

        :return:
        """
        self.logger.info('loading purchases')
        self.file_contents.purchases = functions.read_csv_file(file=self.purchases_file,
                                                               columns=['timestamp', 'user', 'code', 'paid'],
                                                               column_types={'code': str, 'paid': bool})
        self.logger.info('loading of %s purchases successful', len(self.file_contents.purchases))

    def _save_purchases(self) -> None:
        """
        Save the purchases dataframe into a file

        :return:
        """
        functions.write_csv_file(file=self.purchases_file, df=self.file_contents.purchases)

    # basics of users
    @property
    def users_file(self) -> str:
        """
        Abstract property to return the users file
        """
        return self._users_file

    @users_file.setter
    def users_file(self, filename) -> None:
        """
        Setter for the property users_file

        :param filename: value for the property users_file
        :return:
        """
        self._users_file = filename

    def load_users(self) -> None:
        """
        Load the users file into a list

        :return:
        """
        self.logger.info('loading users')
        self.file_contents.users = functions.read_users(users_file=self.users_file)
        self.logger.info('loading of %s users successful', len(self.file_contents.users))

    def _save_users(self) -> None:
        pass
