# -*- coding: utf-8 -*-
"""Test the MNE BIDS converter.

For each supported file format, implement a test.
"""
# Authors: Mainak Jas <mainak.jas@telecom-paristech.fr>
#          Teon L Brooks <teon.brooks@gmail.com>
#          Chris Holdgraf <choldgraf@berkeley.edu>
#          Stefan Appelhoff <stefan.appelhoff@mailbox.org>
#          Matt Sanderson <matt.sanderson@mq.edu.au>
#
# License: BSD (3-clause)
import os
import os.path as op
import pytest
from glob import glob
from datetime import datetime
import platform
import shutil as sh
import json
from distutils.version import LooseVersion

import numpy as np
from numpy.testing import assert_array_equal
import mne
from mne.datasets import testing
from mne.utils import _TempDir, run_subprocess, check_version, requires_nibabel
from mne.io.constants import FIFF
from mne.io.kit.kit import get_kit_info

from mne_bids import (write_raw_bids, read_raw_bids, make_bids_basename,
                      make_bids_folders, write_anat)
from mne_bids.tsv_handler import _from_tsv, _to_tsv
from mne_bids.utils import _find_matching_sidecar
from mne_bids.pick import coil_type

base_path = op.join(op.dirname(mne.__file__), 'io')
subject_id = '01'
subject_id2 = '02'
session_id = '01'
run = '01'
acq = '01'
run2 = '02'
task = 'testing'

bids_basename = make_bids_basename(
    subject=subject_id, session=session_id, run=run, acquisition=acq,
    task=task)
bids_basename_minimal = make_bids_basename(subject=subject_id, task=task)


# WINDOWS issues:
# the bids-validator development version does not work properly on Windows as
# of 2019-06-25 --> https://github.com/bids-standard/bids-validator/issues/790
# As a workaround, we try to get the path to the executable from an environment
# variable VALIDATOR_EXECUTABLE ... if this is not possible we assume to be
# using the stable bids-validator and make a direct call of bids-validator
# also: for windows, shell = True is needed to call npm, bids-validator etc.
# see: https://stackoverflow.com/q/28891053/5201771
@pytest.fixture(scope="session")
def _bids_validate():
    """Fixture to run BIDS validator."""
    shell = False
    bids_validator_exe = ['bids-validator', '--config.error=41',
                          '--config.error=41']
    if platform.system() == 'Windows':
        shell = True
        exe = os.getenv('VALIDATOR_EXECUTABLE', 'n/a')
        if 'VALIDATOR_EXECUTABLE' != 'n/a':
            bids_validator_exe = ['node', exe]

    def _validate(output_path):
        cmd = bids_validator_exe + [output_path]
        run_subprocess(cmd, shell=shell)

    return _validate


