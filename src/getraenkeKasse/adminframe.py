import wx

import functions
import src.getraenkeKasse.sortable


class AdminFrame(wx.Frame):
    """
    Frame to admin stock and purchases
    """

    def __init__(self, parent) -> None:
        """Constructor"""
        self.parent = parent
        self.changed = False
        wx.Frame.__init__(self, None, title='AdminFrame', style=wx.DEFAULT_FRAME_STYLE)
        with self.parent as prt:
            self.panel = wx.Panel(self)
            # prt.load_purchases()
            # prt.load_products()

            if not prt.show_password_dialog(password_message='Please enter administrator PIN'):
                self.Close()

            self.notebook = wx.Notebook(self.panel, pos=(0, 0),
                                        size=wx.Size(prt.display_settings.screen_width - prt.display_settings.btn_width,
                                                     prt.display_settings.screen_height))
            user_purchases_df = functions.summarize_user_purchases(
                purchases=prt.file_contents.purchases,
                products=prt.file_contents.products)[
                ['name', 'money']]
            user_purchases_df['new_mo'] = user_purchases_df['money']
            self.tab1 = src.getraenkeKasse.sortable.SortableListCtrlPanel(parent=self.notebook, super_parent=prt,
                                                                          columns={'names': ['name', 'money', 'new_mo'],
                                                                                   'width': [130, 130, 130],
                                                                                   'type': [str, '{:,.2f}'.format,
                                                                                            '{:,.2f}'.format]},
                                                                          data_frame=user_purchases_df)
            cp_products_df = prt.file_contents.products.copy()
            cp_products_df['new_st'] = cp_products_df['stock']
            self.tab2 = src.getraenkeKasse.sortable.SortableListCtrlPanel(parent=self.notebook, super_parent=prt,
                                                                          columns={'names': ['nr', 'desc', 'stock',
                                                                                             'new_st'],
                                                                                   'width': [80, 320, 100, 100],
                                                                                   'type': [int, str, int, int]},
                                                                          data_frame=cp_products_df[
                                                                              ['nr', 'desc', 'stock', 'new_st']])
            self.notebook.SetFont(prt.display_settings.wx_font)
            self.notebook.AddPage(self.tab1, 'USER')
            self.notebook.AddPage(self.tab2, 'STOCK')

            # Back button
            self.btn_back = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
                                      size=prt.display_settings.wx_button_size,
                                      pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                           prt.display_settings.screen_height - prt.display_settings.btn_height))
            self.btn_back.SetFont(prt.display_settings.wx_font)
            self.btn_back.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

            # Save button
            self.btn_save = wx.Button(self.panel, id=wx.ID_ANY, label='save', name='save',
                                      size=prt.display_settings.wx_button_size,
                                      pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                           prt.display_settings.screen_height - 2 * prt.display_settings.btn_height))
            self.btn_save.SetFont(prt.display_settings.wx_font)
            self.btn_save.Bind(wx.EVT_LEFT_UP, self._onClickSaveButton)

            # Reset button
            self.btn_reset = wx.Button(self.panel, id=wx.ID_ANY, label='reset stock', name='reset',
                                       size=prt.display_settings.wx_button_size,
                                       pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                            prt.display_settings.screen_height - 3 * prt.display_settings.btn_height))
            self.btn_reset.SetFont(prt.display_settings.wx_font)
            self.btn_reset.Bind(wx.EVT_LEFT_UP, self._onClickResetButton)

            # +12 button
            self.btn_twelve = wx.Button(self.panel, id=6012, label='+12', name='twelve',
                                        size=wx.Size(prt.display_settings.btn_width / 2,
                                                     prt.display_settings.btn_height),
                                        pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                             prt.display_settings.screen_height - 4 * prt.display_settings.btn_height))
            self.btn_twelve.SetFont(prt.display_settings.wx_font)
            self.btn_twelve.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            # + 20 button
            self.btn_twenty = wx.Button(self.panel, id=6020, label='+20', name='twenty',
                                        size=wx.Size(prt.display_settings.btn_width / 2,
                                                     prt.display_settings.btn_height),
                                        pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width / 2,
                                             prt.display_settings.screen_height - 4 * prt.display_settings.btn_height))
            self.btn_twenty.SetFont(prt.display_settings.wx_font)
            self.btn_twenty.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            # +1 button
            self.btn_one = wx.Button(self.panel, id=6001, label='+1', name='one',
                                     size=wx.Size(prt.display_settings.btn_width / 2, prt.display_settings.btn_height),
                                     pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                          prt.display_settings.screen_height - 5 * prt.display_settings.btn_height))
            self.btn_one.SetFont(prt.display_settings.wx_font)
            self.btn_one.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            # +5 button
            self.btn_five = wx.Button(self.panel, id=6005, label='+5', name='five',
                                      size=wx.Size(prt.display_settings.btn_width / 2, prt.display_settings.btn_height),
                                      pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width / 2,
                                           prt.display_settings.screen_height - 5 * prt.display_settings.btn_height))
            self.btn_five.SetFont(prt.display_settings.wx_font)
            self.btn_five.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            # Pay button
            self.btn_pay = wx.Button(self.panel, id=wx.ID_ANY, label='pay for user', name='pay',
                                     size=prt.display_settings.wx_button_size,
                                     pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                          prt.display_settings.screen_height - 6 * prt.display_settings.btn_height))
            self.btn_pay.SetFont(prt.display_settings.wx_font)
            self.btn_pay.Bind(wx.EVT_LEFT_UP, self._onClickPayButton)

        self.ShowFullScreen(True)

    def _onClickBackButton(self, _) -> None:
        """"""
        if self.changed:
            if not self.parent.show_confirm_dialog(confirm_message='Do you want to discard?'):
                return None
        self.Close()

    def _onClickSaveButton(self, _) -> None:
        """"""
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
                if stock_old != stock_new:
                    changed_stock.append([nr, stock_old, stock_new])

            result = self.parent.show_confirm_dialog('Do you want to save purchases/products?')
            if result:
                for user in user_paid:
                    self.parent.pay_for_user(user=user)
                self.parent.replenish_stock(changed_stock=changed_stock)
                self.changed = False

    def _onClickResetButton(self, _) -> None:
        """"""
        focus = self.tab2.sortable_list_ctrl.GetFocusedItem()
        product = self.tab2.sortable_list_ctrl.GetItem(focus, 0).GetText()
        stock_old = self.tab2.sortable_list_ctrl.GetItem(focus, 2).GetText()
        result = self.parent.show_confirm_dialog(f'Do you want to reset the new stock for {product}?')
        if result:
            self.tab2.sortable_list_ctrl.SetItem(focus, 3, stock_old)

    def _onClickAddButton(self, event) -> None:
        """"""
        btn_id = event.GetEventObject().GetId()
        addition_to_stock = (btn_id - 6000)
        focus = self.tab2.sortable_list_ctrl.GetFocusedItem()
        stock_new = int(self.tab2.sortable_list_ctrl.GetItem(focus, 3).GetText())
        stock_new = stock_new + addition_to_stock
        self.tab2.sortable_list_ctrl.SetItem(focus, 3, str(stock_new))
        self.changed = True

    def _onClickPayButton(self, _) -> None:
        """"""
        focus = self.tab1.sortable_list_ctrl.GetFocusedItem()
        user = self.tab1.sortable_list_ctrl.GetItem(focus, 0).GetText()
        result = self.parent.show_confirm_dialog(f'Do you want to set all purchases of user {user} as paid?')
        if result:
            self.tab1.sortable_list_ctrl.SetItem(focus, 2, '0.00')
            self.changed = True
