"""
ListFrame of produktListe app
"""
import os.path
from typing import Dict, List

import pandas as pd
import wx
import wx.grid


class ListFrame(wx.Frame):
    """
    Frame to list the products
    """

    def __init__(self, parent, columns: List[Dict[str, int]]):
        """Constructor"""
        wx.Frame.__init__(self, None, title="ListFrame")
        self.parent = parent
        self.columns = columns
        panel = wx.Panel(self)

        self._width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self._height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        with self.parent as prt:
            btn_close = wx.Button(panel, id=wx.ID_ANY, label='close', name='close',
                                  size=wx.Size(prt.display_settings.btn_width, prt.display_settings.btn_height),
                                  pos=(self._width - prt.display_settings.btn_width, 0))
            btn_close.SetFont(prt.display_settings.wx_font)
            btn_close.Bind(wx.EVT_LEFT_UP, self._onClickCloseButton)

            btn_add = wx.Button(panel, id=wx.ID_ANY, label='add', name='add',
                                size=wx.Size(prt.display_settings.btn_width, prt.display_settings.btn_height),
                                pos=(self._width - prt.display_settings.btn_width, 2 * prt.display_settings.btn_height))
            btn_add.SetFont(prt.display_settings.wx_font)
            btn_add.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            btn_edit = wx.Button(panel, id=wx.ID_ANY, label='edit', name='edit',
                                 size=wx.Size(prt.display_settings.btn_width, prt.display_settings.btn_height),
                                 pos=(self._width - prt.display_settings.btn_width,
                                      3 * prt.display_settings.btn_height))
            btn_edit.SetFont(prt.display_settings.wx_font)
            btn_edit.Bind(wx.EVT_LEFT_UP, self._onClickEditButton)

            btn_del = wx.Button(panel, id=wx.ID_ANY, label='delete', name='delete',
                                size=wx.Size(prt.display_settings.btn_width, prt.display_settings.btn_height),
                                pos=(self._width - prt.display_settings.btn_width,
                                     4 * prt.display_settings.btn_height))
            btn_del.SetFont(prt.display_settings.wx_font)
            btn_del.Bind(wx.EVT_LEFT_UP, self._onClickDelButton)

            self.btn_load = wx.Button(panel, id=wx.ID_ANY, label='load', name='load',
                                      size=wx.Size(prt.display_settings.btn_width, prt.display_settings.btn_height),
                                      pos=(self._width - prt.display_settings.btn_width,
                                           5 * prt.display_settings.btn_height))
            self.btn_load.SetFont(prt.display_settings.wx_font)
            self.btn_load.Bind(wx.EVT_LEFT_UP, self._onClickLoadButton)

            if not os.path.isfile(prt.products_file):
                self.btn_load.Disable()

            btn_save = wx.Button(panel, id=wx.ID_ANY, label="save", name="save",
                                 size=wx.Size(prt.display_settings.btn_width, prt.display_settings.btn_height),
                                 pos=(self._width - prt.display_settings.btn_width,
                                      6 * prt.display_settings.btn_height))
            btn_save.SetFont(prt.display_settings.wx_font)
            btn_save.Bind(wx.EVT_LEFT_UP, self._onClickSaveButton)

            self.prod_list = wx.ListCtrl(panel,
                                         size=(self._width - prt.display_settings.btn_width -
                                               2 * prt.display_settings.off_set,
                                               self._height - 2 * prt.display_settings.off_set),
                                         pos=(prt.display_settings.off_set, prt.display_settings.off_set),
                                         style=wx.LC_REPORT | wx.LC_HRULES)
            self.prod_list.SetFont(prt.display_settings.wx_font)
            for index, entry in enumerate(self.columns):
                self.prod_list.InsertColumn(index, entry['text'], width=entry['width'])

            self.SetBackgroundColour("Gray")
            self.ShowFullScreen(True)

    def update_prod_list(self, products_df: pd.DataFrame) -> None:
        """
        Update the ListCtrl showing the product list

        :param products_df: dataframe of products
        :return:
        """
        self.prod_list.DeleteAllItems()
        for _, row in products_df.iterrows():
            self.prod_list.Append(row.tolist())

    def _onClickCloseButton(self, _) -> None:
        """"""
        self.parent.exit()

    def _onClickAddButton(self, _) -> None:
        """"""
        number = self.parent.get_new_number()
        self.parent.show_edit_frame(number=number)

    def _onClickEditButton(self, _) -> None:
        """"""
        first_selected = self.prod_list.GetFirstSelected()
        if first_selected != -1:
            number = int(self.prod_list.GetItemText(first_selected, 0))
            old_values = (self.prod_list.GetItemText(first_selected, i)
                          for i in range(1, self.prod_list.GetColumnCount()))
            self.parent.show_edit_frame(number=number, old_values=old_values)

    def _onClickDelButton(self, _) -> None:
        """"""
        first_selected = self.prod_list.GetFirstSelected()
        if first_selected != -1:
            product_nr = self.prod_list.GetItemText(item=first_selected, col=0)
            if not self.parent.show_confirm_dialog(confirm_message=f'Are you sure to delete #{product_nr}?'):
                return None
            self.parent.delete_item(values={'nr': int(product_nr)})
            self.parent.update_product_listctrl()
        return None

    def _onClickLoadButton(self, _) -> None:
        """"""
        if self.parent.show_confirm_dialog(confirm_message=f'Do you want to load {self.parent.products_file}?'):
            self.parent.load_products()
            self.parent.update_product_listctrl()

    def _onClickSaveButton(self, _) -> None:
        """"""
        if self.parent.show_confirm_dialog(confirm_message=f'Do you want to save to {self.parent.products_file}?'):
            self.parent.save_products()
            self.btn_load.Enable()
