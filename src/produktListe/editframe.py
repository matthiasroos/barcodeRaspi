
from typing import Optional, Tuple

import wx
import wx.grid


class EditFrame(wx.Frame):

    def __init__(self, parent, number: int, old_values: Optional[Tuple[str, str, str]]):
        """Constructor"""

        frame_width = 500
        frame_height = 500

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

        wx.Frame.__init__(self, None, title=title, size=(frame_width, frame_height))

        self.input_names = ['nr', 'code', 'desc', 'price']
        self.input_list = [self.number]

        with self.parent as prt:

            nummer_txt = wx.StaticText(self, label=f'# {self.number}', pos=(40, 20), size=(20, 50))
            nummer_txt.SetFont(prt.display_settings.wx_font)

            code_txt = wx.StaticText(self, label='code', pos=(40, 70), size=(20, 50))
            code_txt.SetFont(prt.display_settings.wx_font)
            code_inp = wx.TextCtrl(self, value=code, pos=(140, 60), size=(300, 50))
            code_inp.SetFont(prt.display_settings.wx_font)
            code_inp.SetMaxLength(13)
            code_inp.SetFocus()
            self.input_list.append(code_inp)

            desc_txt = wx.StaticText(self, label='descr.', pos=(40, 125), size=(20, 50))
            desc_txt.SetFont(prt.display_settings.wx_font)
            desc_inp = wx.TextCtrl(self, value=desc, pos=(140, 115), size=(300, 50))
            desc_inp.SetMaxLength(30)
            desc_inp.SetFont(prt.display_settings.wx_font)
            self.input_list.append(desc_inp)

            price_txt = wx.StaticText(self, label='price', pos=(40, 180), size=(20, 50))
            price_txt.SetFont(prt.display_settings.wx_font)
            price_inp = wx.TextCtrl(self, value=price, pos=(140, 170), size=(300, 50))
            price_inp.SetMaxLength(6)
            price_inp.SetFont(prt.display_settings.wx_font)
            self.input_list.append(price_inp)

            btn_back = wx.Button(self, id=wx.ID_ANY, label="back", name="back",
                                 size=wx.Size(prt.display_settings.btn_width, prt.display_settings.btn_height),
                                 pos=(100, frame_height - 2 * prt.display_settings.btn_height))
            btn_back.SetFont(prt.display_settings.wx_font)
            btn_back.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

            btn_confirm = wx.Button(self, id=wx.ID_ANY, label="confirm", name="confirm",
                                    size=wx.Size(prt.display_settings.btn_width, prt.display_settings.btn_height),
                                    pos=(100 + prt.display_settings.btn_width + 5,
                                         frame_height - 2 * prt.display_settings.btn_height))
            btn_confirm.SetFont(prt.display_settings.wx_font)
            btn_confirm.Bind(wx.EVT_LEFT_UP, self._onClickConfirmButton)
            # btn_confirm.Disable()

        self.Show()

    def _onClickBackButton(self, _) -> None:
        """"""
        self.Close()

    def _onClickConfirmButton(self, _) -> None:
        """"""
        values = {name: inp.GetValue() if isinstance(inp, wx.TextCtrl) else inp
                  for name, inp in zip(self.input_names, self.input_list)}

        # check if code is unique
        if self.parent.check_item(number=self.number, code=values['code'], mode=self.mode):
            if self.mode == 'add':
                # add new item, if input is sane
                if self.parent.add_item(values=values):
                    self.parent.update_product_listctrl()
                else:
                    return None
            if self.mode == 'edit':
                # change item, if input is sane
                if self.parent.edit_item(values=values):
                    self.parent.update_product_listctrl()
                else:
                    return None
            self.Close()
            return None
        self.parent.show_error_dialog(error_message='Code already exists in product list')
        return None
