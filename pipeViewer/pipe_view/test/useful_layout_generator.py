

## @package useful_layout_generator.py
#  @brief Generates a layout file 'useful_layout.alf'. Will not overwriting an
#  existing file by this name, so delete the existing file first

# It is important to know that the layouts used in this test are not shared in any way.
# In argos, there will be an option to load a 'shared' layout, which means that
# one instance of the file is loaded into 1 Layout instance and multiple
# LayoutContexts refer to it.
# In this test, there are simply multiple Layout instances which loaded data from the same
# file on disk

import sys
sys.path.append('../')
from model.layout import Layout
from model.element import Element


l = Layout() # New layout

# Create a column for each buffer with a label at the top
# Each entry in this list is a tuple containing a title for the column,
# a string formatter taking an decimal numeric index, and a number of entries to display
COLS = [#('Fetch Queue',    'top.core0.fetch,FetchQueue.FetchQueue{0}', 10),
        #('FPU Scheduler',  'top.core0.fpu.FPUScheduler.FPUScheduler{0}', 10),
        #('FPU Queue',      'top.core0.fpu.FPUQueue.FPUQueue{0}', 10),
        ('Reorder Buffer', 'top.core0.rob.ReorderBuffer.ReorderBuffer{0}', 32),
        ]

# Entries to draw for each location
LOC_ENTRIES = ['transaction', 'opcode', 'vaddr', 'annotation']

# Layout properties

ELEMENT_WIDTH = 120
ELEMENT_HEIGHT = 20
COL_PADDING = 30
WRAP_AFTER = 5 # Draw every 5 objects on a new Y coordinate

x_init = COL_PADDING
x_pos = x_init
y_init = 15


# Grid Layout of each location in each buffer

# Iterate all location vectors in the COLS list
max_num_entries = 0
for row,(title,fmt,num_entries) in enumerate(COLS):
    max_num_entries = max(max_num_entries, num_entries)
    y_pos = y_init
    
    e = l.CreateElement()
    e.SetProperty('position', (x_pos, y_pos))
    e.SetProperty('dimensions', (ELEMENT_WIDTH * len(LOC_ENTRIES), ELEMENT_HEIGHT))
    e.SetProperty('Content', 'caption')
    e.SetProperty('caption', title + ' Snapshot')
    e.SetProperty('color', (255,255,255)) # White border
    y_pos += int(ELEMENT_HEIGHT * 1.5)

    # Add a caption for each element sub-column
    local_x_pos = x_pos

    for content in LOC_ENTRIES:
        e = l.CreateElement()
        e.SetProperty('position',(local_x_pos, y_pos))
        e.SetProperty('dimensions', (ELEMENT_WIDTH, ELEMENT_HEIGHT))
        e.SetProperty('Content', 'caption')
        e.SetProperty('caption', content)
        e.SetProperty('color', (255,255,255)) # off-white border
        local_x_pos += ELEMENT_WIDTH

    y_pos += int(ELEMENT_HEIGHT * 1.5)

    # Add a set of elements in each row for this location vector (fmt)
    for idx in xrange(num_entries):
        loc_name = fmt.format(idx)

        local_x_pos = x_pos

        # Add an element in a row with each desired content type
        for content in LOC_ENTRIES:
            e = l.CreateElement()
            e.SetProperty('position',(local_x_pos, y_pos))
            e.SetProperty('dimensions', (ELEMENT_WIDTH, ELEMENT_HEIGHT))
            e.SetProperty('Content', content)
            e.SetProperty('LocationString',loc_name)
            e.SetProperty('color', (250,250,250)) # off-white border

            local_x_pos += ELEMENT_WIDTH
            
        y_pos += ELEMENT_HEIGHT

    x_pos += (ELEMENT_WIDTH * len(LOC_ENTRIES)) + COL_PADDING
    
    if (row % WRAP_AFTER) == (WRAP_AFTER-1):
        x_pos = x_init
        y_init += (max_num_entries * ELEMENT_HEIGHT) + (4 * ELEMENT_HEIGHT)


# Crawl layout of 1 buffer

CRAWL_RANGE = (0, 9) # Crawl from this cycle to +9
CRAWL_CONTENT = 'opcode'

# Move to next row for crawls
x_pos = x_init
y_init += (max_num_entries * ELEMENT_HEIGHT) + (4 * ELEMENT_HEIGHT)

# Iterate all location vectors in the COLS list
for row,(title,fmt,num_entries) in enumerate(COLS):
    max_num_entries = max(max_num_entries, num_entries)
    y_pos = y_init
    
    e = l.CreateElement()
    e.SetProperty('position', (x_pos, y_pos))
    e.SetProperty('dimensions', (ELEMENT_WIDTH * len(LOC_ENTRIES), ELEMENT_HEIGHT))
    e.SetProperty('Content', 'caption')
    e.SetProperty('caption', title + ' Crawl')
    e.SetProperty('color', (255,255,255)) # White border
    y_pos += int(ELEMENT_HEIGHT * 1.5)

    # Add a caption for each element sub-column
    local_x_pos = x_pos

    for t_off in xrange(*CRAWL_RANGE):
        e = l.CreateElement()
        e.SetProperty('position',(local_x_pos, y_pos))
        e.SetProperty('dimensions', (ELEMENT_WIDTH, ELEMENT_HEIGHT))
        e.SetProperty('Content', 'caption')
        e.SetProperty('caption', '{0:+}'.format(t_off))
        e.SetProperty('color', (255,255,255)) # off-white border
        local_x_pos += ELEMENT_WIDTH

    y_pos += int(ELEMENT_HEIGHT * 1.5)

    # Add a set of elements in each row for this location vector (fmt)
    for idx in xrange(num_entries):
        loc_name = fmt.format(idx)

        local_x_pos = x_pos

        # Add an element in a row with each desired content type
        for t_off in xrange(*CRAWL_RANGE):
            e = l.CreateElement()
            e.SetProperty('position',(local_x_pos, y_pos))
            e.SetProperty('dimensions', (ELEMENT_WIDTH, ELEMENT_HEIGHT))
            e.SetProperty('Content', CRAWL_CONTENT)
            e.SetProperty('LocationString',loc_name)
            e.SetProperty('t_offset',t_off)
            e.SetProperty('color', (250,250,250)) # off-white border

            local_x_pos += ELEMENT_WIDTH
            
        y_pos += ELEMENT_HEIGHT

    x_pos += (ELEMENT_WIDTH * len(LOC_ENTRIES)) + COL_PADDING
    
    if (row % WRAP_AFTER) == (WRAP_AFTER-1):
        x_pos = x_init
        y_init += (NUM_ROWS * ELEMENT_HEIGHT) + (4 * ELEMENT_HEIGHT)


# Saving

SAVE_TO_FILENAME = 'useful_layout.alf'

import os
if os.path.exists(SAVE_TO_FILENAME):
    raise IOError('Cannot save to file {0} because it already exists. Please remove it.' \
                  .format(SAVE_TO_FILENAME))

l.SaveToFile(SAVE_TO_FILENAME)

print 'Done generating {0}'.format(SAVE_TO_FILENAME)
