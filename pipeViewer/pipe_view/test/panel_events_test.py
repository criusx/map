import wx
import sys


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, title='Click Event Test')
        self.SetBackgroundColour(wx.Colour(70,80,255))

        # Panel (child of Frame)

        self.panel = wx.Panel(self, -1)
        self.panel.SetBackgroundColour(wx.Colour(255,110,0))

        # Canvas (child of Panel)

        self.canvas = wx.Window(self.panel, -1, style=0) # style=0 should prevent wxWS_EX_BLOCK_EVENTS
        ##self.canvas.SetExtraStyle(0)
        self.canvas.SetBackgroundColour(wx.Colour(80,60,25))

        # Layout

        csz = wx.BoxSizer(wx.VERTICAL)
        csz.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 20)
        ##csz.Add(self.playback_controls, 0, wx.EXPAND)
        self.panel.SetSizer(csz)

        psz = wx.BoxSizer(wx.VERTICAL)
        psz.Add(self.panel, 1, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(psz)


        # Bind to panel

        # Panel sees all key events even on the pansl
        self.panel.Bind(wx.EVT_CHAR, self.OnEvent)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnEvent)
        self.panel.Bind(wx.EVT_KEY_UP, self.OnEvent)
        
        # Apparently useless.
        ##self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnEvent)
        ##self.panel.Bind(wx.EVT_LEFT_UP, self.OnEvent)

        # Mouse events required on canvas apparently
        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.OnCanvasEvent)
        self.canvas.Bind(wx.EVT_LEFT_UP, self.OnCanvasEvent)


        # Setting focus to the canvas is required so that keystrokes go somewhere
        # This might not work if the canvas itelf will not accept focus
        assert self.canvas.AcceptsFocus()
        self.canvas.SetFocus()

    def OnEvent(self, evt):
        print 'Event: {0} : {1}'.format(evt.GetEventType(), evt)
        focus = self.FindFocus()
        if focus == self:
            print ' Focus = FRAME'
        elif focus == self.panel:
            print ' Focus = PANEL'
        elif focus == self.canvas:
            print ' Focus = CANVAS'
        else:
            print ' Focus = Unknown: {0}'.format(focus)

    def OnCanvasEvent(self, evt):
        print 'Canvas Event: {0} : {1}'.format(evt.GetEventType(), evt)
        focus = self.FindFocus()
        if focus == self:
            print ' Focus = FRAME'
        elif focus == self.panel:
            print ' Focus = PANEL'
        elif focus == self.canvas:
            print ' Focus = CANVAS'
        else:
            print ' Focus = Unknown: {0}'.format(focus)

        # Turning this on somehow allows click events to set focus on the canvas window.
        # Otherwise, wx.Window would never get the click events setting focus to it
        evt.Skip()

    #def OnChar(self, evt):
    #    print 'ON CHAR {0}'.format(evt.GetKeyCode())


app = wx.App()

f = Frame()
f.Show()

app.MainLoop()
