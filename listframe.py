
import wx
import pandas as pd

import functions
import sortable
import statistics


class ListFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        wx.Frame.__init__(self, None, title='ListFrame', style=wx.DEFAULT_FRAME_STYLE)
        with self.parent as prt:
            prt.get_purchases()
            prt.get_products()
            self.panel = wx.Panel(self)
            notebook = wx.Notebook(self.panel, pos=(0, 0),
                                   size=wx.Size(prt.displaySettings.screen_width-prt.displaySettings.btnWidth,
                                                prt.displaySettings.screen_height))

            tab1 = UserTabPanel(parent=notebook, super_parent=prt,
                                columns={'names': ['name', 'drinks', 'money'],
                                         'width': [180, 180, 180],
                                         'type': [str, int, '{:,.2f}'.format]},
                                data_frame=functions.summarize_user_purchases(
                                    purchases=prt.fileContents.purchases,
                                    products=prt.fileContents.products))
            tab2 = StockTabPanel(parent=notebook, super_parent=prt,
                                 columns={'names': ['nr', 'desc', 'price', 'stock'],
                                          'width': [80, 300, 120, 120],
                                          'type': [int, str, '{:,.2f}'.format, int]},
                                 data_frame=prt.fileContents.products[['nr', 'desc', 'price', 'stock']])
            notebook.SetFont(prt.displaySettings.wxFont)
            notebook.AddPage(tab1, 'USER')
            notebook.AddPage(tab2, 'STOCK')

            self.btnClose = wx.Button(self.panel, id=wx.ID_ANY, label='close', name='close',
                                      size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                      pos=(prt.displaySettings.screen_width - prt.displaySettings.btnWidth, 0))
            self.btnClose.SetFont(prt.displaySettings.wxFont)
            self.btnClose.Bind(wx.EVT_LEFT_UP, self._onClickCloseButton)

            self.btnRestart = wx.Button(self.panel, id=wx.ID_ANY, label='restart', name='restart',
                                        size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                        pos=(prt.displaySettings.screen_width - prt.displaySettings.btnWidth,
                                             prt.displaySettings.btnHeight))
            self.btnRestart.SetFont(prt.displaySettings.wxFont)
            self.btnRestart.Bind(wx.EVT_LEFT_UP, self._onClickRestartButton)

            self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
                                     size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                     pos=(prt.displaySettings.screen_width - 1*prt.displaySettings.btnWidth,
                                          prt.displaySettings.screen_height - prt.displaySettings.btnHeight))
            self.btnBack.SetFont(prt.displaySettings.wxFont)
            self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

        self.ShowFullScreen(True)

    def _onClickCloseButton(self, event):
        """"""
        self.parent.exit()

    def _onClickBackButton(self, event):
        """"""
        self.Close()

    def _onClickRestartButton(self, event):
        """"""
        self.parent.restart()


class UserTabPanel(sortable.SortableListCtrlPanel):

    def __init__(self, parent, super_parent, columns: dict, data_frame: pd.DataFrame):
        super().__init__(parent, super_parent, columns, data_frame)

    def _OnItemClick(self, event):
        focus = self.sortable_list_ctrl.GetFocusedItem()
        clicked_user = self.sortable_list_ctrl.GetItem(focus).GetText()
        with self.super_parent as sprt:
            user_statistics = statistics.UserStatistics(user=clicked_user,
                                                        purchases=sprt.fileContents.purchases,
                                                        products=sprt.fileContents.products)
            sprt.show_confirm_dialog(confirm_message=user_statistics.get_user_statistic())


class StockTabPanel(sortable.SortableListCtrlPanel):

    def __init__(self, parent, super_parent, columns: dict, data_frame: pd.DataFrame):
        super().__init__(parent, super_parent, columns, data_frame)

    def _OnItemClick(self, event):
        focus = self.sortable_list_ctrl.GetFocusedItem()
        clicked_product = int(self.sortable_list_ctrl.GetItem(focus).GetText())
        with self.super_parent as sprt:
            product_statistics = statistics.ProductStatistics(product_nr=clicked_product,
                                                              purchases=sprt.fileContents.purchases,
                                                              products=sprt.fileContents.products)
            sprt.show_confirm_dialog(confirm_message=product_statistics.get_product_statistic())