def test_fif(_bids_validate):
    """Test functionality of the write_raw_bids conversion for fif."""
    output_path = _TempDir()
    data_path = testing.data_path()
    raw_fname = op.join(data_path, 'MEG', 'sample',
                        'sample_audvis_trunc_raw.fif')

    event_id = {'Auditory/Left': 1, 'Auditory/Right': 2, 'Visual/Left': 3,
                'Visual/Right': 4, 'Smiley': 5, 'Button': 32}
    events_fname = op.join(data_path, 'MEG', 'sample',
                           'sample_audvis_trunc_raw-eve.fif')

    raw = mne.io.read_raw_fif(raw_fname)
    write_raw_bids(raw, bids_basename, output_path, events_data=events_fname,
                   event_id=event_id, overwrite=False)

    # Read the file back in to check that the data has come through cleanly.
    # Events and bad channel information was read through JSON sidecar files.
    raw2 = read_raw_bids(bids_basename + '_meg.fif', output_path)
    assert set(raw.info['bads']) == set(raw2.info['bads'])
    events, _ = mne.events_from_annotations(raw2)
    events2 = mne.read_events(events_fname)
    events2 = events2[events2[:, 2] != 0]
    assert_array_equal(events2[:, 0], events[:, 0])

    # check if write_raw_bids works when there is no stim channel
    raw.set_channel_types({raw.ch_names[i]: 'misc'
                           for i in
                           mne.pick_types(raw.info, stim=True, meg=False)})
    output_path = _TempDir()
    with pytest.warns(UserWarning, match='No events found or provided.'):
        write_raw_bids(raw, bids_basename, output_path, overwrite=False)

    _bids_validate(output_path)

    # write the same data but pretend it is empty room data:
    raw = mne.io.read_raw_fif(raw_fname)
    er_date = datetime.fromtimestamp(
        raw.info['meas_date'][0]).strftime('%Y%m%d')
    er_bids_basename = 'sub-emptyroom_ses-{0}_task-noise'.format(str(er_date))
    write_raw_bids(raw, er_bids_basename, output_path, overwrite=False)
    assert op.exists(op.join(
        output_path, 'sub-emptyroom', 'ses-{0}'.format(er_date), 'meg',
        'sub-emptyroom_ses-{0}_task-noise_meg.json'.format(er_date)))
    # test that an incorrect date raises an error.
    er_bids_basename_bad = 'sub-emptyroom_ses-19000101_task-noise'
    with pytest.raises(ValueError, match='Date provided'):
        write_raw_bids(raw, er_bids_basename_bad, output_path, overwrite=False)

    # give the raw object some fake participant data (potentially overwriting)
    raw = mne.io.read_raw_fif(raw_fname)
    raw.info['subject_info'] = {'his_id': subject_id2,
                                'birthday': (1993, 1, 26), 'sex': 1}
    write_raw_bids(raw, bids_basename, output_path, events_data=events_fname,
                   event_id=event_id, overwrite=True)
    # assert age of participant is correct
    participants_tsv = op.join(output_path, 'participants.tsv')
    data = _from_tsv(participants_tsv)
    assert data['age'][data['participant_id'].index('sub-01')] == '9'

    # try and write preloaded data
    raw = mne.io.read_raw_fif(raw_fname, preload=True)
    with pytest.raises(ValueError, match='preloaded'):
        write_raw_bids(raw, bids_basename, output_path,
                       events_data=events_fname, event_id=event_id,
                       overwrite=False)

    raw = mne.io.read_raw_fif(raw_fname)
    raw.anonymize()

    data_path2 = _TempDir()
    raw_fname2 = op.join(data_path2, 'sample_audvis_raw.fif')
    raw.save(raw_fname2)

    bids_basename2 = bids_basename.replace(subject_id, subject_id2)
    raw = mne.io.read_raw_fif(raw_fname2)
    bids_output_path = write_raw_bids(raw, bids_basename2, output_path,
                                      events_data=events_fname,
                                      event_id=event_id, overwrite=False)

    # check that the overwrite parameters work correctly for the participant
    # data
    # change the gender but don't force overwrite.
    raw.info['subject_info'] = {'his_id': subject_id2,
                                'birthday': (1994, 1, 26), 'sex': 2}
    with pytest.raises(FileExistsError, match="already exists"):  # noqa: F821
        write_raw_bids(raw, bids_basename2, output_path,
                       events_data=events_fname, event_id=event_id,
                       overwrite=False)
    # now force the overwrite
    write_raw_bids(raw, bids_basename2, output_path, events_data=events_fname,
                   event_id=event_id, overwrite=True)

    with pytest.raises(ValueError, match='raw_file must be'):
        write_raw_bids('blah', bids_basename, output_path)

    bids_basename2 = 'sub-01_ses-01_xyz-01_run-01'
    with pytest.raises(KeyError, match='Unexpected entity'):
        write_raw_bids(raw, bids_basename2, output_path)

    bids_basename2 = 'sub-01_run-01_task-auditory'
    with pytest.raises(ValueError, match='ordered correctly'):
        write_raw_bids(raw, bids_basename2, output_path, overwrite=True)

    del raw._filenames
    with pytest.raises(ValueError, match='raw.filenames is missing'):
        write_raw_bids(raw, bids_basename2, output_path)

    _bids_validate(output_path)

    assert op.exists(op.join(output_path, 'participants.tsv'))

    # asserting that single fif files do not include the part key
    files = glob(op.join(bids_output_path, 'sub-' + subject_id2,
                         'ses-' + subject_id2, 'meg', '*.fif'))
    for ii, FILE in enumerate(files):
        assert 'part' not in FILE
    assert ii < 1

    # check that split files have part key
    raw = mne.io.read_raw_fif(raw_fname)
    data_path3 = _TempDir()
    raw_fname3 = op.join(data_path3, 'sample_audvis_raw.fif')
    raw.save(raw_fname3, buffer_size_sec=1.0, split_size='10MB',
             split_naming='neuromag', overwrite=True)
    raw = mne.io.read_raw_fif(raw_fname3)
    subject_id3 = '03'
    bids_basename3 = bids_basename.replace(subject_id, subject_id3)
    bids_output_path = write_raw_bids(raw, bids_basename3, output_path,
                                      overwrite=False)
    files = glob(op.join(bids_output_path, 'sub-' + subject_id3,
                         'ses-' + subject_id3, 'meg', '*.fif'))
    for FILE in files:
        assert 'part' in FILE


