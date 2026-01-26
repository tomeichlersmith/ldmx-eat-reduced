@_default:
    just --list --justfile {{ justfile() }}

# test compile and run on single file
test:
    denv fire ana-cfg.py --out out/hist.root $(head -1 enriched-nuclear.list)    

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

# watch slides while developing update
slides:
    typst watch slides/slides.typ --root . --open
