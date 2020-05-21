
import wx

import functions
import src.getraenkeKasse.sortable
import src.getraenkeKasse.statistics


class ListFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        wx.Frame.__init__(self, None, title='ListFrame', style=wx.DEFAULT_FRAME_STYLE)
        with self.parent as prt:
            prt.get_purchases()
            prt.get_products()
            self.panel = wx.Panel(self)
            self.notebook = wx.Notebook(self.panel, pos=(0, 0),
                                        size=wx.Size(prt.displaySettings.screen_width-prt.displaySettings.btnWidth,
                                                     prt.displaySettings.screen_height))

            tab1 = src.getraenkeKasse.sortable.SortableListCtrlPanel(parent=self.notebook, super_parent=prt,
                                                                     columns={'names': ['name', 'drinks', 'money'],
                                                                              'width': [180, 180, 180],
                                                                              'type': [str, int, '{:,.2f}'.format]},
                                                                     data_frame=functions.summarize_user_purchases(
                                                                         purchases=prt.fileContents.purchases,
                                                                         products=prt.fileContents.products))
            tab2 = src.getraenkeKasse.sortable.SortableListCtrlPanel(parent=self.notebook, super_parent=prt,
                                                                     columns={'names': ['nr', 'desc', 'price', 'stock'],
                                                                              'width': [80, 300, 120, 120],
                                                                              'type': [int, str, '{:,.2f}'.format,
                                                                                       int]},
                                                                     data_frame=prt.fileContents.products[
                                                                         ['nr', 'desc', 'price', 'stock']])
            self.notebook.SetFont(prt.displaySettings.wxFont)
            self.notebook.AddPage(tab1, 'USER')
            self.notebook.AddPage(tab2, 'STOCK')

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

            self.btnStatistics = wx.Button(self.panel, id=wx.ID_ANY, label='statistics', name='statistics',
                                           size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                           pos=(prt.displaySettings.screen_width - prt.displaySettings.btnWidth,
                                                3*prt.displaySettings.btnHeight))
            self.btnStatistics.SetFont(prt.displaySettings.wxFont)
            self.btnStatistics.Bind(wx.EVT_LEFT_UP, self._onClickStatisticsButton)

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

    def _onClickStatisticsButton(self, event):
        """"""
        number_page = self.notebook.GetSelection()
        current_page = self.notebook.GetCurrentPage()
        focus = current_page.sortable_list_ctrl.GetFocusedItem()
        if focus == -1:
            return None
        clicked_item = current_page.sortable_list_ctrl.GetItem(focus).GetText()
        stat_obj = None
        if number_page == 0:
            stat_obj = src.getraenkeKasse.statistics.UserStatistics(user=clicked_item,
                                                                    purchases=self.parent.fileContents.purchases,
                                                                    products=self.parent.fileContents.products)
        elif number_page == 1:
            stat_obj = src.getraenkeKasse.statistics.ProductStatistics(product_nr=int(clicked_item),
                                                                       purchases=self.parent.fileContents.purchases,
                                                                       products=self.parent.fileContents.products)
        else:
            pass
        if stat_obj:
            self.parent.show_confirm_dialog(confirm_message=stat_obj.get_statistics())

    def _onClickRestartButton(self, event):
        """"""
        self.parent.restart()
