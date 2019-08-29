class Storage():
    def delete(self, filepath, bucket_name=None):
        raise NotImplementedError()

    def read(self, filepath, bucket_name=None):
        raise NotImplementedError()

    def save_file(self, filename, key=None, bucket_name=None):
        raise NotImplementedError()

    def save(self, filename, contents, bucket_name=None):
        raise NotImplementedError()