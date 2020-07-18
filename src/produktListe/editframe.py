
from typing import Optional, Tuple

import wx
import wx.grid


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

        self.input_names = ['nr', 'code', 'desc', 'price']
        self.input_list = [self.number]

        with self.parent as prt:

            self.NummerTxt = wx.StaticText(self, label=f'# {self.number}', pos=(40, 20), size=(20, 50))
            self.NummerTxt.SetFont(prt.displaySettings.wxFont)

            CodeTxt = wx.StaticText(self, label='code', pos=(40, 70), size=(20, 50))
            CodeTxt.SetFont(prt.displaySettings.wxFont)
            CodeInp = wx.TextCtrl(self, value=code, pos=(140, 60), size=(300, 50))
            CodeInp.SetFont(prt.displaySettings.wxFont)
            CodeInp.SetMaxLength(13)
            CodeInp.SetFocus()
            self.input_list.append(CodeInp)

            DescTxt = wx.StaticText(self, label='descr.', pos=(40, 125), size=(20, 50))
            DescTxt.SetFont(prt.displaySettings.wxFont)
            DescInp = wx.TextCtrl(self, value=desc, pos=(140, 115), size=(300, 50))
            DescInp.SetMaxLength(30)
            DescInp.SetFont(prt.displaySettings.wxFont)
            self.input_list.append(DescInp)

            PriceTxt = wx.StaticText(self, label='price', pos=(40, 180), size=(20, 50))
            PriceTxt.SetFont(prt.displaySettings.wxFont)
            PriceInp = wx.TextCtrl(self, value=price, pos=(140, 170), size=(300, 50))
            PriceInp.SetMaxLength(6)
            PriceInp.SetFont(prt.displaySettings.wxFont)
            self.input_list.append(PriceInp)

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
        values = {name: Input.GetValue() if isinstance(Input, wx.TextCtrl) else Input
                  for name, Input in zip(self.input_names, self.input_list)}

        if self.parent.check_item(number=self.number, code=values['code'], mode=self.mode):
            if self.mode == 'add':
                if self.parent.add_item(values=values):
                    self.parent.update_product_listctrl()
                else:
                    return None
            if self.mode == 'edit':
                if self.parent.edit_item(values=values):
                    self.parent.update_product_listctrl()
                else:
                    return None
            self.Close()
        else:
            self.parent.show_error_dialog(error_message='Code already exists in product list')
