import wx
import wx.grid
import time
import os.path
from typing import Optional, Tuple


class EditFrame(wx.Frame):

    def __init__(self, parent, number: int, old_values: Optional[Tuple[str, str, str]]):
        """Constructor"""

        frameWidth = 500
        frameHeight = 500

        self.parent = parent
        self.number = number

        if old_values is None:
            self.mode = 'add'
            title = 'Add entry'
            code, desc, price = '', '', ''
        else:
            self.mode = 'edit'
            title = 'Edit entry'
            code, desc, price = old_values

        wx.Frame.__init__(self, None, title=title, size=(frameWidth, frameHeight))

        with self.parent as prt:

            self.NummerTxt = wx.StaticText(self, label=f'# {self.number}', pos=(40, 20), size=(20, 50))
            self.NummerTxt.SetFont(prt.displaySettings.wxFont)

            CodeTxt = wx.StaticText(self, label='code', pos=(40, 70), size=(20, 50))
            CodeTxt.SetFont(prt.displaySettings.wxFont)
            self.CodeInp = wx.TextCtrl(self, value=code, pos=(140, 60), size=(300, 50))
            self.CodeInp.SetFont(prt.displaySettings.wxFont)
            self.CodeInp.SetMaxLength(13)
            self.CodeInp.SetFocus()

            DescTxt = wx.StaticText(self, label='descr.', pos=(40, 125), size=(20, 50))
            DescTxt.SetFont(prt.displaySettings.wxFont)
            self.DescInp = wx.TextCtrl(self, value=desc, pos=(140, 115), size=(300, 50))
            self.DescInp.SetMaxLength(30)
            self.DescInp.SetFont(prt.displaySettings.wxFont)

            PriceTxt = wx.StaticText(self, label="price", pos=(40, 180), size=(20, 50))
            PriceTxt.SetFont(prt.displaySettings.wxFont)
            self.PriceInp = wx.TextCtrl(self, value=price, pos=(140, 170), size=(300, 50))
            self.PriceInp.SetMaxLength(6)
            self.PriceInp.SetFont(prt.displaySettings.wxFont)

            btnBack = wx.Button(self, id=wx.ID_ANY, label="back", name="back",
                                size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                pos=(100, frameHeight - 2 * prt.displaySettings.btnHeight))
            btnBack.SetFont(prt.displaySettings.wxFont)
            btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

            btnConfirm = wx.Button(self, id=wx.ID_ANY, label="confirm", name="confirm",
                                   size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                   pos=(100 + prt.displaySettings.btnWidth + 5,
                                        frameHeight - 2 * prt.displaySettings.btnHeight))
            btnConfirm.SetFont(prt.displaySettings.wxFont)
            btnConfirm.Bind(wx.EVT_LEFT_UP, self._onClickConfirmButton)
            # btnConfirm.Disable()

        self.Show()

    def _onClickBackButton(self, event):
        """"""
        self.Close()

    def _onClickConfirmButton(self, event):
        """"""
        code = self.CodeInp.GetValue()
        desc = self.DescInp.GetValue()
        price = self.PriceInp.GetValue()

        if self.parent.check_item(number=self.number, code=code, mode=self.mode):
            if self.mode == 'add':
                self.parent.add_item(number=self.number, code=code, desc=desc, price=price)
            if self.mode == 'edit':
                self.parent.edit_item(number=self.number, code=code, desc=desc, price=price)
            self.Close()


