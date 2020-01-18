#!/bin/bash

function cleanup() {
    rm -f uuid
    return $?
}

function control_c() {
    cleanup
    exit $?
}

function usage() {
    echo "Usage: run_demo.sh <path to MG argos DB> <path to MK argos DB> <MG cycle offset>"
    exit 1
}

trap control_c SIGINT

if [ $# -ne 3 ]
then
    usage
fi

MG_DB=$1
MK_DB=$2
MG_OFFSET=$3

MG_WIDTH=960
MG_HEIGHT=1080
MK_WIDTH=960
MK_HEIGHT=1080

ARGOS_PATH=../argos.py

uuidgen > uuid

SIM_COMM_APPNAME="ARGOS_TWO" $ARGOS_PATH -d $MG_DB -l demo_layouts/mg_evt1.alf -g "$MG_WIDTH,$MG_HEIGHT,$MK_WIDTH,0" -l demo_layouts/rtl.alf -g "0,0,0,0" &
SIM_COMM_TARGET_OFFSET="$3" $ARGOS_PATH -d $MK_DB -l demo_layouts/mklh_evt0.alf -g "$MK_WIDTH,$MK_HEIGHT,0,0" -l demo_layouts/rtl.alf -g "0,0,0,0" &

wait

cleanup

