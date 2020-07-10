import wx
import wx.grid
import time
import os.path


class ListFrame(wx.Frame):

    def __init__(self, parent):
        """Constructor"""
        wx.Frame.__init__(self, None, title="ListFrame")
        self.parent = parent
        panel = wx.Panel(self)

        self._width = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
        self._height = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)

        with self.parent as prt:
            btnClose = wx.Button(panel, id=wx.ID_ANY, label='close', name='close',
                                 size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                 pos=(self._width - prt.displaySettings.btnWidth, 0))
            btnClose.SetFont(prt.displaySettings.wxFont)
            btnClose.Bind(wx.EVT_LEFT_UP, self._onClickCloseButton)

            btnAdd = wx.Button(panel, id=wx.ID_ANY, label='add', name='add',
                               size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                               pos=(self._width - prt.displaySettings.btnWidth, 2 * prt.displaySettings.btnHeight))
            btnAdd.SetFont(prt.displaySettings.wxFont)
            btnAdd.Bind(wx.EVT_LEFT_UP, self._onClickAddButton)

            btnEdit = wx.Button(panel, id=wx.ID_ANY, label='edit', name='edit',
                                size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                pos=(self._width - prt.displaySettings.btnWidth, 3 * prt.displaySettings.btnHeight))
            btnEdit.SetFont(prt.displaySettings.wxFont)
            btnEdit.Bind(wx.EVT_LEFT_UP, self._onClickEditButton)

            btnDel = wx.Button(panel, id=wx.ID_ANY, label='delete', name='delete',
                               size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                               pos=(self._width - prt.displaySettings.btnWidth, 4 * prt.displaySettings.btnHeight))
            btnDel.SetFont(prt.displaySettings.wxFont)
            btnDel.Bind(wx.EVT_LEFT_UP, self._onClickDelButton)

            self.btnLoad = wx.Button(panel, id=wx.ID_ANY, label='load', name='load',
                                     size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                     pos=(
                                         self._width - prt.displaySettings.btnWidth, 5 * prt.displaySettings.btnHeight))
            self.btnLoad.SetFont(prt.displaySettings.wxFont)
            self.btnLoad.Bind(wx.EVT_LEFT_UP, self._onClickLoadButton)

            # TODO
            if not os.path.isfile(prt.productsFile):
                self.btnLoad.Disable()

            btnSave = wx.Button(panel, id=wx.ID_ANY, label="save", name="save",
                                size=wx.Size(prt.displaySettings.btnWidth, prt.displaySettings.btnHeight),
                                pos=(self._width - prt.displaySettings.btnWidth, 6 * prt.displaySettings.btnHeight))
            btnSave.SetFont(prt.displaySettings.wxFont)
            btnSave.Bind(wx.EVT_LEFT_UP, self._onClickSaveButton)

            self.prodList = wx.ListCtrl(panel,
                                        size=(self._width - prt.displaySettings.btnWidth -
                                              2 * prt.displaySettings.offSet,
                                              self._height - 2 * prt.displaySettings.offSet),
                                        pos=(prt.displaySettings.offSet, prt.displaySettings.offSet),
                                        style=wx.LC_REPORT | wx.LC_HRULES)
            self.prodList.SetFont(prt.displaySettings.wxFont)
            self.prodList.InsertColumn(0, '#', width=50)
            self.prodList.InsertColumn(1, 'code', width=250)
            self.prodList.InsertColumn(2, 'description', width=250)
            self.prodList.InsertColumn(3, 'price', width=70)

            self.SetBackgroundColour("Gray")
            self.ShowFullScreen(True)

    def _onClickCloseButton(self, event):
        """"""
        self.parent.exit()

    def _onClickAddButton(self, event):
        """"""
        self.parent.show_edit_frame()

    def _onClickEditButton(self, event):
        """"""
        # TODO
        fi = self.prodList.GetFirstSelected()
        if fi != -1:
            edit = EditFrame()
            edit.initValuesEdit(self.prodList.GetItemText(fi, 0), self.prodList.GetItemText(fi, 1),
                                self.prodList.GetItemText(fi, 2), self.prodList.GetItemText(fi, 3))

    def _onClickDelButton(self, event):
        """"""
        fi = self.prodList.GetFirstSelected()
        if fi != -1:
            if not self.parent.show_confirm_dialog(confirm_message=f'Are your sure to delete #{fi +1}?'):
                return None
            self.prodList.DeleteItem(fi)
            for i in range(fi, self.prodList.GetItemCount()):
                self.prodList.SetStringItem(i, 0, str(i + 1))

    def _onClickLoadButton(self, event):
        """"""
        if self.parent.show_confirm_dialog(confirm_message=f'Do you want to load {self.parent.productsFile}?'):
            self.prodList.DeleteAllItems()
            self.parent.get_products()
            for index, row in self.parent.fileContents.products[['nr', 'code', 'desc', 'price']].iterrows():
                self.prodList.Append([value for value in row])

    def _onClickSaveButton(self, event):
        """"""
        # TODO
        if self.parent.show_confirm_dialog(confirm_message=f'Do you want to save to {self.parent.productsFile}?'):
            fileProdukte = open(productsFile, "w")
        for i in range(self.prodList.GetItemCount()):
            line = ""
            for j in range(4):
                line = line + self.prodList.GetItemText(i, j)
                if j < 3:
                    line = line + ","
                else:
                    line = line + "\n"
            fileProdukte.writelines(line)
        fileProdukte.close()
        self.btnLoad.Enable()

