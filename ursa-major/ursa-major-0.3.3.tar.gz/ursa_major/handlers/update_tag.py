# -*- coding: utf-8 -*-
# Copyright (c) 2019  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>
#            Qixiang Wan <qwan@redhat.com>

from ursa_major import MBS_BUILD_STATES
from ursa_major.handlers.base import BaseHandler
from ursa_major.logger import log


class UpdateTagHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super(UpdateTagHandler, self).__init__(*args, **kwargs)
        self.dry_run = False
        self.wait_regen_repo = False
        self.inheritance_changed = False

    def run(self):
        self.debug = self.args.debug
        self.dry_run = self.args.dry_run
        self.wait_regen_repo = self.args.wait_regen_repo

        self.tag = self.args.tag
        self.tag_config_file = self.args.tag_config_file
        self.load_tag_config()

        if self.tag not in self.tag_config.keys():
            raise RuntimeError("Tag '%s' is not found in tag config file %s" % (self.tag,
                               self.tag_config_file))

        self.connect_koji(dry_run=self.dry_run)
        self.connect_mbs()

        self.tag_info = self.koji.get_tag(self.tag)
        if self.tag_info is None:
            raise RuntimeError("Tag '%s' is not found in koji (profile: %s)" % (self.tag,
                               self.koji.profile))

        modules = self.tag_config.get(self.tag).get('modules', {})
        if not modules:
            log.warning("No module specified for tag '%s' in tag config file", self.tag)
            return

        inheritance = self.koji.get_inheritance_data(self.tag)

        # convert inheritance list to dict for convenience
        # dict key is tag name and value is the inheritance data of that tag
        inheritance_dict = {}
        for tag in inheritance:
            inheritance_dict[tag['name']] = tag

        # for each module in config:
        # 1. check whether there is any ready build exists in MBS
        # 2. check whether the build tag found in step #1 is in inheritance data
        #    already and with same priority, if it is in inheritance but with
        #    different priority, update priority
        # 3. if build tag is not inheritance, add this tag into inheritance
        # 4. check whether there is any old build tags for this module (name+stream)
        #    exist in inheritance, if true, remove these tags from inheritance
        for module in modules:
            log.debug("Processing module in config: \n%s", str(module))
            module_name = module.get('name')
            module_stream = module.get('stream')
            module_priority = module.get('priority')
            module_requires = module.get('requires', None)
            module_buildrequires = module.get('buildrequires', None)

            latest_build_tag = None
            # find out the latest ready module for this config from MBS
            ready_modules = self.mbs.get_modules(
                buildrequires=module_buildrequires,
                requires=module_requires,
                name=module_name,
                stream=module_stream,
                state=MBS_BUILD_STATES['ready'],
                page=1)  # we only need the default first page items
            if ready_modules:
                latest_build_tag = ready_modules[0]['koji_tag']

            if latest_build_tag is None:
                log.warning("There is no ready build found for %s, skipping", str(module))
                continue

            has_latest_tag = latest_build_tag in inheritance_dict
            same_priority = False
            if has_latest_tag:
                same_priority = inheritance_dict[latest_build_tag]['priority'] == module_priority

            if has_latest_tag and same_priority:
                log.info("Tag '%s' is in inheritance data of %s with same priority, skipping",
                         latest_build_tag, self.tag)
                continue

            if has_latest_tag and not same_priority:
                log.info("Tag '%s' is in inhertiance data of %s but has different priority, "
                         "will update inheritance data with new priority",
                         latest_build_tag, self.tag)
                # update with new priority value
                inheritance_dict[latest_build_tag]['priority'] = module_priority
                self.inheritance_changed = True
                continue

            # after check, the latest build tag is not in inheritance, we'll add this
            # tag to inheritance
            latest_tag_info = self.koji.get_tag(latest_build_tag)
            if latest_tag_info is None:
                raise RuntimeError("Tag '%s' is not found in koji (profile: %s)" %
                                   (latest_build_tag, self.koji.profile))

            # this is inheritance data for the latest module build we're going to add
            module_tag_data = {}
            module_tag_data['child_id'] = self.tag_info['id']
            module_tag_data['parent_id'] = latest_tag_info.get('id')
            module_tag_data['name'] = latest_tag_info.get('name')
            module_tag_data['priority'] = module_priority
            module_tag_data['maxdepth'] = module.get('maxdepth', None)
            module_tag_data['intransitive'] = module.get('intransitive', False)
            module_tag_data['noconfig'] = module.get('noconfig', False)
            module_tag_data['pkg_filter'] = module.get('pkg_filter', '')

            # check any old module tag exist in inheritance, for each
            # name + stream combination, there is up to 1 tag can exists
            # in inheritance data. Remove all old tags.
            modules_with_name_stream = self.mbs.get_modules(
                name=module_name,
                stream=module_stream,
                state=[MBS_BUILD_STATES['ready'], MBS_BUILD_STATES['garbage']])

            old_build_tags = [m['koji_tag'] for m in modules_with_name_stream]

            inheritance_old_tags = set(old_build_tags) & set(inheritance_dict.keys())

            # add new inheritance data for this module build, update the inheritance
            # after checking the old tags in inheritance
            log.info("Adding tag '%s' to inheritance data", latest_build_tag)
            inheritance_dict[latest_build_tag] = module_tag_data
            self.inheritance_changed = True

            if len(inheritance_old_tags) == 0:
                # there is no old tag found for this module, do nothing
                continue

            if len(inheritance_old_tags) > 0:
                # found old tag(s) of this NAME:STREAM in inheritance, remove them
                for old_tag in inheritance_old_tags:
                    log.info("Removing tag '%s' from inheritance data", old_tag)
                    inheritance_dict[old_tag]['delete link'] = True

        # modules loop finished, now we have the finalized inheritance data
        if self.inheritance_changed:
            # here we convert the inheritance dict back to list
            inheritance_data = [v for k, v in inheritance_dict.items()]
            self.koji.login()
            log.info("Updating inheritance of tag %s with data: \n%s",
                     self.tag, str(inheritance_data))
            self.koji.set_inheritance_data(self.tag, inheritance_data)
            self.koji.regen_repo(self.tag, wait=self.wait_regen_repo)
        else:
            log.info("No change to inheritance data of tag '%s', skipping",
                     self.tag)
