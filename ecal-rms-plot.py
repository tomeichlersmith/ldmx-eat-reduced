"""plot the minimum cost hcal hit that can still veto the event"""

import argparse
from pathlib import Path

from helpy import HistFile
from helpy.plot import plt, title_bar, annotate
from helpy import samples
import hist

selections = {
    'trigger': 'Trigger',
    'hcalmaxpe': 'Max Back Hcal PE < 10'
}

parser = argparse.ArgumentParser()
parser.add_argument('hist', type=Path, help='histogram file to load histogram from')
args = parser.parse_args()

sample = samples.get(args.hist.parent.stem)
f = HistFile(args.hist, 'ReducedEaT')
for name, label in selections.items():
  h = (f[f'{name}_ecalrms']*sample.hist_scale)
  art = h.plot1d(label=label,flow=None)
plt.yscale('log')
plt.xlim(0,50)
plt.axvline(20, color='gray')
plt.legend(
    title=sample.label,
    loc='lower right'
)
title_bar(r'8GeV  $10^{13}$ EoT')
plt.savefig(
    args.hist.parent / f'ecal-rms.svg',
    bbox_inches='tight'
)
