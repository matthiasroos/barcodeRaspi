
import dataclasses
import os
import sys
from typing import List

import pandas as pd
import wx

import functions
import getraenkeKasse
import src.getraenkeKasse.adminframe
import src.getraenkeKasse.listframe
import src.getraenkeKasse.mainframe
import src.getraenkeKasse.scanframe

PRODUCTS_FILE = 'produkt.txt'
PURCHASES_FILE = 'purchase.txt'
USERS_FILE = 'user.txt'

BUTTON_HEIGHT = 70
BUTTON_WIDTH = 180
FONT_SIZE = 20
OFFSET = 5


@dataclasses.dataclass()
class FileContents:
    products: pd.DataFrame = None
    purchases: pd.DataFrame = None
    users: pd.DataFrame = None


@dataclasses.dataclass()
class DisplaySettings:
    btnHeight = BUTTON_HEIGHT
    btnWidth = BUTTON_WIDTH
    fontSize = FONT_SIZE
    offSet = OFFSET
    wxFont = None
    screen_width: int = None
    screen_height: int = None


class GetraenkeApp:

    def __init__(self):
        self.version = getraenkeKasse.VERSION
        self.displaySettings = DisplaySettings()
        self.fileContents = FileContents()
        self._clicked_user = None

        self.app = wx.App(False)
        if 'BARCODE_DEV' in os.environ:
            self.displaySettings.screen_width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)/2
        else:
            self.displaySettings.screen_width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self.displaySettings.screen_height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        self.displaySettings.wxFont = wx.Font(self.displaySettings.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def run(self):
        self.get_users()

        # code for adding the paid column to PURCHASES_FILE
        if functions.check_column_nr_in_file(PURCHASES_FILE) == 3:
            functions.transform_purchases(purchases_file=PURCHASES_FILE)
            functions.git_push(commit_message='update PURCHASES_FILE via getraenkeKasse.py')
        self.get_purchases()

        # code for adding the stock column to PRODUCTS_FILE
        if functions.check_column_nr_in_file(PRODUCTS_FILE) == 4:
            functions.transform_products(products_file=PRODUCTS_FILE)
            functions.git_push(commit_message='update PRODUCTS_FILE via getraenkeKasse.py')
        self.get_products()

        src.getraenkeKasse.mainframe.MainFrame(self)
        self.app.MainLoop()

    def exit(self):
        sys.exit()

    def restart(self):
        os.execl(sys.executable, sys.executable, *sys.argv)
        sys.exit()

    def show_admin_frame(self):
        src.getraenkeKasse.adminframe.AdminFrame(self)

    def show_list_frame(self):
        src.getraenkeKasse.listframe.ListFrame(self)

    def show_scan_frame(self):
        src.getraenkeKasse.scanframe.ScanFrame(self)

    def show_error_dialog(self, error_message: str):
        dlg = wx.MessageDialog(None, message=error_message, caption='ERROR',
                               style=wx.OK | wx.ICON_WARNING | wx.STAY_ON_TOP)
        # dlg.SetFont(self.displaySettings.wxFont)
        dlg.ShowModal()

    def show_info_dialog(self, info_message: str):
        dlg = wx.MessageDialog(None, message=info_message, caption='INFO',
                               style=wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
        # dlg.SetFont(self.displaySettings.wxFont)
        dlg.ShowModal()

    def show_confirm_dialog(self, confirm_message: str) -> bool:
        dlg = wx.MessageDialog(None, message=confirm_message, caption='CONFIRM',
                               style=wx.OK | wx.CANCEL | wx.ICON_QUESTION | wx.STAY_ON_TOP)
        # dlg.SetFont(self.displaySettings.wxFont)
        choice = dlg.ShowModal()
        if choice == wx.ID_OK:
            return True
        else:
            return False

    def show_password_dialog(self, password_message: str) -> bool:
        dlg = wx.PasswordEntryDialog(parent=None, message=password_message,
                                     defaultValue='', style=wx.OK | wx.CANCEL)
        # dlg.SetFont(self.displaySettings.wxFont)
        dlg.ShowModal()
        if dlg.GetValue() == os.getenv('ADMIN_PASSWORD'):
            return True
        return False

    def bring_git_repo_up_to_date(self, path_repo: str, error_message: str, should_exit: bool = False) -> None:
        if not functions.git_pull(path_repo=path_repo):
            self.show_error_dialog(error_message=error_message)
            if should_exit:
                self.exit()

    def check_in_changes_into_git(self, path_repo: str, files: List[str], commit_message: str,
                                  error_message: str = 'Problem with git (local repo).') -> None:
        if not functions.git_push(path_repo=path_repo, files=files, commit_message=commit_message):
            self.show_error_dialog(error_message=error_message)

    def get_users(self):
        self.fileContents.users = functions.read_users(users_file=USERS_FILE)

    def get_products(self):
        self.fileContents.products = functions.read_csv_file(file=PRODUCTS_FILE,
                                                             columns=['nr', 'code', 'desc', 'price', 'stock'],
                                                             column_type={'code': str, 'price': float})

    def _save_products(self):
        functions.write_csv_file(file=PRODUCTS_FILE, df=self.fileContents.products)

    def _set_stock_for_product(self, nr: int, stock: int):
        self.fileContents.products.loc[self.fileContents.products['nr'] == nr, 'stock'] = stock

    def replenish_stock(self, changed_stock: List[List[int]]):
        self.bring_git_repo_up_to_date(path_repo='./.', error_message='Problem with git (local repo).')
        for product in changed_stock:
            nr, stock_old, stock_new = product
            if stock_old != stock_new:
                self._set_stock_for_product(nr=nr, stock=stock_new)
        self._save_products()
        self.check_in_changes_into_git(path_repo='./.', files=[PRODUCTS_FILE],
                                       commit_message='replenish stock via getraenkeKasse.py')

    def _decrease_stock_for_product(self, code: str) -> bool:
        if self.fileContents.products.loc[self.fileContents.products['code'] == code, 'stock'].values > 0:
            self.fileContents.products.loc[self.fileContents.products['code'] == code, 'stock'] -= 1
            return True
        return False

    def get_purchases(self):
        self.fileContents.purchases = functions.read_csv_file(file=PURCHASES_FILE,
                                                              columns=['timestamp', 'user', 'code', 'paid'],
                                                              column_type={'code': str, 'paid': bool})

    def _save_purchases(self):
        functions.write_csv_file(file=PURCHASES_FILE, df=self.fileContents.purchases)

    def _set_paid_for_user(self, user: str):
        self.fileContents.purchases.loc[self.fileContents.purchases['user'] == user, 'paid'] = True

    def pay_for_user(self, user: str):
        self.bring_git_repo_up_to_date(path_repo='./.', error_message='Problem with git (local repo).')
        self._set_paid_for_user(user=user)
        self._save_purchases()
        self.check_in_changes_into_git(path_repo='./.', files=[PURCHASES_FILE],
                                       commit_message=f'pay for user {user} via getraenkeKasse.py')

    def make_purchase(self, user: str, code: str):
        self.bring_git_repo_up_to_date(path_repo='./.', error_message='Problem with git (local repo).')
        self.fileContents.purchases = functions.add_purchase(purchases=self.fileContents.purchases,
                                                             user=user, code=code)
        self._save_purchases()
        files = [PURCHASES_FILE]
        result = self._decrease_stock_for_product(code=code)
        if result:
            self._save_products()
            files.append(PRODUCTS_FILE)
        else:
            # TODO issue warning for selling without stock
            pass
        self.check_in_changes_into_git(path_repo='./.', files=files, commit_message='purchase via getraenkeKasse.py')


    @property
    def clicked_user(self) -> str:
        return self._clicked_user

    @clicked_user.setter
    def clicked_user(self, user: str):
        self._clicked_user = user
