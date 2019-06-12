#!/usr/bin/python
import wx
import time
import barcodescanner as basc

usersFile = "user.txt"

class UserFrame(wx.Frame):

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "Test Fullscreen")
        panel = wx.Panel(self)

        width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        users = self.readUsers()
        nrUsers = len(users)
        btnHeight = 50
        btnWidth = 150
        offset = 5
        posX = offset
        posY = offset
        self.button = []
        for i in range(0, nrUsers):
            self.button.append(wx.Button(panel, id = wx.ID_ANY, label = users[i], name = users[i], size = wx.Size(btnWidth, btnHeight), pos = (posX, posY)))
            self.button[i].SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.button[i].Bind(wx.EVT_BUTTON, self.onClickNameButton)
            #self.buildButtons(button[i])
            if ((posY + 2*btnHeight + offset) < height):
                posY = posY + btnHeight + offset
            else:
                posY = offset
                posX = posX + btnWidth + offset


        self.SetBackgroundColour("Gray")

        #btnBack = wx.Button(panel, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (width-2*btnWidth, height-btnHeight))
        #self.btnBack = wx.Button(panel, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (0, 0))
        #self.btnBack.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        #self.btnBack.Bind(wx.EVT_BUTTON,self.OnClickedBackButton)
        #self.btnBack.Disable()
        #btnConfirm = wx.Button(panel, id = wx.ID_ANY, label = "confirm", name = "confirm", size = wx.Size(btnWidth, btnHeight), pos = (width-1*btnWidth, height-btnHeight))
        #self.btnConfirm = wx.Button(panel, id = wx.ID_ANY, label = "confirm", name = "confirm", size = wx.Size(btnWidth, btnHeight), pos = ( 100, 100))
        #self.btnConfirm.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        #self.btnConfirm.Bind(wx.EVT_BUTTON,self.OnClickedConfirmButton)
        #self.btnConfirm.Disable()
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
        This method is fired when its corresponding button is pressed
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
        #time.sleep(60)
        self.user = button_by_id.GetLabel()
        #self.btnBack.Enable()
        frameScan = ScanFrame()
        #while True:
        #    print(basc.barcode_reader())

    #def OnClickedBackButton(self, event): 
    #    btn = event.GetEventObject().GetLabel() 
    #    print "Label of pressed button = ",btn
    #    for btn in self.button:
    #        btn.Enable()
    #    self.btnBack.Disable()

    #def OnClickedConfirmButton(self, event):
    #    btn = event.GetEventObject().GetLabel()
   #    print "Label of pressed button = ", btn

class ScanFrame(wx.Frame):
    
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "ScanFame", style = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        panel = wx.Panel(self)

        width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        btnHeight = 50
        btnWidth = 150

        #self.SetBackgroundColour("Gray")

        self.btnBack = wx.Button(panel, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (width-2*btnWidth, height-btnHeight))
        #self.btnBack = wx.Button(panel, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (0, 0))
        self.btnBack.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnBack.Bind(wx.EVT_BUTTON,self.OnClickedBackButton)
        #self.btnBack.Disable()
        self.btnConfirm = wx.Button(panel, id = wx.ID_ANY, label = "confirm", name = "confirm", size = wx.Size(btnWidth, btnHeight), pos = (width-1*btnWidth, height-btnHeight))
        #self.btnConfirm = wx.Button(panel, id = wx.ID_ANY, label = "confirm", name = "confirm", size = wx.Size(btnWidth, btnHeight), pos = ( 100, 100))
        self.btnConfirm.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnConfirm.Bind(wx.EVT_BUTTON,self.OnClickedConfirmButton)
        self.btnConfirm.Disable()
        
        self.Text = wx.StaticText(panel, label = (frame.user+", was darf es sein?"), pos = (width/3, height/3), size = (150, 50))
        self.Text.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.Code = wx.TextCtrl(panel, pos = (width/3, height/2), size = (300, 120))
        self.Code.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))


        self.ShowFullScreen(True)

    def OnClickedBackButton(self, event):
        """"""
        btn = event.GetEventObject().GetLabel()
        print "Label of pressed button = ",btn
        #for btn in self.button:
        #    btn.Enable()
        #self.btnBack.Disable()
        self.Close()

    def OnClickedConfirmButton(self, event):
        """"""
        btn = event.GetEventObject().GetLabel()
        print "Label of pressed button = ", btn





if __name__ == "__main__":
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = UserFrame()
    app.MainLoop()

