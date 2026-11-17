# Plan: running the coffea analysis on LPC HTCondor

Status: implemented 2026-11-17 (D1: batch jobs; D2: cvmfs container; D3: configurable, default 20 files and 1 CPU;
local or condor chosen with `run.py --backend`). Verified:
- unit tests (`tests/test_condor.py`);
- a 3-job split run locally and collected equals a single run (cutflows identical, histograms within 1e-15 relative);
- a 1-file LPC job in the container (`+ApptainerImage`) gives output identical to the same file run locally
  (37 histograms and the cutflows), using 60 s and about 300 MB.

## Contents
- Facts this plan rests on
- Options considered (D1)
- Proposed design (option B)
- Decisions needed (D2, D3)
- Validation
- Not verified yet

## Facts this plan rests on
- Per-chunk processing is CPU-bound, not limited by reading from EOS: a remote and a local copy of the same file take
  the same time (`PERF_PLAN.md`). Spreading files over Condor nodes therefore scales the runtime almost linearly.
- After `e1c3b8f`, one DY file of about 33k events takes about 4.7 s to process with the boosted config.
- The official container `/cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-almalinux9:2026.11.0-py3.13`
  has the same coffea (2026.11.0), awkward (2.14.0), uproot (5.7.7) and hist (2.12.1) as our `dev` env, plus PyYAML
  and mplhep. It differs in numpy (2.5.5 vs 2.5.4) and Python (3.13 vs 3.14). It also has dask, distributed and
  dask_jobqueue, but not lpcjobqueue.
- The repository already runs LPC Condor jobs for the production (`simulation/production/condorBackend.py`), with
  these known quirks (`simulation/JOURNAL.md`, 2026-11-12):
  - the `condor_*` wrappers need to be run via `sh`;
  - cluster ids are unique only per schedd;
  - the schedds do not mount `/cvmfs/cms-griddata`;
  - inputs are transferred only when a job starts, so they must be snapshotted at submission.

## Options considered (D1)
**A. Dask cluster (lpcjobqueue or dask-jobqueue).** A scheduler on the interactive node, with Condor jobs as workers
and coffea's `DaskExecutor`.
- Pros: dynamic load balancing; the same `run.py` call returns the merged result directly.
- Cons:
  - the scheduler and the session must stay alive for the whole run;
  - worker networking back to the interactive node is needed;
  - lpcjobqueue is not in the image and its compatibility with coffea 2026.11 is unverified;
  - a lost scheduler loses the run.

**B. Independent batch jobs, then a local merge (recommended).** Split the fileset into jobs of K files. Each Condor
job runs the processor on its files inside the coffea container and writes a partial `.coffea` file. A collect step
checks that every job finished and accumulates the outputs into the usual `out.coffea`.
- Pros:
  - no long-lived process, so failed jobs can be resubmitted individually;
  - it is the same pattern as our production tooling;
  - nothing new to install.
- Cons:
  - Condor queueing latency (minutes);
  - static splitting;
  - a separate collect step.

## Proposed design (option B)
- `run.py` gains `--fileset JSON`: an explicit fileset that includes the per-sample metadata (`lumiScale`, `isMC`),
  so a job needs neither `xsec.yaml` nor the production bookkeeping.
- A new script, `analysis/condor.py`, with three subcommands:
  - `submit`: builds the fileset (as `run.py --tag` does today, including the lumi scaling) and splits it into
    jobs of K files. It snapshots `bvana/`, `run.py` and the config into `work/<name>/inputs/` and writes a JDL that
    runs `job.sh` in the container. It records `{cluster, schedd}` and the git state of `analysis/`.
  - `status`: shows which jobs are done, running or failed (from the per-job output files and the Condor log).
  - `collect`: refuses if any job is missing, unless `--allow-missing` is given, and then accumulates the parts
    with `coffea.processor.accumulate` into `out.coffea`. The output's provenance (config, tag, lumi, code state)
    is the same as today's.
- `job.sh` runs `python3 run.py <config> --fileset job_k.json --workers <request_cpus> -o part_k.coffea` and
  transfers the result back to the submit directory through Condor's output transfer. Parts are about 1 MB, so EOS
  is not needed for them.
- A grid proxy (`x509userproxy`) is needed for the xrootd reads, as in the production.

## Decisions needed
- **D1:** option B (recommended) or A.
- **D2:** environment: the cvmfs coffea container (recommended: nothing to ship or maintain) or a conda-pack tarball
  of our `dev` env (exact versions, but larger and needs re-packing).
- **D3:** job size: K files per job and `request_cpus`. My proposal is about 20 files per job (about 2–3 min of
  processing on 1 core at today's speed) and 1 CPU. That gives about 20 jobs for the current 368-file tag.

## Validation
- Equivalence: run one tag both locally and through Condor. Every histogram (values and variances) and every
  cutflow must agree. They should be bit-identical if the numpy version difference does not matter; any difference
  will be reported, not assumed away.
- Collect: unit tests showing that accumulating split outputs equals a single run on the same files, and that a
  missing part makes `collect` refuse.
- A test job first: 1 job of 1 file through the full chain before any larger submission.

## Not verified yet
- The exact LPC JDL syntax for running a job in an apptainer image from cvmfs, and whether LPC workers mount
  `/cvmfs/unpacked.cern.ch`. Both will be checked with the 1-file test job.
- Condor queue times at the LPC for short jobs.
- Whether the 4-worker local run's ~60% CPU (`PERF_PLAN.md`) also appears on Condor workers.
