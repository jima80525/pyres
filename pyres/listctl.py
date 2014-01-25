import wx
import wx.lib.mixins.listctrl as listmix

musicdata = {
0 : ("Bad English", "The Price Of Love", "Rock"),
1 : ("DNA featuring Suzanne Vega", "Tom's Diner", "Rock"),
2 : ("George Michael", "Praying For Time", "Rock"),
3 : ("Gloria Estefan", "Here We Are", "Rock"),
4 : ("Linda Ronstadt", "Don't Know Much", "Rock"),
5 : ("Michael Bolton", "How Am I Supposed To Live Without You", "Blues"),
6 : ("Paul Young", "Oh Girl", "Rock"),
}

########################################################################
class TestListCtrl(wx.ListCtrl):

    #----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

########################################################################
class TestListCtrlPanel(wx.Panel, listmix.ColumnSorterMixin):

    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        self.index = 0

        self.list_ctrl = TestListCtrl(self, size=(-1,100),
                         style=wx.LC_REPORT
                         |wx.BORDER_SUNKEN
                         |wx.LC_SORT_ASCENDING
                         )
        self.list_ctrl.InsertColumn(0, "Artist")
        self.list_ctrl.InsertColumn(1, "Title", wx.LIST_FORMAT_RIGHT)
        self.list_ctrl.InsertColumn(2, "Genre")

        items = musicdata.items()
        index = 0
        for key, data in items:
            self.list_ctrl.InsertStringItem(index, data[0])
            self.list_ctrl.SetStringItem(index, 1, data[1])
            self.list_ctrl.SetStringItem(index, 2, data[2])
            self.list_ctrl.SetItemData(index, key)
            index += 1

        # Now that the list exists we can init the other base class,
        # see wx/lib/mixins/listctrl.py
        self.itemDataMap = musicdata
        listmix.ColumnSorterMixin.__init__(self, 3)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list_ctrl)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)

    #----------------------------------------------------------------------
    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.list_ctrl

    #----------------------------------------------------------------------
    def OnColClick(self, event):
        print "column clicked"
        event.Skip()

########################################################################
class MyForm(wx.Frame):

    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "List Control Tutorial")

        # Add a panel so it looks the correct on all platforms
        panel = TestListCtrlPanel(self)

#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()


