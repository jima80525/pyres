#!/usr/bin/python
""" testing a dialog box """

import wx


class MyDialog(wx.Dialog):  # pylint: disable=too-many-public-methods
    """ Dialog """
    def __init__(self, parent, myId, title):
        wx.Dialog.__init__(self, parent, myId, title, size=(350, 300))

        text1 = wx.StaticText(self, -1, "Podcast Name")
        self.podcast_name = wx.TextCtrl(self, -1, "", size=(125, -1))
        wx.CallAfter(self.podcast_name.SetInsertionPoint, 0)

        text2 = wx.StaticText(self, -1, "Url")
        self.podcast_url = wx.TextCtrl(self, -1, "", size=(125, -1))

        space = 1
        sizer = wx.FlexGridSizer(cols=2, hgap=space, vgap=space)
        sizer.AddMany([text1, self.podcast_name,
                       text2, self.podcast_url, ])

        # set up std buttons
        button_sizer = wx.StdDialogButtonSizer()
        button_sizer.AddButton(wx.Button(self, wx.ID_OK))
        button_sizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        button_sizer.Realize()

        # create main sizer and add other sizers to it
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(sizer, 0, wx.ALL, 25)
        border.Add(button_sizer)

        self.SetSizer(border)
        self.SetAutoLayout(True)

    def get_input(self):
        """ read input from the user """
        if self.ShowModal() == wx.ID_OK:
            return (self.podcast_name.GetValue(), self.podcast_url.GetValue())
        else:
            return (None, None)


class MyFrame(wx.Frame):  # pylint: disable=too-many-public-methods
    """ Class to set up initial frame """
    def __init__(self, parent, myId, title):
        wx.Frame.__init__(self, parent, myId, title, size=(550, 500))

        panel = wx.Panel(self, -1)
        wx.Button(panel, 1, 'Show Custom Dialog', (100, 100))
        self.Bind(wx.EVT_BUTTON, self.on_show_custom_dialog, id=1)
        wx.StaticText(panel, -1, "Podcast Name")

    def on_show_custom_dialog(self, event):
        """ called when button is pressed to show dialog """
        dia = MyDialog(self, -1, 'buttons')
        print event
        (name, url) = dia.get_input()
        if name:
            print "name was ", name
            print "url was  ", url
        dia.Destroy()


class MyApp(wx.App):  # pylint: disable=too-many-public-methods
    """ The main app """
    def OnInit(self):  # pylint: disable=invalid-name,no-self-use
        """ Called when app started """
        frame = MyFrame(None, -1, 'customdialog1.py')
        frame.Show(True)
        frame.Centre()
        return True

APP = MyApp(0)
APP.MainLoop()
