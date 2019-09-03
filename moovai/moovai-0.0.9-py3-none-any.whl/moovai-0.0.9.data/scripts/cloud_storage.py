from google.cloud import storage
import os
from urllib.parse import urlparse
from google.cloud import error_reporting

def upload_to_gcs(file, bucket_name, folder):
    """
    uploads provided file to  google cloud storage
    :param file: path of local file to upload
    :return: uri of file stored on google cloud storage
    """
    gcs_client = storage.Client()

    bucket = gcs_client.get_bucket(bucket_name)
    filename = folder + "/" + os.path.basename(file)

    blob = bucket.blob(filename)
    blob.upload_from_filename(file)
    os.remove(file)
    uri = f"gs://{bucket_name}/{filename}"

    return uri

def download_file_gcs(gcs_uri):
    """
    Downloads file from google cloud storage
    :param gcs_uri: URI to file on GCS
    :return: file path downloaded locally
    """
    try:
        storage_client = storage.Client()
        parsed_url = urlparse(gcs_uri)
        bucket_id = parsed_url.netloc
        file_path = parsed_url.path
        gcs_path_file = file_path[1:]
        filename = os.path.basename(file_path)
        bucket = storage_client.get_bucket(bucket_id)
        blob = bucket.blob(gcs_path_file)
        blob.download_to_filename(filename)
        return filename
    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()