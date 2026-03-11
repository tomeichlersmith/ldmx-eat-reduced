"""model for writing Combine datacards"""

from datetime import datetime
from pathlib import Path
import numpy as np


class DataCard:
    """DataCard writer using the builder pattern to construct"""

    def __init__(self, nbin):
        self.nbin = nbin
        self._bkg_syst = []

    def _broadcast_count(self, name, *args, copy_single = False):
        if len(args) == 1 and copy_single:
            return self.nbin*(args[0],)
        if len(args) != self.nbin:
            raise ValueError(f"Too many entries to {name}, expected {self.nbin}, got {len(args)}")
        return args

    
    def _set_count(self, name, *args, copy_single = False):
        setattr(self, name, self._broadcast_count(name, *args, copy_single=copy_single))
        return self
    
    def obs(self, *args):
        return self._set_count('_obs', *args)

    def sig(self, *args):
        return self._set_count('_sig', *args)

    def bkg(self, *args):
        return self._set_count('_bkg', *args)

    def disable(self, name):
        setattr(self, '_'+name, None)
        return self

    def sig_unc(self, *args):
        return self._set_count('_sig_unc', *args, copy_single=True)

    def bkg_stat(self, *args):
        return self._set_count('_bkg_stat', *args, copy_single=True)

    def bkg_syst(self, *args):
        self._bkg_syst.append(self._broadcast_count('_bkg_syst', *args, copy_single=True))
        return self

    def write(self, f):
        if any(map(lambda n: not hasattr(self, n), ['_sig','_bkg'])):
            raise ValueError('One of the required options "sig" or "bkg" was not provided!')

        if isinstance(f, (str,Path)):
            with open(f, 'w') as opened_f:
                self.write(opened_f)
                return

        if not hasattr(self, '_obs'):
            self._obs = tuple(round(b) for b in self._bkg)
        if not hasattr(self, '_bkg_stat'):
            self._bkg_stat = tuple(1/np.sqrt(b) for b in self._bkg)
        if not hasattr(self, '_sig_unc'):
            self._sig_unc = self.nbin*(0.20,)

        bin_names = tuple(f'bin{i}' for i in range(self.nbin))
        f.write("# counting experiment with multiple channels\n")
        f.write(f'# combine datacard generated on {datetime.today().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f"imax {self.nbin}  number of channels\n")
        f.write("jmax 1  number of backgrounds\n")
        kmax=(
            (1 if self._sig_unc is not None else 0) # signal rate uncertainty
            + (self.nbin if self._bkg_stat is not None else 0) # bkgd stat uncertainty in each channel
            + len(self._bkg_syst) # bkgd systematics
        )
        f.write(f"kmax {kmax}  number of nuisance parameters\n")
        f.write("------------\n")
        f.write("# number of observed events in each channel\n")
        f.write(' '.join(('bin',)+bin_names)+'\n')
        f.write(' '.join(['observation']+[f'{o:<d}' for o in self._obs])+'\n')
        f.write("------------\n")
        f.write("# list the expectation for signal and background processes in each of the channels\n")
        f.write(f"{'bin':<14s}")
        for name in bin_names:
            f.write(f'{name:<s} {name:<s} ') # two entries: one bkgd and one signale process
        f.write('\n')
        f.write(f"{'process':<14s}")
        f.write(' '.join(self.nbin*['ap bkg ']))
        f.write('\n')
        f.write(f"{'process':<14s}")
        f.write(' '.join(self.nbin*['0 1 ']))
        f.write('\n')
        f.write(f"{'rate':<14s}")
        for i in range(self.nbin):
            for proc in (self._sig, self._bkg):
                proc_rate = f'{proc[i]:f}'
                f.write(f'{proc_rate:<s} ')
        f.write('\n')
        f.write("------------\n")
        f.write("# list the sources of systematic uncertainty\n")
        if self._sig_unc is not None:
            f.write(f"{'sigrate lnN':<14s}")
            for su in self._sig_unc:
                f.write(f"{1+su:<f} {'-':<s} ")
            f.write('\n')

        if self._bkg_stat is not None:
            for i, (binname, bu) in enumerate(zip(bin_names, self._bkg_stat)):
                f.write(f'{binname+"stat lnN":<14s}')
                for j in range(i):
                    f.write('- - ')
                f.write(f'- {1+bu:<f} ')
                for j in range(self.nbin-i-1):
                    f.write('- - ')
                f.write('\n')

        for i, bkg_syst in enumerate(self._bkg_syst):
            f.write(f"bkgdsyst{i} lnN ")
            for bs in bkg_syst:
                f.write(f'- {1+bs:<f} ')
            f.write('\n')
        
        return


if __name__ == '__main__':
    import sys
    (
        DataCard(3)
        .disable('bkg_stat')
        .sig(0.4, 0.3, 0.2)
        .bkg(1, 10, 100)
        .bkg_syst(0.05)
        .bkg_syst(0.30,0.10, 0.05)
        .write(sys.stdout)
    )
    
    (
        DataCard(1)
        .disable('sig_unc')
        .sig(0.3)
        .bkg(1)
        .bkg_syst(0.05)
        .write(sys.stdout)
    )
    
