import mplhep
mplhep.style.use('ROOT')

import matplotlib.pyplot as plt

def title_bar(
    text=None, *,
    by_ldmx='Simulation Internal',
    exp_text_kw = dict(),
    lumitext_kw = dict(),
    **kwargs
):
    """add a title bar to the plot with mplhep

    'LDMX' is the experiment text.

    Parameters
    ----------
    text: str
        given to mplhep.label.lumitext to appear on upper right hand side
        default None
    by_ldmx: str
        written next to the 'LDMX' experiment label in a slightly smaller size
        default 'Internal'
    exp_text_kw: dict
        key-word arguments to pass to mplhep.label.exp_text
    lumitext_kw: dict
        key-word arguments to pass to mplhep.label.lumitext
    kwargs: dict
        additional keywoard arguments passed to both labeling functions
        mostly helpful for uniformly applying style changes
    """
    mplhep.label.exp_text('LDMX', by_ldmx, **exp_text_kw, **kwargs)
    if text is not None:
        mplhep.label.lumitext(text, **lumitext_kw, **kwargs)


def annotate(
    *args,
    loc = None,
    **kwargs
):
    """a simple wrapper around plt.annotate that implements the corner-of-axes shortcuts
    that plt.legend does"""
    if loc == 'upper left':
        kwargs['ha'] = 'left'
        kwargs['va'] = 'top'
        kwargs['xycoords'] = 'axes fraction'
        kwargs['xy'] = (0.05,0.95)
    elif loc == 'upper right':
        kwargs['ha'] = 'right'
        kwargs['va'] = 'top'
        kwargs['xycoords'] = 'axes fraction'
        kwargs['xy'] = (0.95,0.95)
    elif loc == 'lower left':
        kwargs['ha'] = 'left'
        kwargs['va'] = 'bottom'
        kwargs['xycoords'] = 'axes fraction'
        kwargs['xy'] = (0.05,0.05)
    elif loc == 'lower right':
        kwargs['ha'] = 'right'
        kwargs['va'] = 'bottom'
        kwargs['xycoords'] = 'axes fraction'
        kwargs['xy'] = (0.95,0.05)

    return plt.annotate(*args, **kwargs)