def test_kit(_bids_validate):
    """Test functionality of the write_raw_bids conversion for KIT data."""
    output_path = _TempDir()
    data_path = op.join(base_path, 'kit', 'tests', 'data')
    raw_fname = op.join(data_path, 'test.sqd')
    events_fname = op.join(data_path, 'test-eve.txt')
    hpi_fname = op.join(data_path, 'test_mrk.sqd')
    hpi_pre_fname = op.join(data_path, 'test_mrk_pre.sqd')
    hpi_post_fname = op.join(data_path, 'test_mrk_post.sqd')
    electrode_fname = op.join(data_path, 'test_elp.txt')
    headshape_fname = op.join(data_path, 'test_hsp.txt')
    event_id = dict(cond=1)

    kit_bids_basename = bids_basename.replace('_acq-01', '')

    raw = mne.io.read_raw_kit(
        raw_fname, mrk=hpi_fname, elp=electrode_fname,
        hsp=headshape_fname)
    write_raw_bids(raw, kit_bids_basename, output_path,
                   events_data=events_fname,
                   event_id=event_id, overwrite=False)

    _bids_validate(output_path)
    assert op.exists(op.join(output_path, 'participants.tsv'))

    read_raw_bids(kit_bids_basename + '_meg.sqd', output_path)

    # ensure the channels file has no STI 014 channel:
    channels_tsv = make_bids_basename(
        subject=subject_id, session=session_id, task=task, run=run,
        suffix='channels.tsv',
        prefix=op.join(output_path, 'sub-01', 'ses-01', 'meg'))
    data = _from_tsv(channels_tsv)
    assert 'STI 014' not in data['name']

    # ensure the marker file is produced in the right place
    marker_fname = make_bids_basename(
        subject=subject_id, session=session_id, task=task, run=run,
        suffix='markers.sqd',
        prefix=op.join(output_path, 'sub-01', 'ses-01', 'meg'))
    assert op.exists(marker_fname)

    # test attempts at writing invalid event data
    event_data = np.loadtxt(events_fname)
    # make the data the wrong number of dimensions
    event_data_3d = np.atleast_3d(event_data)
    other_output_path = _TempDir()
    with pytest.raises(ValueError, match='two dimensions'):
        write_raw_bids(raw, bids_basename, other_output_path,
                       events_data=event_data_3d, event_id=event_id,
                       overwrite=True)
    # remove 3rd column
    event_data = event_data[:, :2]
    with pytest.raises(ValueError, match='second dimension'):
        write_raw_bids(raw, bids_basename, other_output_path,
                       events_data=event_data, event_id=event_id,
                       overwrite=True)
    # test correct naming of marker files
    raw = mne.io.read_raw_kit(
        raw_fname, mrk=[hpi_pre_fname, hpi_post_fname], elp=electrode_fname,
        hsp=headshape_fname)
    write_raw_bids(raw,
                   kit_bids_basename.replace('sub-01', 'sub-%s' % subject_id2),
                   output_path, events_data=events_fname, event_id=event_id,
                   overwrite=False)

    _bids_validate(output_path)
    # ensure the marker files are renamed correctly
    marker_fname = make_bids_basename(
        subject=subject_id2, session=session_id, task=task, run=run,
        suffix='markers.sqd', acquisition='pre',
        prefix=os.path.join(output_path, 'sub-02', 'ses-01', 'meg'))
    info = get_kit_info(marker_fname, False)[0]
    assert info['meas_date'] == get_kit_info(hpi_pre_fname,
                                             False)[0]['meas_date']
    marker_fname = marker_fname.replace('acq-pre', 'acq-post')
    info = get_kit_info(marker_fname, False)[0]
    assert info['meas_date'] == get_kit_info(hpi_post_fname,
                                             False)[0]['meas_date']

    # check that providing markers in the wrong order raises an error
    raw = mne.io.read_raw_kit(
        raw_fname, mrk=[hpi_post_fname, hpi_pre_fname], elp=electrode_fname,
        hsp=headshape_fname)
    with pytest.raises(ValueError, match='Markers'):
        write_raw_bids(
            raw,
            kit_bids_basename.replace('sub-01', 'sub-%s' % subject_id2),
            output_path, events_data=events_fname, event_id=event_id,
            overwrite=True)


