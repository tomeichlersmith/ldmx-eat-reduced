from types import SimpleNamespace
from dataclasses import dataclass, field

import uproot
import awkward as ak


@dataclass
class EoT:
    """Calculate equivalent EoT and hold results

    This is a helper class so that other analyses can calculate
    the EoT in the same way and get the results. This class
    also holds all of the ingredients for the EoT as well as
    the number of runs there were.
    """

    nruns: int
    nevents: int
    weight_sum: float
    tot_sim_eot: int
    avg_bias: float = field(default=None, init=False)
    eot: float = field(default=None, init=False)


    def __post_init__(self):
        """Calculate the average bias factor and the EoT estimate
        from the other ingredients"""

        self.avg_bias = self.nevents / self.weight_sum
        self.eot = self.avg_bias*self.tot_sim_eot


    def __str__(self):
        """Override str operator to just print the EoT estimate in scientific notation
        
        The original dataclass print method is still available via the repr operator.

            print(repr(eot_obj))

        gives the full details.
        """
        return f'{self.eot:.1e}'


    @classmethod
    def from_files(cls, *files, weights = None):
        """Estimate the EoT from a set of files given to uproot

            EoT.from_files('/full/path/to/file.root')

        This can take some time since we have to access the files in order to get the weightsum,
        number of events, number of runs, and total number of tries. If the weights are already
        loaded (for example, since the events were loaded as part of another analysis), then
        you can provide the weights to avoid re-accessing the files for the event-by-event
        information and just scanning them for the LDMX_Runs trees which are smaller and
        therefore presumably quicker.

            EoT.from_files('/full/path/to/file.root', weights = events.weight)

        Each of the positional arguments is assumed to be a file path (or glob expression) that
        can be accepted by uproot.concatenate. We look at both the LDMX_Events tree and the
        LDMX_Run tree, so these files must be LDMX event files.
        """

        if weights is None:
            weights = uproot.concatenate(
                { fp : 'LDMX_Events' for fp in files },
                expressions = [ 'EventHeader/weight_' ]
            )['EventHeader/weight_']

        tries = uproot.concatenate(
            { fp : 'LDMX_Run' for fp in files },
            expressions = [ 'RunHeader/numTries_' ]
        )['RunHeader/numTries_']

        return cls(
            nruns = ak.count(tries),
            nevents = ak.count(weights),
            weight_sum = ak.sum(weights),
            tot_sim_eot = ak.sum(tries),
        )

    

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'files',
        nargs='+',
        help='files to estimate EoT for'
    )
    args = parser.parse_args()

    r = EoT.from_files(*args.files)

    print(f'{r.nruns} runs')
    print(f'Sim EoT    S = {r.tot_sim_eot:.1e}')
    print(f'N Events   N = {r.nevents:.1e}')
    print(f'Weight Sum W = {r.weight_sum:.1e}')
    print(f'Avg Bias B = N/W = {r.avg_bias:.2g}')
    print(f'EoT  = B * S = {r.eot:.1e}')


if __name__ == '__main__':
    main()
