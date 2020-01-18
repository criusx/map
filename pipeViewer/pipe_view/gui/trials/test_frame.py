import time
import wx
import sys
sys.path.append('../')
#from model.element import Element


class TestFrame(wx.Frame):

    def __init__(self, parent, id, title):
        size = (100,100)
        wx.Frame.__init__(self, parent, id, title, size)

        self.Bind(wx.EVT_PAINT, self.Paint)
        self.SetBackgroundColour("WHITE")
        self.Centre()
        self.Show(True)
        self.CreateStatusBar()
        self.buffer = wx.EmptyBitmap(size[0],size[1])  # draw to this
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()  # black window otherwise


        self.Draw()
        self.Paint(None)

    def Draw(self):
        self.SetStatusText("I am currently a fake LayoutFrame") # fix this later
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.SetPen(wx.Pen((0,255,255),2,wx.SOLID))
        dc.DrawRectangle(300,100,400,200)
        (width, height)=self.GetSizeTuple()
        dc.DrawRoundedRectangle(0, 0,width, height, 8)

#        dc.Clear()

    def Paint(self, event):
        wx.BufferedPaintDC(self, self.buffer)

    def SetElement(self, element):
        self.__element = element

    def GetElement(self):
        return self.__element



if __name__ == "__main__":
    app = wx.App(0)
    TestFrame(None, -1, "sup")
    app.MainLoop()
