from __future__ import division, print_function

import numpy as np
from numpy.testing import assert_almost_equal
from astropy.io import fits
import pytest
import warnings
import os

from ..utils import KeplerQualityFlags, TessQualityFlags
from ..utils import module_output_to_channel, channel_to_module_output
from ..utils import LightkurveWarning
from ..utils import running_mean, detect_filetype, validate_method
from ..lightcurve import LightCurve

from .. import PACKAGEDIR

def test_channel_to_module_output():
    assert channel_to_module_output(1) == (2, 1)
    assert channel_to_module_output(42) == (13, 2)
    assert channel_to_module_output(84) == (24, 4)
    assert channel_to_module_output(33) == (11, 1)
    with pytest.raises(ValueError):
        channel_to_module_output(0)  # Invalid channel


def test_module_output_to_channel():
    assert module_output_to_channel(2, 1) == 1
    assert module_output_to_channel(13, 2) == 42
    assert module_output_to_channel(24, 4) == 84
    assert module_output_to_channel(11, 1) == 33
    with pytest.raises(ValueError):
        module_output_to_channel(0, 1)  # Invalid module
    with pytest.raises(ValueError):
        module_output_to_channel(2, 0)  # Invalid output


def test_running_mean():
    assert_almost_equal(running_mean([1, 2, 3], window_size=1), [1, 2, 3])
    assert_almost_equal(running_mean([1, 2, 3], window_size=2), [1.5, 2.5])
    assert_almost_equal(running_mean([2, 2, 2], window_size=3), [2])


def test_quality_flag_decoding_kepler():
    """Can the QUALITY flags be parsed correctly?"""
    flags = list(KeplerQualityFlags.STRINGS.items())
    for key, value in flags:
        assert KeplerQualityFlags.decode(key)[0] == value
    # Can we recover combinations of flags?
    assert KeplerQualityFlags.decode(flags[5][0] + flags[7][0]) == [flags[5][1], flags[7][1]]
    assert KeplerQualityFlags.decode(flags[3][0] + flags[4][0] + flags[5][0]) \
        == [flags[3][1], flags[4][1], flags[5][1]]


def test_quality_flag_decoding_tess():
    """Can the QUALITY flags be parsed correctly?"""
    flags = list(TessQualityFlags.STRINGS.items())
    for key, value in flags:
        assert TessQualityFlags.decode(key)[0] == value
    # Can we recover combinations of flags?
    assert TessQualityFlags.decode(flags[5][0] + flags[7][0]) == [flags[5][1], flags[7][1]]
    assert TessQualityFlags.decode(flags[3][0] + flags[4][0] + flags[5][0]) \
        == [flags[3][1], flags[4][1], flags[5][1]]


def test_quality_mask():
    """Can we create a quality mask using KeplerQualityFlags?"""
    quality = np.array([0, 0, 1])
    assert np.all(KeplerQualityFlags.create_quality_mask(quality, bitmask=0))
    assert np.all(KeplerQualityFlags.create_quality_mask(quality, bitmask=None))
    assert np.all(KeplerQualityFlags.create_quality_mask(quality, bitmask='none'))
    assert (KeplerQualityFlags.create_quality_mask(quality, bitmask=1)).sum() == 2
    assert (KeplerQualityFlags.create_quality_mask(quality, bitmask='hardest')).sum() == 2
    # Do we see a ValueError if an invalid bitmask is passed?
    with pytest.raises(ValueError) as err:
        KeplerQualityFlags.create_quality_mask(quality, bitmask='invalidoption')
    assert "not supported" in err.value.args[0]


def test_lightkurve_warning():
    """Can we ignore Lightkurve warnings?"""
    with warnings.catch_warnings(record=True) as warns:
        warnings.simplefilter('ignore', LightkurveWarning)
        time = np.array([1, 2, 3, np.nan])
        flux = np.array([1, 2, 3, 4])
        lc = LightCurve(time=time, flux=flux)
        assert len(warns) == 0


def test_detect_filetype():
    """Can we detect the correct filetype?"""
    k2_path = os.path.join(PACKAGEDIR, "tests", "data", "test-tpf-star.fits")
    tess_path = os.path.join(PACKAGEDIR, "tests", "data", "tess25155310-s01-first-cadences.fits.gz")
    assert detect_filetype(fits.open(k2_path)[0].header) == 'KeplerTargetPixelFile'
    assert detect_filetype(fits.open(tess_path)[0].header) == 'TessTargetPixelFile'


def test_validate_method():
    assert validate_method("foo", ["foo", "bar"]) == "foo"
    assert validate_method("FOO", ["foo", "bar"]) == "foo"
    with pytest.raises(ValueError):
          validate_method("foo", ["bar"])