def test_ctf(_bids_validate):
    """Test functionality of the write_raw_bids conversion for CTF data."""
    output_path = _TempDir()
    data_path = op.join(testing.data_path(download=False), 'CTF')
    raw_fname = op.join(data_path, 'testdata_ctf.ds')

    raw = mne.io.read_raw_ctf(raw_fname)
    with pytest.warns(UserWarning, match='No line frequency'):
        write_raw_bids(raw, bids_basename, output_path=output_path)

    _bids_validate(output_path)
    with pytest.warns(UserWarning, match='Did not find any events'):
        raw = read_raw_bids(bids_basename + '_meg.ds', output_path)

    # test to check that running again with overwrite == False raises an error
    with pytest.raises(FileExistsError, match="already exists"):  # noqa: F821
        write_raw_bids(raw, bids_basename, output_path=output_path)

    assert op.exists(op.join(output_path, 'participants.tsv'))


def test_bti(_bids_validate):
    """Test functionality of the write_raw_bids conversion for BTi data."""
    output_path = _TempDir()
    data_path = op.join(base_path, 'bti', 'tests', 'data')
    raw_fname = op.join(data_path, 'test_pdf_linux')
    config_fname = op.join(data_path, 'test_config_linux')
    headshape_fname = op.join(data_path, 'test_hs_linux')

    raw = mne.io.read_raw_bti(raw_fname, config_fname=config_fname,
                              head_shape_fname=headshape_fname)

    write_raw_bids(raw, bids_basename, output_path, verbose=True)

    assert op.exists(op.join(output_path, 'participants.tsv'))
    _bids_validate(output_path)

    raw = read_raw_bids(bids_basename + '_meg', output_path)


# XXX: vhdr test currently passes only on MNE master. Skip until next release.
# see: https://github.com/mne-tools/mne-python/pull/6558
@pytest.mark.skipif(LooseVersion(mne.__version__) < LooseVersion('0.19'),
                    reason="requires mne 0.19.dev0 or higher")
