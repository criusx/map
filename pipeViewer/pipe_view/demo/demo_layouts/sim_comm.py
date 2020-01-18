#!/usr/bin/env python

import uuid
import os
import Tkinter
import wx
import wx.lib.newevent
import Queue
import threading
import atexit
import time

class SimComm(object):
    def __init__(self, appname, init_uuid=None, tkRoot=None, tkRootFork=True, tkRoot_withdraw=True, wxEvtHandlr=None):
        assert not (tkRoot and wxEvtHandlr), "Cannot use both wx (%s) and tk (%s) from the same thread"%(str(wxEvtHandlr),str(tkRoot))
        assert not (not tkRoot and tkRootFork==False and wxEvtHandlr), "Cannot have wx and make tk in same thread"

        if init_uuid == None:
            init_uuid = os.environ.get('%s_UUID'%(appname))
            if not init_uuid:
                if os.path.exists('uuid'):
                    init_uuid = open('uuid','r').readline().rstrip('\n')
                else:
                    init_uuid = uuid.uuid1()
        self.uuid = init_uuid

        if not tkRoot and not tkRootFork:
            tkRoot = Tkinter.Tk()
            # Only withdraw tkRoot if we are creator
            if tkRoot_withdraw:
                tkRoot.withdraw()

        if tkRoot:
            tkRootFork = False
            self.tkRoot = tkRoot

        self.appname = appname
        self.withdraw = tkRoot_withdraw

        self.tkProc = None
        self.wxEvtHandlr = wxEvtHandlr
        if wxEvtHandlr:
            wxEvtHandlr.__sim_comm = self
            (self.ThreadedResultEvent, self.EVT_THREAD_RESULT) = wx.lib.newevent.NewEvent()
            def OnThreadedResultEvent(event):
                #print "OnThreadedResultEvent: f=%s a=%s k=%s"%(str(event.func),str(event.args),str(event.kwargs))
                #self.tkRet.put(event.func(*event.args,**event.kwargs))
                event.func(*event.args,**event.kwargs)
            wxEvtHandlr.Bind(self.EVT_THREAD_RESULT, OnThreadedResultEvent)
        
        # Run the tk mainloop in a background thread and proxy any calls over
        if tkRootFork:
            self.tkQueue = Queue.Queue()
            self.tkRet = Queue.Queue()
            self.mQueue = Queue.Queue()
            self.upQueue = Queue.Queue()
            self.tkProc = threading.Thread(target=self.__TkRun)
            self.tkProc.daemon = True
            def atExitTkDone():
                def tkDone():
                    if self.tkRoot:
                        try:
                            self.tkRoot.destroy()
                        except:
                            pass
                if self.tkRoot:
                    self.tkQueue.put((tkDone,(), {}))
                self.tkProc.join(5)
            self.tkProc.start()
            self.mQueue.get(True)
            atexit.register(atExitTkDone)
        else:
            tkRoot.eval("tk appname %s_%s"%(appname, self.uuid))

    def __tkProcessQueue(self):
        while True:
            try:
                (func, args, kwargs) =  self.tkQueue.get(False)
                #self.tkRoot.after_idle(func, *args, **kwargs)
                func(*args, **kwargs)
            except Queue.Empty:
                break
        self.tkRoot.after(10,self.__tkProcessQueue)

    def __ProcesMQueue():
        while True:
            try:
                (func, args, kwargs) =  self.mQueue.get(False)
                func(*args,**kwargs)
            except Queue.Empty:
                break

    def __register_proxy(self,func,tkName):
        def __func_proxy(*args,**kwargs):
            if self.wxEvtHandlr:
                def ioReport(func, args, kwargs):
                    if not isinstance(self.wxEvtHandlr, wx._core._wxPyDeadObject):
                        wx.PostEvent(self.wxEvtHandlr,
                            self.ThreadedResultEvent(func=func,
                                                args=args,
                                                kwargs=kwargs))
                ioReport(func,args,kwargs)
            else:
                #print "__func_proxy putting %s,%s,%s"%(str(func),str(args),str(kwargs))
                self.mQueue.put((func,args,kwargs))
            #return self.tkRet.get(True)
        tn = self.tkRoot.register(__func_proxy)
        self.tkRoot.eval("rename %s %s"%(tn,tkName))


    def register(self,func,tkName=None):
        if not tkName:
            tkName = func.func_name
        if not self.tkProc:
            # tk wasn't forked into the background, we are a tk app
            # so just register the function directly
            tn = self.tkRoot.register(func)
            self.tkRoot.eval("rename %s %s"%(tn,tkName))
        else:
            # tk was forked into the background, so queue a request
            # for tk to register this function on our behalf
            self.tkQueue.put((self.__register_proxy,(func,tkName), {}))

    def __TkRun(self):
        self.tkRoot = Tkinter.Tk()
        if self.withdraw:
            self.tkRoot.withdraw()
        self.tkRoot.eval("tk appname %s_%s"%(self.appname, self.uuid))
        self.mQueue.put('ready')
        self.tkRoot.after(10, self.__tkProcessQueue)
        self.tkRoot.mainloop()

    def __send_proxy(self, dstappname, cmd, posted=False):
        try:
            #print "{}: Actually sent req ({})".format(time.time(), posted)
            ret = self.tkRoot.eval('send -async %s_%s %s'%(dstappname, self.uuid, cmd))
            if not posted:
                self.tkRet.put(ret)
        except Tkinter.TclError:
            self.tkRet.put(None)

    def send(self, dstappname, cmd, posted=False):
        #print "%f: send called with %s and %s"%(time.time(), dstappname,cmd)
        if not self.tkProc:
            ret = self.tkRoot.eval('send -async %s_%s %s'%(dstappname, self.uuid, cmd))
            if not posted:
                return ret
        else:
            self.tkQueue.put((self.__send_proxy,(dstappname,cmd,posted), {}))
            if not posted:
                return self.tkRet.get(True)

    def getTkAppName(self):
        if not self.tkProc:
            return self.tkRoot.eval('tk appname')
        else:
            def getTkAppName_proxy():
                try:
                    self.tkRet.put(self.tkRoot.eval('tk appname'))
                except Tkinter.TclError:
                    self.tkRet.put(None)
            self.tkQueue.put((getTkAppName_proxy,(), {}))
            return self.tkRet.get(True)

    def __isup(self, dstappname):
        self.upQueue.put('%s_%s'%(dstappname,self.uuid) in self.tkRoot.winfo_interps())

    def isup(self, dstappname):
        if not self.tkProc:
            return '%s_%s'%(dstappname,self.uuid) in self.tkRoot.winfo_interps()
        else:
            self.tkQueue.put((self.__isup, (dstappname,), {}))
            return self.upQueue.get(True)

    def waitfor(self, dstappname, sleep=0.25, tries=100):
        while tries and not self.isup(dstappname):
            time.sleep(sleep)
            tries -= 1

