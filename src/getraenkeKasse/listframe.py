import wx

import functions
import src.getraenkeKasse.sortable
import src.getraenkeKasse.statistics


class ListFrame(wx.Frame):
    """
    Frame to list the purchases per user and the stock
    """

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        wx.Frame.__init__(self, None, title='ListFrame', style=wx.DEFAULT_FRAME_STYLE)
        with self.parent as prt:
            # prt.load_purchases()
            # prt.load_products()
            self.panel = wx.Panel(self)
            self.notebook = wx.Notebook(self.panel, pos=(0, 0),
                                        size=wx.Size(prt.display_settings.screen_width - prt.display_settings.btn_width,
                                                     prt.display_settings.screen_height))

            tab1 = src.getraenkeKasse.sortable.SortableListCtrlPanel(parent=self.notebook, super_parent=prt,
                                                                     columns={'names': ['name', 'drinks', 'money'],
                                                                              'width': [180, 180, 180],
                                                                              'type': [str, int, '{:,.2f}'.format]},
                                                                     data_frame=functions.summarize_user_purchases(
                                                                         purchases=prt.file_contents.purchases,
                                                                         products=prt.file_contents.products))
            tab2 = src.getraenkeKasse.sortable.SortableListCtrlPanel(parent=self.notebook, super_parent=prt,
                                                                     columns={'names': ['nr', 'desc', 'price', 'stock'],
                                                                              'width': [80, 300, 120, 120],
                                                                              'type': [int, str, '{:,.2f}'.format,
                                                                                       int]},
                                                                     data_frame=prt.file_contents.products[
                                                                         ['nr', 'desc', 'price', 'stock']])
            self.notebook.SetFont(prt.display_settings.wx_font)
            self.notebook.AddPage(tab1, 'USER')
            self.notebook.AddPage(tab2, 'STOCK')

            self.btn_statistics = wx.Button(self.panel, id=wx.ID_ANY, label='statistics', name='statistics',
                                            size=prt.display_settings.wx_button_size,
                                            pos=(prt.display_settings.screen_width - prt.display_settings.btn_width,
                                                 3 * prt.display_settings.btn_height))
            self.btn_statistics.SetFont(prt.display_settings.wx_font)
            self.btn_statistics.Bind(wx.EVT_LEFT_UP, self._onClickStatisticsButton)

            self.btn_back = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
                                      size=prt.display_settings.wx_button_size,
                                      pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                           prt.display_settings.screen_height - prt.display_settings.btn_height))
            self.btn_back.SetFont(prt.display_settings.wx_font)
            self.btn_back.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

        self.ShowFullScreen(True)

    def _onClickBackButton(self, _) -> None:
        """"""
        self.Close()

    def _onClickStatisticsButton(self, _) -> None:
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
                                                                    purchases=self.parent.file_contents.purchases,
                                                                    products=self.parent.file_contents.products)
        elif number_page == 1:
            stat_obj = src.getraenkeKasse.statistics.ProductStatistics(product_nr=int(clicked_item),
                                                                       purchases=self.parent.file_contents.purchases,
                                                                       products=self.parent.file_contents.products)
        else:
            pass
        if stat_obj:
            self.parent.show_confirm_dialog(confirm_message=stat_obj.get_statistics())
