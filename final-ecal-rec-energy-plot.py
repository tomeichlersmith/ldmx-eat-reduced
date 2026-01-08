"""plot the minimum cost hcal hit that can still veto the event"""

import argparse
from pathlib import Path

from helpy import HistFile
from helpy.plot import plt, title_bar
from helpy import samples
import hist

parser = argparse.ArgumentParser()
parser.add_argument('hist', type=Path, help='histogram file to load histogram from')
args = parser.parse_args()

sample = samples.get(args.hist.parent.stem)

f = HistFile(args.hist, 'ReducedEaT')
h = f['final_total_ecal_rec_energy'].to_hist()*sample.hist_scale

h[hist.rebin(5)].plot1d(
    yerr=False,
    flow=None
)
plt.xlim(0,4000)
plt.annotate(
    '\n'.join([
        'Only Even Ecal Layers',
        sample.label,
        'Hcal Back Max PE < 10',
        'Ecal RMS < 20 mm'
    ]),
    xy=(0.05,0.95),
    xycoords='axes fraction',
    ha='left', va='top'
)
plt.ylabel('Events / 50 MeV')
title_bar(r'8GeV  $10^{13}$ EoT')
plt.savefig(
    args.hist.parent / f'final-ecal-rec-energy.pdf',
    bbox_inches='tight'
)

