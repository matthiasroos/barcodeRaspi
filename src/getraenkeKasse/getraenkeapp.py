

from __future__ import annotations

import dataclasses
import os
import sys
from typing import Dict, List

import pandas as pd
import wx

import functions
import getraenkeKasse
import src.app
import src.getraenkeKasse.adminframe
import src.getraenkeKasse.listframe
import src.getraenkeKasse.mainframe
import src.getraenkeKasse.scanframe


class GetraenkeApp(src.app.App):
    """
    App ...
    """

    def __init__(self,
                 button_height: int,
                 button_width: int,
                 font_size: int,
                 offset: int,
                 file_names: Dict[str, str]
                 ):
        super().__init__()

        self.display_settings.btn_height = button_height
        self.display_settings.btn_width = button_width
        self.display_settings.font_size = font_size
        self.display_settings.wx_button_size = wx.Size(self.display_settings.btn_width,
                                                       self.display_settings.btn_height)
        self.display_settings.wx_font = wx.Font(self.display_settings.font_size, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.display_settings.off_set = offset
        self.products_file = file_names['products']
        self.purchases_file = file_names['purchases']
        self.users_file = file_names['users']

        self.version = getraenkeKasse.VERSION
        self.clicked_user = None

    def run(self):
        """
        Implementation of the abstract run method

        :return:
        """
        self.load_users()

        # code for adding the paid column to PURCHASES_FILE
        if functions.check_column_nr_in_file(self.purchases_file) == 3:
            functions.transform_purchases(purchases_file=self.purchases_file)
            functions.git_push(path_repo='./.',
                               files=[self.purchases_file],
                               commit_message='update PURCHASES_FILE via getraenkeKasse.py')
        self.load_purchases()

        # code for adding the stock column to PRODUCTS_FILE
        if functions.check_column_nr_in_file(self.products_file) == 4:
            functions.transform_products(products_file=self.products_file)
            functions.git_push(path_repo='./.',
                               files=[self.products_file],
                               commit_message='update PRODUCTS_FILE via getraenkeKasse.py')
        self.load_products()

        src.getraenkeKasse.mainframe.MainFrame(self)
        self.app.MainLoop()

    def show_admin_frame(self):
        """
        Show the admin frame

        :return:
        """
        src.getraenkeKasse.adminframe.AdminFrame(self)

    def show_list_frame(self):
        """
        Show the list frame

        :return:
        """
        src.getraenkeKasse.listframe.ListFrame(self)

    def show_scan_frame(self):
        """
        Show the scan frame

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


    def _set_stock_for_product(self, nr: int, stock: int):
        self.file_contents.products.loc[self.file_contents.products['nr'] == nr, 'stock'] = stock

    def replenish_stock(self, changed_stock: List[List[int]]):
        self.bring_git_repo_up_to_date(path_repo='./.', error_message='Problem with git (local repo).')
        for product in changed_stock:
            nr, stock_old, stock_new = product
            if stock_old != stock_new:
                self._set_stock_for_product(nr=nr, stock=stock_new)
        self._save_products()
        self.check_in_changes_into_git(path_repo='./.', files=[self.products_file],
                                       commit_message='replenish stock via getraenkeKasse.py')

    def _decrease_stock_for_product(self, code: str) -> bool:
        if self.file_contents.products.loc[self.file_contents.products['code'] == code, 'stock'].values > 0:
            self.file_contents.products.loc[self.file_contents.products['code'] == code, 'stock'] -= 1
            return True
        return False



    def _set_paid_for_user(self, user: str):
        self.file_contents.purchases.loc[self.file_contents.purchases['user'] == user, 'paid'] = True

    def pay_for_user(self, user: str):
        self.bring_git_repo_up_to_date(path_repo='./.', error_message='Problem with git (local repo).')
        self._set_paid_for_user(user=user)
        self._save_purchases()
        self.check_in_changes_into_git(path_repo='./.', files=[self.purchases_file],
                                       commit_message=f'pay for user {user} via getraenkeKasse.py')

    def make_purchase(self, user: str, code: str):
        self.bring_git_repo_up_to_date(path_repo='./.', error_message='Problem with git (local repo).')
        self.file_contents.purchases = functions.add_purchase(purchases=self.file_contents.purchases,
                                                              user=user, code=code)
        self._save_purchases()
        files = [self.purchases_file]
        result = self._decrease_stock_for_product(code=code)
        if result:
            self._save_products()
            files.append(self.products_file)
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
