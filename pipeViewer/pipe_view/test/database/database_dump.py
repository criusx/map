

import os
import sys
import pprint
sys.path.append('../../model')

import database
import database_handle

if len(sys.argv) > 1:
    FILE_PREFIX = sys.argv[1]
else:
    FILE_PREFIX = 'data_test_0'

# Create Database
db = database.Database(FILE_PREFIX)

# Create handle refering to Database
dbhandle = database_handle.DatabaseHandle(db)

# Shortcut to the query api of this dbhandle (sparta's transactiondb.IntervalWindow object)
qapi = dbhandle.query_api

print(db)
print(dbhandle)
print(qapi)
print(repr(db))
print(repr(dbhandle))
print(repr(qapi))


### Perform a query in the middle of the file
##hc1 = int( (qapi.getFileStart() + qapi.getFileEnd()) / 2)
##
##results1 = qapi.query(hc1) # Stab query. Results are an sparta transactiondb.IntervalList object
### Note, qapi could be discarded after this query since results stand alone
##
##print('results1: {0}'.format(results1))
##
### Make another query (results1 is unaffected)
##hc2 = hc1 + 1
##results2 = qapi.query(hc2) # Stab query. Results are an sparta transactiondb.IntervalList object
### Note that results1 is still around
##
##print('results2: {0}'.format(results2))

# Helper for displaying results of a query. Displays the given hc in local tick
# for each location for each transaction found
def print_results(res, hc):
    for idx,trans in enumerate(res):
        loc_id = trans.getLocationID()

        # Get location string based on location ID, then use string to get location
        # info tuple (loc_id,loc_str,clock_id)
        loc_str = dbhandle.database.location_manager.getLocationString(loc_id)
        if loc_str is None:
            loc_str = "Unkonwn Location ID"
            loc_info = dbhandle.database.location_manager.LOC_NOT_FOUND
        else:
            loc_info = dbhandle.database.location_manager.getLocationInfo(loc_str, {})

        clock_id = loc_info[2] # (loc_id, loc_str, clock_id)
        if clock_id != dbhandle.database.location_manager.NO_CLOCK:
            clk = dbhandle.database.clock_manager.getClockDomain(clock_id)
            clk_name = clk.name
            loc_cycle = clk.HypercycleToLocal(hc)
        else:
            clk = None
            clk_name = '-'
            loc_cycle = 'n/a'

        print('{0} @ "{1}" clk="{2}" hc={3} loc_cyc={4}'.format(trans, loc_str, clk_name, hc, loc_cycle))

        # Note, each transaction has:
        ##trans.getComponentID
        ##trans.getTransactionID
        ##trans.getLocationID
        ##trans.getFlags
        ##trans.getParentTransactionID
        ##trans.getOpcode
        ##trans.getVirtualAddress
        ##trans.getRealAddress
        ##trans.getAnnotationLength
        ##trans.getAnnotation
        ##trans.getLeft
        ##trans.getRight
        ##trans.getType
        ##trans.getTypeString

        return num_enties


# Actually display queries

num_trans = 0
LOC_ID_FILTER = [513]
trans_ids = {}

for i in range(qapi.getFileStart() + qapi.getFileEnd()):
    results = qapi.query(i)

    ##for idx,trans in enumerate(results):
    ##num_entries += print_results(results, i)
    if i % 250 == 1 and num_trans > 0:
        print('[{0:>6}: {1} w/ ID=513'.format(i-1, num_trans))

    trans = []
    for tr in results:
        if tr.getLocationID() in LOC_ID_FILTER:
            tid = tr.getTransactionID()
            if tid not in trans_ids:
                ##trans.append(tr.makeRealCopy())
                trans_ids[tid] = None
                print tr

print ('{0} transactions total'.format(len(trans_ids)))

##print('Results for query 1 at {0}'.format(hc1))
##print_results(results1, hc1)
##
##print('\nResults for query 2 at {0}'.format(hc2))
##print_results(results2, hc2)

# Done with queries

# Deleting things here is not necessary. They will go out of scope and be garbage collected
del dbhandle # Doing this *should* cause the dbhandle to have no more refcount and be freed (soon after)
