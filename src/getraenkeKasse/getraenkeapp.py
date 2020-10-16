

from __future__ import annotations

import dataclasses
import os
import sys
from typing import List

import pandas as pd
import wx

import functions
import getraenkeKasse
import src.app
import src.getraenkeKasse.adminframe
import src.getraenkeKasse.listframe
import src.getraenkeKasse.mainframe
import src.getraenkeKasse.scanframe

PRODUCTS_FILE = 'produkt.txt'
PURCHASES_FILE = 'purchase.txt'
USERS_FILE = 'user.txt'

BUTTON_HEIGHT = 70
BUTTON_WIDTH = 180
FONT_SIZE = 18
OFFSET = 5


class GetraenkeApp(src.app.App):
    """
    App ...
    """

    def __init__(self):
        super().__init__()

        self.display_settings.btn_height = BUTTON_HEIGHT
        self.display_settings.btn_width = BUTTON_WIDTH
        self.display_settings.font_size = FONT_SIZE
        self.display_settings.wx_button_size = wx.Size(self.display_settings.btn_width,
                                                       self.display_settings.btn_height)
        self.display_settings.wx_font = wx.Font(self.display_settings.font_size, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.display_settings.off_set = OFFSET
        self.products_file = PRODUCTS_FILE

        self.version = getraenkeKasse.VERSION
        self._clicked_user = None

    def run(self):
        """


        :return:
        """
        self.get_users()

        # code for adding the paid column to PURCHASES_FILE
        if functions.check_column_nr_in_file(PURCHASES_FILE) == 3:
            functions.transform_purchases(purchases_file=PURCHASES_FILE)
            functions.git_push(path_repo='./.',
                               files=[PURCHASES_FILE],
                               commit_message='update PURCHASES_FILE via getraenkeKasse.py')
        self.get_purchases()

        # code for adding the stock column to PRODUCTS_FILE
        if functions.check_column_nr_in_file(PRODUCTS_FILE) == 4:
            functions.transform_products(products_file=PRODUCTS_FILE)
            functions.git_push(path_repo='./.',
                               files=[PRODUCTS_FILE],
                               commit_message='update PRODUCTS_FILE via getraenkeKasse.py')
        self.load_products()

        src.getraenkeKasse.mainframe.MainFrame(self)
        self.app.MainLoop()

    def show_admin_frame(self):
        """


        :return:
        """
        src.getraenkeKasse.adminframe.AdminFrame(self)

    def show_list_frame(self):
        """


        :return:
        """
        src.getraenkeKasse.listframe.ListFrame(self)

    def show_scan_frame(self):
        """


        :return:
        """
        src.getraenkeKasse.scanframe.ScanFrame(self)

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
        self.file_contents.users = functions.read_users(users_file=USERS_FILE)

    def _set_stock_for_product(self, nr: int, stock: int):
        self.file_contents.products.loc[self.file_contents.products['nr'] == nr, 'stock'] = stock

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
        if self.file_contents.products.loc[self.file_contents.products['code'] == code, 'stock'].values > 0:
            self.file_contents.products.loc[self.file_contents.products['code'] == code, 'stock'] -= 1
            return True
        return False

    def get_purchases(self):
        self.file_contents.purchases = functions.read_csv_file(file=PURCHASES_FILE,
                                                               columns=['timestamp', 'user', 'code', 'paid'],
                                                               column_types={'code': str, 'paid': bool})

    def _save_purchases(self):
        functions.write_csv_file(file=PURCHASES_FILE, df=self.file_contents.purchases)

    def _set_paid_for_user(self, user: str):
        self.file_contents.purchases.loc[self.file_contents.purchases['user'] == user, 'paid'] = True

    def pay_for_user(self, user: str):
        self.bring_git_repo_up_to_date(path_repo='./.', error_message='Problem with git (local repo).')
        self._set_paid_for_user(user=user)
        self._save_purchases()
        self.check_in_changes_into_git(path_repo='./.', files=[PURCHASES_FILE],
                                       commit_message=f'pay for user {user} via getraenkeKasse.py')

    def make_purchase(self, user: str, code: str):
        self.bring_git_repo_up_to_date(path_repo='./.', error_message='Problem with git (local repo).')
        self.file_contents.purchases = functions.add_purchase(purchases=self.file_contents.purchases,
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
