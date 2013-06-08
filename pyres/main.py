#!/usr/bin/python
import wx
import wx.lib.mixins.listctrl as listmix
import time
import db
import rss


########################################################################
class MyListCtrl(wx.ListCtrl, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, 1,
                             style=wx.LC_REPORT |wx.LC_SORT_ASCENDING)
        self.index = 0

        self.InsertColumn(0, "Title", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(1, "Date")
        self.InsertColumn(2, "State")

        # Now that the list exists we can init the other base class,
        # see wx/lib/mixins/listctrl.py
        listmix.ColumnSorterMixin.__init__(self, 2)

    def FillInListData(self, episodes):
        self.DeleteAllItems()
        self.itemDataMap = dict()
        index = 0
        for data in episodes:
            pos = self.InsertStringItem(index, data[0])
            self.SetStringItem(pos, 1, data[1])
            self.SetStringItem(pos, 2, data[2])
            self.SetItemData(pos, index)
            # convert string date to a datetime object for proper sorting
            data[1] = time.strptime(data[1], "%x:%X")
            # then store that in the itemDataMap so the column sorter can
            # get to it
            self.itemDataMap[index] = data
            index += 1
        self.SortListItems(1,0)

    #----------------------------------------------------------------------
    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self


########################################################################


#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

# JHA TODO
# This is just a hack to kick start us.  Need to have a way to specify a db on
# command line and also need to have the "add new feed" flow worked out
urls = (
    "http://rss.sciam.com/sciam/60-second-psych",
    "http://thehistoryofbyzantium.wordpress.com/feed/",
)

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MyFrame, self).__init__(*args, **kwargs)

        # initialize data base
        self.InitDb('rss.db')

        # set up menus
        self.InitMenus()

        # set up treeCtrl for left panel
        treebox = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self, -1)
        self.tree = self.InitTreeCtrl(panel1)
        treebox.Add(self.tree, 1, wx.EXPAND)
        panel1.SetSizer(treebox)

        # panel2 will have a list control
        listbox = wx.BoxSizer(wx.VERTICAL)
        panel2 = wx.Panel(self, -1)
        self.list = MyListCtrl(panel2)
        listbox.Add(self.list, 1, wx.EXPAND)
        panel2.SetSizer(listbox)

        # now set up the main box to hold the two control boxes
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(panel1, 1, wx.EXPAND)
        hbox.Add(panel2, 1, wx.EXPAND)
        self.SetSizer(hbox)

        # finally configure our frame
        self.SetSize((450, 350))
        self.SetTitle('Pyres')
        self.Centre()
        self.Show(True)

    def InitDb(self, db_name):
        self.conn, self.cur = db.open_podcasts(db_name)
        # JHA TODO this needs to query database for urls
        # JHA do we want to do this at start?  or on demand?
        for u in urls:
            rss.add_episodes_from_feed(self.cur, u)

    def InitTreeCtrl(self, panel):
        tree = wx.TreeCtrl(panel, 1, wx.DefaultPosition, (-1,-1),
                                wx.TR_HIDE_ROOT|wx.TR_ROW_LINES|wx.TR_HAS_BUTTONS)

        root = tree.AddRoot('Pyres')
        pc = tree.AppendItem(root, 'Podcasts')
        pcs = db.get_podcast_names(self.cur)

        for podcast in pcs:
            tree.AppendItem(pc, podcast)
        tree.Expand(pc)

        dv = tree.AppendItem(root, 'Devices')
        tree.AppendItem(dv, "Not Yet Implemented")

        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged, id=1)
        return tree

    def OnTreeSelChanged(self, event):
        item =  event.GetItem()
        itemText = self.tree.GetItemText(item)
        if "Podcasts" not in itemText:
            episodes = db.find_episodes_and_states(self.cur, self.tree.GetItemText(item))
            self.list.FillInListData(episodes)

    def InitMenus(self):
        # create the file menu
        fileMenu = wx.Menu()
        fitem = fileMenu.Append(wx.ID_ANY, 'Add Url', 'Add URL for podcast')
        self.Bind(wx.EVT_MENU, self.OnAddUrl, fitem)

        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

        menubar = wx.MenuBar()
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

    def OnQuit(self, e):
        db.close_podcasts(self.conn)
        self.Close()

    def OnAddUrl(self, e):
        print "in Add Url"

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'pyres.py')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()


