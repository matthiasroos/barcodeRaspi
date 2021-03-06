
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
            offset = sprt.display_settings.off_set
            self.sortable_list_ctrl = SortableListCtrl(parent=self,
                                                       size=((sprt.display_settings.screen_width -
                                                              sprt.display_settings.btn_width - 2 * offset),
                                                             sprt.display_settings.screen_height - 2 * offset),
                                                       pos=(offset, offset),
                                                       style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_SORT_DESCENDING)
            self.sortable_list_ctrl.SetFont(sprt.display_settings.wx_font)
            for i, (name, width) in enumerate(zip(columns.get('names'), columns.get('width'))):
                self.sortable_list_ctrl.InsertColumn(i, name, width=width)
            values_dict = {}
            for index, row in data_frame.iterrows():
                values_list = [row[column] for column in columns.get('names')]
                values_dict[index] = values_list
                self.sortable_list_ctrl.Append([type_(value) for value, type_ in zip(values_list, columns.get('type'))])
                self.sortable_list_ctrl.SetItemData(index, index)

            self.itemDataMap = values_dict  # used by ColumnSorterMixin
            listmix.ColumnSorterMixin.__init__(self, len(columns.get('names')))
            self.sortable_list_ctrl.Bind(wx.EVT_LIST_COL_CLICK, self._OnColumnClick)
            self.sortable_list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnItemClick)

    # used by ColumnSorterMixin
    def GetListCtrl(self) -> SortableListCtrl:
        """"""
        return self.sortable_list_ctrl

    def _OnColumnClick(self, event) -> None:
        """"""
        event.Skip()

    def _OnItemClick(self, event) -> None:
        """"""
        pass
