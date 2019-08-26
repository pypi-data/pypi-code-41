import logging
import os.path
import shutil
import tempfile
import unittest

import git
import ruamel.yaml

import lesana


class testCollection(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(os.path.join(self.collection.basedir, '.lesana'))

    def test_empty(self):
        self.collection = lesana.Collection('tests/data/empty')
        self.assertEqual(self.collection.settings, {})

        self.collection.update_cache()
        self.assertIsNotNone(self.collection.stemmer)

    def test_load_simple(self):
        self.collection = lesana.Collection('tests/data/simple')
        self.assertIsNotNone(self.collection.settings)
        self.assertEqual(
            self.collection.settings['name'],
            "Simple lesana collection"
            )
        self.assertEqual(len(self.collection.settings['fields']), 5)
        self.assertEqual(len(self.collection.indexed_fields), 2)

        self.collection.update_cache()
        self.assertIsNotNone(self.collection.stemmer)

    def test_load_wrong_language(self):
        # This loads a collection with an invalid value in lang
        with self.assertLogs(level=logging.WARNING) as cm:
            self.collection = lesana.Collection('tests/data/wrong')
        self.assertEqual(len(cm.output), 1)
        self.assertIn("Invalid language", cm.output[0])
        # The collection will default to english, but should still work.
        self.collection.update_cache()
        self.assertIsNotNone(self.collection.settings)
        self.assertIsNotNone(self.collection.stemmer)

    def test_load_no_index_for_one_entry(self):
        # This loads a collection where some of the entries have no
        # "index" field
        with self.assertLogs(level=logging.WARNING):
            self.collection = lesana.Collection('tests/data/wrong')
        self.collection.update_cache()
        self.assertIsNotNone(self.collection.settings)
        self.assertIsNotNone(self.collection.stemmer)
        # Fields with no "index" entry are not indexed
        self.assertEqual(len(self.collection.settings['fields']), 4)
        self.assertEqual(len(self.collection.indexed_fields), 1)

    def test_load_safe(self):
        self.collection = lesana.Collection('tests/data/simple')
        self.collection.safe = True
        self.collection.update_cache()

    def test_full_search(self):
        self.collection = lesana.Collection('tests/data/simple')
        self.collection.start_search('Item')
        res = self.collection.get_all_search_results()
        matches = list(res)
        self.assertEqual(len(matches), 2)
        for m in matches:
            self.assertIsInstance(m, lesana.Entry)

    def test_search(self):
        self.collection = lesana.Collection('tests/data/simple')
        self.collection.start_search('Item')
        res = self.collection.get_search_results()
        matches = list(res)
        self.assertEqual(len(matches), 2)
        for m in matches:
            self.assertIsInstance(m, lesana.Entry)

    def test_search_wildcard(self):
        self.collection = lesana.Collection('tests/data/simple')
        self.collection.start_search('Ite*')
        res = self.collection.get_search_results()
        matches = list(res)
        self.assertEqual(len(matches), 2)
        for m in matches:
            self.assertIsInstance(m, lesana.Entry)

    def test_search_non_init(self):
        self.collection = lesana.Collection('tests/data/simple')
        matches = list(self.collection.get_search_results())
        self.assertEqual(matches, [])
        matches = list(self.collection.get_all_search_results())
        self.assertEqual(matches, [])

    def test_all_entries(self):
        self.collection = lesana.Collection('tests/data/simple')
        res = self.collection.get_all_documents()
        matches = list(res)
        self.assertEqual(len(matches), 3)
        for m in matches:
            self.assertIsInstance(m, lesana.Entry)

    def test_entry_from_uid(self):
        self.collection = lesana.Collection('tests/data/simple')
        entry = self.collection.entry_from_uid(
            '11189ee47ddf4796b718a483b379f976'
            )
        self.assertEqual(entry.uid, '11189ee47ddf4796b718a483b379f976')
        self.collection.safe = True
        entry = self.collection.entry_from_uid(
            '11189ee47ddf4796b718a483b379f976'
            )
        self.assertEqual(entry.uid, '11189ee47ddf4796b718a483b379f976')

    def test_entry_from_short_uid(self):
        self.collection = lesana.Collection('tests/data/simple')
        entries = self.collection.entries_from_short_uid(
            '11189ee4'
            )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].uid, '11189ee47ddf4796b718a483b379f976')
        entries = self.collection.entries_from_short_uid(
            '11189ee47ddf4796b718a483b379f976'
            )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].uid, '11189ee47ddf4796b718a483b379f976')
        entries = self.collection.entries_from_short_uid(
            '12345678'
            )
        self.assertEqual(len(entries), 0)

    def test_index_missing_file(self):
        self.collection = lesana.Collection('tests/data/simple')
        with self.assertLogs(level=logging.WARNING) as cm:
            self.collection.update_cache(['non_existing_file'])
        self.assertEqual(len(cm.output), 1)
        self.assertIn("non_existing_file", cm.output[0])

    def test_get_entry_missing_uid(self):
        self.collection = lesana.Collection('tests/data/simple')
        entry = self.collection.entry_from_uid('this is not an uid')
        self.assertIsNone(entry)


