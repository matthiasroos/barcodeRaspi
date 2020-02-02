
import os
import sys
import wx
import wx.lib.mixins.listctrl as listmix

import functions
import getraenkeKasse

btnHeight = 80
btnWidth = 200
fontSize = 25


class ListFrame(wx.Frame):

    def __init__(self, userframe):
        """Constructor"""
        wx.Frame.__init__(self, None, title="ListFrame", style=wx.DEFAULT_FRAME_STYLE)
        panel = SortableListCtrlPanel(self, userframe)

        self.btnClose = wx.Button(panel, id=wx.ID_ANY, label="close", name="close", size=wx.Size(btnWidth, btnHeight),
                                  pos=(userframe.getWidth() - btnWidth, 0))
        self.btnClose.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnClose.Bind(wx.EVT_LEFT_UP, self._onClickCloseButton)
        self.btnBack = wx.Button(panel, id=wx.ID_ANY, label="back", name="back", size=wx.Size(btnWidth, btnHeight),

        self.btnRestart = wx.Button(self.panel, id=wx.ID_ANY, label='restart', name='restart',
                                    size=wx.Size(btnWidth, btnHeight), pos=(userframe.getWidth() - btnWidth, btnHeight))
        self.btnRestart.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnRestart.Bind(wx.EVT_LEFT_UP, self._onClickRestartButton)

                                 pos=(userframe.getWidth() - 1 * btnWidth, userframe.getHeight() - btnHeight))
        self.btnBack.SetFont(wx.Font(fontSize, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.btnBack.Bind(wx.EVT_LEFT_UP, self._onClickBackButton)

        self.ShowFullScreen(True)

    def _onClickCloseButton(self, event):
        """"""
        sys.exit()

    def _onClickBackButton(self, event):
        """"""
        self.Close()

    def _onClickRestartButton(self, event):
        """"""
        getraenkeKasse.restart()


class SortableListCtrl(wx.ListCtrl):

    def __init__(self, parent, size, pos, style):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, pos, size, style)


class SortableListCtrlPanel(wx.Panel, listmix.ColumnSorterMixin):

    def __init__(self, parent, userframe):
        """Constructor"""
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        # show sums for each user
        offset = 5
        self.purchList = SortableListCtrl(parent=self, size=((userframe.getWidth() - btnWidth - 2*offset),
                                                             userframe.getHeight() - 2*offset),
                                          pos=(offset, offset),
                                          style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_SORT_DESCENDING)
        self.purchList.SetFont(wx.Font((fontSize - 5), wx.SWISS, wx.NORMAL, wx.BOLD))
        self.purchList.InsertColumn(0, 'name', width=180)
        self.purchList.InsertColumn(1, 'drinks', width=180)
        self.purchList.InsertColumn(2, 'money', width=180)
        index = 0
        users_purchases_df = functions.getPurchases()
        unique_users = users_purchases_df['user'].unique()
        usersPurchases_dict = {}
        for user in unique_users:
            nr, money = functions.getUserPurchases(users_purchases_df, user)
            usersPurchases_dict[index] = [user, int(nr), float("{:.2f}".format(money))]
            self.purchList.Append([user, nr, "{:.2f}".format(money)])
            self.purchList.SetItemData(index, index)
            index += 1

        self.itemDataMap = usersPurchases_dict  # used by ColumnSorterMixin
        listmix.ColumnSorterMixin.__init__(self, 3)
        self.purchList.Bind(wx.EVT_LIST_COL_CLICK, self._OnColumnClick)
        self.purchList.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnItemClick)

    # used by ColumnSorterMixin
    def GetListCtrl(self):
        return self.purchList

    def _OnColumnClick(self, event):
        event.Skip()

    def _OnItemClick(self, event):
        focus = self.purchList.GetFocusedItem()
        print(self.purchList.GetItem(focus).GetText())
