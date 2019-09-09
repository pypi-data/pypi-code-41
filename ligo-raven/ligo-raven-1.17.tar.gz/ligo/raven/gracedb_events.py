# Project Librarian: Alex Urban
#              Graduate Student
#              UW-Milwaukee Department of Physics
#              Center for Gravitation & Cosmology
#              <alexander.urban@ligo.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Module to define functions and attributes corresponding
to both gravitational-wave candidates and external triggers.
"""
__author__ = "Alex Urban <alexander.urban@ligo.org>"


# Imports.
import healpy as hp
import tempfile

from ligo.gracedb.rest import GraceDb, DEFAULT_SERVICE_URL
from ligo.skymap.io import fits


#######################################################
# Define object classes for GWs and external triggers #
#######################################################

class ExtTrig(object):
    """ Instance of an external trigger event (i.e. gamma-ray burst) """
    def __init__(self, graceid, gracedb=None, search_for_gw_triggers=False,
                 fitsfile='glg_healpix_all_bn_v00.fit'):
        self.graceid = graceid
        self.fits = fitsfile  # name of fits file
        if search_for_gw_triggers:
            self.neighbor_type = 'G'
        else:
            self.neighbor_type = 'S'  # by default, look for superevents

        # Initiate correct instance of GraceDb.
        if gracedb is None:
            self.gracedb = GraceDb(DEFAULT_SERVICE_URL)
        else:
            self.gracedb = gracedb

        # Inherit other properties from GraceDb.
        event = self.gracedb.event(graceid).json()
        self.inst = event['pipeline']  # instrument that detected the event
        self.gpstime = float(event['gpstime'])  # event time in GPS seconds

    def submit_gracedb_log(self, message, filename=None, filecontents=None,
                           tag_name=[]):
        """ Wrapper for gracedb.writeLog() for this event """
        if filecontents is not None:
            self.gracedb.writeLog(self.graceid, message, filename,
                                  filecontents, tag_name=tag_name)
        elif filename is not None:
            self.gracedb.writeLog(self.graceid, message, filename,
                                  tag_name=tag_name)
        else:
            self.gracedb.writeLog(self.graceid, message, tag_name=tag_name)

    def sky_map(self):
        """ Returns a numpy array equivalent to the one that would get written
            to a FITS file for this event, with resolution nside """
        kwargs = {'mode': 'w+b'}
        with tempfile.NamedTemporaryFile(**kwargs) as skymapfile:
            skymap = self.gracedb.files(self.graceid, self.fits,
                                        raw=True).read()
            skymapfile.write(skymap)
            skymapfile.flush()
            skymapfile.seek(0)
            self.skymap = hp.read_map(skymapfile.name)
        return self.skymap

    def write_fits(self, nside, publish=False):
        """ Write a FITS file containing the sky map for this event, with
            resolution nside, and upload to GraceDB if the 'publish' flag is
            passed """

        # Write to a .fits file.
        fits.write_sky_map(self.fits, self.sky_map(nside), objid=self.graceid,
                           gps_time=self.gpstime)

        # Publish to GraceDB if the 'publish' flag is passed.
        if publish:
            self.submit_gracedb_log(self.graceid, "RAVEN: Uploaded sky map",
                                    filename=self.fits, tag_name="sky_loc")


class GW(object):
    """ Instance of a gravitational-wave candidate event """
    def __init__(self, graceid, fitsfile=None, gracedb=None):
        self.graceid = graceid  # graceid of GW candidate
        self.neighbor_type = 'E'
        self.fits = fitsfile  # name of fits file

        if self.fits:
            self.sky_map = fits.read_sky_map(self.fits)

        # Initiate correct instance of GraceDb.
        if gracedb is None:
            self.gracedb = GraceDb(DEFAULT_SERVICE_URL)
        else:
            self.gracedb = gracedb

        # Inherit the FAR and event time from GraceDb.
        event = self.gracedb.event(self.graceid).json()
        self.far = event['far']
        self.gpstime = float(event['gpstime'])

    def submit_gracedb_log(self, message, tag_name=None):
        """ wrapper for gracedb.writeLog() for this event """
        if tag_name is None:
            tag_name = []
        self.gracedb.writeLog(self.graceid, message, tag_name=tag_name)


class SE(object):
    """Instance of a superevent"""
    def __init__(self, superevent_id, fitsfile=None, gracedb=None):
        self.graceid = superevent_id
        self.neighbor_type = 'E'
        self.fits = fitsfile  # name of fits file

        if gracedb is None:
            self.gracedb = GraceDb(DEFAULT_SERVICE_URL)
        else:
            self.gracedb = gracedb

        # Inherit the FAR and event time of the preferred event from GraceDb.
        superevent = self.gracedb.superevent(superevent_id).json()
        self.preferred_event = superevent['preferred_event']
        self.far = superevent['far']
        self.gpstime = superevent['t_0']

        if self.fits:
            # self.sky_map = fits.read_sky_map( self.fits )
            kwargs = {'mode': 'w+b'}
            with tempfile.NamedTemporaryFile(**kwargs) as skymapfile:
                skymap = self.gracedb.files(self.graceid,
                                            self.fits, raw=True).read()
                skymapfile.write(skymap)
                skymapfile.flush()
                skymapfile.seek(0)
                skymap = fits.read_sky_map(skymapfile.name, moc=False)[0]
                self.sky_map = skymap

    def submit_gracedb_log(self, message, filename=None, filecontents=None,
                           tag_name=[]):
        """ Wrapper for gracedb.writeLog() for this event """
        if filecontents is not None:
            self.gracedb.writeLog(self.graceid, message, filename,
                                  filecontents, tag_name=tag_name)
        elif filename is not None:
            self.gracedb.writeLog(self.graceid, message, filename,
                                  tag_name=tag_name)
        else:
            self.gracedb.writeLog(self.graceid, message, tag_name=tag_name)
