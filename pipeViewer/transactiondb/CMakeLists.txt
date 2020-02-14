cmake_minimum_required(VERSION 3.10)

project(transactiondb)

set(TRANSACTIONDB_SRC_DIR ${PROJECT_SOURCE_DIR}/src)

##################################################################
# Build the transactiondb.so
##################################################################
add_custom_command(OUTPUT transactiondb.sh
  COMMAND printf 'SYSINCDIRS="$ENV{SYSINCDIRS}"
  YAML_CPP="${YAML_CPP}"
  PY_SRC_DIR="${CMAKE_CURRENT_SOURCE_DIR}/src"
  BOOST_LIBS="${PY_MOD_BOOST_LIBS}"
  SPARTA_BASE="${SPARTA_BASE}"
  BOOST="${BOOST_DIR}"
  BOOST_LIBDIR="${Boost_LIBRARY_DIR}"
  SIM_PLATFLAGS="${BOOST_LD_FLAGS}"
  TARGETDIR="lib"
  BUILD_MODULES="transactiondb"
  REQUIRED_SPARTA_LIBS="sparta"
  LIB_SPARTA_BUILT_PATH="${SPARTA_BASE}/release"
  python3 ${CMAKE_CURRENT_SOURCE_DIR}/setup.py build_ext --inplace;' > transactiondb.sh && chmod +x transactiondb.sh DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/setup.py)

add_custom_target (transactiondb_sh_driver ALL DEPENDS transactiondb.sh)

add_custom_command(OUTPUT lib/transactiondb.so
  COMMAND ./transactiondb.sh
  DEPENDS
  transactiondb.sh)

add_custom_target (transactiondb_driver ALL DEPENDS
  ${SPARTA_BASE}/release/libsparta.a
  lib/transactiondb.so
  ${TRANSACTIONDB_SRC_DIR}/common.pxd
  ${TRANSACTIONDB_SRC_DIR}/intervalwindow.pyx
  ${TRANSACTIONDB_SRC_DIR}/transactiondb.pyx
  ${CMAKE_CURRENT_SOURCE_DIR}/setup.py
  ${TRANSACTIONDB_SRC_DIR}/Reader.hpp
  ${TRANSACTIONDB_SRC_DIR}/TransactionDatabaseInterface.hpp)
