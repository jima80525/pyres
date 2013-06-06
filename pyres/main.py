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
        #wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        wx.Panel.__init__(self, parent, -1)

        self.index = 0

        #self.list_ctrl = TestListCtrl(self, size=(-1,100),
        #self.list_ctrl = wx.ListCtrl(self, size=(-1,100),
        self.list_ctrl = wx.ListCtrl(self, 1, wx.DefaultPosition, (-1, -1),
                         style=wx.LC_REPORT
                         #|wx.BORDER_SUNKEN
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

        #sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 5)
        #self.SetSizer(sizer)

    #----------------------------------------------------------------------
    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.list_ctrl

    #----------------------------------------------------------------------
    def OnColClick(self, event):
        print "column clicked"
        event.Skip()

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

#---------------------------------------------------
#def dummy():
    #pcs = db.get_podcast_names(cur)

    #for podcast in pcs:
        #episodes = db.find_episodes_to_download(cur, podcast)
        #toMark = True
        #print "----------------------------------------"
        #print podcast
        #print "----------------------------------------"
        #for e in episodes:
            #if toMark:
                #db.mark_episode_downloaded(cur, podcast, e[0])
                #print e, "MARKED"
                #toMark = False
            #else:
                #print e

        #print
#---------------------------------------------------

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
                         #|wx.BORDER_SUNKEN
                         |wx.LC_SORT_ASCENDING
                         )
        list_ctrl.InsertColumn(0, "Artist")
        list_ctrl.InsertColumn(1, "Title", wx.LIST_FORMAT_RIGHT)
        list_ctrl.InsertColumn(2, "Genre")

        items = musicdata.items()
        index = 0
        for key, data in items:
            list_ctrl.InsertStringItem(index, data[0])
            list_ctrl.SetStringItem(index, 1, data[1])
            list_ctrl.SetStringItem(index, 2, data[2])
            list_ctrl.SetItemData(index, key)
            index += 1

        # Now that the list exists we can init the other base class,
        # see wx/lib/mixins/listctrl.py
        #self.itemDataMap = musicdata
        #listmix.ColumnSorterMixin.__init__(self, 3)
        #self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, list_ctrl)
        return list_ctrl

    def InitMenus(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)


    def OnTreeSelChanged(self, event):
        item =  event.GetItem()
        print "selchanged"
        print item
        #self.display.SetLabel(self.tree.GetItemText(item))

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


