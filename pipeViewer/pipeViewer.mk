#
# Defines variables required for building the Cython core example
#
ifndef ARGOS_CORE_VARS_MK_PARSED
export ARGOS_CORE_VARS_MK_PARSED:=1

# Export some environment vars for the python subshell when building extensions
export TARGETDIR


################################################################################
# Easymake configuration

export CPP_SUFFIX   ?= cpp
export EASYMAKE_DIR ?= /sarc/spa/tools/easymake

################################################################################

# ifndef ARGOS_CORE_VARS_MK_PARSED
endif
