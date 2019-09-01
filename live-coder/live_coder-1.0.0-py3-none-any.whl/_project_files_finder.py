from ._update_print_references import find_imports


class ProjectFilesFinder:
    '''
        Finds all files possibly relevent to a list of test classes.
        Looks at test imports and then those imports imports and so on.
    '''
    def __init__(self, project_folder, test_class_ids):
        test_file_paths = self._test_files_from_test_classes(project_folder, test_class_ids)
        self.found_files = set(test_file_paths)
        self.files_to_check = test_file_paths
        self.project_folder = project_folder

    @staticmethod
    def _test_files_from_test_classes(project_folder, test_class_ids):
        test_files = set()
        for a_test_class_id in test_class_ids:
            file_path = '/'.join(
                a_test_class_id.split('.')[:-1]
            ) + '.py'
            test_files.add(project_folder + file_path)
        return list(test_files)

    def _unique_imports(self, file_path):
        file_text = open(file_path, 'r').read()
        file_paths = find_imports(self.project_folder, file_path, file_text)
        return list( set(file_paths) - set(self.found_files) )

    def run(self):
        while self.files_to_check:
            file_paths = self._unique_imports(self.files_to_check.pop(0))
            self.files_to_check += file_paths
            self.found_files.update(file_paths)
        return list(self.found_files)