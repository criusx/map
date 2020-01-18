

# Shows layout file saving and loading

# It is important to know that the layouts used in this test are not shared in any way.
# In argos, there will be an option to load a 'shared' layout, which means that
# one instance of the file is loaded into 1 Layout instance and multiple
# LayoutContexts refer to it.
# In this test, there are simply multiple Layout instances which loaded data from the same
# file on disk

import wx
import sys
import os
sys.path.append('../')
from model.layout import Layout
from model.element import Element

# Load a layout from disk and save it back somewhere else as a temporary file

lay1 = Layout('test_load_layout.alf')
assert lay1.GetFilename() == 'test_load_layout.alf'
assert lay1.CanSaveToFile() # Could still save again - no changes on disk

lay1.SaveToFile('test_saved_layout.alf') # SaveAs (temporary file)
assert lay1.GetFilename() == 'test_saved_layout.alf'
assert lay1.CanSaveToFile() # Could still save again - no changes on disk since last save/load

# Now load the same layout (NOT SHARED) and modify it, then save it

lay2 = Layout('test_saved_layout.alf')
e = lay2.CreateElement()
e.SetProperty('position',(0,100))
e.SetProperty('Content','transaction')
e.SetProperty('LocationString','')
assert lay2.CanSaveToFile() # Could still save again
lay2.SaveToFile() # Save at current location: GetFilename().
# Note that the file has NOT CHANGED since it was loaded by lay2, so lay2 is
# allowed to save back to this disk at will.
assert lay2.CanSaveToFile() # Could still save again

# IMPORTANT: Layout 1, which refers to test_saved_layout.alf CANNOT save now
# because it detects that the file has changed on disk.
# This situation MUST be tested before any GUI "save" action can be done
# ("save-as" would have to request overwrite from user if the file the user
# chose to save as already existed regardless of that file's content)
assert lay1.GetFilename() == 'test_saved_layout.alf'
assert not lay1.CanSaveToFile() # NOT ABLE TO SAVE because lay2 wrote a different layout to this filename

# At this point, when a user clicked 'save' on a frame associated with lay1, we'd ask the
# user if they were sure they wanted to overwrite the changes. If the user says yes,
# remove the existing file and then write it. This explicit step prevents accidental
# overwrites and makes it clear that changes ARE (probably) BEING LOST

os.remove(lay1.GetFilename())
lay1.SaveToFile() # Saving back to file is allowed since it is now GONE
assert lay1.GetFilename() == 'test_saved_layout.alf'
assert lay1.CanSaveToFile() # Saving is ok again - No changes on disk since last save/load

assert lay2.GetFilename() == 'test_saved_layout.alf'
assert not lay2.CanSaveToFile() # lay2 detects different file on disk - cannot save

print 'Done'
