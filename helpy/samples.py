"""holding sample-specific information"""

from dataclasses import dataclass

@dataclass
class SampleSpec:
    nruns: int
    attempts_per_run: float

    @property
    def attempts(self):
        return nruns*attempts_per_run


SAMPLES = {
    'dimuon': SampleSpec(
        nruns = 1200,
        attempts_per_run = 1e6
    ),
    'enriched-nuclear': SampleSpec(
        nruns = 10*5000,
        attempts_per_run = 1e6
    ),
}

def hist_scale(name, eot_target = 1e13):
    return eot_target/SAMPLES[name].attempts 
