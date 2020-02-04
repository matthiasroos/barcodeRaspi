
import os
import wx

import functions


class UserFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        wx.Frame.__init__(self, None, title="Test Fullscreen")
        self.panel = wx.Panel(self)

        # read User list
        self._users = functions.readUsers()
        nrUsers = len(self._users)

        # read Product list
        self._products_df = functions.readProducts()
        self._LenCode = functions.calcLengthCode(self._products_df)

        offset = 10
        posX = offset
        posY = offset

        with self.parent as prt:
            # User buttons
            self.button = []
            for i in range(0, nrUsers):
                self.button.append(wx.Button(self.panel, id=wx.ID_ANY, label=self._users[i], name=self._users[i],
                                             size=wx.Size(prt.btnWidth, prt.btnHeight), pos=(posX, posY)))
                self.button[i].SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
                self.button[i].Bind(wx.EVT_LEFT_UP, self._onClickNameButton)
                # self.buildButtons(button[i])
                if (posY + 2 * prt.btnHeight + offset) < prt.screen_height:
                    posY = posY + prt.btnHeight + offset
                else:
                    posY = offset
                    posX = posX + prt.btnWidth + offset

            # List button
            self.btnList = wx.Button(self.panel, id=wx.ID_ANY, label="List", name="list",
                                     size=wx.Size(prt.btnWidth, prt.btnHeight),
                                     pos=(prt.screen_width - 1*prt.btnWidth, prt.screen_height - prt.btnHeight))
            self.btnList.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.btnList.Bind(wx.EVT_LEFT_UP, self._onClickListButton)

            self.textVersion = wx.StaticText(self.panel, label='ver. ' + prt.version,
                                             size=wx.Size(prt.btnWidth, prt.btnHeight),
                                             pos=(prt.screen_width - 1*prt.btnWidth,
                                                  prt.screen_height - 1.7*prt.btnHeight))
            self.textVersion.SetFont(wx.Font(prt.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.SetBackgroundColour("Gray")

        self.ShowFullScreen(True)

    def _onClickNameButton(self, event):
        """"""
        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)
        self.parent.clickedUser = button_by_id.GetLabel()
        self.parent.showScanFrame()

    def _onClickListButton(self, event):
        """"""
        self.parent.showListFrame()

    def getLengthCode(self):
        """"""
        return self._LenCode

    def getProducts(self):
        """"""
        return self._products_df

