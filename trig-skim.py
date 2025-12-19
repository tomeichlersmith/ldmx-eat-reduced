import argparse
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='input ROOT file to trigger skim', type=Path)
args = parser.parse_args()

from LDMX.Framework import ldmxcfg
p = ldmxcfg.Process('ana')
p.sequence = [ ldmxcfg.Analyzer.from_file('TriggerSkim.cxx') ]
p.inputFiles = [str(args.input_file)]
p.outputFiles = [str(args.input_file.stem)+'_trig_skim.root']
p.skimDefaultIsDrop()
p.skimConsider(p.sequence[0].instanceName)
