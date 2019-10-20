#!/usr/bin/python3
import wx
import wx.lib.mixins.listctrl as listmix
import time
#import barcodescanner as basc
import os
import sys
import git
import datetime
import hashlib
import socket
import struct


usersFile = "user.txt"
productsFile = "produkt.txt"
purchasesFile = "purchase.txt"
btnHeight = 80
btnWidth = 200
fontSize = 25


class UserFrame(wx.Frame):

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "Test Fullscreen")
        panel = wx.Panel(self)

        type(self)._width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        type(self)._height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        # read User list
        type(self)._users = self._readUsers()
        nrUsers = len(type(self)._users)

        # read Product list
        type(self)._products, type(self)._productsDict  = self._readProducts()
        nrProducts = len(self._products)
        type(self)._LenCode = self._calcLengthCode()

        offset = 10
        posX = offset
        posY = offset

        # User buttons
        self.button = []
        for i in range(0, nrUsers):
            self.button.append(wx.Button(panel, id = wx.ID_ANY, label = type(self)._users[i], name = type(self)._users[i], size = wx.Size(btnWidth, btnHeight), pos = (posX, posY)))
            self.button[i].SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.button[i].Bind(wx.EVT_LEFT_UP, self._onClickNameButton)
            #self.buildButtons(button[i])
            if ((posY + 2*btnHeight + offset) < type(self)._height):
                posY = posY + btnHeight + offset
            else:
                posY = offset
                posX = posX + btnWidth + offset

        # List button
        self.btnList = wx.Button(panel, id = wx.ID_ANY, label = "List", name = "list", size = wx.Size(btnWidth, btnHeight), pos = (type(self)._width-1*btnWidth, type(self)._height-btnHeight))
        self.btnList.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnList.Bind(wx.EVT_LEFT_UP, self._onClickListButton)

        self.SetBackgroundColour("Gray")
        self.ShowFullScreen(True)        
    
    def _readUsers(self):
        """"
        Read users from usersFile
        """
        if not os.path.isfile(usersFile):
            raise Exception("usersFile not found!")
        fileUsers = open(usersFile, "r")
        users = []
        for line in fileUsers:
            users.append(line.rstrip())
        fileUsers.close()
        return users

    def _readProducts(self):
        """"
        Read products from productsFile
        """
        if not os.path.isfile(productsFile):
            raise Exception("prodcutsFile not found!")
        fileProducts = open(productsFile, "r")
        prod = list()
        prodDict = {}
        for line in fileProducts:
            ll = line.split(",")
            ll[3] = ll[3][:-1]
            prod.append(ll)
            prodDict[ll[1]] = ll[3]
        fileProducts.close()
        return prod, prodDict

    def _calcLengthCode(self):
        """"""
        length = set()
        for code in self._products:
            tmpLen = len(code)
            if  tmpLen > 0:
                if tmpLen not in length:
                    length.add(tmpLen)
        return length

    def _onClickNameButton(self, event):
        """
        This method is fired when a User button is pressed
        """

        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)
        type(self).user = button_by_id.GetLabel()
        frameScan = ScanFrame()

    def _onClickListButton(self, event):
        """
        This method is fired when the List button is pressed
        """
        frameList = ListFrame()

    def getWidth(self):
        """"""
        return type(self)._width

    def getHeight(self):
        """"""
        return type(self)._height

    def getLengthCode(self):
        """"""
        return type(self)._LenCode

    def getProducts(self):
        """"""
        return type(self)._products

    def getProductsDict(self):
        """"""
        return type(self)._productsDict


