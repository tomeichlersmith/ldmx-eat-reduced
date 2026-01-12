"""plot the minimum cost hcal hit that can still veto the event"""

import argparse
from pathlib import Path

from helpy import HistFile
from helpy.plot import plt, title_bar, annotate
from helpy import samples
import hist

selections = {
    'trigger': 'Trigger',
    'ecalrms': 'Trigger\nEcal RMS < 20 mm',
    'lowenergy': '\n'.join(['Trigger','Ecal RMS < 20 mm',r'$E_\text{Ecal} < 3.16$GeV'])
}

parser = argparse.ArgumentParser()
parser.add_argument('hist', type=Path, help='histogram file to load histogram from')
parser.add_argument('--selection', default='trigger', choices = list(selections.keys()), help='what cut to apply')
args = parser.parse_args()

sample = samples.get(args.hist.parent.stem)
f = HistFile(args.hist, 'ReducedEaT')
h = (
    f[f'{args.selection}_hcal_min_cost_strip_layer'].to_hist()
    *sample.hist_scale
)

art = h.plot2d(
    flow='show',
    norm='log'
)
art.cbar.set_label('Events')
annotate(
    '\n'.join([
        'Minimum Cost Hit above 10PE',
        'Back Hcal Only',
        sample.label,
        selections[args.selection]
    ]),
    loc='upper right'
)
title_bar(r'8GeV  $10^{13}$ EoT')
plt.savefig(
    args.hist.parent / f'{args.selection}-hcal-min-cost-strip-layer.svg',
    bbox_inches='tight'
)

