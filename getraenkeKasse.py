#!/usr/bin/python3
import datetime

import os
import sys
import time
import wx

import functions
import userframe

version = '0.1.2'


def restart():
    os.execl(sys.executable, sys.executable, *sys.argv)
    sys.exit()


class getraenkeKasse():

    def __init__(self):
        self.products = None
        self.version = version
        self.purchases = None
        self.users = None
        self._clickedUser = None

        self.app = wx.App(False)

    def run(self):
        frame = userframe.UserFrame()
        self.app.MainLoop()

    @property
    def clickedUser(self) -> str:
        return self._clickedUser

    @clickedUser.setter
    def clickedUser(self, user: str):
        self._clickedUser = user


if __name__ == "__main__":

    if 'BARCODE_DEV' not in os.environ:
        # check network
        if not functions.checkNetwork():
            print("No network available. Exiting...")
            sys.exit()

        # test local time
        timeT = functions.getTimefromNTP()
        if timeT[0] != time.ctime():
            print("Date/time not synchronized with NTP. Exiting...")
            sys.exit()

    if not ('BARCODE_DEV' in os.environ or 'BARCODE_TEST' in os.environ):
        print('yes2')
        # check for new commits in local repository
        if not functions.gitPull("./."):
            print("Problem with git (local repo). Exiting...")
            sys.exit()

        # check for new version of getraenkeKasse.py script on github
        hasher_old = functions.getMD5Hash("barcodeRaspi/getraenkeKasse.py")
        if not functions.gitPull("barcodeRaspi"):
            print("Problem with git (GitHub). Exiting...")
            sys.exit()

        hasher_new = functions.getMD5Hash("barcodeRaspi/getraenkeKasse.py")
        if hasher_new.hexdigest() != hasher_old.hexdigest():
            # getraenkeKasse.py has changed, script is restarted
            print("new version from gitHub, script is restarting...")
            restart()

    gk = getraenkeKasse()
    gk.run()