#### TEST CODE BELOW ####
if __name__ == '__main__':
    def foo(a,b):
        print str(a)+" and "+str(b)
    x = SimComm("FOO", tkRootFork=False)

    def xyz(s,r):
        print "s=%s r=%s"%(str(s),str(r))
    print "appname %s_%s"%(x.appname, x.uuid)
    def rval():
        return [2,2,3,4,5]
    x.register(rval)
    print "%s"%(x.getTkAppName())

    print "FOG=%s"%(str(x.waitfor('FOG')))
    print "%s"%(str(x.send('FOG',"puts here")))
    print "%s"%(str(x.send('FOG',"aval")))
    print "adfasdf"

    x.tkRoot.mainloop()

if __name__ == 'f__main__':
    app = wx.App()

    frame = wx.Frame(None, -1, 'foo')
    frame.Show()

    def foo(a,b):
        print str(a)+" and "+str(b)
    x = SimComm("FOO", wxEvtHandlr=frame)
    #def xyz(s,r):
    #    print "s=%s r=%s"%(str(s),str(r))
    #x.register(xyz)
    #x.register(xyz)
    def rval():
        return [1,2,3,4,5]
    x.register(rval)

    #while True:
    #    try:
    #        txt = raw_input()
    #        exec(txt)
    #        print "here"
    #    except SyntaxError:
    #        pass
    #    except NameError:
    #        pass
    #    except EOFError:
    #        break
    #    except KeyboardInterrupt:
    #        exit(0)
    print "FOG=%s"%(str(x.waitfor('FOG')))
    print "%s"%(str(x.send('FOG',"puts here")))
    print "%s"%(str(x.send('FOG',"aval")))
    print "%s"%(x.getTkAppName())
   
    app.MainLoop()
    #x.tkRoot.mainloop()

