import sys
import wx
sys.path.append('../')
from model.element import Element
from model.layout import Layout
from model.layout_context import Layout_Context
# from gui.element_propsdlg import Element_PropsDlg
# from gui.dragscroll import DragScrollerExample

i = 7.5


## This test is about hashability of elements
if i == 7.5:
    one = Element()
    two = Element()
    three = Element()
    four = Element()
    five = Element()

    map = {one: (1,1), two:(2,2),three:(3,3),four:(4,4),five:(5,5)}
    print map

if i == 7:
    lyt = Layout()
    start = lyt.CreateElement()
    end = lyt.CreateElement()
    vaddr = lyt.CreateElement()
    start.SetProperty('Content', 'start')
    end.SetProperty('Content', 'end')
    vaddr.SetProperty('Content','vaddr')
    lytctxt = Layout_Context(lyt)
    print repr(lytctxt)
    print


    paddr = lyt.CreateElement()
    flags = lyt.CreateElement()
    clock = lyt.CreateElement()

    paddr.SetProperty('Content', 'paddr')
    flags.SetProperty('Content', 'flags')
    clock.SetProperty('Content', 'clock')


    paddr.SetProperty('LocationString', 'gpu')
    clock.SetProperty('LocationString', 'gpu')
    flags.SetProperty('LocationString', 'gpu')
    print repr(lytctxt)

    end.SetProperty('t_offset', -10 )
    vaddr.SetProperty('t_offset', +10)
    flags.SetProperty('t_offset', -10 )
    clock.SetProperty('t_offset', +10)
    print repr(lytctxt)

    end.SetProperty('t_offset', 5 )
    vaddr.SetProperty('t_offset', 5)
    flags.SetProperty('t_offset', 5 )
    paddr.SetProperty('t_offset', 5)
    print repr(lytctxt)

## Tests before i6 had the ordered_dict underneath layout
## i6 saw the ordered_dict become a series of nested dictionaries
## i7 and beyond should see ordered_dict within layout_context, and the
## entries should be [Element, val] instead of Elements
if i == 6:


    lyt = Layout()
    one = lyt.CreateElement()
    one.SetProperty('Content','start')
    one.SetProperty('LocationString', 'bottom')
    #one.SetProperty('t_offset', 20)
    two = lyt.CreateElement(one)
    two.SetProperty('Content','end')
    three = lyt.CreateElement()
    three.SetProperty('Content','opcode')
    four = lyt.CreateElement()
    four.SetProperty('Content', 'clock')
    print repr(lyt)

    three.SetProperty('LocationString','top.cp0')
    print
    print repr(lyt)


if i == 5:
    app = wx.App(0)
    dlg = Element_PropsDlg(None, -1, "this be a test")
    drg = DragScrollerExample(dlg)
    app.MainLoop()


if i == 4:
    app = wx.App(0)
    dlg = Element_PropsDlg(None, -1, "this be a test")
    app.MainLoop()



if i == 3:
    #    try:
    app = wx.App(0)
    one = Element()
    dlg = ElementDlg(None, -1, "Element Properties Dialog",one)
    app.MainLoop()
    print one


#    except:
 #       print("crud")

if i == 2:
    lyt = Layout()
    one = lyt.CreateElement()
    one.SetProperty('Content','flags')
    two = lyt.CreateElement()
    two.SetProperty('Content','parent')
    three = lyt.CreateElement()
    three.SetProperty('Content','clock')
    four = lyt.CreateElement()
    print repr(lyt)
    three.SetProperty('IDstring','top.cp0')
    print
    print repr(lyt)

    four.SetProperty('IDstring','top.cpu1')
    print repr(lyt)
    print

    one.SetProperty('IDstring', 'top1.cpu20')
    print repr(lyt)
    print

    two.SetProperty('IDstring','top.cpu')
    print repr(lyt)
    print


    one.SetProperty('Content','clock')

    two.SetProperty('color', (2,2,5))
    two.SetProperty('IDstring', 'top.cpu')


    print repr(lyt)


if i == 1:
    try:
        one = Element()
        one.SetProperty('color',(0,0,0))
        #one.SetProperty('color',(-1,2,4))
        one.SetProperty('dimensions',(10,10))
        #one.SetProperty('dimensions',('f',20))
        one.SetProperty('IDstring', 'top.cpu0')
        #one.SetProperty('IDstring', 124)
        one.SetProperty('position', (23,43))
        #one.SetProperty('position', (23,32,32))
        one.SetProperty('caption', "this is a test")
        #one.SetProperty('caption', 234)
        one.SetProperty('t_offset', 0)
        #one.SetProperty('t_offset', 23)
        one.SetProperty('annotation', 'this is a test')
        #one.SetProperty('annotation', ('this is a test','this is a test'))
        one.SetProperty('Content', 'flags')
        #one.SetProperty('Content', 'this is a test')

        two = Element(one)
        two.SetProperty('color', (0,0,20))
        two.SetProperty('Content','parent')
        three = Element(one)
        two.SetProperty('IDstring', 'top.cpu1')
        print one
        print two
        print three



    except ValueError as v:
        print v

    except TypeError as t:
        print t
