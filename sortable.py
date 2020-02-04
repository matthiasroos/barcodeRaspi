

import wx
import wx.lib.mixins.listctrl as listmix

import functions


class SortableListCtrl(wx.ListCtrl):

    def __init__(self, parent, size, pos, style):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, pos, size, style)


class SortableListCtrlPanel(wx.Panel, listmix.ColumnSorterMixin):

    def __init__(self, parent, super_parent):
        """Constructor"""
        self.super_parent = super_parent
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        with self.super_parent as sprt:
            # show sums for each user
            offset = 5
            self.purchList = SortableListCtrl(parent=self, size=((sprt.screen_width - sprt.btnWidth - 2*offset),
                                                                  sprt.screen_height - 2*offset),
                                              pos=(offset, offset),
                                              style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_SORT_DESCENDING)
            self.purchList.SetFont(wx.Font((sprt.fontSize - 5), wx.SWISS, wx.NORMAL, wx.BOLD))
            self.purchList.InsertColumn(0, 'name', width=180)
            self.purchList.InsertColumn(1, 'drinks', width=180)
            self.purchList.InsertColumn(2, 'money', width=180)
            index = 0
            users_purchases_df = functions.getPurchases()
            unique_users = users_purchases_df['user'].unique()
            usersPurchases_dict = {}
            for user in unique_users:
                nr, money = functions.getUserPurchases(users_purchases_df, user)
                usersPurchases_dict[index] = [user, int(nr), float('{:.2f}'.format(money))]
                self.purchList.Append([user, nr, '{:.2f}'.format(money)])
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