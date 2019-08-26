# Copyright (C) 2019  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from celery import current_app as app

from swh.loader.npm.loader import NpmLoader


@app.task(name=__name__ + '.LoadNpm')
def load_npm(package_name, package_url=None, package_metadata_url=None):
    return NpmLoader().load(package_name, package_url, package_metadata_url)