def test_vhdr(_bids_validate):
    """Test write_raw_bids conversion for BrainVision data."""
    output_path = _TempDir()
    data_path = op.join(base_path, 'brainvision', 'tests', 'data')
    raw_fname = op.join(data_path, 'test.vhdr')

    raw = mne.io.read_raw_brainvision(raw_fname)

    # inject a bad channel
    assert not raw.info['bads']
    injected_bad = ['FP1']
    raw.info['bads'] = injected_bad

    # write with injected bad channels
    write_raw_bids(raw, bids_basename_minimal, output_path, overwrite=False)
    _bids_validate(output_path)

    # read and also get the bad channels
    raw = read_raw_bids(bids_basename_minimal + '_eeg.vhdr', output_path)

    # Check that injected bad channel shows up in raw after reading
    np.testing.assert_array_equal(np.asarray(raw.info['bads']),
                                  np.asarray(injected_bad))

    # Test that correct channel units are written ... and that bad channel
    # is in channels.tsv
    channels_tsv_name = op.join(output_path, 'sub-{}'.format(subject_id),
                                'eeg', bids_basename_minimal + '_channels.tsv')
    data = _from_tsv(channels_tsv_name)
    assert data['units'][data['name'].index('FP1')] == 'µV'
    assert data['units'][data['name'].index('CP5')] == 'n/a'
    assert data['status'][data['name'].index(injected_bad[0])] == 'bad'

    # check events.tsv is written
    events_tsv_fname = channels_tsv_name.replace('channels', 'events')
    assert op.exists(events_tsv_fname)

    # create another bids folder with the overwrite command and check
    # no files are in the folder
    data_path = make_bids_folders(subject=subject_id, kind='eeg',
                                  output_path=output_path, overwrite=True)
    assert len([f for f in os.listdir(data_path) if op.isfile(f)]) == 0

    # Also cover iEEG
    # We use the same data and pretend that eeg channels are ecog
    raw = mne.io.read_raw_brainvision(raw_fname)
    raw.set_channel_types({raw.ch_names[i]: 'ecog'
                           for i in mne.pick_types(raw.info, eeg=True)})
    output_path = _TempDir()
    write_raw_bids(raw, bids_basename, output_path, overwrite=False)
    _bids_validate(output_path)


def test_edf(_bids_validate):
    """Test write_raw_bids conversion for European Data Format data."""
    output_path = _TempDir()
    data_path = op.join(testing.data_path(), 'EDF')
    raw_fname = op.join(data_path, 'test_reduced.edf')

    raw = mne.io.read_raw_edf(raw_fname, preload=True)
    # XXX: hack that should be fixed later. Annotation reading is
    # broken for this file with preload=False and read_annotations_edf
    raw.preload = False

    raw.rename_channels({raw.info['ch_names'][0]: 'EOG'})
    raw.info['chs'][0]['coil_type'] = FIFF.FIFFV_COIL_EEG_BIPOLAR
    raw.rename_channels({raw.info['ch_names'][1]: 'EMG'})
    raw.set_channel_types({'EMG': 'emg'})

    write_raw_bids(raw, bids_basename, output_path)

    # Reading the file back should raise an error, because we renamed channels
    # in `raw` and used that information to write a channels.tsv. Yet, we
    # saved the unchanged `raw` in the BIDS folder, so channels in the TSV and
    # in raw clash
    with pytest.raises(RuntimeError, match='Channels do not correspond'):
        read_raw_bids(bids_basename + '_eeg.edf', output_path)

    bids_fname = bids_basename.replace('run-01', 'run-%s' % run2)
    write_raw_bids(raw, bids_fname, output_path, overwrite=True)
    _bids_validate(output_path)

    # ensure there is an EMG channel in the channels.tsv:
    channels_tsv = make_bids_basename(
        subject=subject_id, session=session_id, task=task, run=run,
        suffix='channels.tsv', acquisition=acq,
        prefix=op.join(output_path, 'sub-01', 'ses-01', 'eeg'))
    data = _from_tsv(channels_tsv)
    assert 'ElectroMyoGram' in data['description']

    # check that the scans list contains two scans
    scans_tsv = make_bids_basename(
        subject=subject_id, session=session_id, suffix='scans.tsv',
        prefix=op.join(output_path, 'sub-01', 'ses-01'))
    data = _from_tsv(scans_tsv)
    assert len(list(data.values())[0]) == 2

    # Also cover iEEG
    # We use the same data and pretend that eeg channels are ecog
    raw.set_channel_types({raw.ch_names[i]: 'ecog'
                           for i in mne.pick_types(raw.info, eeg=True)})
    output_path = _TempDir()
    write_raw_bids(raw, bids_basename, output_path)
    _bids_validate(output_path)


