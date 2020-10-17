
import wx


class MainFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        self.parent = parent
        wx.Frame.__init__(self, None, title="UserFrame")
        self.panel = wx.Panel(self)

        off_set = self.parent.display_settings.off_set
        posX = off_set
        posY = off_set

        with self.parent as prt:
            # User buttons
            self.button = []
            for i, user in enumerate(prt.file_contents.users):
                self.button.append(wx.Button(self.panel, id=wx.ID_ANY, label=user, name=user,
                                             size=prt.display_settings.wx_button_size,
                                             pos=(posX, posY)))
                self.button[i].SetFont(prt.display_settings.wx_font)
                self.button[i].Bind(wx.EVT_LEFT_UP, self._onClickNameButton)
                if (posY + 2 * prt.display_settings.btn_height + off_set) < prt.display_settings.screen_height:
                    posY = posY + prt.display_settings.btn_height + off_set
                else:
                    posY = off_set
                    posX = posX + prt.display_settings.btn_width + off_set

            # List button
            self.btn_list = wx.Button(self.panel, id=wx.ID_ANY, label="List", name="list",
                                      size=prt.display_settings.wx_button_size,
                                      pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                           prt.display_settings.screen_height - prt.display_settings.btn_height))
            self.btn_list.SetFont(prt.display_settings.wx_font)
            self.btn_list.Bind(wx.EVT_LEFT_UP, self._onClickListButton)

            # Admin button
            self.btn_admin = wx.Button(self.panel, id=wx.ID_ANY, label="Admin", name="admin",
                                       size=prt.display_settings.wx_button_size,
                                       pos=(prt.display_settings.screen_width - 1 * prt.display_settings.btn_width,
                                            prt.display_settings.screen_height - 2 * prt.display_settings.btn_height))
            self.btn_admin.SetFont(prt.display_settings.wx_font)
            self.btn_admin.Bind(wx.EVT_LEFT_UP, self._onClickAdminButton)

            # Close Button
            self.btn_close = wx.Button(self.panel, id=wx.ID_ANY, label='close', name='close',
                                       size=prt.display_settings.wx_button_size,
                                       pos=(prt.display_settings.screen_width - prt.display_settings.btn_width, 0))
            self.btn_close.SetFont(prt.display_settings.wx_font)
            self.btn_close.Bind(wx.EVT_LEFT_UP, self._onClickCloseButton)

            # Restart Button
            self.btn_restart = wx.Button(self.panel, id=wx.ID_ANY, label='restart', name='restart',
                                         size=prt.display_settings.wx_button_size,
                                         pos=(prt.display_settings.screen_width - prt.display_settings.btn_width,
                                              prt.display_settings.btn_height))
            self.btn_restart.SetFont(prt.display_settings.wx_font)
            self.btn_restart.Bind(wx.EVT_LEFT_UP, self._onClickRestartButton)

            self.text_version = wx.StaticText(self.panel, label='ver. ' + prt.version,
                                              size=prt.display_settings.wx_button_size,
                                              pos=(
                                                  prt.display_settings.screen_width - 0.9 * prt.display_settings.btn_width,
                                                  prt.display_settings.screen_height - 2.7 * prt.display_settings.btn_height))
            self.text_version.SetFont(prt.display_settings.wx_font)
            self.SetBackgroundColour("Gray")

        self.ShowFullScreen(True)

    def _onClickNameButton(self, event) -> None:
        """"""
        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)
        self.parent.clicked_user = button_by_id.GetLabel()
        self.parent.show_scan_frame()

    def _onClickListButton(self, _) -> None:
        """"""
        self.parent.show_list_frame()

    def _onClickAdminButton(self, _) -> None:
        """"""
        self.parent.show_admin_frame()

    def _onClickCloseButton(self, _) -> None:
        """"""
        if self.parent.show_confirm_dialog(confirm_message='Do you want to exit?'):
            self.parent.exit()

    def _onClickRestartButton(self, _) -> None:
        """"""
        if self.parent.show_confirm_dialog(confirm_message='Do you want to restart?'):
            self.parent.restart()
