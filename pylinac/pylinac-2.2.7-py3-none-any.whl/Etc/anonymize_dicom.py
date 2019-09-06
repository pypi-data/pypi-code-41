import dianonymous

paths_to_files_and_dirs = [r'C:\Users\James\Desktop\CatPhan504\High quality head']
output_dir = r'C:\Users\James\Desktop\CatPhan504\High quality head\anon'

dianonymous.anonymize(
    paths_to_files_and_dirs,
    output=output_dir,
    anon_id=None,    # optional string to use for output patient id
    anon_name=None,  # optional string to use for output patient name
    recurse=False,   # recurse any input subdirectories looking for dicom files
    private=True,    # delete any private tags
)