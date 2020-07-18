
import os.path
from typing import Dict, List

import pandas as pd
import wx
import wx.grid


class ListFrame(wx.Frame):

    def __init__(self, parent, columns: List[Dict[str, int]]):
        """Constructor"""
        wx.Frame.__init__(self, None, title="ListFrame")
        self.parent = parent
        self.columns = columns
        panel = wx.Panel(self)

        self._width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self._height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        with self.parent as prt:
            btnClose = wx.Button(panel, id=wx.ID_ANY, label='close', name='close',
                                 size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                 pos=(self._width - prt.displaySettings.btnWidth, 0))
            btnClose.SetFont(prt.displaySettings.wxFont)
            btnClose.Bind(wx.EVT_LEFT_UP, self._onClickCloseButton)

            btnAdd = wx.Button(panel, id=wx.ID_ANY, label='add', name='add',
                               size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                               pos=(self._width - prt.displaySettings.btnWidth, 2 * prt.displaySettings.btnHeight))
            btnAdd.SetFont(prt.displaySettings.wxFont)
            btnAdd.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            btnEdit = wx.Button(panel, id=wx.ID_ANY, label='edit', name='edit',
                                size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                pos=(self._width - prt.displaySettings.btnWidth, 3 * prt.displaySettings.btnHeight))
            btnEdit.SetFont(prt.displaySettings.wxFont)
            btnEdit.Bind(wx.EVT_LEFT_UP, self._onClickEditButton)

            btnDel = wx.Button(panel, id=wx.ID_ANY, label='delete', name='delete',
                               size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                               pos=(self._width - prt.displaySettings.btnWidth, 4 * prt.displaySettings.btnHeight))
            btnDel.SetFont(prt.displaySettings.wxFont)
            btnDel.Bind(wx.EVT_LEFT_UP, self._onClickDelButton)

            self.btnLoad = wx.Button(panel, id=wx.ID_ANY, label='load', name='load',
                                     size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                     pos=(
                                         self._width - prt.displaySettings.btnWidth, 5 * prt.displaySettings.btnHeight))
            self.btnLoad.SetFont(prt.displaySettings.wxFont)
            self.btnLoad.Bind(wx.EVT_LEFT_UP, self._onClickLoadButton)

            if not os.path.isfile(prt.productsFile):
                self.btnLoad.Disable()

            btnSave = wx.Button(panel, id=wx.ID_ANY, label="save", name="save",
                                size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                pos=(self._width - prt.displaySettings.btnWidth, 6 * prt.displaySettings.btnHeight))
            btnSave.SetFont(prt.displaySettings.wxFont)
            btnSave.Bind(wx.EVT_LEFT_UP, self._onClickSaveButton)

            self.prodList = wx.ListCtrl(panel,
                                        size=(self._width - prt.displaySettings.btnWidth -
                                              2 * prt.displaySettings.offSet,
                                              self._height - 2 * prt.displaySettings.offSet),
                                        pos=(prt.displaySettings.offSet, prt.displaySettings.offSet),
                                        style=wx.LC_REPORT | wx.LC_HRULES)
            self.prodList.SetFont(prt.displaySettings.wxFont)
            for index, entry in enumerate(self.columns):
                self.prodList.InsertColumn(index, entry['text'], width=entry['width'])

            self.SetBackgroundColour("Gray")
            self.ShowFullScreen(True)

    def update_prodList(self, products_df: pd.DataFrame):
        """"""
        self.prodList.DeleteAllItems()
        for index, row in products_df.iterrows():
            self.prodList.Append([value for value in row])

    def _onClickCloseButton(self, event):
        """"""
        self.parent.exit()

    def _onClickAddButton(self, event):
        """"""
        number = self.parent.get_new_number()
        self.parent.show_edit_frame(number=number)

    def _onClickEditButton(self, event):
        """"""
        fi = self.prodList.GetFirstSelected()
        if fi != -1:
            number = int(self.prodList.GetItemText(fi, 0))
            old_values = (self.prodList.GetItemText(fi, i) for i in range(1, self.prodList.GetColumnCount()))
            self.parent.show_edit_frame(number=number, old_values=old_values)

    def _onClickDelButton(self, event):
        """"""
        fi = self.prodList.GetFirstSelected()
        if fi != -1:
            product_nr = self.prodList.GetItemText(item=fi, col=0)
            if not self.parent.show_confirm_dialog(confirm_message=f'Are your sure to delete #{product_nr}?'):
                return None
            self.parent.delete_item(number=int(product_nr))
            self.parent.update_product_listctrl()

    def _onClickLoadButton(self, event):
        """"""
        if self.parent.show_confirm_dialog(confirm_message=f'Do you want to load {self.parent.productsFile}?'):
            self.parent.load_products()
            self.parent.update_product_listctrl()

    def _onClickSaveButton(self, event):
        """"""
        if self.parent.show_confirm_dialog(confirm_message=f'Do you want to save to {self.parent.productsFile}?'):
            self.parent.save_products()
            self.btnLoad.Enable()
