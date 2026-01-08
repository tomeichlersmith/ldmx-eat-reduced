"""holding sample-specific information"""

import warnings
from dataclasses import dataclass

@dataclass
class SampleSpec:
    nruns: int
    attempts_per_run: float
    label: str

    def __post_init__(self):
        self.attempts = self.nruns*self.attempts_per_run
        self.hist_scale = 1e13/self.attempts



SAMPLES = {
    'dimuon': SampleSpec(
        nruns = 1200,
        attempts_per_run = 1e6,
        label = 'Dimuon'
    ),
    'enriched-nuclear': SampleSpec(
        nruns = 10*5000,
        attempts_per_run = 1e6,
        label = 'Enriched Nuclear'
    ),
}

def get(name):
    if name not in SAMPLES:
        raise ValueError('Sample name {name} not in known samples.')
    return SAMPLES[name]