def test_bdf(_bids_validate):
    """Test write_raw_bids conversion for Biosemi data."""
    output_path = _TempDir()
    data_path = op.join(base_path, 'edf', 'tests', 'data')
    raw_fname = op.join(data_path, 'test.bdf')

    raw = mne.io.read_raw_bdf(raw_fname)
    with pytest.warns(UserWarning, match='No line frequency found'):
        write_raw_bids(raw, bids_basename, output_path, overwrite=False)
    _bids_validate(output_path)

    # Test also the reading of channel types from channels.tsv
    # the first channel in the raw data is not MISC right now
    test_ch_idx = 0
    assert coil_type(raw.info, test_ch_idx) != 'misc'

    # we will change the channel type to MISC and overwrite the channels file
    bids_fname = bids_basename + '_eeg.bdf'
    channels_fname = _find_matching_sidecar(bids_fname, output_path,
                                            'channels.tsv')
    channels_dict = _from_tsv(channels_fname)
    channels_dict['type'][test_ch_idx] = 'MISC'
    _to_tsv(channels_dict, channels_fname)

    # Now read the raw data back from BIDS, with the tampered TSV, to show
    # that the channels.tsv truly influences how read_raw_bids sets ch_types
    # in the raw data object
    raw = read_raw_bids(bids_fname, output_path)
    assert coil_type(raw.info, test_ch_idx) == 'misc'

    # Test cropped assertion error
    raw = mne.io.read_raw_bdf(raw_fname)
    raw.crop(0, raw.times[-2])
    with pytest.raises(AssertionError, match='cropped'):
        write_raw_bids(raw, bids_basename, output_path)


def test_set(_bids_validate):
    """Test write_raw_bids conversion for EEGLAB data."""
    # standalone .set file
    output_path = _TempDir()
    data_path = op.join(testing.data_path(), 'EEGLAB')

    # .set with associated .fdt
    output_path = _TempDir()
    data_path = op.join(testing.data_path(), 'EEGLAB')
    raw_fname = op.join(data_path, 'test_raw.set')

    raw = mne.io.read_raw_eeglab(raw_fname)

    # embedded - test mne-version assertion
    tmp_version = mne.__version__
    mne.__version__ = '0.16'
    with pytest.raises(ValueError, match='Your version of MNE is too old.'):
        write_raw_bids(raw, bids_basename, output_path)
    mne.__version__ = tmp_version

    # proceed with the actual test for EEGLAB data
    write_raw_bids(raw, bids_basename, output_path, overwrite=False)
    read_raw_bids(bids_basename + '_eeg.set', output_path)

    with pytest.raises(FileExistsError, match="already exists"):  # noqa: F821
        write_raw_bids(raw, bids_basename, output_path=output_path,
                       overwrite=False)
    _bids_validate(output_path)

    # check events.tsv is written
    # XXX: only from 0.18 onwards because events_from_annotations
    # is broken for earlier versions
    events_tsv_fname = op.join(output_path, 'sub-' + subject_id,
                               'ses-' + session_id, 'eeg',
                               bids_basename + '_events.tsv')
    if check_version('mne', '0.18'):
        assert op.exists(events_tsv_fname)

    # Also cover iEEG
    # We use the same data and pretend that eeg channels are ecog
    raw.set_channel_types({raw.ch_names[i]: 'ecog'
                           for i in mne.pick_types(raw.info, eeg=True)})
    output_path = _TempDir()
    write_raw_bids(raw, bids_basename, output_path)
    _bids_validate(output_path)


