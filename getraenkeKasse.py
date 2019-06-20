#!/usr/bin/python
import wx
import time
import barcodescanner as basc

usersFile = "user.txt"
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
        """"Read users from usersFile"""
        fileUsers = open(usersFile, "r")
        users = []
        for line in fileUsers:
            users.append(line.rstrip())
        fileUsers.close()
        return users

    def onClickNameButton(self, event):
        """
        This method is fired when a User button is pressed
        """
        #button = event.GetEventObject()
        #print "The button you pressed was labeled: " + button.GetLabel()
        #print "The button's name is " + button.GetName()

        button_id = event.GetId()
        button_by_id = self.FindWindowById(button_id)
        print "The button you pressed was labeled: " + button_by_id.GetLabel()
        print "The button's name is " + button_by_id.GetName()
       
        #for btn in self.button:
        #    if button_by_id.GetLabel() != btn.GetLabel():
        #        btn.Disable()
        #lbl = wx.StaticText(self, -1, style=wx.ALIGN_CENTER, label=button_by_id.GetName())
        #self.update()
        type(self).user = button_by_id.GetLabel()
        #self.btnBack.Enable()
        frameScan = ScanFrame()
        #while True:
        #    print(basc.barcode_reader())

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
        
        self.Text = wx.StaticText(panel, label = (UserFrame.user+", was darf es sein?"), pos = (UserFrame.width/3, UserFrame.height/3), size = (150, 50))
        self.Text.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Code = wx.TextCtrl(panel, pos = (UserFrame.width/3, UserFrame.height/2), size = (300, 120))
        self.Code.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Code.SetFocus()

        self.ShowFullScreen(True)

    def onClickBackButton(self, event):
        """"""
        self.Close()

    def onClickConfirmButton(self, event):
        """"""
        btn = event.GetEventObject().GetLabel()
        print "Label of pressed button = ", btn


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

