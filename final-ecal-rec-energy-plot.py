"""plot the minimum cost hcal hit that can still veto the event"""

import argparse
from pathlib import Path

from helpy import HistFile
from helpy.plot import plt, title_bar

import matplotlib as mpl
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=mpl.color_sequences['tab10'])

from helpy import samples
import hist

from reach.hcal_options import hcal_options

parser = argparse.ArgumentParser()
parser.add_argument('hist', type=Path, help='histogram file to load histogram from')
parser.add_argument('--options', nargs='+', help='hcal option short names', default=['entireback','funnel3','funnel2_withside6', 'prototype'], choices=list(hcal_options.keys()))
args = parser.parse_args()

sample = samples.get('enriched-nuclear') #args.hist.parent.stem)

f = HistFile(args.hist, 'ReducedEaT')

options = list((option, hcal_options[option]) for option in args.options)
for key, label in options:
    h = f[f'{key}_final_total_ecal_rec_energy']*sample.hist_scale
    h[hist.rebin(5)].plot1d(
        yerr=False,
        flow=None,
        label=label,
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
    args.hist.parent / f'final-ecal-rec-energy.pdf',
    bbox_inches='tight'
)

