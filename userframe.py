
import os
import wx

import functions
import getraenkeKasse
import listframe
import scanframe

btnHeight = 80
btnWidth = 200
fontSize = 25


class UserFrame(wx.Frame):

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Test Fullscreen")
        self.panel = wx.Panel(self)

        if 'BARCODE_DEV' in os.environ:
            self._width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)/2
        else:
            self._width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self._height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        # read User list
        self._users = functions.readUsers()
        nrUsers = len(self._users)

        # read Product list
        self._LenCode = functions.calcLengthCode(self._products_df)
        self._products_df = functions.readProducts()

        offset = 10
        posX = offset
        posY = offset

        # User buttons
        self.button = []
        for i in range(0, nrUsers):
            self.button.append(wx.Button(self.panel, id=wx.ID_ANY, label=self._users[i], name=self._users[i],
                                         size=wx.Size(btnWidth, btnHeight), pos=(posX, posY)))
            self.button[i].SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.button[i].Bind(wx.EVT_LEFT_UP, self._onClickNameButton)
            # self.buildButtons(button[i])
            if (posY + 2 * btnHeight + offset) < self._height:
                posY = posY + btnHeight + offset
            else:
                posY = offset
                posX = posX + btnWidth + offset

        # List button
        self.btnList = wx.Button(self.panel, id=wx.ID_ANY, label="List", name="list", size=wx.Size(btnWidth, btnHeight),
                                 pos=(self._width - 1*btnWidth, self._height - btnHeight))
        self.btnList.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnList.Bind(wx.EVT_LEFT_UP, self._onClickListButton)

        self.textVersion = wx.StaticText(self.panel, label='ver. ' + getraenkeKasse.version,
                                         size=wx.Size(btnWidth, btnHeight),
                                         pos=(self._width - 1*btnWidth, self._height - 1.7 * btnHeight))
        self.textVersion.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.SetBackgroundColour("Gray")
        self.ShowFullScreen(True)

    def _onClickNameButton(self, event):
        """"""
        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)
        self.user = button_by_id.GetLabel()
        scanframe.ScanFrame(self)

    def _onClickListButton(self, event):
        """"""
        listframe.ListFrame(self)

    def getWidth(self):
        """"""
        return self._width

    def getHeight(self):
        """"""
        return self._height

    def getLengthCode(self):
        """"""
        return self._LenCode

    def getProducts(self):
        """"""
        return self._products_df

