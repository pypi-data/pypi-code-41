"""
PyMBS is a Python library for use in modeling Mortgage-Backed Securities.
Copyright (C) 2019  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com
"""

import pytest

from pymbs.api import NotFoundError
from pymbs.enums import iTunesESrA


def test_get_track_raises(app):
    """get_track should raise an exception when track can't be found.

    The calls to app.get_playlist() and app.get_tracks() is what
    distinguishes this test as a Functional test. For the purposes of
    this test, we are assuming that theses methods return a valid
    iTunes objects.

    The target method under test here is app.get_track()
    """
    requested_playlist = 'Music'
    playlist = app.get_playlist(requested_playlist)
    collection = app.get_tracks(playlist)
    requested_track = "Weekend At Bernie's XLII"

    with pytest.raises(NotFoundError):
        app.get_track(collection, requested_track)


def test_track_in(app):
    requested_playlist = 'Music'
    playlist = app.get_playlist(requested_playlist)
    collection = app.get_tracks(playlist)
    requested_track = "A Salty Dog"

    track = app.get_track(collection, requested_track)
    assert track.name() == requested_track


def test_search_track(app):
    playlist = 'Music'
    search_text = "Big Yellow Taxi"
    constraint = iTunesESrA.SONGS

    results = app.search(playlist, search_text, constraint)

    for track in results:
        print(track.name())

    assert len(results) > 0
