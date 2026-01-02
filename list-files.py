"""create an input file for GNU parallel that lists input files"""

from pathlib import Path
import argparse

base = Path('/local/cms/user/eichl008/ldmx/eat/v14/8gev/bkgd')
batches = ['dimuon'] + [f'enriched-nuclear-{i}' for i in range(10)] + [f'unbiased-{i}' for i in range(10)]

parser = argparse.ArgumentParser()
parser.add_argument('batch', choices=batches+['ALL'], help='which batch to enumerate')
parser.add_argument('nper', type=int, help='number of files per job')
args = parser.parse_args()

with open(args.batch+'.list','w') as f:
    for batch in batches:
        if batch == args.batch or args.batch == 'ALL':
            file_list = (fp for fp in (base / batch).iterdir() if fp.suffix == '.root')
            # group into N elements, not ordered
            # https://docs.python.org/3/library/itertools.html#itertools-recipes
            iterators = [iter(file_list)] * args.nper
            for grp in zip(*iterators, strict=True):
                for fp in grp:
                    f.write(f'{fp} ')
                f.write('\n')
