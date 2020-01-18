cmake_minimum_required(VERSION 3.15)
project (PipeViewer)

find_package(PythonInterp 3.5 REQUIRED)

find_package(PythonLibs 3.5 REQUIRED)

if(NOT ${PYTHON})
    find_program(PYTHON 'python3')
endif()

set(SETUP_PY "${CMAKE_SOURCE_DIR}/argos_view/core/setup.py")

set(PY_OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/build")

add_custom_command(OUTPUT "${PY_OUTPUT}"
                   COMMAND ${PYTHON} ${SETUP_PY} build_ext
                   COMMAND ${CMAKE_COMMAND} -E touch ${PY_OUTPUT}
                   )
add_custom_target(a_py ALL DEPENDS "${PY_OUTPUT}")


