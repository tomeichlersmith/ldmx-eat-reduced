import argparse
parser = argparse.ArgumentParser()
parser.add_argument('input_file', nargs='+',help='input ROOT files to study')
parser.add_argument('-n','--n-events',type=int,default=-1,help='maximum number of events to study')
parser.add_argument('--n-files',type=int,help='maximum number of files to process')
parser.add_argument('-o','--output',default='hist.root',help='output file to write histograms into')
args = parser.parse_args()

from pathlib import Path
def explode_input_file(inf, lst):
    if isinstance(inf, list):
        for i in inf:
            explode_input_file(i, lst)
    elif isinstance(inf, str):
        infp = Path(inf)
        if infp.is_dir():
            lst.extend(str(fp) for fp in infp.iterdir() if fp.suffix == '.root')
        elif infp.is_file():
            if infp.suffix == '.root':
                lst.append(str(infp))
    else:
        print(inf, 'unknown, skipping')

path_lst = []
explode_input_file(args.input_file, path_lst)

if args.n_files is not None:
    path_lst = path_lst[:args.n_files]

from LDMX.Framework import ldmxcfg
p = ldmxcfg.Process('ana')
p.sequence = [ ldmxcfg.Analyzer.from_file('ReducedEaT.cxx') ]
p.inputFiles = path_lst
p.histogramFile = args.output
p.maxEvents = args.n_events
