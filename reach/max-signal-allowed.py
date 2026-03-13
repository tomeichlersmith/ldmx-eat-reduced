import pandas as pd
import uproot
import argparse
from pathlib import Path
from harvester.plot import plt_msa
from hcal_options import hcal_options

parser = argparse.ArgumentParser()
parser.add_argument('combine', help='results from combine', type=Path)
parser.add_argument('-o', '--output', help='directory to put output images', type=Path)
args = parser.parse_args()

if args.output is None:
    args.output = args.combine.parent

with uproot.open(args.combine) as f:
    msa = pd.DataFrame(
        f['limit'].arrays(library='np')
    ).set_index(['option', 'mh'])

all_options = list(hcal_options.items())+[('paper', 'Full LDMX')]

plt_msa(
    *(
        (msa.loc[option, :], label)
        for option, label in all_options
    ),
    show_kw = {
        "filename": args.output / 'max-signal-allowed-all.pdf',
        "stage": "Simulation Internal",
        "beam": 8,
        "display": False
    }
)

plt_msa(
    *((msa.loc[option,:], label) for option, label in all_options if option != "prototype"),
    show_kw = {
        "filename": args.output / 'max-signal-allowed-no-prototype.pdf',
        "stage": "Simulation Internal",
        "beam": 8,
        "display": False
    }
)
