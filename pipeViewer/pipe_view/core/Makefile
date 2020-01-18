
include $(CURDIR)/../../pipeViewer.mk

all:: $(TARGETDIR)/core.so $(TARGETDIR)/logsearch.so link

export EXPLICITDEPS := src/logsearch.pyx src/log_search.cpp src/helpers.h src/common.pxd setup.py Makefile
export ARGOS_VERSION := $(shell cat $(CURDIR)/../../.VERSION)

$(TARGETDIR)/core.so:: $(EXPLICITDEPS)
	@# Temporary workaround for problem where including easymamke stops make
	@# from working but omitting it means we have no TARGETDIR
	@if [ "$(TARGETDIR)" == "" ]; then \
		echo "YOU MUST MAKE FROM OUTSIDE THIS DIRECTORY "; \
		false; \
	fi;
	BUILD=core ARGOS_VERSION=$(ARGOS_VERSION) ./setup.py build_ext --inplace

$(TARGETDIR)/logsearch.so:: $(EXPLICITDEPS)
	@# Temporary workaround for problem where including easymamke stops make
	@# from working but omitting it means we have no TARGETDIR
	@if [ "$(TARGETDIR)" == "" ]; then \
		echo "YOU MUST MAKE FROM OUTSIDE THIS DIRECTORY "; \
		false; \
	fi;
	BUILD=logsearch ARGOS_VERSION=$(ARGOS_VERSION) ./setup.py build_ext --inplace

clean::
	# Remove local build directory
	rm -rf build/
	rm -rf $(TARGETDIR)

# Symlink from lib/core.so to this platform's .so
link: $(TARGETDIR)/core.so $(TARGETDIR)/logsearch.so
	mkdir -p lib
	ln -sf ../$(TARGETDIR)/core.so lib/core.so
	ln -sf ../$(TARGETDIR)/logsearch.so lib/logsearch.so

.PHONY: link

##include $(EASYMAKE_DIR)/GNUmakefile.easy
