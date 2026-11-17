#!/bin/bash
# Condor job of condor.py, run in the coffea container. Args: job index, workers, chunksize.
set -e
idx=$1 workers=$2 chunksize=$3
echo "job $idx on $(hostname) at $(date)"
tar -xzf analysis.tgz
python3 run.py config.yaml --fileset job_$idx.json --workers $workers --chunksize $chunksize -o part_$idx.coffea
echo "done at $(date)"
