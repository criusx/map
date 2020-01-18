"""
This is a testing-purposes-only file. The Database Handle & related classes
have been added to the model-side, and this is an attempt to get data
displaying in the view, in a single frame.
-Josh

"""
import wx
import sys
sys.path.append('../')
from model.layout import Layout
from model.layout_context import Layout_Context
from model.element import Element
from gui.layout_frame import Layout_Frame







class MyApp(wx.App):
    def OnInit(self):
        one = Element()
        one.SetProperty('color', (100,30,170))
        one.SetProperty('position',(500,500))
        two = Element(one)
        two.SetProperty('position', (550,500))
        three = Element()
        three.SetProperty('position', (600,500))
        layout = Layout()
        layout.CreateElement(one)
        layout.CreateElement(two)
        layout.CreateElement(three)
        context = Layout_Context(layout)
        frame = Layout_Frame(None, -1, 'Frame 1', context)
        frame.Show(True)
        frame.Centre()
        return True

app = MyApp(0)
app.MainLoop()
