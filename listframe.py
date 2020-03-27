
import wx

import functions
import sortable


class TabTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is the second tab", (20, 20))


class ListFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        wx.Frame.__init__(self, None, title='ListFrame', style=wx.DEFAULT_FRAME_STYLE)
        with self.parent as prt:
            prt.get_purchases()
            prt.get_products()
            self.panel = wx.Panel(self)
            notebook = wx.Notebook(self.panel, pos=(0, 0),
                                   size=wx.Size(prt.displaySettings.screen_width-prt.displaySettings.btnWidth,
                                                prt.displaySettings.screen_height))

            tab1 = sortable.SortableListCtrlPanel(parent=notebook, super_parent=prt,
                                                  columns={'names': ['name', 'drinks', 'money'],
                                                           'width': [180, 180, 180],
                                                           'type': [str, int, '{:,.2f}'.format]},
                                                  data_frame=functions.summarize_user_purchases(
                                                      purchases=prt.fileContents.purchases,
                                                      products=prt.fileContents.products))
            tab2 = TabTwo(notebook)
            notebook.SetFont(wx.Font(prt.displaySettings.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            notebook.AddPage(tab1, 'USER')
            notebook.AddPage(tab2, 'STOCK')

            self.btnClose = wx.Button(self.panel, id=wx.ID_ANY, label='close', name='close',
                                      size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                      pos=(prt.displaySettings.screen_width - prt.displaySettings.btnWidth, 0))
            self.btnClose.SetFont(wx.Font(prt.displaySettings.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnClose.Bind(wx.EVT_LEFT_UP, self._onClickCloseButton)

            self.btnRestart = wx.Button(self.panel, id=wx.ID_ANY, label='restart', name='restart',
                                        size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                        pos=(prt.displaySettings.screen_width - prt.displaySettings.btnWidth,
                                             prt.displaySettings.btnHeight))
            self.btnRestart.SetFont(wx.Font(prt.displaySettings.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnRestart.Bind(wx.EVT_LEFT_UP, self._onClickRestartButton)

            self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
                                     size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                     pos=(prt.displaySettings.screen_width - 1*prt.displaySettings.btnWidth,
                                          prt.displaySettings.screen_height - prt.displaySettings.btnHeight))
            self.btnBack.SetFont(wx.Font(prt.displaySettings.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

        self.ShowFullScreen(True)

    def _onClickCloseButton(self, event):
        """"""
        self.parent.exit()

    def _onClickBackButton(self, event):
        """"""
        self.Close()

    def _onClickRestartButton(self, event):
        """"""
        self.parent.restart()



