#!/bin/bash
# Rebuilds the AN cutflow tables (dev env with uproot): per-step counts from the one-file cutflow production
# (20261118_cutflow, NANOs copied locally with xrdcp to $NANO) and the reco final rows of the full productions.
# Usage: ./make_cutflow.sh [NANO dir, default ../../cutflow_20261118] [--no-final-recompute]
set -e
here=$(cd "$(dirname "$0")" && pwd)
nano=${1:-$here/../../cutflow_20261118}
work=$here/../../simulation/production/work
list=$here/cutflow_samples.txt
final=$here/cutflow_final_rows.json
if [ "$2" != --no-final-recompute ]; then
    python3 "$here/final_rows.py" "$final" $(grep -v '^#' "$list" | awk -v w="$work" '{print $1"="w"/"$3"/"$2"/merged/sample.json"}')
fi
table() {  # out names...
    local out=$1; shift
    local args=()
    for n in "$@"; do args+=("$n=$nano/$(awk -v n="$n" '$1==n{print $2}' "$list").root"); done
    python3 "$here/make_cutflow.py" "$here/$out" --final "$final" "${args[@]}"
}
table cutflow_table.tex ZZto2L2Q WZto2L2Q DY_PTLL200to400 DY_PTLL400to600 DY_PTLL600 TTto2L2Nu WWto2L2Nu
table cutflow_table_top.tex tbq_lnu_t tbarbq_lnu_t tbq_2q_t tbarbq_2q_t tb_lnu_s tbarb_lnu_s tb_2q_s
table cutflow_table_tw.tex tWm_2l2nu tWm_lnu2q tWm_4q tbarWp_2l2nu tbarWp_lnu2q tbarWp_4q
table cutflow_table_zh.tex ZH_bb ZH_cc ZH_gg ZH_WW4q ZH_WWlnu2q
table cutflow_table_ggzh.tex ggZH_bb ggZH_cc ggZH_gg ggZH_WW4q ggZH_WWlnu2q
