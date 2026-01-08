"""plot the minimum cost hcal hit that can still veto the event"""

import argparse
from pathlib import Path

from helpy import HistFile
from helpy.plot import plt, title_bar
from helpy import samples
import hist

selections = {
    'trigger': 'Trigger',
    'ecalrms': 'Ecal RMS < 20 mm'
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
plt.annotate(
    '\n'.join([
        'Minimum Cost Hit above 10PE',
        'Back Hcal Only',
        sample.label,
        selections[args.selection]
    ]),
    xy=(0.95,0.95),
    xycoords='axes fraction',
    ha='right', va='top'
)
title_bar(r'8GeV  $10^{13}$ EoT')
plt.savefig(
    args.hist.parent / f'{args.selection}-hcal-min-cost-strip-layer.pdf',
    bbox_inches='tight'
)

