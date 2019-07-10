#!/usr/bin/python
import wx
import wx.grid
import time

productsFile = "produkt.txt"
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
        btnSave.Bind(wx.EVT_LEFT_UP, self.onClickSaveButton)

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

    def onClickSaveButton(self, event):
        """"""
        fileProdukte = open(productsFile, "w")
        for i in range(self.prodList.GetItemCount()):
            line = ""
            for j in range(4):
                line = line + self.prodList.GetItemText(i,j)
                if j < 3:
                    line = line + ","
                else:
                    line = line + "\n"
            fileProdukte.writelines(line)




class EditFrame(wx.Frame):

    frameWidth = 500
    frameHeight = 300

    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title = "Add/Edit entry", size = (type(self).frameWidth, type(self).frameHeight))

        self.number = frame.prodList.GetItemCount()
        self.NummerTxt = wx.StaticText(self, label = ("#"+str(self.number+1)), pos = (40, 20), size = (20, 50))
        self.NummerTxt.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))

        CodeTxt = wx.StaticText(self, label = ("code"), pos = (40, 70), size = (20, 50))
        CodeTxt.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.CodeInp = wx.TextCtrl(self, pos = (140, 60), size = (300, 50))
        self.CodeInp.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.CodeInp.SetMaxLength(13)
        self.CodeInp.SetFocus()

        DescTxt = wx.StaticText(self, label = ("descr."), pos = (40, 125), size = (20, 50))
        DescTxt.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.DescInp = wx.TextCtrl(self, pos = (140, 115), size = (300, 50))
        self.DescInp.SetMaxLength(20)
        self.DescInp.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))

        PriceTxt = wx.StaticText(self, label = ("price"), pos = (40, 180), size = (20, 50))
        PriceTxt.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.PriceInp = wx.TextCtrl(self, pos = (140, 170), size = (300, 50))
        self.PriceInp.SetMaxLength(6)
        self.PriceInp.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))


        btnBack = wx.Button(self, id = wx.ID_ANY, label = "back", name = "back", size = wx.Size(btnWidth, btnHeight), pos = (60, type(self).frameHeight-2*btnHeight))
        btnBack.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        #btnBack.Bind(wx.EVT_LEFT_UP,self.onClickBackButton)
        
        btnConfirm = wx.Button(self, id = wx.ID_ANY, label = "confirm", name = "confirm", size = wx.Size(btnWidth, btnHeight), pos = (60+btnWidth+5, type(self).frameHeight-2*btnHeight))
        btnConfirm.SetFont(wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.BOLD))
        btnConfirm.Bind(wx.EVT_LEFT_UP,self.onClickConfirmButton)
        #btnConfirm.Disable()

        self.Show()

    def initValuesEdit(self, number, code, desc, price):
        """"""
        self.number = number
        self.NummerTxt.SetLabel("#"+number)
        self.CodeInp.SetValue(code)
        self.DescInp.SetValue(desc)
        self.PriceInp.SetValue(price)

    def onClickBackButton(self, event):
        """"""
        self.Close()

    def onClickConfirmButton(self, event):
        """"""
        nr = frame.prodList.GetItemCount()
        code = self.CodeInp.GetValue()
        if nr == self.number:
            for i in range(frame.prodList.GetItemCount()):
                if (code == frame.prodList.GetItemText(i,1)):
                    # code is already in list
                    return
            frame.prodList.Append([str(nr+1), self.CodeInp.GetValue(), self.DescInp.GetValue(), self.PriceInp.GetValue()])
        else:
            ind = int(self.number)-1
            for i in range(frame.prodList.GetItemCount()):
                if code == frame.prodList.GetItemText(i,1):
                    if i != ind:
                        # code was changed to one already in list
                        return
            frame.prodList.SetStringItem(ind, 0, str(self.number))
            frame.prodList.SetStringItem(ind, 1, self.CodeInp.GetValue())
            frame.prodList.SetStringItem(ind, 2, self.DescInp.GetValue())
            frame.prodList.SetStringItem(ind, 3, self.PriceInp.GetValue())
        self.Close()

if __name__ == "__main__":
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = ListFrame()
    app.MainLoop()

