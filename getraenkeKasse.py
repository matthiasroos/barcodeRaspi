#!/usr/bin/python3

import os
import sys
import time

import wx

import adminframe
import functions
import listframe
import scanframe
import userframe

version = '0.1.2'
btnHeight = 80
btnWidth = 200
fontSize = 25


class GetraenkeKasse():

    def __init__(self):
        self.products = None
        self.version = version
        self.btnHeight = btnHeight
        self.btnWidth = btnWidth
        self.fontSize = fontSize
        self.purchases = None
        self.users = None
        self._clicked_user = None

        self.app = wx.App(False)
        if 'BARCODE_DEV' in os.environ:
            self.screen_width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)/2
        else:
            self.screen_width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self.screen_height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def run(self):
        self.get_users()
        self.get_products()
        userframe.UserFrame(self)
        self.app.MainLoop()

    def exit(self):
        sys.exit()

    def restart(self):
        os.execl(sys.executable, sys.executable, *sys.argv)
        sys.exit()

    def show_admin_frame(self):
        adminframe.AdminFrame(self)

    def show_list_frame(self):
        listframe.ListFrame(self)

    def show_scan_frame(self):
        scanframe.ScanFrame(self)

    def show_error_dialog(self, error_message: str):
        dlg = wx.MessageDialog(None, message=error_message, caption='ERROR', style=wx.OK | wx.ICON_WARNING)
        dlg.SetFont(wx.Font(self.fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        dlg.ShowModal()

    def get_users(self):
        self.users = functions.read_users()

    def get_products(self):
        self.products = functions.read_products()

    @property
    def clicked_user(self) -> str:
        return self._clicked_user

    @clicked_user.setter
    def clicked_user(self, user: str):
        self._clicked_user = user


if __name__ == "__main__":

    gk = GetraenkeKasse()
    if 'BARCODE_DEV' not in os.environ:
        # check network
        if not functions.checkNetwork():
            gk.show_error_dialog(error_message='No network available. Exiting...')
            sys.exit()

        # test local time
        timeT = functions.getTimefromNTP()
        if timeT[0] != time.ctime():
            gk.show_error_dialog(error_message='Date/time not synchronized with NTP. Exiting...')
            sys.exit()

    if not ('BARCODE_DEV' in os.environ or 'BARCODE_TEST' in os.environ):
        print('yes2')
        # check for new commits in local repository
        if not functions.git_pull("./."):
            gk.show_error_dialog(error_message='Problem with git (local repo). Exiting...')
            sys.exit()

        # check for new version of getraenkeKasse.py script on github
        hasher_old = functions.getMD5Hash("barcodeRaspi/getraenkeKasse.py")
        if not functions.git_pull("barcodeRaspi"):
            gk.show_error_dialog(error_message='Problem with git (GitHub). Exiting...')
            sys.exit()

        hasher_new = functions.getMD5Hash("barcodeRaspi/getraenkeKasse.py")
        if hasher_new.hexdigest() != hasher_old.hexdigest():
            # getraenkeKasse.py has changed, script is restarted
            print("new version from gitHub, script is restarting...")
            gk.restart()

    gk.run()
