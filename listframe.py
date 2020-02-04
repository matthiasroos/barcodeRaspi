
import os
import sys
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
            self.panel = wx.Panel(self)
            notebook = wx.Notebook(self.panel, pos=(0, 0), size=wx.Size(prt.screen_width-prt.btnWidth, prt.screen_height))

            tab1 = sortable.SortableListCtrlPanel(parent=notebook, super_parent=prt,
                                                  columns={'names': ['name', 'drinks', 'money'], 'width': [180, 180, 180]},
                                                  data_frame=functions.summarizeUserPurchases())
            tab2 = TabTwo(notebook)
            tab3 = sortable.SortableListCtrlPanel(parent=notebook, super_parent=prt,
                                                  columns={'names': ['xxx', 'yyy', 'zzz'], 'width': [180, 180, 180]},
                                                  data_frame=None)
            notebook.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            notebook.AddPage(tab1, 'USER')
            notebook.AddPage(tab2, 'STOCK')
            notebook.AddPage(tab3, 'XYZ')

            self.btnClose = wx.Button(self.panel, id=wx.ID_ANY, label='close', name='close',
                                      size=wx.Size(prt.btnWidth, prt.btnHeight),
                                      pos=(prt.screen_width - prt.btnWidth, 0))
            self.btnClose.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnClose.Bind(wx.EVT_LEFT_UP, self._onClickCloseButton)

            self.btnRestart = wx.Button(self.panel, id=wx.ID_ANY, label='restart', name='restart',
                                        size=wx.Size(prt.btnWidth, prt.btnHeight),
                                        pos=(prt.screen_width - prt.btnWidth, prt.btnHeight))
            self.btnRestart.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnRestart.Bind(wx.EVT_LEFT_UP, self._onClickRestartButton)

            self.btnBack = wx.Button(self.panel, id=wx.ID_ANY, label='back', name='back',
                                     size=wx.Size(prt.btnWidth, prt.btnHeight),
                                     pos=(prt.screen_width - 1*prt.btnWidth, prt.screen_height - prt.btnHeight))
            self.btnBack.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

        self.ShowFullScreen(True)

    def _onClickCloseButton(self, event):
        """"""
        sys.exit()

    def _onClickBackButton(self, event):
        """"""
        self.Close()

    def _onClickRestartButton(self, event):
        """"""
        self.parent.restart()



