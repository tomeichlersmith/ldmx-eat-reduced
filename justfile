@_default:
    just --list --justfile {{ justfile() }}

# test compile and run on single file
test:
    denv fire ana-cfg.py --out out/hist.root $(head -1 enriched-nuclear.list)    

# test compile trigger analyzer and run on single file
test-trig:
    denv fire trig-ana-cfg.py --out out/trig-hist.root $(head -1 true-inclusive-0.list)    

# run trigger analyzer over entire true-inclusive sample
run-trig:
    ./fire-parallel trig-ana-cfg.py --out-dir out/true-inclusive :::: true-inclusive-0.list
    ./fire-parallel trig-ana-cfg.py --out-dir out/unbiased :::: unbiased.list

# run over input sample
run sample:
    ./fire-parallel ana-cfg.py --out-dir out/{{sample}} :::: {{sample}}.list

# run over enriched-nuclear
enriched-nuclear: (run "enriched-nuclear")

# copy output directory from workstation to here
sync:
    rsync -avmu \
      --exclude '*/hists/*' \
      --exclude '*/logs/*' \
      umn.workstation:ldmx/eat/reduced/out/ \
      out/
    rsync -avmu \
      --exclude '*/hists/*' \
      --exclude '*/logs/*' \
      umn.zebra01:/export/scratch/users/eichl008/ldmx/eat/reduced/out/ \
      out/

# watch slides while developing update
slides:
    typst watch slides/slides.typ --root . --open
