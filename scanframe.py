
import os
import wx

import functions


class ScanFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        wx.Frame.__init__(self, None, title="ScanFrame", style=wx.DEFAULT_FRAME_STYLE)
        self.panel = wx.Panel(self)
        self.parent = parent

        with self.parent as prt:
            self.btnNoCode = wx.Button(self.panel, id=wx.ID_ANY, label="no barcode", name="no barcode",
                                       size=wx.Size(prt.btnWidth, prt.btnHeight),
                                       pos=(prt.screen_width - 3*prt.btnWidth,
                                            prt.screen_height - prt.btnHeight))
            self.btnNoCode.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnNoCode.Bind(wx.EVT_LEFT_UP, self._onClickNoCodeButton)
            self.btnNoCode.Disable()
            self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label="back", name="back",
                                     size=wx.Size(prt.btnWidth, prt.btnHeight),
                                     pos=(prt.screen_width - 2*prt.btnWidth,
                                          prt.screen_height - prt.btnHeight))
            self.btnBack.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)
            self.btnConfirm = wx.Button(self.panel, id=wx.ID_ANY, label="confirm", name="confirm",
                                        size=wx.Size(prt.btnWidth, prt.btnHeight),
                                        pos=(prt.screen_width - 1*prt.btnWidth,
                                             prt.screen_width - prt.btnHeight))
            self.btnConfirm.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnConfirm.Bind(wx.EVT_LEFT_UP, self._onClickConfirmButton)
            self.btnConfirm.Disable()

            self.Text = wx.StaticText(self.panel, label=(prt.clickedUser + ", what can I get you?"),
                                      pos=(prt.screen_width / 5, prt.screen_height * 1 / 5), size=(150, 50))
            self.Text.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))

            self.Code = wx.TextCtrl(self.panel, pos=(prt.screen_width / 5, prt.screen_height * 1 / 5 + 70),
                                    size=(320, 50))
            self.Code.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.Code.SetMaxLength(13)
            self.Code.SetFocus()
            self.Code.Bind(wx.EVT_TEXT, self._onChangeCode)

            self.Product = wx.StaticText(self.panel, label="",
                                         pos=(prt.screen_width / 5, prt.screen_height * 1 / 5 + 150),
                                         size=(150, 50))
            self.Product.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.ShowFullScreen(True)

    def _onClickNoCodeButton(self, event):
        """"""
        self.btnNoCode.Disable()
        self.Code.Hide()
        self.cmbProducts = wx.ComboBox(self.panel, id=wx.ID_ANY,
                                       pos=(self.parent.getWidth() / 5,
                                            self.parent.getHeight() * 1 / 5 + 70),
                                       size=(320, 50))
        nrProducts = len(self.parent.products)

    def _onClickBackButton(self, event):
        """"""
        self.Close()

    def _onClickConfirmButton(self, event):
        """"""
        self.Disable()
        self.btnConfirm.SetLabel("saving...")

        if not ('BARCODE_DEV' in os.environ or 'BARCODE_TEST' in os.environ):
            # check local repo for changes
            functions.gitPull("./.")

        functions.savePurchase(user=self.parent.clickedUser, code=self.Code.GetValue())

        if not ('BARCODE_DEV' in os.environ or 'BARCODE_TEST' in os.environ):
            # commit & push purchase
            functions.gitPush("./.")
        self.Close()

    def _onChangeCode(self, event):
        """"""
        code = self.Code.GetValue()
        if len(code) in self.parent.getLengthCode():
            prod_df = self.parent.getProducts()
            select_df = prod_df[prod_df['code'] == code]
            if not select_df.empty:
                ind = select_df.first_valid_index()
                self.Product.SetLabel(str(select_df.at[ind, 'desc']) + "\t Price: " +
                                      "{:.2f}".format(select_df.at[ind, 'price']))
                self.btnConfirm.Enable()
                return None
        self.Product.SetLabel("")
        self.btnConfirm.Disable()