class testEntries(unittest.TestCase):
    def setUp(self):
        self.collection = lesana.Collection('tests/data/simple')
        self.basepath = 'tests/data/simple/items'
        self.filenames = []

    def tearDown(self):
        for fname in self.filenames:
            os.remove(fname)
        shutil.rmtree(os.path.join(self.collection.basedir, '.lesana'))

    def test_simple(self):
        fname = '085682ed-6792-499d-a3ab-9aebd683c011.yaml'
        with open(os.path.join(self.basepath, fname)) as fp:
            data = ruamel.yaml.safe_load(fp)
        entry = lesana.Entry(self.collection, data=data, fname=fname)
        self.assertEqual(entry.idterm, 'Q'+data['uid'])
        fname = '11189ee47ddf4796b718a483b379f976.yaml'
        uid = '11189ee47ddf4796b718a483b379f976'
        with open(os.path.join(self.basepath, fname)) as fp:
            data = ruamel.yaml.safe_load(fp)
        entry = lesana.Entry(self.collection, data=data, fname=fname)
        self.assertEqual(entry.idterm, 'Q'+uid)
        self.assertEqual(entry.short_id, uid[:8])

    def test_write_new(self):
        new_entry = lesana.Entry(self.collection)
        self.collection.save_entries(entries=[new_entry])
        entry_fname = 'tests/data/simple/items/' + new_entry.fname
        self.filenames.append(entry_fname)
        with open(entry_fname) as fp:
            text = fp.read()
        self.assertIn('quantity (integer): how many items are there', text)
        self.assertIn('other (yaml):', text)
        self.assertNotIn('position (string)', text)
        written = ruamel.yaml.safe_load(text)
        self.assertIsInstance(written['quantity'], int)
        self.assertIsInstance(written['name'], str)

    def test_entry_representation(self):
        uid = '11189ee47ddf4796b718a483b379f976'
        entry = self.collection.entry_from_uid(uid)
        self.assertEqual(
            str(entry),
            uid
            )
        label = '{{ uid }}: {{ name }}'
        self.collection.settings['entry_label'] = label
        self.assertEqual(
            str(entry),
            '{uid}: {name}'.format(uid=uid, name='Another item')
            )

    def test_entry_creation_uid_but_no_filename(self):
        fname = '11189ee47ddf4796b718a483b379f976.yaml'
        with open(os.path.join(self.basepath, fname)) as fp:
            data = ruamel.yaml.safe_load(fp)
        data['uid'] = '11189ee47ddf4796b718a483b379f976'
        entry = lesana.Entry(self.collection, data=data)
        self.assertEqual(entry.fname, fname)

    def test_entry_creation_no_uid_no_filename(self):
        fname = '11189ee47ddf4796b718a483b379f976.yaml'
        with open(os.path.join(self.basepath, fname)) as fp:
            data = ruamel.yaml.safe_load(fp)
        entry = lesana.Entry(self.collection, data=data)
        self.assertIsNotNone(entry.uid)
        self.assertIsNotNone(entry.fname)

    def test_entry_creation_filename_but_no_uid(self):
        fname = '11189ee47ddf4796b718a483b379f976.yaml'
        uid = '11189ee47ddf4796b718a483b379f976'
        with open(os.path.join(self.basepath, fname)) as fp:
            data = ruamel.yaml.safe_load(fp)
        entry = lesana.Entry(self.collection, data=data, fname=fname)
        self.assertEqual(entry.uid, uid)

    def test_entry_str_filename_and_uid(self):
        fname = '11189ee47ddf4796b718a483b379f976.yaml'
        with open(os.path.join(self.basepath, fname)) as fp:
            data = ruamel.yaml.safe_load(fp)
        data['uid'] = '11189ee47ddf4796b718a483b379f976'
        entry = lesana.Entry(self.collection, data=data)
        self.assertEqual(str(entry), data['uid'])
        self.collection.settings['entry_label'] = '{{ uid }}: {{ name }}'
        self.assertEqual(str(entry), data['uid'] + ': Another item')

    def test_entry_str_filename_no_uid(self):
        fname = '11189ee47ddf4796b718a483b379f976.yaml'
        with open(os.path.join(self.basepath, fname)) as fp:
            data = ruamel.yaml.safe_load(fp)
        entry = lesana.Entry(self.collection, data=data)
        uid = entry.uid
        self.assertEqual(str(entry), uid)
        self.collection.settings['entry_label'] = '{{ uid }}: {{ name }}'
        self.assertEqual(str(entry), uid + ': Another item')


