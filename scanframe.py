
import os
import wx

import functions

btnHeight = 80
btnWidth = 200
fontSize = 25


class ScanFrame(wx.Frame):

    def __init__(self, userframe):
        """Constructor"""
        wx.Frame.__init__(self, None, title="ScanFrame", style=wx.DEFAULT_FRAME_STYLE)
        self.panel = wx.Panel(self)
        self.userframeObj = userframe

        self.btnNoCode = wx.Button(self.panel, id=wx.ID_ANY, label="no barcode", name="no barcode",
                                   size=wx.Size(btnWidth, btnHeight),
                                   pos=(self.userframeObj.getWidth() - 3*btnWidth,
                                        self.userframeObj.getHeight() - btnHeight))
        self.btnNoCode.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnNoCode.Bind(wx.EVT_LEFT_UP, self._onClickNoCodeButton)
        self.btnNoCode.Disable()
        self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label="back", name="back",
                                 size=wx.Size(btnWidth, btnHeight),
                                 pos=(self.userframeObj.getWidth() - 2*btnWidth,
                                      self.userframeObj.getHeight() - btnHeight))
        self.btnBack.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)
        self.btnConfirm = wx.Button(self.panel, id=wx.ID_ANY, label="confirm", name="confirm",
                                    size=wx.Size(btnWidth, btnHeight),
                                    pos=(self.userframeObj.getWidth() - 1*btnWidth,
                                         self.userframeObj.getHeight() - btnHeight))
        self.btnConfirm.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnConfirm.Bind(wx.EVT_LEFT_UP, self._onClickConfirmButton)
        self.btnConfirm.Disable()

        self.Text = wx.StaticText(self.panel, label=(self.userframeObj.user + ", what can I get you?"),
                                  pos=(self.userframeObj.getWidth()/5,
                                       self.userframeObj.getHeight()*1/5), size=(150, 50))
        self.Text.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.Code = wx.TextCtrl(self.panel,
                                pos=(self.userframeObj.getWidth()/5, self.userframeObj.getHeight()*1/5 + 70),
                                size=(320, 50))
        self.Code.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Code.SetMaxLength(13)
        self.Code.SetFocus()
        self.Code.Bind(wx.EVT_TEXT, self._onChangeCode)

        self.Product = wx.StaticText(self.panel, label="", pos=(
            self.userframeObj.getWidth() / 5, self.userframeObj.getHeight() * 1 / 5 + 150), size=(150, 50))
        self.Product.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.ShowFullScreen(True)

    def _onClickNoCodeButton(self, event):
        """"""
        self.btnNoCode.Disable()
        self.Code.Hide()
        self.cmbProducts = wx.ComboBox(self.panel, id=wx.ID_ANY,
                                       pos=(self.userframeObj.getWidth()/5,
                                            self.userframeObj.getHeight()*1/5 + 70),
                                       size=(320, 50))
        nrProducts = len(self.userframeObj.products)

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

        functions.savePurchase(user=self.userframeObj.user, code=self.Code.GetValue())

        if not ('BARCODE_DEV' in os.environ or 'BARCODE_TEST' in os.environ):
            # commit & push purchase
            functions.gitPush("./.")
        self.Close()

    def _onChangeCode(self, event):
        """"""
        code = self.Code.GetValue()
        if len(code) in self.userframeObj.getLengthCode():
            prod_df = self.userframeObj.getProducts()
            select_df = prod_df[prod_df['code'] == code]
            if not select_df.empty:
                ind = select_df.first_valid_index()
                self.Product.SetLabel(str(select_df.at[ind, 'desc']) + "\t Price: " +
                                      "{:.2f}".format(select_df.at[ind, 'price']))
                self.btnConfirm.Enable()
                return None
        self.Product.SetLabel("")
        self.btnConfirm.Disable()
