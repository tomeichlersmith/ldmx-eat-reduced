"""plot the minimum cost hcal hit that can still veto the event"""

import argparse
from pathlib import Path

from helpy import HistFile
from helpy.plot import plt, title_bar
from helpy import samples
import hist

selections = {
    'trigger': 'Trigger',
    'hcalmaxpe': 'Trigger && Max Back Hcal PE < 10',
    'ecalrms': 'Trigger && Ecal RMS < 20 mm',
    'final': 'Trigger && Both'
}

parser = argparse.ArgumentParser()
parser.add_argument('hist', type=Path, help='histogram file to load histogram from')
args = parser.parse_args()

sample = samples.get(args.hist.parent.stem)

f = HistFile(args.hist, 'ReducedEaT')

for name, label in selections.items():
    h = f[f'{name}_total_ecal_rec_energy']*sample.hist_scale
    h[hist.rebin(5)].plot1d(
        yerr=False,
        flow=None,
        label=label
    )
   
plt.yscale('log')
plt.xlim(0,4000)
plt.legend(
    title=sample.label,
    loc='upper left'
)
plt.ylabel('Events / 50 MeV')
title_bar(r'8GeV  $10^{13}$ EoT')
for boundary in (3160, 2760, 2000, 1000):
    plt.axvline(boundary, color = 'gray', ymax = 0.7)
plt.savefig(
    args.hist.parent / f'ecal-rec-energy.svg',
    bbox_inches='tight'
)

