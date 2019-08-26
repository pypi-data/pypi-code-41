import logging
import os
import uuid

import ruamel.yaml
import xapian
import jinja2

from pkg_resources import resource_string

try:
    import git
    git_available = True
except ImportError:
    git_available = False


class Entry(object):
    def __init__(self, collection, data={}, fname=None):
        self.collection = collection
        self.data = data or self.empty_data()
        self.fname = fname
        self.uid = self.data.get('uid', None)
        if not self.uid:
            if self.fname:
                self.uid, ext = os.path.splitext(os.path.basename(self.fname))
            else:
                self.uid = uuid.uuid4().hex
        if not self.fname:
            self.fname = self.uid + '.yaml'

    def __str__(self):
        label = self.collection.settings.get('entry_label', None)
        if label:
            t = jinja2.Template(label)
            return t.render(**self.get_data())
        else:
            return self.uid

    def get_data(self):
        d = self.data.copy()
        d['uid'] = self.uid
        d['fname'] = self.fname
        d['short_id'] = self.short_id
        return d

    def empty_data(self):
        data = ''
        for field in self.collection.settings['fields']:
            if not field.get('help', None) is None:
                data += "# {name} ({type}): {help}\n".format(**field)
            t = field['type']
            if t == 'string':
                data += ("{name}: ''\n".format(**field))
            elif t == 'text':
                data += ("{name}: |\n    .\n".format(**field))
            elif t == 'integer':
                data += ("{name}: 0\n".format(**field))
            else:
                data += ("{name}: \n".format(**field))
        return ruamel.yaml.load(data, Loader=ruamel.yaml.RoundTripLoader)

    @property
    def yaml_data(self):
        return ruamel.yaml.dump(self.data, Dumper=ruamel.yaml.RoundTripDumper)

    @property
    def idterm(self):
        return "Q"+self.uid

    @property
    def short_id(self):
        return self.uid[:8]

    def validate(self):
        errors = []
        valid = True
        for field in self.collection.settings['fields']:
            value = self.data.get(field['name'], None)
            if not value:
                # empty fields are always fine
                continue
            t = field['type']
            if t == 'integer':
                try:
                    int(value)
                except ValueError:
                    valid = False
                    errors.append({
                        'field': field['name'],
                        'error': 'Invalid value for integer field: {}'.format(
                            value
                            ),
                        })
            elif t == 'float':
                try:
                    float(value)
                except ValueError:
                    valid = False
                    errors.append({
                        'field': field['name'],
                        'error': 'Invalid value for float field: {}'.format(
                            value
                            ),
                        })
        return valid, errors


