#!/bin/bash
# LPC condor job: unpack the CMSSW tarball, run the cmsRun config on a file chunk, stage both outputs out to EOS.
# Args: index inputFiles(comma-separated URLs) outDir(URL) tarball(URL) config globalTag isMC lumiMask(or "none") cmsswConfig
#       writeConstituents(0|1)
set -e
idx=$1 files=$2 outDir=$3 tarball=$4 config=$5 gt=$6 isMC=$7 mask=$8 cfg=$9 constituents=${10}
echo "job $idx on $(hostname) at $(date)"
top=$PWD
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp -s "$tarball" cmssw.tgz
tar -xzf cmssw.tgz
release=$(tar -tzf cmssw.tgz | head -1 | cut -d/ -f1)
rm cmssw.tgz
cd "$release/src"
scramv1 b ProjectRename > /dev/null
eval "$(scramv1 runtime -sh)"
cd "$top"
extraArgs=()
[ "$mask" != none ] && extraArgs=("lumiMask=$mask")
[ "$constituents" = 1 ] && extraArgs+=("writeConstituents=1")
cmsRun -j report.xml "$cfg" config="$config" globalTag="$gt" isMC="$isMC" inputFiles="$files" \
    outputFile=nano.root histFile=hists.root "${extraArgs[@]}"
# nano last: a job counts as done only when both outputs exist.
xrdcp -f "hists.root" "$outDir/hists_$idx.root?eos.atomic=1"
xrdcp -f "nano.root" "$outDir/nano_$idx.root?eos.atomic=1"
echo "done at $(date)"
