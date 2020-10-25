
import time

import wx

import functions


class ScanFrame(wx.Frame):
    """
    Frame to scan the products
    """

    def __init__(self, parent):
        """Constructor"""
        wx.Frame.__init__(self, None, title="ScanFrame", style=wx.DEFAULT_FRAME_STYLE)
        self.panel = wx.Panel(self)
        self.parent = parent

        self.counter = 1

        with self.parent as prt:
            prt.load_products()
            self.btn_nocode = wx.Button(self.panel, id=wx.ID_ANY, label="no barcode", name="no barcode",
                                        size=prt.display_settings.wx_button_size,
                                        pos=(prt.display_settings.screen_width - 3 * prt.display_settings.btn_width,
                                             prt.display_settings.screen_height - prt.display_settings.btn_height))
            self.btn_nocode.SetFont(prt.display_settings.wx_font)
            self.btn_nocode.Bind(wx.EVT_LEFT_UP, self._onClickNoCodeButton)
            self.btn_nocode.Disable()

            self.btn_back = wx.Button(self.panel, id=wx.ID_ANY, label="back", name="back",
                                      size=prt.display_settings.wx_button_size,
                                      pos=(prt.display_settings.screen_width - 2 * prt.display_settings.btn_width,
                                           prt.display_settings.screen_height - prt.display_settings.btn_height))
            self.btn_back.SetFont(prt.display_settings.wx_font)
            self.btn_back.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

            self.btn_confirm = wx.Button(self.panel, id=wx.ID_ANY, label="confirm", name="confirm",
                                         size=prt.display_settings.wx_button_size,
                                         pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                              prt.display_settings.screen_height - prt.display_settings.btn_height))
            self.btn_confirm.SetFont(prt.display_settings.wx_font)
            self.btn_confirm.Bind(wx.EVT_LEFT_UP, self._onClickConfirmButton)
            self.btn_confirm.Disable()

            self.txt_grt = wx.StaticText(self.panel, label=f'{prt.clicked_user}, what can I get you?',
                                         pos=(prt.display_settings.screen_width / 5,
                                              prt.display_settings.screen_height * 1 / 5),
                                         size=(150, 50))
            self.txt_grt.SetFont(prt.display_settings.wx_font)

            self.txt_code = wx.TextCtrl(self.panel, pos=(prt.display_settings.screen_width / 5,
                                                         prt.display_settings.screen_height * 1 / 5 + 70),
                                        size=(320, 50))
            self.txt_code.SetFont(prt.display_settings.wx_font)
            self.txt_code.SetMaxLength(13)
            self.txt_code.SetFocus()
            self.txt_code.Bind(wx.EVT_TEXT, self._onChangeCode)

            self.btn_plus = wx.Button(self.panel, id=7001, label='+', name='plus',
                                      size=wx.Size(prt.display_settings.btn_height,
                                                   prt.display_settings.btn_height),
                                      pos=(prt.display_settings.screen_width / 5 + 350,
                                           prt.display_settings.screen_height * 1 / 5 + 50))
            self.btn_plus.SetFont(prt.display_settings.wx_font)
            self.btn_plus.Bind(wx.EVT_LEFT_UP, self._onClickPlusMinusButton)

            self.btn_minus = wx.Button(self.panel, id=7002, label='-', name='minus',
                                       size=wx.Size(prt.display_settings.btn_height,
                                                    prt.display_settings.btn_height),
                                       pos=(
                                           prt.display_settings.screen_width / 5 + 360 + prt.display_settings.btn_height,
                                           prt.display_settings.screen_height * 1 / 5 + 50))
            self.btn_minus.SetFont(prt.display_settings.wx_font)
            self.btn_minus.Bind(wx.EVT_LEFT_UP, self._onClickPlusMinusButton)
            self.btn_minus.Disable()

            self.Product = wx.StaticText(self.panel, label="", pos=(prt.display_settings.screen_width/5,
                                                                    prt.display_settings.screen_height*1/5 + 150),
                                         size=(150, 50))
            self.Product.SetFont(prt.display_settings.wx_font)

        self.ShowFullScreen(True)

    def _onClickNoCodeButton(self, _) -> None:
        """"""
        self.btn_nocode.Disable()
        self.txt_code.Hide()
        self.cmbProducts = wx.ComboBox(self.panel, id=wx.ID_ANY,
                                       pos=(self.parent.display_settings.screen_width / 5,
                                            self.parent.display_settings.screen_height * 1 / 5 + 70),
                                       size=(320, 50))
        nrProducts = len(self.parent.products)

    def _onClickBackButton(self, _) -> None:
        """"""
        self.Close()

    def _onClickConfirmButton(self, _) -> None:
        """"""
        self.Disable()
        self.Update()
        functions.check_environment_ONLY_DEV(time.sleep(7))
        self.parent.make_purchase(user=self.parent.clicked_user,
                                  code=self.txt_code.GetValue(),
                                  count=self.counter)
        self.Close()

    def _onChangeCode(self, _) -> None:
        """"""
        code = self.txt_code.GetValue()
        prod_df = self.parent.file_contents.products
        if len(code) in functions.calc_length_code(products_df=prod_df):
            select_df = prod_df[prod_df['code'] == code]
            if not select_df.empty:
                ind = select_df.first_valid_index()
                price = select_df.at[ind, 'price']
                label = f"{select_df.at[ind, 'desc']}\t Price: {self.counter}x{price:.2f} = {self.counter * price:.2f}"
                self.Product.SetLabel(label=label)
                self.btn_confirm.Enable()
                return None
        self.Product.SetLabel("")
        self.btn_confirm.Disable()

    def _onClickPlusMinusButton(self, event) -> None:
        """"""
        btn_id = event.GetId()
        if btn_id == 7001:
            self.counter += 1
            self.btn_minus.Enable()
        else:
            self.counter -= 1
            if self.counter == 1:
                self.btn_minus.Disable()
        self._onChangeCode(None)
