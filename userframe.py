import wx


class UserFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        wx.Frame.__init__(self, None, title="UserFrame")
        self.panel = wx.Panel(self)

        offset = self.parent.displaySettings.offSet
        posX = offset
        posY = offset

        with self.parent as prt:
            # User buttons
            self.button = []
            for i in range(0, len(prt.fileContents.users)):
                self.button.append(wx.Button(self.panel, id=wx.ID_ANY, label=prt.fileContents.users[i],
                                             name=prt.fileContents.users[i],
                                             size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                             pos=(posX, posY)))
                self.button[i].SetFont(prt.displaySettings.wxFont)
                self.button[i].Bind(wx.EVT_LEFT_UP, self._onClickNameButton)
                if (posY + 2 * prt.displaySettings.btnHeight + offset) < prt.displaySettings.screen_height:
                    posY = posY + prt.displaySettings.btnHeight + offset
                else:
                    posY = offset
                    posX = posX + prt.displaySettings.btnWidth + offset

            # List button
            self.btnList = wx.Button(self.panel, id=wx.ID_ANY, label="List", name="list",
                                     size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                     pos=(prt.displaySettings.screen_width - 1*prt.displaySettings.btnWidth,
                                          prt.displaySettings.screen_height - prt.displaySettings.btnHeight))
            self.btnList.SetFont(prt.displaySettings.wxFont)
            self.btnList.Bind(wx.EVT_LEFT_UP, self._onClickListButton)

            # Admin button
            self.btnAdmin = wx.Button(self.panel, id=wx.ID_ANY, label="Admin", name="admin",
                                      size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                      pos=(prt.displaySettings.screen_width - 1*prt.displaySettings.btnWidth,
                                           prt.displaySettings.screen_height - 2*prt.displaySettings.btnHeight))
            self.btnAdmin.SetFont(prt.displaySettings.wxFont)
            self.btnAdmin.Bind(wx.EVT_LEFT_UP, self._onClickAdminButton)

            self.textVersion = wx.StaticText(self.panel, label='ver. ' + prt.version,
                                             size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                             pos=(prt.displaySettings.screen_width - 1*prt.displaySettings.btnWidth,
                                                  prt.displaySettings.screen_height - 2.7*prt.displaySettings.btnHeight))
            self.textVersion.SetFont(prt.displaySettings.wxFont)
            self.SetBackgroundColour("Gray")

        self.ShowFullScreen(True)

    def _onClickNameButton(self, event):
        """"""
        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)
        self.parent.clicked_user = button_by_id.GetLabel()
        self.parent.show_scan_frame()

    def _onClickListButton(self, event):
        """"""
        self.parent.show_list_frame()

    def _onClickAdminButton(self, event):
        """"""
        self.parent.show_admin_frame()
