

import sys
import pprint
sys.path.append('../../model')

import location_manager
import clock_manager

FILE_PREFIX = 'data_test_0'

# Locations
lmgr = location_manager.LocationManager(FILE_PREFIX)

print(lmgr)
print(str(lmgr))
print(repr(lmgr))
print(len(lmgr))

tmp = lmgr.getLocationInfo('top.core{core=1}.regs.reg0', {foo:0})
print(tmp)

linfo = lmgr.getLocationInfo('top.core0.regs.reg0', {})
print(linfo)

print('All location strings:')
pprint.pprint(lmgr.getLocationStrings())
print('Completion strings for "top.core":')
pprint.pprint(lmgr.getLocationStringCompletions('top.core'))

print(lmgr.getLocationString(linfo[0]))
assert lmgr.getLocationString(linfo[0]) == linfo[1]

assert lmgr.LOC_NOT_FOUND is lmgr.getLocationInfo('not a real location', {})

try:
    lmgr.LOC_NOT_FOUND is lmgr.getLocationInfo(-1, {})
except TypeError:
    pass
else:
    raise Except('Should have thrown TypeError')


# Clocks
cmgr = clock_manager.ClockManager(FILE_PREFIX)
print cmgr
print(str(cmgr))
print(repr(cmgr))
print(len(cmgr))

clk = cmgr.getClockDomain(linfo[2])
print(clk)

try:
    _ = cmgr.getClockDomain(-1)
except KeyError:
    pass
else:
    raise Exception('Should have thrown IndexError')

try:
    _ = cmgr.getClockDomain(1000000000000000000000)
except KeyError:
    pass
else:
    raise Exception('Should have thrown IndexError')

local = 1000
hc = clk.LocalToHypercycle(local)
print('From local {0}, hc = {1}'.format(local, hc))
print('From hc = {0}, back to local = {1}'.format(hc, clk.HypercycleToLocal(hc)))
print('From hc = {0}, hc for next local cycle = {1}'.format(hc+1, clk.NextLocalCycle(hc+1)))
