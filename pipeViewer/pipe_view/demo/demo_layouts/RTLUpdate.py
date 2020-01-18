import sys

#import sim_comm
import os,imp
from functools import partial
modpath = os.path.dirname(__file__)
sim_comm = imp.load_source('sim_comm',modpath+"/sim_comm.py")
from threading import Timer, Lock

##
# @brief Prototype Update Routine
# @usage To run this function, make sure this file is in the same directory as your layout. Then
# set the on_update property for the object you want to have call this function. In this case,
# on_update should be CustomUpdate:MyUpdate
# @param pair ElementValue
# @param context LayoutContext
# @param index Number of times this function has been called this update cycle.
def MyUpdate(pair, context, index):
    if index == -255:
        MyUpdate.hastimer = False

    if MyUpdate.inprogress:
        #print "MyUpdate.inprogress %s"%(MyUpdate.reason)
        #Autoconnect#if index == -255:
        #Autoconnect#    MyUpdate.hastimer = True
        #Autoconnect#    Timer(1.0, MyUpdate, (pair,context,-255)).start()
        return
    try:
        #print "MyUpdate.entry: %d"%(index)
        MyUpdate.lock.acquire()
        #print "Lock acquired: %d"%(index)

        MyUpdate.all_connected = False # calculated and used later
        MyUpdate.inprogress = True
        MyUpdate.reason = "MyUpdate entry: %d"%(index)
        fr = context.GetFrame()
        if not MyUpdate.inited and not fr == None:
            #print "Initializing...."
            appname = os.environ.get('SIM_COMM_APPNAME')
            #print "appname=%s"%(appname)
            if not appname:
                appname = 'ARGOS'
            MyUpdate.sim_comm = sim_comm.SimComm(appname, wxEvtHandlr=fr)
            MyUpdate.clkNames = []
            for clk in context.dbhandle.database.clock_manager.getClocks():
                MyUpdate.clks[clk.name] = clk
                MyUpdate.clkNames.append(clk.name)
            if 'core_clk0' in MyUpdate.clkNames:
                MyUpdate.clk = 'core_clk0'
            else:
                MyUpdate.clk = MyUpdate.clkNames[0]

            def DoExit(retval):
                #print "Received DoExit!!!!"
                os._exit(int(retval))
            MyUpdate.DoExit = DoExit
            MyUpdate.sim_comm.register(DoExit)
    
            def GoToHC( val ):
                progress = MyUpdate.inprogress
                try:
                    MyUpdate.inprogress = True
                    MyUpdate.reason = "GoToHC: %d"%(index)
                    context.GoToHC(int(val))
                finally:
                    MyUpdate.inprogress = progress
            MyUpdate.sim_comm.register(GoToHC)
    
            def GetClocks():
                return MyUpdate.clkNames
            MyUpdate.sim_comm.register(GetClocks)
    
            def GetClock():
                return MyUpdate.clk
            MyUpdate.sim_comm.register(GetClock)
    
            def SetClock(clk):
                MyUpdate.clk = clk
                return clk
            MyUpdate.sim_comm.register(SetClock)
    
            def GetCycle():
                return MyUpdate.clks[MyUpdate.clk].HypercycleToLocal(context.GetHC())
            MyUpdate.sim_comm.register(GetCycle)
   
            def _TellGoTo(appidx, force=False):
                #print "_TellGoTo called with: %d"%(int(appidx))
                # this if statement means we will only communicate with
                # with existing (not None) and connected (True) targets
                if MyUpdate.target_connected[appidx]:
                    if MyUpdate.target_client[appidx] == 'VERDI':
                        SendFunc = MyUpdate.SendRTLGoToCycle
                    elif 'ARGOS' in MyUpdate.target_client[appidx]:
                        SendFunc = MyUpdate.SendArgosGoToCycle
                    SendFunc(appidx, MyUpdate.clks[MyUpdate.clk].HypercycleToLocal(context.GetHC()) + MyUpdate.target_offset[appidx], force=force)
            MyUpdate._TellGoto = _TellGoTo
 
            def GoToCycle(caller, cyc):
                try:
                    #print "GoToCycle caller=%s"%(str(caller))
                    if caller:
                        try:
                            caller = MyUpdate.target_appnames.index(caller)
                        except:
                            caller = -1 # usually SIMCTL
                    progress = MyUpdate.inprogress
                    MyUpdate.inprogress = True
                    MyUpdate.reason = "GoToCycle: %d"%(index)
                    cyc = int(cyc)
                    if caller >= 0:
                        cyc -= MyUpdate.target_offset[caller]

                    context.GoToHC(MyUpdate.clks[MyUpdate.clk].LocalToHypercycle(cyc), no_broadcast=True)
                    if MyUpdate.inited and not MyUpdate.__in_control:
                        for idx in range(len(MyUpdate.target_appnames)):
                            # if we were called from a remote app then skip the caller
                            if not idx == caller:
                                _TellGoTo(idx)
                finally:
                    MyUpdate.inprogress = progress
            MyUpdate.GoToCycle=GoToCycle
            MyUpdate.sim_comm.register(GoToCycle)

            def SetRTLOffset(cycles):
                cycles = int(cycles)
                for idx in range(len(MyUpdate.target_appnames)):
                    if MyUpdate.target_type[idx] == 'RTL':
                        MyUpdate.target_offset[idx]=int(cycles)
                MyUpdate.rtl_offset = cycles
                return cycles
            MyUpdate.sim_comm.register(SetRTLOffset)

            def GoToRTLTime(*args):
                #print "GoToRTLTime called"
                if MyUpdate.__in_control:
                    return
                try:
                    MyUpdate.__in_control = 1
                    #print "GoToRTLTime %s"%(str(args))
                    idx = int(args[0])
                    if not MyUpdate.target_appnames[idx] == None:
                        cycle = (eval(args[2])+5000)/(10*1000)
                        #print "Going to %d"%(int(cycle))
                        MyUpdate.GoToCycle(None, cycle-MyUpdate.target_offset[idx])

                        # FIXME: Now move everyone else that we control
                        #        except for our caller at IDX
                        for i in range(len(MyUpdate.target_appnames)):
                            # Skip our caller
                            if i == idx:
                                continue
                            _TellGoTo(i, force=True)
                            
                finally:
                    MyUpdate.__in_control = 0
            MyUpdate.GoToRTLTime = GoToRTLTime
    
            def AdjustRTLTimeUnit(*args):
                #print "AdjustRTLTimeUnit: %s"%(str(args))
                idx = int(args[0])
                if MyUpdate.target_client[idx] == 'VERDI':
                    MyUpdate.target_connected[idx] = False
            MyUpdate.AdjustRTLTimeUnit = AdjustRTLTimeUnit

            def AddTarget(target_appname, target_client, target_type, target_offset=None):
                if target_appname in MyUpdate.target_appnames:
                    return False

                if target_offset == None:
                    if target_type == 'RTL':
                        target_offset = MyUpdate.rtl_offset
                    else:
                        target_offset = 0
                MyUpdate.target_appnames.append(target_appname)
                MyUpdate.target_connected.append(False)
                MyUpdate.target_client.append(target_client)
                MyUpdate.target_type.append(target_type)
                MyUpdate.target_offset.append(int(target_offset))
                MyUpdate.target_range.append(None)

                idx = len(MyUpdate.target_appnames)-1
                if (target_client == 'VERDI'):
                    MyUpdate.sim_comm.register(partial(MyUpdate.GoToRTLTime,idx),'GoToRTLTime_%d'%(idx))
                    MyUpdate.sim_comm.register(partial(MyUpdate.AdjustRTLTimeUnit,idx),'AdjustRTLTimeUnit_%d'%(idx))

                # FIXME: Try to connect to target here?????
                # FIXME: Add any registered callbacks with target here
                # FIXME: Tell target to go to offset cycle here?

                # Disconnect
                return True
            MyUpdate.sim_comm.register(AddTarget)
            MyUpdate.AddTarget = AddTarget

            def SetTargetOffset(target_appname, target_offset):
                try:
                    idx = MyUpdate.target_appnames.index(target_appname)
                except ValueError:
                    return False

                if not MyUpdate.target_offset[idx] == target_offset:
                    MyUpdate.target_offset[idx] = int(target_offset)
                    # ?FIXME: Tell target to go to offset cycle here?

                return True
            MyUpdate.sim_comm.register(SetTargetOffset)

            def DelTarget(target_appname):
                try:
                    idx = MyUpdate.target_appnames.index(target_appname)
                except ValueError:
                    return False

                # if MyUpdate.target_connected[idx]:
                #     FIXME: Remove any registered callbacks with target here

                # don't remove instead mark empty
                # this is because we use callbacks with idx
                # to determine caller. If we would delete an item
                # then the callback's wouldn't match.
                MyUpdate.target_connected[idx] = None
                MyUpdate.target_appnames[idx] = None
                Mydate.target_client[idx] = None
                MyUpdate.target_type[idx] = None
                MyUpdate.target_offset[idx] = None

                return True
            MyUpdate.sim_comm.register(DelTarget)

            # FIXME: Remove this when the capability to choose targets is added to sm_corr's argos_menu
            target_offset = os.environ.get('SIM_COMM_TARGET_OFFSET')
            if target_offset is None:
                target_offset = 0
            else:
                target_offset = int(target_offset)

            if 'ARGOS' in MyUpdate.sim_comm.appname:
                MyUpdate.AddTarget('ARGOS_RTL', 'ARGOS', 'RTL')
                if MyUpdate.sim_comm.appname == 'ARGOS_TWO':
                    MyUpdate.AddTarget('ARGOS', 'ARGOS', 'PERF')
                else:
                    MyUpdate.AddTarget('ARGOS_TWO', 'ARGOS', 'PERF', target_offset)
                MyUpdate.AddTarget('RTL', 'VERDI', 'RTL')

            el = pair.GetElement()
            elc = el.HasChanged()
            lo = context.GetLayout()
            loc = lo.HasChanged()
            el.SetProperty('caption', 'Initialized: %s'%(MyUpdate.sim_comm.getTkAppName()))
            if not elc:
                el._MarkAsUnchanged()
            if not loc:
                lo._Layout__MarkAsUnchanged()
            MyUpdate.inited = True
   
        # RTL Integration
        def _SendRTLGoToCycle(appidx, cycle):
            # conversion factors
            rtl_cvt = { 's':int(1e15), 'ms':int(1e12), 'us':1e9, 'ns':1e6, 'ps':1e3, 'fs':1.00 }

            # convert to RTL cycle number into femtoseconds
            cycle *= 10
            cycle -= 5
            cycle *= rtl_cvt['ns'] # ns->fs

            if (cycle < MyUpdate.target_range[appidx][0]*MyUpdate.target_range[appidx][2]*rtl_cvt[MyUpdate.target_range[appidx][3]]):
                #print "RTL Cycle number too small"
                pass
            elif (cycle > MyUpdate.target_range[appidx][1]*MyUpdate.target_range[appidx][2]*rtl_cvt[MyUpdate.target_range[appidx][3]]):
                #print "RTL Cycle number too large"
                pass
            else:
                # convert to RTL window time
                cycle /= MyUpdate.target_range[appidx][4]*rtl_cvt[MyUpdate.target_range[appidx][5]]
                # send command to RTL viewer
                MyUpdate.sim_comm.send(MyUpdate.target_appnames[appidx],"srcSetCursorTime %f"%(cycle), posted=True)
                #print "send srcSetCursorTime %f"%(cycle)
        MyUpdate._SendRTLGoToCycle = _SendRTLGoToCycle

        def SendRTLGoToCycle(appidx, cycle, force=False):
            #print "SendRTLGoToCycle"
            appidx = int(appidx)
            if MyUpdate.__in_control and not force:
                return
            restore_control = MyUpdate.__in_control
            try:
                MyUpdate.__in_control = 1
                _SendRTLGoToCycle(appidx, cycle)
            finally:
                MyUpdate.__in_control = restore_control
        MyUpdate.SendRTLGoToCycle = SendRTLGoToCycle

        # RTL Integration
        def _SendArgosGoToCycle(appidx,cycle):
            MyUpdate.sim_comm.send(MyUpdate.target_appnames[appidx],"GoToCycle %s %d"%(MyUpdate.sim_comm.appname, cycle), posted=True)
        MyUpdate._SendArgosGoToCycle = _SendArgosGoToCycle

        def SendArgosGoToCycle(appidx,cycle, force=False):
            cycle = int(cycle)
            #print "SendArgosGoToCycle"
            if MyUpdate.__in_control and not force:
                return
            restore_control = MyUpdate.__in_control
            try:
                MyUpdate.__in_control = 1

                _SendArgosGoToCycle(appidx,cycle)
            finally:
                MyUpdate.__in_control = restore_control
        MyUpdate.SendArgosGoToCycle = SendArgosGoToCycle

        #print "Is Inited?: %s"%(str(MyUpdate.inited))
        # Note it would be nice to always check if we are connected
        # but this slows down the user interface too much
        if MyUpdate.inited:
            for idx in range(len(MyUpdate.target_appnames)):
                if MyUpdate.target_appnames[idx] == None:
                    continue
                #print "Target %s has %s"%(MyUpdate.target_appnames[idx],str(MyUpdate.target_connected[idx]))
                if not MyUpdate.target_connected[idx]:
                    #print "Trying: %s"%(MyUpdate.target_appnames[idx])
                    if MyUpdate.target_client[idx] == 'VERDI':
                        MyUpdate.target_connected[idx] = MyUpdate.sim_comm.isup(MyUpdate.target_appnames[idx])
                        #print "partially connected?: %s"%(MyUpdate.target_connected[idx])

                        if MyUpdate.target_connected[idx]:
                            target_cycles = MyUpdate.sim_comm.send(MyUpdate.target_appnames[idx],'wvGetFileTimeRange')
                            #print "wvGetFileTimeRange gave %s"%(str(target_cycles))

                            if not target_cycles:
                                MyUpdate.target_connected[idx] = False
                   
                        if MyUpdate.target_connected[idx]:
                            target_appname = MyUpdate.target_appnames[idx]
                            #print "wvGetFileTimeRange gave %s"%(str(target_cycles))
                            target_cycles = target_cycles.split()
                            #print(len(target_cycles))
                            rtl_wunit = MyUpdate.sim_comm.send(target_appname,'wvGetWindowTimeUnit')
                            #print "target_cycles=%s"%(str(target_cycles))
                            #print "rtl_wunit=%s"%(str(rtl_wunit))
                            MyUpdate.target_range[idx] = [int(target_cycles[0]), int(target_cycles[1]), float(target_cycles[3][:-2]), target_cycles[3][-2:], float(rtl_wunit[:-2]), rtl_wunit[-2:]]
                            #print "target_range=%s"%(str(MyUpdate.target_range[idx]))
                            #MyUpdate.sim_comm.send(target_appname,'RemoveEventCallback [tk appname] wvCursorTimeChange 1', posted=True)
                            MyUpdate.sim_comm.send(target_appname,'AddEventCallback [tk appname] GoToRTLTime_%d wvCursorTimeChange 1'%(idx), posted=True)
                            #self.__tkRoot.eval(target_appname,'RemoveEventCallback [tk appname] wvWindowTimeUnitChanged 1', posted=True)
                            MyUpdate.sim_comm.send(target_appname,'AddEventCallback [tk appname] AdjustRTLTimeUnit_%d wvWindowTimeUnitChanged 1'%(idx), posted=True)
                            #self.__tkRoot.eval(target_appname,'RemoveEventCallback [tk appname] wvZoom 1', posted=True)
                            # There appears to be a bug in Verdi, where wvWindowTimeUnitChanged isn't called when signals are restored
                            # this causes us to be out of Sync with what time units Verdi is using. wvZoom is called on signal restoration
                            # so this is a workaround for that bug. Cause us to regrab time info when zoom is called.
                            MyUpdate.sim_comm.send(target_appname,'AddEventCallback [tk appname] AdjustRTLTimeUnit_%d wvZoom 1'%(idx), posted=True)

                            #print "tmpname: %s"%(tmpname)
                    else: # Assumption for now not VERDI must be ARGOS
                        MyUpdate.target_connected[idx] = MyUpdate.sim_comm.isup(MyUpdate.target_appnames[idx])

                        if MyUpdate.target_connected[idx]:
                            # FIXME, am I RTL or PERF? this is asking to add me as a target.
                            # FIXME, how do I register the callback for GoToCycle_(targetidx)? Or do I just remove the idx and have caller tell me who it is?
                            MyUpdate.sim_comm.send(MyUpdate.target_appnames[idx],'AddTarget %s ARGOS PERF 0'%(MyUpdate.sim_comm.appname), posted=True)
                            pass
 
                MyUpdate.__in_control = 0 # don't call myself
                for idx in range(len(MyUpdate.target_appnames)):
                    if MyUpdate.target_type[idx] == 'RTL':
                        MyUpdate.target_offset[idx]=MyUpdate.rtl_offset

        el = pair.GetElement()
        elc = el.HasChanged()
        lo = context.GetLayout()
        loc = lo.HasChanged()
        is_connected = False
        MyUpdate.all_connected = True
        for idx in range(len(MyUpdate.target_appnames)):
            if MyUpdate.target_connected[idx]:
                is_connected = True
            else:
                MyUpdate.all_connected = False
        if is_connected:
            el.SetProperty('color', (0,255,0))
        else:
            el.SetProperty('color', (255,0,0))
        if not elc:
            el._MarkAsUnchanged()
        if not loc:
            lo._Layout__MarkAsUnchanged()

        if MyUpdate.inited and not MyUpdate.__in_control and not index == -255:
            for idx in range(len(MyUpdate.target_appnames)):
                MyUpdate._TellGoto(idx)
                #if MyUpdate.target_appnames[idx] == None:
                #    continue
                #if MyUpdate.target_connected[idx]:
                #    if MyUpdate.target_client[idx] == 'VERDI':
                #        SendFunc = MyUpdate.SendRTLGoToCycle
                #    elif MyUpdate.target_client[idx] == 'ARGOS':
                #        SendFunc = MyUpdate.SendArgosGoToCycle
                #    SendFunc(idx, MyUpdate.clks[MyUpdate.clk].HypercycleToLocal(context.GetHC()) + MyUpdate.target_offset[idx])

        #el = pair.GetElement()
        #print "HasChanged: %s"%(str(el.HasChanged()))
    finally:
        MyUpdate.inprogress = False
        #Autoconnect#if (fr == None or not MyUpdate.all_connected) and not MyUpdate.hastimer:
        if (fr == None or not MyUpdate.inited) and not MyUpdate.hastimer:
            MyUpdate.hastimer = True
            Timer(1.0, MyUpdate, (pair,context,-255)).start()
        try:
            MyUpdate.lock.release()
            #print "Lock released"
        except AttributeError:
            pass


MyUpdate.inited = False
MyUpdate.lock = Lock()
MyUpdate.hastimer = False
MyUpdate.sim_comm = None
MyUpdate.clkNames = []
MyUpdate.clk = ''
MyUpdate.clks = {}
MyUpdate.inprogress = False
MyUpdate.__in_control = 0
MyUpdate.rtl_offset = 0

MyUpdate.target_appnames  = []  # Appname
MyUpdate.target_connected = [] # Are we connected and in control
MyUpdate.target_client = [] # ARGOS=Argos viewing fiat or fsdb2argos, VERDI=Verdi
MyUpdate.target_type = [] # PERF=viewing fiat, RTL=Verdi or Argos for fiat
MyUpdate.target_offset = [] # Cycle offset from us to target
MyUpdate.target_range = [] # Valid cycle numbers


