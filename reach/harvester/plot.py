"""plotting utilities"""

import matplotlib as mpl
import mplhep
import mplhep.error_estimation

mpl.style.use(mplhep.style.ROOT)
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=mpl.color_sequences['tab10'])

import matplotlib.pyplot as plt



def show(
    beam = None, *,
    lumi = '$10^{13}$ EoT',
    stage = 'Internal',
    ax = None,
    filename = None,
    display = True,
    exp_loc = 0
):
    if beam is not None:
        mplhep.label.lumitext(
            f'{beam} GeV' if lumi is None else f'{lumi} ({beam} GeV)',
            ax = ax
        )
    mplhep.label.exp_text('LDMX',stage, loc=exp_loc, ax=ax)
    if filename is not None:
        plt.savefig(
            filename,
            bbox_inches='tight'
    )
    if display:
        plt.show()
    else:
        plt.clf()


def plt_msa(
    *args, legend_kw = {}, show_kw = {}, **plt_kwargs
):
    for msa, label in args:
        plt.errorbar(
            msa.index,
            msa.limit,
            yerr=msa.limitErr,
            label=label,
            fmt='o',
            **plt_kwargs
        )
    plt.xscale('log')
    plt.legend(**legend_kw)
    plt.xlabel(r"$m_{A'} /$ MeV")
    plt.ylabel("Max Produced Signal Allowed")
    show(**show_kw)
