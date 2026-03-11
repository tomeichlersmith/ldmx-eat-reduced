from pathlib import Path
import uproot
import pickle

import pandas as pd

def _from_options(options, run = None):
    # sort options by last modified time
    options.sort(key = lambda f: f.stat().st_mtime)
    if run is None:
        run = options[-1]
    elif isinstance(run, int):
        run = options[run]
    elif isinstance(run, str):
        match = [ o for o in options if o.stem == run ]
        if len(match) == 0:
            raise ValueError(f'No run matching {run} in {options}.')
        elif len(match) > 1:
            raise ValueError(f'More than one matching {run} in {options}.')
        run = match[0]
    elif not isinstance(run, Path):
        raise TypeError(f'{run} is not None, an int, str, or Path.')
    print(f'Selected {run}')
    return run


def load_hists(run = None):
    fp = _from_options(
        [
            f
            for f in Path('../analysis/coffea/hists/rms-on-both').iterdir()
            if f.suffix == '.pkl'
        ],
        run = run
    )
    with open(fp, 'rb') as f:
        return pickle.load(f)


def load_max_signal_allowed(run = None):
    fp = _from_options(
        [
            f
            for f in Path.cwd().iterdir()
            if f.stem.startswith('higgsCombine.') and f.suffix == '.root'
        ],
        run = run
    )
    with uproot.open(fp) as f:
        return pd.DataFrame(f['limit'].arrays(library='np'))


def load_signal_rates(f = '../prod-rate/eat-nom-rates.csv'):
    import pandas as pd
    rates = pd.read_csv(f).set_index(['target','beam','min_efrac','map'])
    rates['rate'] = rates.rate/0.01**2 # remove eps2 dependence
    return rates