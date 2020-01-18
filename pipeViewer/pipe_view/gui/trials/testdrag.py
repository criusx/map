import wx
import wx.lib.dragscroller as drgscrl

class TestDrag(wx.Frame):
    def  __init__(self,parent,id, title):
        wx.Frame.__init__(self, parent, id, title, size = (600,600))
        self.win = wx.ScrolledWindow(self)
        self.win2 = drgscrl.DragScroller(self.win)
        self.win.SetScrollbars(50,50,55,40)

        self.win.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.win.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.win.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.PaintDC(self.win)
        self.win.DoPrepareDC(dc)

        pen = wx.Pen(wx.BLACK, 5)
        dc.SetPen(pen)

        for y in range(10):
            for x in range(10):
                dc.DrawCircle(x*400+20, y*400+20, 200)

        dc.DrawText('Right click and drag in the direction you want to scroll.',
                    20, 20)
        dc.DrawText('The distance from the start of the drag determines the speed.',
                    20, 50)



    def OnRightDown(self, event):
        print(event.GetPosition())
        self.win2.Start(event.GetPosition())

    def OnRightUp(self, event):
        self.win2.Stop()


class MyApp(wx.App):
    def OnInit(self):
        frame = TestDrag(None, -1, 'testing a dragger')
        frame.Show(True)
        frame.Centre()
        return True

app = MyApp(0)
app.MainLoop()