class ScanFrame(wx.Frame):
    
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "ScanFrame", style = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.panel = wx.Panel(self)

        self.btnNoCode = wx.Button(self.panel, id = wx.ID_ANY, label = "no barcode", name = "no barcode", size = wx.Size(btnWidth, btnHeight), pos = (frame.getWidth()-3*btnWidth, frame.getHeight()-btnHeight))
        self.btnNoCode.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnNoCode.Bind(wx.EVT_LEFT_UP,self._onClickNoCodeButton)
        self.btnNoCode.Disable()
        self.btnBack = wx.Button(self.panel, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (frame.getWidth()-2*btnWidth, frame.getHeight()-btnHeight))
        self.btnBack.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnBack.Bind(wx.EVT_LEFT_UP,self._onClickBackButton)
        self.btnConfirm = wx.Button(self.panel, id = wx.ID_ANY, label = "confirm", name = "confirm", size = wx.Size(btnWidth, btnHeight), pos = (frame.getWidth()-1*btnWidth, frame.getHeight()-btnHeight))
        self.btnConfirm.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnConfirm.Bind(wx.EVT_LEFT_UP,self._onClickConfirmButton)
        self.btnConfirm.Disable()
        
        self.Text = wx.StaticText(self.panel, label = (UserFrame.user+", what can I get you?"), pos = (frame.getWidth()/5, frame.getHeight()*1/5), size = (150, 50))
        self.Text.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.Code = wx.TextCtrl(self.panel, pos = (frame.getWidth()/5, frame.getHeight()*1/5+70), size = (320, 50))
        self.Code.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Code.SetMaxLength(13)
        self.Code.SetFocus()
        self.Code.Bind(wx.EVT_TEXT, self._onChangeCode)

        self.Product = wx.StaticText(self.panel,  label = "", pos = (frame.getWidth()/5, frame.getHeight()*1/5+150), size = (150, 50))
        self.Product.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.ShowFullScreen(True)

    def _onClickNoCodeButton(self, event):
        """"""
        self.btnNoCode.Disable()
        self.Code.Hide()
        self.cmbProducts = wx.ComboBox(self.panel, id = wx.ID_ANY,  pos = (frame.getWidth()/5, frame.getHeight()*1/5+70), size = (320, 50))
        nrProducts = len(UserFrame.products)

    def _onClickBackButton(self, event):
        """"""
        self.Close()

    def _onClickConfirmButton(self, event):
        """"""
        self.Disable()
        self.btnConfirm.SetLabel("saving...")
        # check local repo for changes
        gitPull("./.")

        if not os.path.isfile(purchasesFile):
            raise Exception("purchasesFile not found!")
        filePurchases = open(purchasesFile, "a")
        line = datetime.datetime.now().isoformat() + "," + UserFrame.user + "," + self.Code.GetValue() + "\n"
        filePurchases.writelines(line)
        filePurchases.close()
        line = datetime.datetime.now().isoformat() + "," + frame.user + "," + self.Code.GetValue() + "\n"

        # commit & push purchase
        try:
            repoLocal = git.Repo("./.")
            repoLocal.git.add(purchasesFile)
            repoLocal.index.commit("purchase via getraenkeKasse.py")
            origin = repoLocal.remote(name='origin')
            origin.push()
        except:
            print('Some error occured while pushing the code')

        self.Close()

    def _onChangeCode(self, event):
        """"""
        code = self.Code.GetValue()
        if len(code) in frame.getLengthCode():
            for pr in frame.getProducts():
                if code == pr[1]:
                    self.Product.SetLabel((pr[2] + "\t Price: " + pr[3]))
                    self.btnConfirm.Enable()
                    return None
        self.Product.SetLabel("")
        self.btnConfirm.Disable()

class SortableListCtrl(wx.ListCtrl):

    def __init__(self, parent, size, pos, style):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, pos, size, style)