class Collection(object):
    """
    """
    PARSER_FLAGS = (
        xapian.QueryParser.FLAG_BOOLEAN |
        xapian.QueryParser.FLAG_PHRASE |
        xapian.QueryParser.FLAG_LOVEHATE |
        xapian.QueryParser.FLAG_WILDCARD
        )

    def __init__(self, directory=None, itemdir='items'):
        self.basedir = directory or os.getcwd()
        self.itemdir = os.path.join(self.basedir, itemdir)
        try:
            with open(os.path.join(self.basedir, 'settings.yaml')) as fp:
                self.settings = ruamel.yaml.load(
                    fp,
                    ruamel.yaml.RoundTripLoader
                    )
        except FileNotFoundError:
            self.settings = ruamel.yaml.safe_load("{}")
        os.makedirs(os.path.join(self.basedir, '.lesana'), exist_ok=True)
        if 'lang' in self.settings:
            try:
                self.stemmer = xapian.Stem(self.settings['lang'])
            except xapian.InvalidArgumentError:
                logging.warning(
                    "Invalid language %s, in settings.yaml: using english.",
                    self.settings['lang']
                    )
                self.stemmer = xapian.Stem('english')
        else:
            self.stemmer = xapian.Stem('english')
        self._enquire = None
        # This selects whether to load all other yaml files with
        # safe_load or load + RoundTripLoader
        self.safe = False
        self.entry_class = Entry

    def _index_file(self, fname, cache):
        with open(os.path.join(self.itemdir, fname)) as fp:
            if self.safe:
                data = ruamel.yaml.safe_load(fp)
            else:
                data = ruamel.yaml.load(fp, ruamel.yaml.RoundTripLoader)
        entry = self.entry_class(self, data, fname)
        valid, errors = entry.validate()
        if not valid:
            logging.warning(
                "Not indexing {fname}: invalid data".format(fname=fname)
                )
            return False, errors

        doc = xapian.Document()
        self.indexer.set_document(doc)

        # Fields with prefix, for field search
        for field in self.indexed_fields:
            if field['multi']:
                values = entry.data.get(field['name'])
            else:
                values = [entry.data.get(field['name'])]
            if not values:
                values = []
            for v in values:
                try:
                    self.indexer.index_text(
                        str(v),
                        1,
                        field['prefix'])
                except ValueError as e:
                    logging.info("Not indexing empty? value {}: {}".format(
                        entry.data.get(field['name']),
                        str(e)))
        # unprefixed fields, for full text search
        for field in self.indexed_fields:
            if field.get('free_search', False):
                if field['multi']:
                    values = entry.data.get(field['name'])
                else:
                    values = [entry.data.get(field['name'])]
                if not values:
                    values = []
                for v in values:
                    try:
                        self.indexer.index_text(v)
                        self.indexer.increase_termpos()
                    except ValueError as e:
                        # probably already logged earlier
                        pass
        doc.set_data(entry.yaml_data)
        doc.add_boolean_term(entry.idterm)
        doc.add_value(0, entry.fname.encode('utf-8'))

        cache.replace_document(entry.idterm, doc)
        return True, []

    @property
    def indexed_fields(self):
        fields = []
        for field in self.settings['fields']:
            if field.get('index', '') in ['free', 'field']:
                prefix = field.get('prefix', 'X'+field['name'].upper())
                fields.append({
                    'prefix': prefix,
                    'name': field['name'],
                    'free_search': field['index'] == 'free',
                    'multi': field['type'] in ['list']
                    })
        return fields

    def update_cache(self, fnames=None):
        """
        Update the xapian db with the data in files.

        ``fnames`` is a list of *basenames* of files in ``self.itemdir``.

        If no files have been passed, add everything.

        Return the number of files that have been added to the cache.
        """
        cache = xapian.WritableDatabase(
            os.path.join(self.basedir, '.lesana/xapian'),
            xapian.DB_CREATE_OR_OPEN
            )
        self.indexer = xapian.TermGenerator()
        self.indexer.set_stemmer(self.stemmer)
        if not fnames:
            try:
                fnames = os.listdir(self.itemdir)
            except FileNotFoundError:
                logging.warning(
                    "No such file or directory: %s, not updating cache".format(
                        self.itemdir)
                    )
                return 0
        updated = 0
        for fname in fnames:
            try:
                valid, errors = self._index_file(fname, cache)
            except IOError as e:
                logging.warning("Could not load file {}: {}".format(
                    fname,
                    str(e))
                    )
            else:
                if valid:
                    updated += 1
                else:
                    logging.warning(
                        "File {fname} could not be indexed: {errors}".format(
                            fname=fname,
                            errors=errors)
                        )
        return updated

    def save_entries(self, entries=[]):
        for e in entries:
            complete_name = os.path.join(
                self.itemdir,
                e.fname
                )
            with open(complete_name, 'w') as fp:
                fp.write(e.yaml_data)

    def git_add_files(self, files=[]):
        if not git_available:
            logging.warning(
                "python3-git not available, could not initalise " +
                "the git repository.")
            return False
        if not self.settings.get('git', False):
            logging.info(
                "This collection is configured not to use git"
                )
            return False
        try:
            repo = git.Repo(self.basedir, search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError as e:
            logging.warning(
                "Could not find a git repository in {}".format(
                    self.basedir))
            return False
        repo.index.add(files)
        return True

    def _get_cache(self):
        try:
            cache = xapian.Database(
                os.path.join(self.basedir, '.lesana/xapian'),
                )
        except xapian.DatabaseOpeningError:
            logging.info("No database found, indexing entries.")
            self.update_cache()
            cache = xapian.Database(
                os.path.join(self.basedir, '.lesana/xapian'),
                )
        return cache

    def start_search(self, querystring):
        """
        Prepare a search for querystring.
        """
        cache = self._get_cache()
        queryparser = xapian.QueryParser()
        queryparser.set_stemmer(self.stemmer)
        queryparser.set_database(cache)

        for field in self.indexed_fields:
            queryparser.add_prefix(field['name'], field['prefix'])

        query = queryparser.parse_query(
                querystring,
                self.PARSER_FLAGS)

        self._enquire = xapian.Enquire(cache)
        self._enquire.set_query(query)

    def get_search_results(self, offset=0, pagesize=12):
        if not self._enquire:
            return
        for match in self._enquire.get_mset(offset, pagesize):
            yield self._match_to_entry(match)

    def get_all_search_results(self):
        if not self._enquire:
            return
        offset = 0
        pagesize = 100
        while True:
            mset = self._enquire.get_mset(offset, pagesize)
            if mset.size() == 0:
                break
            for match in mset:
                yield self._match_to_entry(match)
            offset += pagesize

    def get_all_documents(self):
        cache = self._get_cache()
        postlist = cache.postlist("")
        for post in postlist:
            doc = cache.get_document(post.docid)
            yield self._doc_to_entry(doc)

    def _match_to_entry(self, match):
        return self._doc_to_entry(match.document)

    def _doc_to_entry(self, doc):
        fname = doc.get_value(0).decode('utf-8')
        if self.safe:
            data = ruamel.yaml.safe_load(doc.get_data())
        else:
            data = ruamel.yaml.load(
                doc.get_data(),
                ruamel.yaml.RoundTripLoader
                )
        entry = self.entry_class(
            self,
            data=data,
            fname=fname,
            )
        return entry

    def entry_from_uid(self, uid):
        cache = self._get_cache()
        postlist = cache.postlist('Q'+uid)
        for pitem in postlist:
            return self._doc_to_entry(cache.get_document(pitem.docid))
        return None

    def entries_from_short_uid(self, suid):
        # It would be better to search for partial UIDs inside xapian,
        # but I still can't find a way to do it, so this is a workable
        # workaround on repos where the uids are stored in the
        # filenames.
        potential_uids = [
            os.path.splitext(f)[0]
            for f in os.listdir(self.itemdir)
            if f.startswith(suid)
            ]
        return [self.entry_from_uid(u) for u in potential_uids if u]

    def remove_entries(self, uids):
        cache = xapian.WritableDatabase(
            os.path.join(self.basedir, '.lesana/xapian'),
            xapian.DB_CREATE_OR_OPEN
            )
        for uid in uids:
            entry = self.entry_from_uid(uid)
            if entry is not None:
                cache.delete_document(entry.idterm)
                os.remove(os.path.join(self.itemdir, entry.fname))
            else:
                logging.warning("No such entry: {}, ignoring".format(uid))
        cache.commit()
        cache.close()

    @classmethod
    def init(
            cls,
            directory=None,
            git_enabled=True,
            edit_file=None,
            settings={}
            ):
        """
        Initialize a lesana repository

        directory defaults to .
        if git_enabled is True, git support is enabled and if possible a git
        repository is initalized.
        edit_file is a syncronous function that runs on a filename
        (possibly opening the file in an editor) and should manage its
        own errors.
        """
        c_dir = os.path.abspath(directory or '.')
        os.makedirs(c_dir, exist_ok=True)
        if git_enabled:
            # Try to initalize a git repo
            if git_available:
                repo = git.Repo.init(c_dir, bare=False)
            else:
                logging.warning(
                    "python3-git not available, could not initalise " +
                    "the git repository.")
                repo = None
            # Add .lesana directory to .gitignore and add it to the
            # staging
            lesana_ignored = False
            try:
                with open(os.path.join(c_dir, '.gitignore'), 'r') as fp:
                    for line in fp:
                        if '.lesana' in line:
                            lesana_ignored = True
                            continue
            except FileNotFoundError:
                pass
            if not lesana_ignored:
                with open(os.path.join(c_dir, '.gitignore'), 'a') as fp:
                    fp.write('#Added by lesana init\n.lesana')
                if repo:
                    repo.index.add(['.gitignore'])
            # TODO: Add hook to index files as they are pulled
        # If it doesn't exist, create a skeleton of settings.yaml file
        # then open settings.yaml for editing
        filepath = os.path.join(c_dir, 'settings.yaml')
        if not os.path.exists(filepath):
            skel = resource_string(
                'lesana', 'data/settings.yaml'
                ).decode('utf-8')
            skel_dict = ruamel.yaml.load(skel, ruamel.yaml.RoundTripLoader)
            skel_dict['git'] = git_enabled
            skel_dict.update(settings)
            with open(filepath, 'w') as fp:
                ruamel.yaml.dump(
                    skel_dict,
                    stream=fp,
                    Dumper=ruamel.yaml.RoundTripDumper
                    )
        if edit_file:
            edit_file(filepath)
        if git_enabled and repo:
            repo.index.add(['settings.yaml'])
        coll = cls(c_dir)
        os.makedirs(os.path.join(coll.basedir, coll.itemdir), exist_ok=True)
        return coll
