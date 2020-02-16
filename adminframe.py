
import wx

import functions


class AdminFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        wx.Frame.__init__(self, None, title='AdminFrame', style=wx.DEFAULT_FRAME_STYLE)
        with self.parent as prt:
            self.panel = wx.Panel(self)
            notebook = wx.Notebook(self.panel, pos=(0, 0),
                                   size=wx.Size(prt.screen_width-prt.btnWidth, prt.screen_height))

            tab1 = UserTab(parent=notebook, super_parent=prt)
            tab2 = StockTab(parent=notebook, super_parent=prt)
            notebook.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            notebook.AddPage(tab1, 'USER')
            notebook.AddPage(tab2, 'STOCK')

            self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
                                     size=wx.Size(prt.btnWidth, prt.btnHeight),
                                     pos=(prt.screen_width - 1 * prt.btnWidth, prt.screen_height - prt.btnHeight))
            self.btnBack.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

        self.ShowFullScreen(True)

    def _onClickBackButton(self, event):
        """"""
        self.Close()


class UserTab(wx.Panel):

    def __init__(self, parent, super_parent):
        self.parent = parent
        self.super_parent = super_parent
        wx.Panel.__init__(self, parent)
        with self.super_parent as sprt:
            pass
            #self.Text = wx.StaticText(parent, label='User:',
            #                          pos=(sprt.screen_width / 5, sprt.screen_height * 1 / 5), size=(150, 50))
            t = wx.StaticText(self, -1, "User:", (20, 20))

        # self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
        #                         size=wx.Size(prt.btnWidth, prt.btnHeight),
        #                         pos=(prt.screen_width - 1 * prt.btnWidth, prt.screen_height - prt.btnHeight))
        # self.btnBack.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        # self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)


class StockTab(wx.Panel):

    def __init__(self, parent, super_parent):
        self.parent = parent
        self.super_parent = super_parent
        wx.Panel.__init__(self, parent)
        with self.super_parent as sprt:
            pass
