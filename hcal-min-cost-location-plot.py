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
parser.add_argument('--scale', type=float, default=1.0)
args = parser.parse_args()

f = HistFile(args.hist, 'ReducedEaT')
h = f[f'{args.selection}_hcal_min_cost_strip_layer'].to_hist()

(h*args.scale).plot2d(
    flow='show',
    norm='log'
)
plt.annotate(
    '\n'.join([
        args.label,
        args.selection.capitalize()
    ]),
    xy=(0.95,0.95),
    xycoords='axes fraction',
    ha='right', va='top'
)
title_bar()
plt.savefig(
    args.hist.parent / f'{args.selection}-hcal-min-cost-strip-layer.png',
    bbox_inches='tight'
)

