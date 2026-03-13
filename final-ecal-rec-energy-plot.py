"""plot the minimum cost hcal hit that can still veto the event"""

import argparse
from pathlib import Path

from helpy import HistFile
from helpy.plot import plt, title_bar
from helpy import samples
import hist

from reach.hcal_options import hcal_options

parser = argparse.ArgumentParser()
parser.add_argument('hist', type=Path, help='histogram file to load histogram from')
args = parser.parse_args()

sample = samples.get(args.hist.parent.stem)

f = HistFile(args.hist, 'ReducedEaT')

for key, label in hcal_options.items():
    h = f[f'{key}_final_total_ecal_rec_energy']*sample.hist_scale
    h[hist.rebin(5)].plot1d(
        yerr=False,
        flow=None,
        label=label,
        histtype='bar' if key == 'entireback' else 'step'
    )

plt.xlim(0,4000)
plt.legend(
    title='\n'.join([
        'Only Even Ecal Layers',
        sample.label,
        'Trigger',
        'Hcal Max PE < 10',
        'Ecal RMS < 20 mm'
    ]),
    loc='upper left',
    bbox_to_anchor = (1,1)
)
plt.yscale('log')
plt.ylabel('Events / 50 MeV')
title_bar(r'8GeV  $10^{13}$ EoT')
for boundary in (3160, 2760, 2000, 1000):
    plt.axvline(boundary, color = 'gray', linestyle = 'dotted')
plt.savefig(
    args.hist.parent / f'final-ecal-rec-energy.svg',
    bbox_inches='tight'
)

