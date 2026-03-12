# reach estimate

This directory takes the histograms filled by [ReducedEaT](../ReducedEaT.cxx) and follows
the same reach-estimate procedure as done for the 2025 EaT Paper.

1. Fit background and project into three coarse analysis bins: `bkgd-prediction.py`
2. Write input cards and list of jobs for `combine`: `construct-datacard.py`
3. Run `combine` to extract maximum signal yield: `combine/run`
4. Plot maximum signal yield

Besides running `combine`, the python scripts for plotting and fitting have
an environment managed by `uv`.
```
# 1. does fit and makes plots, putting bkgd-prediction.json and plots into
#    the path/to directory
uv run bkgd-prediction.py path/to/hist.root
# 2. writes datacards to combine/cards directory
uv run construct-datacard.py path/to/bkgd-prediction.json
# 3. writes combine output to combine/ directory
./combine/run NAME
# use the PARALLEL environment variable to add more options to GNU parallel, e.g.
PARALLEL="-j2" ./combine/run Test
```
