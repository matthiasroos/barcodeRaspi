#!/usr/bin/python
import wx
import wx.grid
import time

productlist = "produt.txt"
btnHeight = 50
btnWidth = 150
fontsize = 14


class ListFrame(wx.Frame):

    width = []
    height = []

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "ListFrame")
        panel = wx.Panel(self)

        type(self).width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        type(self).height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        offset = 5

        btnClose = wx.Button(panel, id = wx.ID_ANY, label = "close", name = "close", size = wx.Size(btnWidth, btnHeight), pos = (type(self).width-btnWidth, 0))
        #btnClose = wx.Button(panel, id = wx.ID_ANY, label = "close", name = "close", size = wx.Size(btnWidth, btnHeight), pos = ((type(self).width/2)-btnWidth, 0))
        btnClose.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        btnClose.Bind(wx.EVT_LEFT_UP,self.onClickCloseButton)

        btnAdd = wx.Button(panel, id = wx.ID_ANY, label = "add", name = "add", size = wx.Size(btnWidth, btnHeight), pos = (type(self).width-btnWidth, 2*btnHeight))
        btnAdd.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        btnAdd.Bind(wx.EVT_LEFT_UP, self.onClickAddButton)

        btnEdit = wx.Button(panel, id = wx.ID_ANY, label = "edit", name = "edit", size = wx.Size(btnWidth, btnHeight), pos = (type(self).width-btnWidth, 3*btnHeight))
        btnEdit.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        btnEdit.Bind(wx.EVT_LEFT_UP, self.onClickEditButton)

        btnDel = wx.Button(panel, id = wx.ID_ANY, label = "delete", name = "delete", size = wx.Size(btnWidth, btnHeight), pos = (type(self).width-btnWidth, 4*btnHeight))
        btnDel.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        btnDel.Bind(wx.EVT_LEFT_UP, self.onClickDelButton)

        btnSave = wx.Button(panel, id = wx.ID_ANY, label = "save", name = "save", size = wx.Size(btnWidth, btnHeight), pos = (type(self).width-btnWidth, 5*btnHeight))
        btnSave.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.prodList = wx.ListCtrl(panel, size=((type(self).width-btnWidth-2*offset), type(self).height-2*offset), pos = (offset, offset), style = wx.LC_REPORT|wx.LC_HRULES)
        self.prodList.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.prodList.InsertColumn(0, '#', width = 50)
        self.prodList.InsertColumn(1, 'code', width = 250)
        self.prodList.InsertColumn(2, 'description', width = 250)
        self.prodList.InsertColumn(3, 'price', width = 70)

        self.SetBackgroundColour("Gray")
        self.ShowFullScreen(True)        
    
    def onClickCloseButton(self, event):
        """"""
        exit()

    def onClickAddButton(self, event):
        """"""
        edit = EditFrame()

    def onClickEditButton(self, event):
        """"""
        fi = self.prodList.GetFirstSelected()
        if fi != -1:
            edit = EditFrame()
            edit.initValuesEdit(self.prodList.GetItemText(fi,0), self.prodList.GetItemText(fi,1), self.prodList.GetItemText(fi,2), self.prodList.GetItemText(fi,3))

    def onClickDelButton(self, event):
        """"""
        fi = self.prodList.GetFirstSelected()
        if fi != -1:
            self.prodList.DeleteItem(fi)
            for i in range(fi, self.prodList.GetItemCount()):
                self.prodList.SetStringItem(i, 0, str(i+1))


class EditFrame(wx.Frame):

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "Add/Edit entry", size = (500, 500))

        btnBack = wx.Button(self, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (ListFrame.width-2*btnWidth, ListFrame.height-btnHeight))
        btnBack.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        #btnBack.Bind(wx.EVT_LEFT_UP,self.onClickBackButton)
        
        btnConfirm = wx.Button(self, id = wx.ID_ANY, label = "confirm", name = "confirm", size = wx.Size(btnWidth, btnHeight), pos = (ListFrame.width-1*btnWidth, ListFrame.height-btnHeight))
        btnConfirm.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        #btnConfirm.Bind(wx.EVT_LEFT_UP,self.onClickConfirmButton)
        btnConfirm.Disable()

        Text = wx.StaticText(self, label = ("was darf es sein?"), pos = (ListFrame.width/3, ListFrame.height/3), size = (150, 50))
        Text.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        Code = wx.TextCtrl(self, pos = (ListFrame.width/3, ListFrame.height/2), size = (300, 120))
        Code.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
        Code.SetFocus()


        self.Show()


if __name__ == "__main__":
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = ListFrame()
    app.MainLoop()

