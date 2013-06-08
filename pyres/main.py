#!/usr/bin/python

# treectrl.py
# Name:         ListCtrl.py

import wx
import db
import rss




#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------


import wx
import wx.lib.mixins.listctrl as listmix

########################################################################
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

state_to_string = {
    0 : "To Download",
    1 : "Downloaded",
    2 : "Copied to Device",
    3 : "Finished",
    4 : "Unknown"
}

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MyFrame, self).__init__(*args, **kwargs)

        self.InitDb('rss.db')
        self.InitMenus()

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        treebox = wx.BoxSizer(wx.VERTICAL)
        listbox = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self, -1)
        panel2 = wx.Panel(self, -1)
        #panel2= TestListCtrlPanel(self)

        # panel1 will have the tree control
        self.tree = self.InitTreeCtrl(panel1)

        # panel2 will have a list control
        self.list = self.InitListCtrl(panel2)

        # for now panel two just has a static text box JHA TODO
        #self.display = wx.StaticText(panel2, -1, '',(10,10), style=wx.ALIGN_CENTRE)

        treebox.Add(self.tree, 1, wx.EXPAND)
        listbox.Add(self.list, 1, wx.EXPAND)
        hbox.Add(panel1, 1, wx.EXPAND)
        hbox.Add(panel2, 1, wx.EXPAND)
        panel1.SetSizer(treebox)
        panel2.SetSizer(listbox)
        self.SetSizer(hbox)

        self.SetSize((450, 350))
        self.SetTitle('Pyres')
        self.Centre()
        self.Show(True)

    def InitDb(self, db_name):
        self.conn, self.cur = db.open_podcasts(db_name)
        for u in urls:
            rss.add_episodes_from_feed(self.cur, u)

    def InitTreeCtrl(self, panel):
        tree = wx.TreeCtrl(panel, 1, wx.DefaultPosition, (-1,-1),
                                #wx.TR_ROW_LINES|wx.TR_HAS_BUTTONS)
                                wx.TR_HIDE_ROOT|wx.TR_ROW_LINES|wx.TR_HAS_BUTTONS)

        #root = tree.AddRoot('Podcasts')
        root = tree.AddRoot('Pyres')
        pc = tree.AppendItem(root, 'Podcasts')
        pcs = db.get_podcast_names(self.cur)

        for podcast in pcs:
            #tree.AppendItem(root, podcast)
            tree.AppendItem(pc, podcast)
        tree.Expand(pc)

        dv = tree.AppendItem(root, 'Devices')
        tree.AppendItem(dv, "Not Yet Implemented")

        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged, id=1)
        return tree

    def InitListCtrl(self, panel):
        self.index = 0

        list_ctrl = wx.ListCtrl(panel, 1,
                         style=wx.LC_REPORT
                         |wx.LC_SORT_ASCENDING
                         )
        list_ctrl.InsertColumn(0, "Title", wx.LIST_FORMAT_RIGHT)
        list_ctrl.InsertColumn(1, "State")

        # Now that the list exists we can init the other base class,
        # see wx/lib/mixins/listctrl.py
        #self.itemDataMap = musicdata
        #listmix.ColumnSorterMixin.__init__(self, 3)
        #self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, list_ctrl)
        return list_ctrl

    def FillInListData(self, episodes):
        self.list.DeleteAllItems()
        index = 0
        for data in episodes:
            pos = self.list.InsertStringItem(index, data[0])
            self.list.SetStringItem(pos, 1, state_to_string[data[1]])
            self.list.SetItemData(index, index)
            index += 1

    def OnTreeSelChanged(self, event):
        item =  event.GetItem()
        itemText = self.tree.GetItemText(item)
        if "Podcasts" not in itemText:
            episodes = db.find_episodes_and_states(self.cur, self.tree.GetItemText(item))
            self.FillInListData(episodes)

    def InitMenus(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

    def OnQuit(self, e):
        db.close_podcasts(self.conn)
        self.Close()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'treectrl.py')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()


