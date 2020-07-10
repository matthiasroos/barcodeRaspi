import wx
import wx.grid
import time
import os.path


class EditFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        frameWidth = 500
        frameHeight = 500
        wx.Frame.__init__(self, None, title="Add entry", size=(frameWidth, frameHeight))

        self.mode = "add"
        self.number = frame.prodList.GetItemCount()
        self.NummerTxt = wx.StaticText(self, label=("# " + str(self.number + 1)), pos=(40, 20), size=(20, 50))
        self.NummerTxt.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))

        CodeTxt = wx.StaticText(self, label="code", pos=(40, 70), size=(20, 50))
        CodeTxt.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.CodeInp = wx.TextCtrl(self, pos=(140, 60), size=(300, 50))
        self.CodeInp.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.CodeInp.SetMaxLength(13)
        self.CodeInp.SetFocus()

        DescTxt = wx.StaticText(self, label="descr.", pos=(40, 125), size=(20, 50))
        DescTxt.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.DescInp = wx.TextCtrl(self, pos=(140, 115), size=(300, 50))
        self.DescInp.SetMaxLength(30)
        self.DescInp.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))

        PriceTxt = wx.StaticText(self, label="price", pos=(40, 180), size=(20, 50))
        PriceTxt.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.PriceInp = wx.TextCtrl(self, pos=(140, 170), size=(300, 50))
        self.PriceInp.SetMaxLength(6)
        self.PriceInp.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))

        btnBack = wx.Button(self, id=wx.ID_ANY, label="back", name="back", size=wx.Size(btnWidth, btnHeight),
                            pos=(100, frameHeight - btnHeight))
        btnBack.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

        btnConfirm = wx.Button(self, id=wx.ID_ANY, label="confirm", name="confirm", size=wx.Size(btnWidth, btnHeight),
                               pos=(100 + btnWidth + 5, frameHeight - btnHeight))
        btnConfirm.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        btnConfirm.Bind(wx.EVT_LEFT_UP, self._onClickConfirmButton)
        # btnConfirm.Disable()

        self.Show()

    def initValuesEdit(self, number, code, desc, price):
        """"""
        self.number = number
        self.mode = "edit"
        self.NummerTxt.SetLabel("# " + number)
        self.CodeInp.SetValue(code)
        self.DescInp.SetValue(desc)
        self.PriceInp.SetValue(price)
        self.SetTitle("Edit entry")

    def _onClickBackButton(self, event):
        """"""
        self.Close()

    def _onClickConfirmButton(self, event):
        """"""
        nr = frame.prodList.GetItemCount()
        code = self.CodeInp.GetValue()
        if self.mode == "add":
            # add mode
            for i in range(frame.prodList.GetItemCount()):
                if (code == frame.prodList.GetItemText(i, 1)):
                    # code is already in list
                    return
            frame.prodList.Append \
                ([str(nr + 1), self.CodeInp.GetValue(), self.DescInp.GetValue(), self.PriceInp.GetValue()])
        elif self.mode == "edit":
            # edit mode
            ind = int(self.number) - 1
            for i in range(frame.prodList.GetItemCount()):
                if code == frame.prodList.GetItemText(i, 1):
                    if i != ind:
                        # code was changed to one already in list
                        return
            frame.prodList.SetStringItem(ind, 0, str(self.number))
            frame.prodList.SetStringItem(ind, 1, self.CodeInp.GetValue())
            frame.prodList.SetStringItem(ind, 2, self.DescInp.GetValue())
            frame.prodList.SetStringItem(ind, 3, self.PriceInp.GetValue())
        self.Close()
