#!/bin/bash
# Builds the EEC library's Python module into bvana/_ext/ for the dev environment and for the coffea container of the
# condor jobs (condor.py ships bvana/). Rerun after changing simulation/EECs.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
BUILD=$HERE/../simulation/EECs/pybind/build.sh
IMG=/cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-almalinux9:2026.11.0-py3.13
PB=$IMG/usr/local/lib/python3.13/site-packages/pybind11/include
DEV=/uscms/home/srothman/nobackup/mambaforge/envs/dev
"$BUILD" "$HERE/bvana/_ext" "$DEV/include/python3.14" "$PB" .cpython-314-x86_64-linux-gnu.so
"$BUILD" "$HERE/bvana/_ext" "$IMG/usr/local/include/python3.13" "$PB" .cpython-313-x86_64-linux-gnu.so