@requires_nibabel()
def test_write_anat(_bids_validate):
    """Test writing anatomical data."""
    # Get the MNE testing sample data
    output_path = _TempDir()
    data_path = testing.data_path()
    raw_fname = op.join(data_path, 'MEG', 'sample',
                        'sample_audvis_trunc_raw.fif')

    event_id = {'Auditory/Left': 1, 'Auditory/Right': 2, 'Visual/Left': 3,
                'Visual/Right': 4, 'Smiley': 5, 'Button': 32}
    events_fname = op.join(data_path, 'MEG', 'sample',
                           'sample_audvis_trunc_raw-eve.fif')

    raw = mne.io.read_raw_fif(raw_fname)
    write_raw_bids(raw, bids_basename, output_path, events_data=events_fname,
                   event_id=event_id, overwrite=False)

    # Write some MRI data and supply a `trans`
    trans_fname = raw_fname.replace('_raw.fif', '-trans.fif')
    trans = mne.read_trans(trans_fname)

    # Get the T1 weighted MRI data file
    # Needs to be converted to Nifti because we only have mgh in our test base
    t1w_mgh = op.join(data_path, 'subjects', 'sample', 'mri', 'T1.mgz')

    anat_dir = write_anat(output_path, subject_id, t1w_mgh, session_id, acq,
                          raw=raw, trans=trans, verbose=True)
    _bids_validate(output_path)

    # Validate that files are as expected
    t1w_json_path = op.join(anat_dir, 'sub-01_ses-01_acq-01_T1w.json')
    assert op.exists(t1w_json_path)
    assert op.exists(op.join(anat_dir, 'sub-01_ses-01_acq-01_T1w.nii.gz'))
    with open(t1w_json_path, 'r') as f:
        t1w_json = json.load(f)
    print(t1w_json)
    # We only should have AnatomicalLandmarkCoordinates as key
    np.testing.assert_array_equal(list(t1w_json.keys()),
                                  ['AnatomicalLandmarkCoordinates'])
    # And within AnatomicalLandmarkCoordinates only LPA, NAS, RPA in that order
    anat_dict = t1w_json['AnatomicalLandmarkCoordinates']
    point_list = ['LPA', 'NAS', 'RPA']
    np.testing.assert_array_equal(list(anat_dict.keys()),
                                  point_list)
    # test the actual values of the voxels (no floating points)
    for i, point in enumerate([(66, 51, 46), (41, 32, 74), (17, 53, 47)]):
        coords = anat_dict[point_list[i]]
        np.testing.assert_array_equal(np.asarray(coords, dtype=int),
                                      point)

    # BONUS: test also that we can find the matching sidecar
        side_fname = _find_matching_sidecar('sub-01_ses-01_acq-01_T1w.nii.gz',
                                            output_path, 'T1w.json')
        assert op.split(side_fname)[-1] == 'sub-01_ses-01_acq-01_T1w.json'

    # Now try some anat writing that will fail
    # We already have some MRI data there
    with pytest.raises(IOError, match='`overwrite` is set to False'):
        write_anat(output_path, subject_id, t1w_mgh, session_id, acq,
                   raw=raw, trans=trans, verbose=True, overwrite=False)

    # pass some invalid type as T1 MRI
    with pytest.raises(ValueError, match='must be a path to a T1 weighted'):
        write_anat(output_path, subject_id, 9999999999999, session_id, raw=raw,
                   trans=trans, verbose=True, overwrite=True)

    # Return without writing sidecar
    sh.rmtree(anat_dir)
    write_anat(output_path, subject_id, t1w_mgh, session_id)
    # Assert that we truly cannot find a sidecar
    with pytest.raises(RuntimeError, match='Did not find any'):
        _find_matching_sidecar('sub-01_ses-01_acq-01_T1w.nii.gz',
                               output_path, 'T1w.json')

    # trans has a wrong type
    wrong_type = 1
    match = 'transform type {} not known, must be'.format(type(wrong_type))
    with pytest.raises(ValueError, match=match):
        write_anat(output_path, subject_id, t1w_mgh, session_id, raw=raw,
                   trans=wrong_type, verbose=True, overwrite=True)

    # trans is a str, but file does not exist
    wrong_fname = 'not_a_trans'
    match = 'trans file "{}" not found'.format(wrong_fname)
    with pytest.raises(IOError, match=match):
        write_anat(output_path, subject_id, t1w_mgh, session_id, raw=raw,
                   trans=wrong_fname, verbose=True, overwrite=True)

    # However, reading trans if it is a string pointing to trans is fine
    write_anat(output_path, subject_id, t1w_mgh, session_id, raw=raw,
               trans=trans_fname, verbose=True, overwrite=True)

    # Writing without a session does NOT yield "ses-None" anywhere
    anat_dir2 = write_anat(output_path, subject_id, t1w_mgh, None)
    assert 'ses-None' not in anat_dir2
    assert op.exists(op.join(anat_dir2, 'sub-01_T1w.nii.gz'))

    # specify trans but not raw
    with pytest.raises(ValueError, match='must be specified if `trans`'):
        write_anat(output_path, subject_id, t1w_mgh, session_id, raw=None,
                   trans=trans, verbose=True, overwrite=True)
