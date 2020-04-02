
import pandas as pd
import wx

import functions
import sortable


class AdminFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        self.changed = False
        wx.Frame.__init__(self, None, title='AdminFrame', style=wx.DEFAULT_FRAME_STYLE)
        with self.parent as prt:
            self.panel = wx.Panel(self)
            prt.get_purchases()
            prt.get_products()


            self.notebook = wx.Notebook(self.panel, pos=(0, 0),
                                        size=wx.Size(prt.displaySettings.screen_width-prt.displaySettings.btnWidth,
                                                     prt.displaySettings.screen_height))
            self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._onNotebookChanged)
            self.tab1 = UserTabPanel(parent=self.notebook, super_parent=prt)
            products_df = prt.fileContents.products.copy()
            products_df['new_st'] = products_df['stock']
            self.tab2 = StockTabPanel(parent=self.notebook, super_parent=prt,
                                      columns={'names': ['nr', 'desc', 'stock', 'new_st'],
                                               'width': [80, 420, 130, 130],
                                               'type': [int, str, int, int]},
                                      data_frame=products_df[['nr', 'desc', 'stock', 'new_st']])
            self.notebook.SetFont(prt.displaySettings.wxFont)
            self.notebook.AddPage(self.tab1, 'USER')
            self.notebook.AddPage(self.tab2, 'STOCK')

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
            self.btnSave.Hide()

        self.ShowFullScreen(True)

    def _onClickBackButton(self, event):
        if self.changed:
            if not self.parent.show_confirm_dialog(confirm_message='Do you want to discard '):
                return None
        self.Close()

    def _onClickSaveButton(self, event):
        if self.changed:
            for i in range(0, self.tab2.sortable_list_ctrl.GetItemCount()):
                stock_old = self.tab2.sortable_list_ctrl.GetItem(i, col=2).GetText()
                stock_new = self.tab2.sortable_list_ctrl.GetItem(i, col=3).GetText()
                if stock_old != stock_new:
                    self.parent.set_stock_for_product(nr=int(self.tab2.sortable_list_ctrl.GetItem(i, col=0).GetText()),
                                                      stock=stock_new)
            self.parent.save_products()

    def _onNotebookChanged(self, event):
        try:
            if self.notebook.GetSelection() == 1:
                self.btnSave.Show()
            else:
                self.btnSave.Hide()
        except AttributeError:
            pass


class UserTabPanel(wx.Panel):

    def __init__(self, parent, super_parent):
        self.parent = parent
        self.super_parent = super_parent
        wx.Panel.__init__(self, self.parent)
        self.chosen_user = ''
        with self.super_parent as sprt:
            self.Text = wx.StaticText(self, label='User:',
                                      pos=(50, sprt.displaySettings.screen_height*1/5), size=(150, 50))
            self.Text.SetFont(sprt.displaySettings.wxFont)
            self.all_users_purchases = functions.summarize_user_purchases(purchases=sprt.fileContents.purchases,
                                                                          products=sprt.fileContents.products)

            users_list = self.all_users_purchases['name'].to_list()
            self.userChoice = wx.Choice(self, choices=users_list,
                                        pos=(200, sprt.displaySettings.screen_height*1/5), size=(150, 50))
            self.userChoice.SetFont(sprt.displaySettings.wxFont)
            self.userChoice.Bind(wx.EVT_CHOICE, self._onChooseUser)

            self.userSum = wx.StaticText(self, label="", pos=(sprt.displaySettings.screen_width / 5,
                                                              sprt.displaySettings.screen_height * 1 / 5 + 120),
                                         size=(150, 50))
            self.userSum.SetFont(sprt.displaySettings.wxFont)

            self.btnPay = wx.Button(self, id=wx.ID_ANY, label='pay', name='pay',
                                    size=wx.Size(sprt.displaySettings.btnWidth, sprt.displaySettings.btnHeight),
                                    pos=(sprt.displaySettings.screen_width / 5,
                                         sprt.displaySettings.screen_height * 1 / 5 + 180))
            self.btnPay.SetFont(sprt.displaySettings.wxFont)
            self.btnPay.Bind(wx.EVT_LEFT_UP, self._onClickPayButton)

    def _onChooseUser(self, event):
        self.chosen_user = self.userChoice.GetString(self.userChoice.GetSelection())
        sum_user = self.all_users_purchases.loc[self.all_users_purchases['name'] == self.chosen_user, 'money'].item()
        self.userSum.SetLabel(label=f"{self.chosen_user}:\t\t{'{:,.2f}'.format(sum_user)}")

    def _onClickPayButton(self, event):
        if self.chosen_user:
            self.super_parent.set_paid_for_user(self.chosen_user)
            self.super_parent.save_purchases()
            self.userSum.SetLabel(label=f"{self.chosen_user}:\t\t0.00")


class StockTabPanel(sortable.SortableListCtrlPanel):

    def __init__(self, parent, super_parent, columns: dict, data_frame: pd.DataFrame):
        super().__init__(parent, super_parent, columns, data_frame)
        self.parent = parent
        self.super_parent = super_parent

    def _OnItemClick(self, event):
        focus = self.sortable_list_ctrl.GetFocusedItem()
        stock_old = self.sortable_list_ctrl.GetItem(focus, 2).GetText()
        stock_new = self.sortable_list_ctrl.GetItem(focus, 3).GetText()
        dlg = NewStockInputDialog(parent=self.parent, super_parent=self.super_parent, title='Stock',
                                  size=(300, 250), style=wx.STAY_ON_TOP)
        dlg.ShowModal()


class NewStockInputDialog(wx.Dialog):

    def __init__(self, parent, super_parent, title, size, style):
        super().__init__(parent, title=title, size=size, style=style)
        self.parent = parent
        self.super_parent = super_parent
        panel = wx.Panel(self)

        self.btnOne = wx.Button(panel, id=wx.ID_ANY, label='+1', size=(50, 20), pos=(75, 50))
        self.btnOne.SetFont(self.super_parent.displaySettings.wxFont)
        #self.btnOne.Bind(wx.EVT_LEFT_UP, self._onClickPayButton)

        self.btnFive = wx.Button(panel, id=wx.ID_ANY, label='+5', size=(50, 20), pos=(75, 50))
        self.btnFive.SetFont(self.super_parent.displaySettings.wxFont)

        self.btnTwelve = wx.Button(panel, id=wx.ID_ANY, label='+12', size=(50, 20), pos=(75, 50))
        self.btnTwelve.SetFont(self.super_parent.displaySettings.wxFont)

        self.btnTwenty = wx.Button(panel, id=wx.ID_ANY, label='+20', size=(50, 20), pos=(75, 50))
        self.btnTwenty.SetFont(self.super_parent.displaySettings.wxFont)

        self.btnOK = wx.Button(self, wx.ID_OK)

        self.btnCancel = wx.Button(self, wx.ID_CANCEL)

        sizer = self.CreateStdDialogButtonSizer(flags=wx.OK | wx.CANCEL)
        sizer.Add(self.btnOK, 0, wx.BOTTOM | wx.RIGHT, 10)
        sizer.Add(self.btnCancel, 0, wx.BOTTOM | wx.LEFT, 10)
        self.SetSizer(sizer)
