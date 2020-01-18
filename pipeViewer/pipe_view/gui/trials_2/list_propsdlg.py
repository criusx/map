
import time
import wx
import sys
sys.path.append('../')
from model.element import Element
import wx.lib.mixins.listctrl  as  listmix


class ListDlg(wx.Frame):

    def __init__(self, parent, id, title, element=None):
        size = (100,100)
        self.__parent = parent
        if element is not None:
            self.__element = element
        else:
            self.__element = Element()
        wx.Frame.__init__(self, parent, id, title, size)

        self.__timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Draw, self.__timer)

        self.Bind(wx.EVT_PAINT, self.Paint)
        self.SetBackgroundColour("WHITE")
        self.Centre()
        self.Show(True)
        self.CreateStatusBar()
        self.buffer = wx.EmptyBitmap(size[0],size[1])  # draw to this
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()  # black window otherwise


        sampleList=['type','start','end','transaction','loc','loc_id','flags','parent','opcode','vaddr','paddr','annotation','caption','clock']
        combo = wx.ComboBox(self, 500, "default val", (90,50), (160, -1),
                            sampleList, wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, combo)

        sizer = wx.BoxSizer(wx.VERTICAL)
        lower = wx.BoxSizer(wx.HORIZONTAL)

        self.list = JoshCtrl(self, id,
                             style=wx.LC_REPORT
                             | wx.BORDER_NONE
                             | wx.LC_SORT_ASCENDING,
                             element=self.__element
                                 )

        sizer.Add(self.list, 1, wx.EXPAND)
        lower.Add(wx.StaticText(self, -1, "Content:"),2,wx.ALIGN_RIGHT)
        lower.Add(combo, 0, wx.ALIGN_RIGHT)
        sizer.Add(lower, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)



        self.Draw()

    def Draw(self, evt=None):
        self.__timer.Stop()
        font = self.GetStatusBar().GetFont()
        font.SetWeight(wx.NORMAL)
        self.GetStatusBar().SetFont(font)
        self.GetStatusBar().SetBackgroundColour(wx.WHITE)
        self.SetStatusText("I don't currently know what Frame I belong to")#fix this later
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()

    def RaiseError(self, error):
        self.SetStatusText(str(error))
        font = self.GetStatusBar().GetFont()
        font.SetWeight(wx.BOLD)
        self.GetStatusBar().SetFont(font)
        self.GetStatusBar().SetBackgroundColour(wx.RED)
        self.__timer.Start()


    def Paint(self, event):
        wx.BufferedPaintDC(self, self.buffer)

    def SetElement(self, element):
        self.__element = element

    def GetElement(self):
        return self.__element

    def EvtComboBox(self, evt):
        cb = evt.GetEventObject()
        self.__element.SetProperty('Content', evt.GetString())


class JoshCtrl(wx.ListCtrl,
                   listmix.ListCtrlAutoWidthMixin,
                   listmix.TextEditMixin):

    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, element=None):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.__element = element
        self.__keys = []
        self.Populate()
        listmix.TextEditMixin.__init__(self)
        self.__parent = parent

    def OpenEditor(self,col,row):
        if col == 1:
            super(JoshCtrl,self).OpenEditor(col,row)

    def SetStringItem(self, index, col, data):
        try:
            self.__element.SetProperty(self.__keys[index],data)
            super(JoshCtrl,self).SetStringItem(index,col,str(self.__element.GetProperty(self.__keys[index])))
        except ValueError as v:
            self.__parent.RaiseError(v)


    def Populate(self):
        # for normal, simple columns, you can add them like this:
        self.InsertColumn(0, "Property")
        self.InsertColumn(5, "Value", wx.LIST_FORMAT_RIGHT)

        index = 0
        props = self.__element.GetProperty("All")
        for key in props:
            if key is not 'Content':
                self.__keys.append(key)
                self.InsertStringItem(index, key)
                self.SetStringItem(index, 1, str(props[key]))
                #super(JoshCtrl,self).SetStringItem(index, 1, 'sofa')
                if index % 2:
                    self.SetItemBackgroundColour(index, "white")
                else:
                    self.SetItemBackgroundColour(index, "gray")
                index += 1

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, 100)
        self.currentItem = 0
