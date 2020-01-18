
include $(CURDIR)/pipeViewer.mk

SUBDIRS := $(CURDIR)/argos_view

include $(EASYMAKE_DIR)/GNUmakefile.easy

install:: release

release::
	@echo "Run scripts/release.py to make a release of pipeViewer"

.PHONY:: cscope.files install
cscope.files cscope_files:
	@echo "Making cscope.files..."
	@rm -f cscope.files
	@find -name "*.cpp" -o -name "*.h" > cscope.files

pull: GIT-PULL
