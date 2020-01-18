import wx
import wx.lib.ogl as ogl
import sys
sys.path.append('../')
from model.element import Element
from model.layout import Layout
from gui.element_propsdlg import ElementDlg

#----------------------------------------------------------------------

class DrawElement(ogl.RectangleShape):
    def __init__(self,w=1.0,h=1.0):
        ogl.RectangleShape.__init__(self,w,h)


class DrawnShape(ogl.DrawnShape):
    def __init__(self):
        ogl.DrawnShape.__init__(self)

        self.SetDrawnBrush(wx.WHITE_BRUSH)
        self.SetDrawnPen(wx.BLACK_PEN)
        self.DrawArc((0, -10), (30, 0), (-30, 0))

        self.SetDrawnPen(wx.Pen("#ff8030"))
        self.DrawLine((-30, 5), (30, 5))

        self.SetDrawnPen(wx.Pen("#00ee10"))
        self.DrawRoundedRectangle((-20, 10, 40, 10), 5)

        self.SetDrawnPen(wx.Pen("#9090f0"))
        self.DrawEllipse((-30, 25, 60, 20))

        self.SetDrawnTextColour(wx.BLACK)
        self.SetDrawnFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.DrawText("DrawText", (-26, 28))

        self.SetDrawnBrush(wx.GREEN_BRUSH)
        self.DrawPolygon([(-100, 5), (-45, 30), (-35, 20), (-30, 5)])

        self.SetDrawnPen(wx.BLACK_PEN)
        self.DrawLines([(30, -45), (40, -45), (40 ,45), (30, 45)])

        # Make sure to call CalculateSize when all drawing is done
        self.CalculateSize()


#----------------------------------------------------------------------

class RoundedRectangleShape(ogl.RectangleShape):
    def __init__(self, w=0.0, h=0.0):
        ogl.RectangleShape.__init__(self, w, h)
        self.SetCornerRadius(-0.3)



#----------------------------------------------------------------------

class MyEvtHandler(ogl.ShapeEvtHandler):
    def __init__(self, log, frame):
        ogl.ShapeEvtHandler.__init__(self)
        self.log = log
        self.statbarFrame = frame

    def UpdateStatusBar(self, shape):
        x, y = shape.GetX(), shape.GetY()
        width, height = shape.GetBoundingBoxMax()
        self.statbarFrame.SetStatusText("Pos: (%d, %d)  Size: (%d, %d)" %
                                        (x, y, width, height))


    def OnLeftClick(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        canvas = shape.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        if shape.Selected():
            shape.Select(False, dc)
            #canvas.Redraw(dc)
            canvas.Refresh(False)
        else:
            redraw = False
            shapeList = canvas.GetDiagram().GetShapeList()
            toUnselect = []

            for s in shapeList:
                if s.Selected():
                    # If we unselect it now then some of the objects in
                    # shapeList will become invalid (the control points are
                    # shapes too!) and bad things will happen...
                    toUnselect.append(s)

            shape.Select(True, dc)

            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)

                ##canvas.Redraw(dc)
                canvas.Refresh(False)

        self.UpdateStatusBar(shape)


    def OnEndDragLeft(self, x, y, keys=0, attachment=0):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)

        if not shape.Selected():
            self.OnLeftClick(x, y, keys, attachment)

        self.UpdateStatusBar(shape)


    def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
        ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
        self.UpdateStatusBar(self.GetShape())


    def OnMovePost(self, dc, x, y, oldX, oldY, display):
        shape = self.GetShape()
        ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
        self.UpdateStatusBar(shape)
        if "wxMac" in wx.PlatformInfo:
            shape.GetCanvas().Refresh(False)

    def OnRightClick(self, *dontcare):
        self.log.WriteText("%s\n" % self.GetShape())
        print('fat')


#----------------------------------------------------------------------

class TestWindow(ogl.ShapeCanvas):
    def __init__(self, parent, log, frame):
        one = Element()
        dlg = ElementDlg(None, -1, "Element Properties Dialog",one)
        ogl.ShapeCanvas.__init__(self, parent)

        maxWidth  = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth/20, maxHeight/20)

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE") #wx.WHITE)
        self.diagram = ogl.Diagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.shapes = []
        self.save_gdi = []

        rRectBrush = wx.Brush("MEDIUM TURQUOISE", wx.SOLID)
        dsBrush = wx.Brush("WHEAT", wx.SOLID)


        self.MyAddShape(
            ogl.RectangleShape(85, 50),
            305, 60, wx.BLACK_PEN, wx.LIGHT_GREY_BRUSH, "Rectangle"
            )

        self.MyAddShape(
            RoundedRectangleShape(95, 70),
            345, 145, wx.Pen(wx.RED, 2), rRectBrush, "Rounded Rect"
            )

        self.MyAddShape(
            DrawElement(95,70),
            250, 50, wx.Pen(wx.RED, 2), rRectBrush, one.GetProperty("Content")
            )


        """
        bmp = images.Test2.GetBitmap()
        mask = wx.Mask(bmp, wx.BLUE)
        bmp.SetMask(mask)

        s = ogl.BitmapShape()
        s.SetBitmap(bmp)
        self.MyAddShape(s, 225, 130, None, None, "Bitmap")
        """
        #dc = wx.ClientDC(self)
        #self.PrepareDC(dc)

        for x in range(len(self.shapes)):
            fromShape = self.shapes[x]
            if x+1 == len(self.shapes):
                toShape = self.shapes[0]
            else:
                toShape = self.shapes[x+1]

            line = ogl.LineShape()
            line.SetCanvas(self)
            line.SetPen(wx.BLACK_PEN)
            line.SetBrush(wx.BLACK_BRUSH)
            line.AddArrow(ogl.ARROW_ARROW)
            line.MakeLineControlPoints(2)
            fromShape.AddLine(line, toShape)
            self.diagram.AddShape(line)
            line.Show(True)


    def MyAddShape(self, shape, x, y, pen, brush, text):

        shape.SetDraggable(True, True)
        shape.SetCanvas(self)
        shape.SetX(x)
        shape.SetY(y)
        if pen:
            shape.SetPen(pen)
        if brush:
            shape.SetBrush(brush)
        if text:
            for line in text.split('\n'):
                shape.AddText(line)
        shape.SetShadowMode(ogl.SHADOW_RIGHT)
        self.diagram.AddShape(shape)
        shape.Show(True)

        evthandler = MyEvtHandler(self.log, self.frame)
        evthandler.SetShape(shape)
        evthandler.SetPreviousHandler(shape.GetEventHandler())
        shape.SetEventHandler(evthandler)

        self.shapes.append(shape)
        return shape


    def OnBeginDragLeft(self, x, y, keys):
        self.log.write("OnBeginDragLeft: %s, %s, %s\n" % (x, y, keys))

    def OnEndDragLeft(self, x, y, keys):
        self.log.write("OnEndDragLeft: %s, %s, %s\n" % (x, y, keys))


#----------------------------------------------------------------------

def runTest(frame, nb, log):
    # This creates some pens and brushes that the OGL library uses.
    # It should be called after the app object has been created, but
    # before OGL is used.
    ogl.OGLInitialize()

    win = TestWindow(nb, log, frame)
    return win

#----------------------------------------------------------------------



if __name__ == '__main__':
    print('WHAT?')
    import sys, os
    import run
    run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