class SortableListCtrlPanel(wx.Panel, listmix.ColumnSorterMixin):

    def __init__(self, parent):
        """Constrcutor"""
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        # calculate sum for each user
        if not os.path.isfile(purchasesFile):
            raise Exception("purchasesFile not found!")
        filePurchases = open(purchasesFile, "r")
        usersPurchases = dict()
        for line in filePurchases:
            ll = line.split(",")
            for key, value in usersPurchases.items():
                user, nr, money = value
                if user == ll[1]:
                    usersPurchases[key] = (user, nr + 1, money + float(frame.getProductsDict()[ll[2].rstrip()]))
                    break
            else:
                nr = len(usersPurchases)
                usersPurchases[nr] = (ll[1], 1, float(frame.getProductsDict()[ll[2].rstrip()]))

        # show sums for each user
        offset = 5
        self.purchList = SortableListCtrl(parent = self, size = ((frame.getWidth()-btnWidth-2*offset), frame.getHeight()-2*offset), pos = (offset, offset), style = wx.LC_REPORT|wx.LC_HRULES|wx.LC_SORT_DESCENDING)
        self.purchList.SetFont(wx.Font((fontSize-5), wx.SWISS, wx.NORMAL, wx.BOLD))
        self.purchList.InsertColumn(0, 'name', width = 180)
        self.purchList.InsertColumn(1, 'drinks', width = 180)
        self.purchList.InsertColumn(2, 'money', width = 180)
        index = 0
        for key, value in usersPurchases.items():
            user, nr, money = value
            self.purchList.Append([user, nr, "{:.2f}".format(money)])
            self.purchList.SetItemData(index, key)
            index += 1

        self.itemDataMap = usersPurchases # used by ColumnCorterMixin
        listmix.ColumnSorterMixin.__init__(self, 3)
        self.purchList.Bind(wx.EVT_LIST_COL_CLICK, self._OnColumnClick)

    # used by ColumnSorterMixin
    def GetListCtrl(self):
        return self.purchList

    def _OnColumnClick(self, event):
        event.Skip()


class ListFrame(wx.Frame):

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "ListFrame", style = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        panel = SortableListCtrlPanel(self)

        self.btnClose = wx.Button(panel, id = wx.ID_ANY, label = "close", name = "close", size = wx.Size(btnWidth, btnHeight), pos = (frame.getWidth()-btnWidth, 0))
        self.btnClose.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnClose.Bind(wx.EVT_LEFT_UP,self._onClickCloseButton)
        self.btnBack = wx.Button(panel, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (frame.getWidth()-1*btnWidth, frame.getHeight()-btnHeight))
        self.btnBack.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnBack.Bind(wx.EVT_LEFT_UP,self._onClickBackButton)

        self.ShowFullScreen(True)

    def _onClickCloseButton(self, event):
        """"""
        exit()

    def _onClickBackButton(self, event):
        """"""
        self.Close()


if __name__ == "__main__":

    # main subfunctions start
    def getMD5Hash(filename):
        hasher = hashlib.md5()
        with open(filename, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        #print(hasher.hexdigest())
        return hasher

    def checkNetwork(host="8.8.8.8", port=53, timeout=3):
        """
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            print(ex)
            return False

    def getTimefromNTP():
        addrNTP='0.de.pool.ntp.org'
        REFRENCE_TIME_1970 = 2208988800      # Reference time
        client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        data = b'\x1b' + 47 * b'\0'
        client.sendto( data, (addrNTP, 123))
        data, address = client.recvfrom( 1024 )
        if data:
            t = struct.unpack( '!12I', data )[10]
            t -= REFRENCE_TIME_1970
        return time.ctime(t),t

    def gitPull(pathRepo):
        try:
            repo = git.Repo(pathRepo)
            repo.remotes.origin.pull()
            return True
        except git.GitCommandError as exception:
            print(exception)
            if exception.stdout:
                print("!! stdout was:")
                print(exception.stdout)
            if exception.stderr:
                print("!! stderr was:")
                print(exception.stderr)
            return False

    # main subfunctions end



    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.

    # check network
    if not checkNetwork():
        print("No network available. Exiting...")
        sys.exit()

    # test local time
    timeT = getTimefromNTP()
    if (timeT[0] != time.ctime()):
        print("Date/time not synchronized with NTP. Exiting...")
        sys.exit()

    # check for new commits in local repository
    if not gitPull("./."):
        print("Problem with git (local repo). Exiting...")
        sys.exit()

    # check for new version of getraenkeKasse.py script on github
    hasher_old = getMD5Hash("barcodeRaspi/getraenkeKasse.py")
    if not gitPull("barcodeRaspi"):
        print("Problem with git (GitHub). Exiting...")
        sys.exit()

    hasher_new = getMD5Hash("barcodeRaspi/getraenkeKasse.py")
    if (hasher_new.hexdigest() != hasher_old.hexdigest()):
        # getraenkeKasse.py has changed, script is restarted
        print("new version from gitHub, script is restarting...")
        os.execv(__file__, sys.argv)
        sys.exit()

    frame = UserFrame()
    app.MainLoop()