class testComplexCollection(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.collection = lesana.Collection('tests/data/complex')

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(os.path.join(self.collection.basedir, '.lesana'))

    def test_init(self):
        self.assertIsNotNone(self.collection.settings)
        self.assertEqual(
            self.collection.settings['name'],
            "Fully featured lesana collection"
            )
        self.assertEqual(len(self.collection.settings['fields']), 6)
        self.assertIsNotNone(self.collection.stemmer)
        self.assertEqual(len(self.collection.indexed_fields), 5)

    def test_index(self):
        self.collection.update_cache()

    def test_indexing_list(self):
        self.collection.update_cache(['73097121f1874a6ea2f927db7dc4f11e.yaml'])
        self.collection.start_search('tags:this')
        res = self.collection.get_search_results()
        matches = list(res)
        self.assertEqual(len(matches), 1)
        for m in matches:
            self.assertIsInstance(m, lesana.Entry)


class testCollectionWithErrors(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.collection = lesana.Collection('tests/data/wrong')

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(os.path.join(self.collection.basedir, '.lesana'))

    def test_init(self):
        self.assertIsNotNone(self.collection.settings)
        self.assertEqual(
            self.collection.settings['name'],
            "Lesana collection with certain errors"
            )
        self.assertEqual(len(self.collection.settings['fields']), 4)
        self.assertIsNotNone(self.collection.stemmer)
        self.assertEqual(len(self.collection.indexed_fields), 1)

    def test_index(self):
        loaded = self.collection.update_cache()
        self.assertEqual(loaded, 0)


class testCollectionCreation(unittest.TestCase):
    def test_init(self):
        tmpdir = tempfile.mkdtemp()
        collection = lesana.Collection.init(tmpdir)
        self.assertIsInstance(collection, lesana.Collection)
        self.assertTrue(os.path.isdir(os.path.join(tmpdir, '.git')))
        self.assertTrue(os.path.isdir(os.path.join(tmpdir, '.lesana')))
        self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'settings.yaml')))
        self.assertTrue(os.path.isfile(os.path.join(tmpdir, '.gitignore')))
        # and then run it twice on the same directory, nothing should break
        collection = lesana.Collection.init(tmpdir)
        self.assertIsInstance(collection, lesana.Collection)
        self.assertTrue(os.path.isdir(os.path.join(tmpdir, '.git')))
        self.assertTrue(os.path.isdir(os.path.join(tmpdir, '.lesana')))
        self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'settings.yaml')))
        self.assertTrue(os.path.isfile(os.path.join(tmpdir, '.gitignore')))
        created = lesana.Collection(tmpdir)
        self.assertTrue(created.settings['git'])
        shutil.rmtree(tmpdir)

    def do_nothing(*args, **kwargs):
        # A function that does nothing instead of editing a file
        pass

    def test_init_edit_file(self):
        tmpdir = tempfile.mkdtemp()
        collection = lesana.Collection.init(tmpdir, edit_file=self.do_nothing)
        self.assertIsInstance(collection, lesana.Collection)
        self.assertTrue(os.path.isdir(os.path.join(tmpdir, '.git')))
        self.assertTrue(os.path.isdir(os.path.join(tmpdir, '.lesana')))
        self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'settings.yaml')))
        self.assertTrue(os.path.isfile(os.path.join(tmpdir, '.gitignore')))
        shutil.rmtree(tmpdir)

    def test_init_no_git(self):
        tmpdir = tempfile.mkdtemp()
        collection = lesana.Collection.init(tmpdir, git_enabled=False)
        self.assertIsInstance(collection, lesana.Collection)
        self.assertFalse(os.path.isdir(os.path.join(tmpdir, '.git')))
        self.assertTrue(os.path.isdir(os.path.join(tmpdir, '.lesana')))
        self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'settings.yaml')))
        self.assertFalse(os.path.isfile(os.path.join(tmpdir, '.gitignore')))
        # and then run it twice on the same directory, nothing should break
        collection = lesana.Collection.init(tmpdir, git_enabled=False)
        self.assertIsInstance(collection, lesana.Collection)
        self.assertFalse(os.path.isdir(os.path.join(tmpdir, '.git')))
        self.assertTrue(os.path.isdir(os.path.join(tmpdir, '.lesana')))
        self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'settings.yaml')))
        self.assertFalse(os.path.isfile(os.path.join(tmpdir, '.gitignore')))
        created = lesana.Collection(tmpdir)
        self.assertFalse(created.settings['git'])
        shutil.rmtree(tmpdir)

    def test_deletion(self):
        tmpdir = tempfile.mkdtemp()
        shutil.copy('tests/data/simple/settings.yaml', tmpdir)
        shutil.copytree(
            'tests/data/simple/items',
            os.path.join(tmpdir, 'items'),
            )
        collection = lesana.Collection.init(tmpdir)
        # We start with one item indexed with the term "another"
        collection.start_search('another')
        mset = collection._enquire.get_mset(0, 10)
        self.assertEqual(mset.get_matches_estimated(), 1)
        # Then delete it
        collection.remove_entries(['11189ee47ddf4796b718a483b379f976'])
        # An now we should have none
        self.assertFalse(os.path.exists(os.path.join(
            tmpdir,
            'items',
            '11189ee47ddf4796b718a483b379f976.yaml'
            )))
        collection.start_search('another')
        mset = collection._enquire.get_mset(0, 10)
        self.assertEqual(mset.get_matches_estimated(), 0)

    def _find_file_in_git_index(self, fname, index):
        found = False
        for (path, stage) in index.entries:
            if fname in path:
                found = True
                break
        return found

    def test_git_adding(self):
        tmpdir = tempfile.mkdtemp()
        shutil.copy('tests/data/simple/settings.yaml', tmpdir)
        shutil.copytree(
            'tests/data/simple/items',
            os.path.join(tmpdir, 'items'),
            )
        collection = lesana.Collection.init(tmpdir)
        fname = '11189ee47ddf4796b718a483b379f976.yaml'
        repo = git.Repo(tmpdir)
        # By default, this collection doesn't have any git entry in the
        # settings (but there is a repo)
        collection.git_add_files([os.path.join(collection.itemdir, fname)])
        self.assertFalse(self._find_file_in_git_index(fname, repo.index))
        # Then we set it to false
        collection.settings['git'] = False
        collection.git_add_files([os.path.join(collection.itemdir, fname)])
        self.assertFalse(self._find_file_in_git_index(fname, repo.index))
        # And only when it's set to true we should find the file in the
        # staging area
        collection.settings['git'] = True
        collection.git_add_files([os.path.join(collection.itemdir, fname)])
        self.assertTrue(self._find_file_in_git_index(fname, repo.index))
        shutil.rmtree(tmpdir)

    def test_init_custom_settings(self):
        tmpdir = tempfile.mkdtemp()
        collection = lesana.Collection.init(
            tmpdir,
            edit_file=self.do_nothing,
            settings={
                'name': 'A different name',
                'fields': [
                    {'name': 'title', 'type': 'string'},
                    {'name': 'author', 'type': 'string'},
                    ],
                },
            )
        self.assertIsInstance(collection, lesana.Collection)
        self.assertTrue(os.path.isfile(os.path.join(tmpdir, 'settings.yaml')))
        self.assertEqual(collection.settings['name'], 'A different name')
        self.assertEqual(len(collection.settings['fields']), 2)
        shutil.rmtree(tmpdir)


if __name__ == '__main__':
    unittest.main()
