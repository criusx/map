



import wx

class Layout_Canvas():

    def __init__(self, win=None, layout = None):
        self.__win = win
        self.__layout = layout
        self.__selected = False


    def OnButtonClicked(self, event):
        print 'click'

    def FoundClick(self, event):
        print 'Layout canvas got it'

    def OnPaint(self):
        dc = wx.PaintDC(self.__win)
        self.__win.DoPrepareDC(dc)

        for e in self.__layout.GetElements():
            (x,y),(w,h) = e.GetProperty('position'),e.GetProperty('dimensions')
            pen  = wx.Pen(e.GetProperty('color'), 2)
            dc.SetPen(pen)
            dc.DrawRectangle(x,y,w,h)


    def DetectCollision(self, pt):
        mx,my = pt
        for e in self.__layout.GetElements():
            x,y = e.GetProperty('position')
            w,h = e.GetProperty('dimensions')
            if x<=mx<=(x+w) and y<=my<=(y+h):
                return e


    def Drag(self, element):
        print element.GetProperty('position')
        if self.__selected:
            self.Drag(element)

    def EndDrag(self):
        self.__selected = False

    def OnLeftDouble(self, event):
        print 'double'
