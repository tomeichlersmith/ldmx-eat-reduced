from harvester.datacard import DataCard
import json
import os
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('bkgd', type=Path, help='background predictions to do reach for')
parser.add_argument('--scale', type=float, help='scale factor to multiply background by', default=1)
args = parser.parse_args()

here = Path(__file__).parent

with open(here / 'paper-bkgd-prediction.json', 'r') as f:
    paper_bkgd_yield = json.load(f)["8"]

with open(here / 'paper-sig-eff.json', 'r') as f:
    paper_sig_eff = json.load(f)["8"]

with open(args.bkgd, 'r') as f:
    bkgd_yields = json.load(f)

combine_dir = here / 'combine' / 'cards'
combine_dir.mkdir(parents=True, exist_ok=True)

with open(combine_dir / 'jobs.list', 'w') as jobs:
    for option, by in [('paper',paper_bkgd_yield)]+list(bkgd_yields.items()):
        for proc, se in paper_sig_eff.items():
            datacard_path = str(combine_dir / f'{option}-{proc}.txt')
            (
                DataCard(3)
                .sig(*se)
                .bkg(*(args.scale*events for events in by["fit_val"]))
                .bkg_stat(*(
                    ((up - lo)/2/fit_val)
                    for up, lo, fit_val in
                    zip(by["up"], by["lo"], by["fit_val"], strict=True)
                ))
                .bkg_syst(0.05)
                .bkg_syst(0.0, 0.6, 0.7)
                .write(datacard_path)
            )
            for q in [0.5]: #[0.025, 0.16, 0.5, 0.84, 0.975]:
                jobs.write(' '.join([
                    datacard_path,
                    f'--keyword-value option={option}',
                    f'--mass {proc[2:]}',
                    f'--expectedFromGrid={q}'
                ]))
                jobs.write('\n')
