
import abc
import dataclasses
import os
import sys
from typing import Optional

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
    def productsFile(self):
        """
        Abstract property to return the products file

        :return:
        """
        raise NotImplementedError

    @productsFile.setter
    def productsFile(self, value):
        self._productsFile = value

    def get_products(self) -> None:
        self.fileContents.products = functions.read_csv_file(file=self.productsFile,
                                                             columns=['nr', 'code', 'desc', 'price', 'stock'],
                                                             column_type={'code': str, 'price': float})

    def _save_products(self) -> None:
        functions.write_csv_file(file=self.productsFile, df=self.fileContents.products)
