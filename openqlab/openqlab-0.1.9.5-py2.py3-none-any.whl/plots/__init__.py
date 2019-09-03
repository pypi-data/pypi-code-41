from .time_domain import zero_span, scope
from .frequency_domain import amplitude_phase, power_spectrum, relative_input_noise
from .gaussian_beam import beam_profile

import matplotlib as mpl

# mpl.style.use(['seaborn-colorblind','seaborn-dark'])
# if hasattr(mpl, 'style'):
#     mpl.style.use('seaborn-dark')
    # mpl.style.use('openqlab')
# mpl.style.use('ggplot')
