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
Module containing time- and sky- coincidence search functions.
"""
__author__ = "Alex Urban <alexander.urban@ligo.org>"


# Imports.
import json
import os
import re
import sys

import healpy as hp
import numpy as np

from .gracedb_events import SE, ExtTrig
from ligo.gracedb.rest import GraceDb, DEFAULT_SERVICE_URL


#########################################################
# Functions implementing the actual coincidence search. #
#########################################################

def query(event_type, gpstime, tl, th, gracedb=None, group=None,
          pipelines=None):
    """ Query for coincident events of type event_type occurring within a
        window of [tl, th] seconds around gpstime. """

    # Perform a sanity check on the time window.
    if tl >= th:
        sys.stderr.write("ERROR: The time window [tl, th] must have tl < th.")
        sys.exit(1)

    # Initiate correct instance of GraceDb.
    if gracedb is None:
        gracedb = GraceDb(DEFAULT_SERVICE_URL)

    # Perform the GraceDB query.
    start, end = gpstime + tl, gpstime + th

    if event_type != 'Superevent':  # Searching for external events
        arg = '{0} {1} .. {2}'.format(event_type, start, end)
        # Return list of graceids of coincident events.
        results = list(gracedb.events(arg))
        if pipelines:
            results = [event for event in results if event['pipeline']
                       in pipelines]
        return results

    else:  # Searching for superevents
        arg = '{0} .. {1}'.format(start, end)
        # Return list of coincident superevent_ids.
        results = list(gracedb.superevents(arg))
        if group:
            results = [superevent for superevent in results if gracedb.event(
                       superevent['preferred_event']).json()['group'] == group]
        return results


def search(event, tl, th, gracedb=None, group=None, pipelines=None):
    """ Perform a search for neighbors coincident in time within
        a window [tl, th] seconds around an event. Uploads the
        results to the selected gracedb server. """

    # Identify neighbor types with their graceid strings.
    types = {'G': 'GW', 'E': 'External event', 'S': 'Superevent',
             'T': 'Test'}
    groups = {'G': 'CBC Burst', 'E': 'External', 'S': 'Superevent'}

    # Initiate correct instance of GraceDb.
    if gracedb is None:
        gracedb = GraceDb(DEFAULT_SERVICE_URL)

    # Grab any and all neighboring events.
    # Filter results depending on the group if specified.
    neighbors = query(groups[event.neighbor_type], event.gpstime, tl, th,
                      gracedb=gracedb, group=group, pipelines=pipelines)

    # If no neighbors, report a null result.
    if not neighbors:
        if group:
            message = "RAVEN: No %s %s candidates in window [%+d, %+d] \
                seconds" % (types[event.neighbor_type], group, tl, th)
        elif pipelines:
            message = "RAVEN: No %s %s candidates in window [%+d, %+d] \
                seconds" % (types[event.neighbor_type], pipelines, tl, th)
        else:
            message = "RAVEN: No %s candidates in window [%+d, %+d] \
                seconds" % (types[event.neighbor_type], tl, th)
        gracedb.writeLog(event.graceid, message, tag_name=["ext_coinc"])

    # If neighbors are found, report each of them.
    else:
        for neighbor in neighbors:
            if event.neighbor_type == 'S':
                # search called on a external event
                deltat = event.gpstime - neighbor['t_0']
                superid = neighbor['superevent_id']
                extid = event.graceid
                tl_m, th_m = tl, th
                relat_word = ['before', 'after']
            else:
                # search called on a superevent
                deltat = event.gpstime - neighbor['gpstime']
                superid = event.graceid
                extid = neighbor['graceid']
                tl_m, th_m = -th, -tl
                relat_word = ['after', 'before']
            if deltat < 0:
                relat_word.reverse()
                deltat = abs(deltat)
            selink = 'superevents/'
            extlink = 'events/'
            gracedb_url = re.findall('(.*)api/', gracedb._service_url)[0]

            # Send message to external event
            if group:
                message1 = "RAVEN: {0} {1} candidate <a href='{2}{3}".format(
                               types['S'], group, gracedb_url, selink)
            else:
                message1 = "RAVEN: {0} candidate <a href='{1}{2}".format(
                           types['S'], gracedb_url, selink)
            message1 += "%s'>%s</a> within [%+d, %+d] seconds" % (
                            superid, superid,
                            tl_m, th_m)
            message1 += ", about {0:.3f} second(s) {1} {2}".format(
                            float(deltat),
                            relat_word[0],
                            types['E'])
            gracedb.writeLog(extid, message1, tag_name=["ext_coinc"])

            # Send message to superevent
            if pipelines:
                message2 = "RAVEN: {0} {1} <a href='{2}{3}".format(
                    types['E'], pipelines, gracedb_url, extlink)
            else:
                message2 = "RAVEN: {0} <a href='{1}{2}".format(
                               types['E'], gracedb_url, extlink)
            message2 += "%s'>%s</a> within [%+d, %+d] seconds" % (
                            extid, extid, -th_m, -tl_m)
            message2 += ", about {0:.3f} second(s) {1} {2}".format(
                            float(deltat),
                            relat_word[1],
                            types['S'])
            gracedb.writeLog(superid, message2, tag_name=["ext_coinc"])

    # Return search results.
    return neighbors


def skymap_overlap_integral(se_skymap, exttrig_skymap):
    """ Calculate the sky map overlap integral of the two sky maps. """

    nside_s = hp.npix2nside(len(se_skymap))
    nside_e = hp.npix2nside(len(exttrig_skymap))
    if nside_s > nside_e:
        exttrig_skymap = hp.ud_grade(exttrig_skymap, nside_out=nside_s)
    else:
        se_skymap = hp.ud_grade(se_skymap, nside_out=nside_e)
    se_norm = se_skymap.sum()
    exttrig_norm = exttrig_skymap.sum()
    if se_norm > 0 and exttrig_norm > 0:
        skymap_overlap_integral = (
            np.dot(se_skymap, exttrig_skymap)
            / se_norm / exttrig_norm
            * len(se_skymap))
        return skymap_overlap_integral
    else:
        message = ("RAVEN: ERROR: At least one sky map has a probability "
                   "density that sums to zero or less.")
        return message


def coinc_far(se_id, exttrig_id, tl, th, grb_search='GRB', se_fitsfile=None,
              ext_fitsfile='glg_healpix_all_bn_v00.fit', incl_sky=False,
              gracedb=None):
    """ Calculate the significance of a gravitational wave candidate with the
        addition of an external astrophyical counterpart in terms of a
        coincidence false alarm rate. This includes a temporal and a
        space-time type. """

    # Create the SE and ExtTrig objects based on string inputs.
    se = SE(se_id, fitsfile=se_fitsfile, gracedb=gracedb)
    exttrig = ExtTrig(exttrig_id, fitsfile=ext_fitsfile, gracedb=gracedb)

    # Is the GW superevent candidate's FAR sensible?
    if not se.far:
        message = ("RAVEN: WARNING: This GW superevent candidate's FAR is a "
                   " NoneType object.")
        return message

    # Chooses the GCN rate based on search
    if grb_search == 'GRB':
        # The combined rate of independent GRB discovery by Swift and Fermi
        # Updated based on an analysis done by Peter Shawhan
        # https://dcc.ligo.org/cgi-bin/private/DocDB/ShowDocument?docid=T1900297&version=
        gcn_rate = 547. / (365. * 24. * 60. * 60.)

    elif grb_search == 'SubGRB':
        # Rate of subthreshold GRBs (rate of threshold plus rate of
        # subthreshold). Introduced based on an analysis done by Peter Shawhan
        # https://dcc.ligo.org/cgi-bin/private/DocDB/ShowDocument?docid=T1900297&version=
        gcn_rate = 612. / (365. * 24. * 60. * 60.)
    else:
        message = ("RAVEN: WARNING: Invalid search. RAVEN only considers "
                   "'GRB' and 'SubGRB'.")
        return message

    # First, proceed with only time coincidence.
    temporal_far = (th - tl) * gcn_rate * se.far

    # Include sky coincidence if desired.
    if incl_sky:
        se_skymap = se.sky_map
        exttrig_skymap = exttrig.sky_map()
        skymap_overlap = skymap_overlap_integral(se_skymap, exttrig_skymap)
        if isinstance(skymap_overlap, str):
            return skymap_overlap
        try:
            spatiotemporal_far = temporal_far / skymap_overlap
        except ZeroDivisionError:
            message = ("RAVEN: WARNING: Sky maps minimally overlap. "
                       "Sky map overlap integral is {0:.2e}. "
                       "There is strong evidence against these events being "
                       "coincident.").format(skymap_overlap)
            return message
    else:
        spatiotemporal_far = None

    return {"temporal_coinc_far": temporal_far,
            "spatiotemporal_coinc_far": spatiotemporal_far,
            "preferred_event": se.preferred_event,
            "external_event": exttrig.graceid}


def calc_signif_gracedb(se_id, exttrig_id, tl, th, grb_search='GRB',
                        se_fitsfile=None,
                        ext_fitsfile='glg_healpix_all_bn_v00.fit',
                        incl_sky=False, gracedb=None):
    """ Calculates and uploads the coincidence false alarm rate
        of the given superevent to the selected gracedb server. """

    # Create the SE and ExtTrig objects based on string inputs.
    se = SE(se_id, fitsfile=se_fitsfile, gracedb=gracedb)
    exttrig = ExtTrig(exttrig_id, fitsfile=ext_fitsfile, gracedb=gracedb)

    # Create coincidence_far.json
    coinc_far_output = coinc_far(se_id, exttrig_id, tl, th,
                                 grb_search=grb_search,
                                 se_fitsfile=se_fitsfile,
                                 ext_fitsfile=ext_fitsfile,
                                 incl_sky=incl_sky, gracedb=gracedb)
    if isinstance(coinc_far_output, str):
        se.submit_gracedb_log(coinc_far_output, tag_name=["ext_coinc"])
        return
    coincidence_far = json.dumps(coinc_far_output)

    gracedb_events_url = re.findall('(.*)api/', se.gracedb._service_url)[0]
    link1 = 'events/'
    link2 = 'superevents/'

    with open('coincidence_far.json', 'w+') as fp:
        fp.write(coincidence_far)
        fp.flush()
        fp.seek(0)
        message = ("RAVEN: Computed coincident FAR(s) in Hz with external "
                   "trigger <a href='{0}").format(gracedb_events_url + link1)
        message += "{0}'>{1}</a>".format(exttrig.graceid, exttrig.graceid)
        gracedb.writeLog(se_id, message, 'coincidence_far.json',
                         coincidence_far, tag_name=["ext_coinc"])

        message = ("RAVEN: Computed coincident FAR(s) in Hz with superevent "
                   "<a href='{0}").format(gracedb_events_url + link2)
        message += "{0}'>{1}</a>".format(se.graceid, se.graceid)
        gracedb.writeLog(exttrig_id, message, 'coincidence_far.json',
                         coincidence_far, tag_name=["ext_coinc"])
    os.remove('coincidence_far.json')

    return
