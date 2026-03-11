from . import datacard
from . import fit
from . import io
from . import plot


def signal_events_to_y(s, event_yield_epsilon_1, alpha_D, mA_over_mChi):
    """Calculate the y corresponding to the input number of signal events s

    From the number of signal events s,
    we can calculate the corresponding interaction strength.

      s = epsilon^2 * N_{epsilon = 1}
        = y / alphaD * (mA / mChi)^4 * N_{epsilon = 1}

    Solving for y:

      y = s /( (1/alphaD)*(mA / mChi)^4 * N_{epsilon = 1})

    Parameters
    ----------
    s : float
        Number of signal events 
    event_yield_epsilon_1 : float
        Number of events with signal if mixing strength epsilon was one
    alpha_D : float
        dark sector interaction strength
    mA_over_mChi: float
        ratio of dark photon mass to dark fermion mass
    """

    return s/((1./alpha_D)*(mA_over_mChi**4)*event_yield_epsilon_1)