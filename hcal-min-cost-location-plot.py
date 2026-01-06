"""plot the minimum cost hcal hit that can still veto the event"""

import argparse
from pathlib import Path

from helpy import HistFile
from helpy.plot import plt, title_bar
import hist

parser = argparse.ArgumentParser()
parser.add_argument('hist', type=Path, help='histogram file to load histogram from')
parser.add_argument('--label', help='additional sample label')
parser.add_argument('--selection', default='trigger', help='what cut to apply')
parser.add_argument('--scale', default=1.0)
args = parser.parse_args()

f = HistFile(args.hist, 'ReducedEaT')
h = f[f'{args.selection}_hcal_min_cost_strip_layer'].to_hist()

scales = {
    'dimuon': 1e13/(1.2e9),
    'enriched-nuclear': 1e13/(787*1e6)
}

if args.scale in scales:
    scale = scales[args.scale]
else:
    scale = float(args.scale)


art = (h*scale).plot2d(
    flow='show',
    norm='log'
)
art.cbar.set_label('Events')
plt.annotate(
    '\n'.join([
        'Minimum Cost Hit above 10PE',
        args.label,
        args.selection.capitalize(),
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

