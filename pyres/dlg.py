#!/usr/bin/python

import wx

class MyDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(350,300))

        l1 = wx.StaticText(self, -1, "Podcast Name")
        self.podcast_name = wx.TextCtrl(self, -1, "", size=(125, -1))
        wx.CallAfter(self.podcast_name.SetInsertionPoint, 0)

        l2 = wx.StaticText(self, -1, "Url")
        self.podcast_url = wx.TextCtrl(self, -1, "", size=(125, -1))

        space = 1
        sizer = wx.FlexGridSizer(cols=2, hgap=space, vgap=space)
        sizer.AddMany([ l1, self.podcast_name,
                        l2, self.podcast_url,
                        ])

        # set up std buttons
        btnSizer = wx.StdDialogButtonSizer()
        btnSizer.AddButton(wx.Button(self, wx.ID_OK))
        btnSizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        btnSizer.Realize()

        # create main sizer and add other sizers to it
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(sizer, 0, wx.ALL, 25)
        border.Add(btnSizer)

        self.SetSizer(border)
        self.SetAutoLayout(True)

    def GetInput(self):
        if self.ShowModal() == wx.ID_OK:
            return (self.podcast_name.GetValue(), self.podcast_url.GetValue())
        else:
            return (None, None)

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(550,500))

        panel = wx.Panel(self, -1)
        wx.Button(panel, 1, 'Show Custom Dialog', (100,100))
        self.Bind (wx.EVT_BUTTON, self.OnShowCustomDialog, id=1)

    def OnShowCustomDialog(self, event):
        dia = MyDialog(self, -1, 'buttons')
        (name, url) = dia.GetInput()
        if name:
            print "name was ", name
            print "url was  ", url
        dia.Destroy()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'customdialog1.py')
        frame.Show(True)
        frame.Centre()
        return True

app = MyApp(0)
app.MainLoop()


