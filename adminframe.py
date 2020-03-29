
import pandas as pd
import wx

import functions
import sortable


class AdminFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        wx.Frame.__init__(self, None, title='AdminFrame', style=wx.DEFAULT_FRAME_STYLE)
        with self.parent as prt:
            self.panel = wx.Panel(self)
            prt.get_purchases()
            prt.get_products()

            notebook = wx.Notebook(self.panel, pos=(0, 0),
                                   size=wx.Size(prt.displaySettings.screen_width-prt.displaySettings.btnWidth,
                                                prt.displaySettings.screen_height))

            tab1 = UserTabPanel(parent=notebook, super_parent=prt)
            products_df = prt.fileContents.products
            products_df['new_st'] = products_df['stock']
            tab2 = StockTabPanel(parent=notebook, super_parent=prt,
                                 columns={'names': ['desc', 'stock', 'new_st'],
                                          'width': [420, 130, 130],
                                          'type': [str, int, int]},
                                 data_frame=prt.fileContents.products[['desc', 'stock', 'new_st' ]])
            notebook.SetFont(prt.displaySettings.wxFont)
            notebook.AddPage(tab1, 'USER')
            notebook.AddPage(tab2, 'STOCK')

            self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
                                     size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                     pos=(prt.displaySettings.screen_width - 1*prt.displaySettings.btnWidth,
                                          prt.displaySettings.screen_height - prt.displaySettings.btnHeight))
            self.btnBack.SetFont(prt.displaySettings.wxFont)
            self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

            self.btnSave = wx.Button(self.panel, id=wx.ID_ANY, label='save', name='save',
                                     size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                     pos=(prt.displaySettings.screen_width - 1*prt.displaySettings.btnWidth,
                                          prt.displaySettings.screen_height - 2*prt.displaySettings.btnHeight))
            self.btnSave.SetFont(prt.displaySettings.wxFont)
            self.btnSave.Bind(wx.EVT_LEFT_UP, self._onClickSaveButton)

        self.ShowFullScreen(True)

    def _onClickBackButton(self, event):
        self.Close()

    def _onClickSaveButton(self, event):
        pass


class UserTabPanel(wx.Panel):

    def __init__(self, parent, super_parent):
        self.parent = parent
        self.super_parent = super_parent
        wx.Panel.__init__(self, self.parent)
        with self.super_parent as sprt:
            self.Text = wx.StaticText(self, label='User:',
                                      pos=(50, sprt.displaySettings.screen_height*1/5), size=(150, 50))
            self.Text.SetFont(sprt.displaySettings.wxFont)
            all_users_purchases = functions.summarize_user_purchases(purchases=sprt.fileContents.purchases,
                                                                     products=sprt.fileContents.products)

            users_list = all_users_purchases['name'].to_list()
            self.userChoice = wx.Choice(self, choices=users_list,
                                        pos=(200, sprt.displaySettings.screen_height*1/5), size=(150, 50))
            self.userChoice.SetFont(sprt.displaySettings.wxFont)
            self.userChoice.Bind(wx.EVT_CHOICE, self._onChooseUser)

            self.userSum = wx.StaticText(self, label="", pos=(sprt.displaySettings.screen_width / 5,
                                                              sprt.displaySettings.screen_height * 1 / 5 + 150),
                                         size=(150, 50))

        # self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
        #                         size=wx.Size(prt.btnWidth, prt.btnHeight),
        #                         pos=(prt.screen_width - 1 * prt.btnWidth, prt.screen_height - prt.btnHeight))
        # self.btnBack.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        # self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

    def _onChooseUser(self, event):
        chosen_user = self.userChoice.GetString(self.userChoice.GetSelection())


class StockTabPanel(sortable.SortableListCtrlPanel):

    def __init__(self, parent, super_parent, columns: dict, data_frame: pd.DataFrame):
        super().__init__(parent, super_parent, columns, data_frame)

    def _onChooseProduct(self, event):
        chosen_product_nr = self.productChoice.GetSelection()
