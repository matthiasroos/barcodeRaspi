import wx

import functions
import src.getraenkeKasse.sortable


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

            if not prt.show_password_dialog(password_message='Please enter administrator PIN'):
                self.Close()

            self.notebook = wx.Notebook(self.panel, pos=(0, 0),
                                        size=wx.Size(prt.displaySettings.screen_width - prt.displaySettings.btnWidth,
                                                     prt.displaySettings.screen_height))
            user_purchases_df = functions.summarize_user_purchases(
                purchases=prt.fileContents.purchases,
                products=prt.fileContents.products)[
                ['name', 'money']]
            user_purchases_df['new_mo'] = user_purchases_df['money']
            self.tab1 = src.getraenkeKasse.sortable.SortableListCtrlPanel(parent=self.notebook, super_parent=prt,
                                                                          columns={'names': ['name', 'money', 'new_mo'],
                                                                                   'width': [130, 130, 130],
                                                                                   'type': [str, '{:,.2f}'.format,
                                                                                            '{:,.2f}'.format]},
                                                                          data_frame=user_purchases_df)
            cp_products_df = prt.fileContents.products.copy()
            cp_products_df['new_st'] = cp_products_df['stock']
            self.tab2 = src.getraenkeKasse.sortable.SortableListCtrlPanel(parent=self.notebook, super_parent=prt,
                                                                          columns={'names': ['nr', 'desc', 'stock',
                                                                                             'new_st'],
                                                                                   'width': [80, 320, 100, 100],
                                                                                   'type': [int, str, int, int]},
                                                                          data_frame=cp_products_df[
                                                                              ['nr', 'desc', 'stock', 'new_st']])
            self.notebook.SetFont(prt.displaySettings.wxFont)
            self.notebook.AddPage(self.tab1, 'USER')
            self.notebook.AddPage(self.tab2, 'STOCK')

            # Back button
            self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
                                     size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                     pos=(prt.displaySettings.screen_width - 1 * prt.displaySettings.btnWidth,
                                          prt.displaySettings.screen_height - prt.displaySettings.btnHeight))
            self.btnBack.SetFont(prt.displaySettings.wxFont)
            self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

            # Save button
            self.btnSave = wx.Button(self.panel, id=wx.ID_ANY, label='save', name='save',
                                     size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                     pos=(prt.displaySettings.screen_width - 1 * prt.displaySettings.btnWidth,
                                          prt.displaySettings.screen_height - 2 * prt.displaySettings.btnHeight))
            self.btnSave.SetFont(prt.displaySettings.wxFont)
            self.btnSave.Bind(wx.EVT_LEFT_UP, self._onClickSaveButton)

            # Reset button
            self.btnReset = wx.Button(self.panel, id=wx.ID_ANY, label='reset stock', name='reset',
                                      size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                      pos=(prt.displaySettings.screen_width - 1 * prt.displaySettings.btnWidth,
                                           prt.displaySettings.screen_height - 3 * prt.displaySettings.btnHeight))
            self.btnReset.SetFont(prt.displaySettings.wxFont)
            self.btnReset.Bind(wx.EVT_LEFT_UP, self._onClickResetButton)

            # +12 button
            self.btnTwelve = wx.Button(self.panel, id=6012, label='+12', name='twelve',
                                       size=wx.Size(prt.displaySettings.btnWidth / 2, prt.displaySettings.btnHeight),
                                       pos=(prt.displaySettings.screen_width - 1 * prt.displaySettings.btnWidth,
                                            prt.displaySettings.screen_height - 4 * prt.displaySettings.btnHeight))
            self.btnTwelve.SetFont(prt.displaySettings.wxFont)
            self.btnTwelve.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            # + 20 button
            self.btnTwenty = wx.Button(self.panel, id=6020, label='+20', name='twenty',
                                       size=wx.Size(prt.displaySettings.btnWidth / 2, prt.displaySettings.btnHeight),
                                       pos=(prt.displaySettings.screen_width - 1 * prt.displaySettings.btnWidth / 2,
                                            prt.displaySettings.screen_height - 4 * prt.displaySettings.btnHeight))
            self.btnTwenty.SetFont(prt.displaySettings.wxFont)
            self.btnTwenty.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            # +1 button
            self.btnOne = wx.Button(self.panel, id=6001, label='+1', name='one',
                                    size=wx.Size(prt.displaySettings.btnWidth / 2, prt.displaySettings.btnHeight),
                                    pos=(prt.displaySettings.screen_width - 1 * prt.displaySettings.btnWidth,
                                         prt.displaySettings.screen_height - 5 * prt.displaySettings.btnHeight))
            self.btnOne.SetFont(prt.displaySettings.wxFont)
            self.btnOne.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            # +5 button
            self.btnFive = wx.Button(self.panel, id=6005, label='+5', name='five',
                                     size=wx.Size(prt.displaySettings.btnWidth / 2, prt.displaySettings.btnHeight),
                                     pos=(prt.displaySettings.screen_width - 1 * prt.displaySettings.btnWidth / 2,
                                          prt.displaySettings.screen_height - 5 * prt.displaySettings.btnHeight))
            self.btnFive.SetFont(prt.displaySettings.wxFont)
            self.btnFive.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            # Pay button
            self.btnPay = wx.Button(self.panel, id=wx.ID_ANY, label='pay for user', name='pay',
                                    size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                    pos=(prt.displaySettings.screen_width - 1 * prt.displaySettings.btnWidth,
                                         prt.displaySettings.screen_height - 6 * prt.displaySettings.btnHeight))
            self.btnPay.SetFont(prt.displaySettings.wxFont)
            self.btnPay.Bind(wx.EVT_LEFT_UP, self._onClickPayButton)

        self.ShowFullScreen(True)

    def _onClickBackButton(self, event):
        if self.changed:
            if not self.parent.show_confirm_dialog(confirm_message='Do you want to discard?'):
                return None
        self.Close()

    def _onClickSaveButton(self, event):
        if self.changed:
            user_paid = []
            count = self.tab1.sortable_list_ctrl.GetItemCount()
            for row in range(0, count):
                money_old = self.tab1.sortable_list_ctrl.GetItem(row, col=1).GetText()
                money_new = self.tab1.sortable_list_ctrl.GetItem(row, col=2).GetText()
                if money_old != money_new:
                    user_paid.append(self.tab1.sortable_list_ctrl.GetItem(row, col=0).GetText())

            changed_stock = []
            count = self.tab2.sortable_list_ctrl.GetItemCount()
            for row in range(0, count):
                nr = int(self.tab2.sortable_list_ctrl.GetItem(row, col=0).GetText())
                stock_old = int(self.tab2.sortable_list_ctrl.GetItem(row, col=2).GetText())
                stock_new = int(self.tab2.sortable_list_ctrl.GetItem(row, col=3).GetText())
                changed_stock.append([nr, stock_old, stock_new])

            result = self.parent.show_confirm_dialog('Do you want to save purchases/products?')
            if result:
                for user in user_paid:
                    self.parent.pay_for_user(user=user)
                self.parent.replenish_stock(changed_stock=changed_stock)
                self.changed = False

    def _onClickResetButton(self, event):
        focus = self.tab2.sortable_list_ctrl.GetFocusedItem()
        product = self.tab2.sortable_list_ctrl.GetItem(focus, 0).GetText()
        stock_old = self.tab2.sortable_list_ctrl.GetItem(focus, 2).GetText()
        result = self.parent.show_confirm_dialog(f'Do you want to reset the new stock for {product}?')
        if result:
            self.tab2.sortable_list_ctrl.SetItem(focus, 3, stock_old)

    def _onClickAddButton(self, event):
        btnId = event.GetEventObject().GetId()
        addition_to_stock = (btnId - 6000)
        focus = self.tab2.sortable_list_ctrl.GetFocusedItem()
        stock_new = int(self.tab2.sortable_list_ctrl.GetItem(focus, 3).GetText())
        stock_new = stock_new + addition_to_stock
        self.tab2.sortable_list_ctrl.SetItem(focus, 3, str(stock_new))
        self.changed = True

    def _onClickPayButton(self, event):
        focus = self.tab1.sortable_list_ctrl.GetFocusedItem()
        user = self.tab1.sortable_list_ctrl.GetItem(focus, 0).GetText()
        result = self.parent.show_confirm_dialog(f'Do you want to set all purchases of user {user} as paid?')
        if result:
            self.tab1.sortable_list_ctrl.SetItem(focus, 2, '0.00')
            self.changed = True
