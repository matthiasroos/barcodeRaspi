
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

            self.Text = wx.StaticText(self.panel, label=(prt.clicked_user + ", what can I get you?"),
                                      pos=(prt.display_settings.screen_width / 5,
                                           prt.display_settings.screen_height * 1 / 5),
                                      size=(150, 50))
            self.Text.SetFont(prt.display_settings.wx_font)

            self.Code = wx.TextCtrl(self.panel, pos=(prt.display_settings.screen_width / 5,
                                                     prt.display_settings.screen_height * 1 / 5 + 70),
                                    size=(320, 50))
            self.Code.SetFont(prt.display_settings.wx_font)
            self.Code.SetMaxLength(13)
            self.Code.SetFocus()
            self.Code.Bind(wx.EVT_TEXT, self._onChangeCode)

            self.Product = wx.StaticText(self.panel, label="", pos=(prt.display_settings.screen_width/5,
                                                                    prt.display_settings.screen_height*1/5 + 150),
                                         size=(150, 50))
            self.Product.SetFont(prt.display_settings.wx_font)

        self.ShowFullScreen(True)

    def _onClickNoCodeButton(self, _) -> None:
        """"""
        self.btn_nocode.Disable()
        self.Code.Hide()
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
        self.parent.make_purchase(user=self.parent.clicked_user, code=self.Code.GetValue())
        self.Close()

    def _onChangeCode(self, _) -> None:
        """"""
        code = self.Code.GetValue()
        prod_df = self.parent.fileContents.products
        if len(code) in functions.calc_length_code(products_df=prod_df):
            select_df = prod_df[prod_df['code'] == code]
            if not select_df.empty:
                ind = select_df.first_valid_index()
                self.Product.SetLabel(label=f"{str(select_df.at[ind, 'desc'])}\t Price: " +
                                      "{:.2f}".format(select_df.at[ind, 'price']))
                self.btn_confirm.Enable()
                return None
        self.Product.SetLabel("")
        self.btn_confirm.Disable()
