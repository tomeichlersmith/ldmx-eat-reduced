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

samples = {
    'true-inclusive': ('10^{7}', 'True Inclusive'),
    'unbiased': (r'9.5 \times 10^{8}', 'Unbiased')
}
sample_lumi, sample_label = samples.get(args.hist.parent.stem, ('???', '???'))

f = HistFile(args.hist, 'CenterTowerTrigger')

for key, label in [
    ('total', 'All Layers and Modules'),
    ('center_tower', 'All Layers, Center Module'),
    ('front', 'First 20 Layers, All Modules'),
    ('center_tower_front', 'First 20 Layers, Center Module')
]:
    h = f[f'{key}_energy']
    npass = h[:3000j:sum]
    h[hist.rebin(5)].plot1d(
        yerr=False,
        flow=None,
        label=f'{label} ({npass:.0f})',
    )


plt.xlim(0,8000)
plt.legend(
    title='\n'.join([
        'Only Even Ecal Layers',
        sample_label
    ]),
    loc='upper left',
)
plt.yscale('log')
plt.ylabel('Events / 50 MeV')
title_bar(f'8GeV  ${sample_lumi}$ EoT')
plt.savefig(
    args.hist.parent / f'trig-energy-comp.pdf',
    bbox_inches='tight'
)

