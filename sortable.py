
import pandas as pd
import wx
import wx.lib.mixins.listctrl as listmix


class SortableListCtrl(wx.ListCtrl):

    def __init__(self, parent, size, pos, style):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, pos, size, style)


class SortableListCtrlPanel(wx.Panel, listmix.ColumnSorterMixin):

    def __init__(self, parent, super_parent, columns: dict, data_frame: pd.DataFrame):
        """Constructor"""
        self.super_parent = super_parent
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        with self.super_parent as sprt:
            offset = sprt.displaySettings.offSet
            self.sortable_list_ctrl = SortableListCtrl(parent=self,
                                                       size=((sprt.displaySettings.screen_width -
                                                              sprt.displaySettings.btnWidth - 2*offset),
                                                             sprt.displaySettings.screen_height - 2*offset),
                                                       pos=(offset, offset),
                                                       style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_SORT_DESCENDING)
            self.sortable_list_ctrl.SetFont(sprt.displaySettings.wxFont)
            nr_columns = len(columns.get('names'))
            for i in range(0, nr_columns):
                self.sortable_list_ctrl.InsertColumn(i, columns.get('names')[i], width=columns.get('width')[i])
            index = 0
            values_dict = {}
            for index, row in data_frame.iterrows():
                values_list = [row[column] for column in columns.get('names')]
                values_dict[index] = values_list
                self.sortable_list_ctrl.Append([columns.get('type')[i](value) for i, value in enumerate(values_list)])
                self.sortable_list_ctrl.SetItemData(index, index)
                index += 1

            self.itemDataMap = values_dict  # used by ColumnSorterMixin
            listmix.ColumnSorterMixin.__init__(self, 3)
            self.sortable_list_ctrl.Bind(wx.EVT_LIST_COL_CLICK, self._OnColumnClick)
            self.sortable_list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnItemClick)

    # used by ColumnSorterMixin
    def GetListCtrl(self):
        return self.sortable_list_ctrl

    def _OnColumnClick(self, event):
        event.Skip()

    def _OnItemClick(self, event):
        pass
