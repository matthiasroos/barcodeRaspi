#!/usr/bin/python3

import os
import time

import src.getraenkeKasse.getraenkeapp
import functions

VERSION = '0.1.3'

PRODUCTS_FILE = 'produkt.txt'
PURCHASES_FILE = 'purchase.txt'
USERS_FILE = 'user.txt'

BUTTON_HEIGHT = 70
BUTTON_WIDTH = 180
FONT_SIZE = 18
OFFSET = 5


if __name__ == "__main__":

    gk = src.getraenkeKasse.getraenkeapp.GetraenkeApp(button_height=BUTTON_HEIGHT,
                                                      button_width=BUTTON_WIDTH,
                                                      font_size=FONT_SIZE,
                                                      offset=OFFSET,
                                                      file_names={'products': PRODUCTS_FILE,
                                                                  'purchases': PURCHASES_FILE,
                                                                  'users': USERS_FILE})

    # check network
    if not functions.checkNetwork():
        gk.show_error_dialog(error_message='No network available. Exiting...')
        gk.exit()

    if 'BARCODE_DEV' not in os.environ:
        # test local time
        timeT = functions.getTimefromNTP()
        if timeT[0] != time.ctime():
            gk.show_error_dialog(error_message='Date/time not synchronized with NTP. Exiting...')
            gk.exit()

    # check for new commits in local repository
    gk.bring_git_repo_up_to_date(path_repo='./.', error_message='Problem with git (local repo).', should_exit=True)

    # check for new version of getraenkeKasse.py script on github
    hash_old = functions.getMD5Hash('barcodeRaspi/getraenkeKasse.py')
    gk.bring_git_repo_up_to_date(path_repo='barcodeRaspi', error_message='Problem with git (GitHub). Exiting...',
                                 should_exit=True)

    hash_new = functions.getMD5Hash('barcodeRaspi/getraenkeKasse.py')
    if hash_new.hexdigest() != hash_old.hexdigest():
        # getraenkeKasse.py has changed, script is restarted
        print("new version from gitHub, script is restarting...")
        gk.restart()

    gk.run()
