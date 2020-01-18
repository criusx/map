import sys
import wx
import wx.lib.mixins.listctrl  as  listmix

#---------------------------------------------------------------------------

listctrldata = {
1 : ("Hey!", "You can edit", "me!"),
2 : ("Try changing the contents", "by", "clicking"),
3 : ("in", "a", "cell"),
4 : ("See how the length columns", "change", "?"),
5 : ("You can use", "TAB,", "cursor down,"),
6 : ("and cursor up", "to", "navigate"),
}

#---------------------------------------------------------------------------

class JoshCtrl(wx.ListCtrl,
                   listmix.ListCtrlAutoWidthMixin,
                   listmix.TextEditMixin):

    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.Populate()
        listmix.TextEditMixin.__init__(self)

    def Populate(self):
        # for normal, simple columns, you can add them like this:
        self.InsertColumn(0, "Column 1")
        self.InsertColumn(1, "Column 2")
        self.InsertColumn(2, "Column 3")
        self.InsertColumn(3, "Len 1", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(4, "Len 2", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(5, "Len 3", wx.LIST_FORMAT_RIGHT)

        items = listctrldata.items()
        for key, data in items:
            index = self.InsertStringItem(sys.maxint, data[0])
            self.SetStringItem(index, 1, data[1])
            self.SetStringItem(index, 2, data[2])
            self.SetItemData(index, key)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, 100)

        self.currentItem = 0


    def SetStringItem(self, index, col, data):
        if col in range(3):
            wx.ListCtrl.SetStringItem(self, index, col, data)
            wx.ListCtrl.SetStringItem(self, index, 3+col, str(len(data)))
        else:
            try:
                datalen = int(data)
            except:
                return

            wx.ListCtrl.SetStringItem(self, index, col, data)

            data = self.GetItem(index, col-3).GetText()
            wx.ListCtrl.SetStringItem(self, index, col-3, data[0:datalen])




class JoshCtrlPanel(wx.Panel ):



    def __init__(self, parent, id, title, element=None):
        size = (100,100)

        if element is not None:
            self.__element = element
        wx.Frame.__init__(self, parent, id, title, size)
        wx.Panel.__init__(self, parent, id, style=wx.WANTS_CHARS)
        self.Bind(wx.EVT_PAINT, self.Paint)
        self.SetBackgroundColour("WHITE")
        self.Centre()
        self.Show(True)
        self.CreateStatusBar()
        self.buffer = wx.EmptyBitmap(size[0],size[1])  # draw to this
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()  # black window otherwise


        sizer = wx.BoxSizer(wx.VERTICAL)

        self.list = TestListCtrl(self, tID,
                                 style=wx.LC_REPORT
                                 | wx.BORDER_NONE
                                 | wx.LC_SORT_ASCENDING
                                 )

        sizer.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
