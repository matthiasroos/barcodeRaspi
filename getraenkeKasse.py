#!/usr/bin/python
import wx
import time
import barcodescanner as basc
import os.path

usersFile = "user.txt"
productsFile = "produkt.txt"
btnHeight = 50
btnWidth = 150


class UserFrame(wx.Frame):

    width = []
    height = []
    user = []

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "Test Fullscreen")
        panel = wx.Panel(self)

        type(self).width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        type(self).height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        # read User list
        users = self.readUsers()
        nrUsers = len(users)

        # read Product list
        self.products = self.readProducts()
        nrProducts = len(self.products)
        self.LenCode = self.getLengthCode()

        offset = 5
        posX = offset
        posY = offset

        # User buttons
        self.button = []
        for i in range(0, nrUsers):
            self.button.append(wx.Button(panel, id = wx.ID_ANY, label = users[i], name = users[i], size = wx.Size(btnWidth, btnHeight), pos = (posX, posY)))
            self.button[i].SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.button[i].Bind(wx.EVT_LEFT_UP, self.onClickNameButton)
            #self.buildButtons(button[i])
            if ((posY + 2*btnHeight + offset) < type(self).height):
                posY = posY + btnHeight + offset
            else:
                posY = offset
                posX = posX + btnWidth + offset

        # List button
        self.btnList = wx.Button(panel, id = wx.ID_ANY, label = "List", name = "list", size = wx.Size(btnWidth, btnHeight), pos = (type(self).width-1*btnWidth, type(self).height-btnHeight))
        self.btnList.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnList.Bind(wx.EVT_LEFT_UP, self.onClickListButton)


        self.SetBackgroundColour("Gray")
        self.ShowFullScreen(True)        
    
    def readUsers(self):
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

    def readProducts(self):
        """"
        Read products from productsFile
        """
        if not os.path.isfile(productsFile):
            raise Exception("prodcutsFile not found!")
        fileProducts = open(productsFile, "r")
        prod = list()
        for line in fileProducts:
            prod.append(line.decode("utf-8").split(","))
        fileProducts.close()
        return prod

    def getLengthCode(self):
        """"""
        length = set()
        for code in self.products:
            tmpLen = len(code[1])
            if  tmpLen > 0:
                if tmpLen not in length:
                    length.add(tmpLen)
        return length

    def onClickNameButton(self, event):
        """
        This method is fired when a User button is pressed
        """

        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)
       
        type(self).user = button_by_id.GetLabel()
        frameScan = ScanFrame()

    def onClickListButton(self, event):
        """
        This method is fired when the List button is pressed
        """
        frameList = ListFrame()


class ScanFrame(wx.Frame):
    
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "ScanFrame", style = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        panel = wx.Panel(self)


        #self.SetBackgroundColour("Gray")

        self.btnBack = wx.Button(panel, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (UserFrame.width-2*btnWidth, UserFrame.height-btnHeight))
        #self.btnBack = wx.Button(panel, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (0, 0))
        self.btnBack.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnBack.Bind(wx.EVT_LEFT_UP,self.onClickBackButton)
        #self.btnBack.Disable()
        self.btnConfirm = wx.Button(panel, id = wx.ID_ANY, label = "confirm", name = "confirm", size = wx.Size(btnWidth, btnHeight), pos = (UserFrame.width-1*btnWidth, UserFrame.height-btnHeight))
        #self.btnConfirm = wx.Button(panel, id = wx.ID_ANY, label = "confirm", name = "confirm", size = wx.Size(btnWidth, btnHeight), pos = ( 100, 100))
        self.btnConfirm.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnConfirm.Bind(wx.EVT_LEFT_UP,self.onClickConfirmButton)
        self.btnConfirm.Disable()
        
        self.Text = wx.StaticText(panel, label = (UserFrame.user+", what can I get you?"), pos = (UserFrame.width/5, UserFrame.height*1/5), size = (150, 50))
        self.Text.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.Code = wx.TextCtrl(panel, pos = (UserFrame.width/5, UserFrame.height*1/5+70), size = (300, 50))
        self.Code.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Code.SetMaxLength(13)
        self.Code.SetFocus()
        self.Code.Bind(wx.EVT_TEXT,self.onChangeCode)

        self.Product = wx.StaticText(panel,  label = "", pos = (UserFrame.width/5, UserFrame.height*1/5+150), size = (150, 50))
        self.Product.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.ShowFullScreen(True)

    def onClickBackButton(self, event):
        """"""
        self.Close()

    def onClickConfirmButton(self, event):
        """"""
        btn = event.GetEventObject().GetLabel()
        print "Label of pressed button = ", btn

    def onChangeCode(self,event):
        """"""
        code = self.Code.GetValue()
        if len(code) in frame.LenCode:
            for pr in frame.products:
                if code == pr[1]:
                    self.Product.SetLabel((pr[2] + "\t Price: " + pr[3]))
                    self.btnConfirm.Enable()
                    return None
        self.Product.SetLabel("")
        self.btnConfirm.Disable()


class ListFrame(wx.Frame):

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "ListFrame", style = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        panel = wx.Panel(self)

        self.btnClose = wx.Button(panel, id = wx.ID_ANY, label = "close", name = "close", size = wx.Size(btnWidth, btnHeight), pos = (UserFrame.width-btnWidth, 0))
        self.btnClose.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnClose.Bind(wx.EVT_LEFT_UP,self.onClickCloseButton)
        self.btnBack = wx.Button(panel, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (UserFrame.width-2*btnWidth, UserFrame.height-btnHeight))
        self.btnBack.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnBack.Bind(wx.EVT_LEFT_UP,self.onClickBackButton)


        self.ShowFullScreen(True)

    def onClickCloseButton(self, event):
        """"""
        exit()

    def onClickBackButton(self, event):
        """"""
        self.Close()


if __name__ == "__main__":
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = UserFrame()
    app.MainLoop()

