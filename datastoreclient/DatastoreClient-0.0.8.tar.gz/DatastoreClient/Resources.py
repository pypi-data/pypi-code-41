from minio import Minio
import logging as log
import os
import json
from DatastoreClient.utils import turn_metadata, parallel
from tqdm import tqdm


class Resource(object):
    """Base Resource Class"""

    protoype = {
        "model": {
            "bucket": "which bucket you want to put it in?",
            "source": "tell me more detail about where this object come from!",
            "train": "which train this model come from?",
        },
        "weight": {
            "bucket": "which bucket you want to put it in?",
            "source": "tell me more detail about where this object come from!",
            "train": "which train this model come from?",
        },
        "attachment": {
            "bucket": "which bucket you want to put it in?",
            "source": "tell me more detail about where this object come from!",
            "class_tree": {
                "key": "this is a value, please use a json object to class this object"
            },
        },
        "raw": {
            "bucket": "which bucket you want to put it in?",
            "source": "tell me more detail about where this object come from!",
            "class_tree": {
                "key": "this is a value, please use a json object to class this object"
            },
        },
    }

    def __init__(self, uploader=None, queryer=None):
        self.uploader = uploader
        self.queryer = queryer

    def check_metadata(self, metadata):
        protoype = self.protoype[self.__class__.__name__.lower()]
        if set(protoype) - set(metadata):
            log.INFO({"your metadata should catains all protoype kyes: ": protoype})
            raise Exception(
                {"your metadata should catains all protoype kyes: ": protoype}
            )

    def create(self, path_to_file_or_files, metadata):
        self.check_metadata(metadata)
        files = self.uploader.prepare_files(path_to_file_or_files, metadata)
        paralleled_files = parallel(self._check_version, files)
        files = []
        for paralleled_file in paralleled_files:
            files = files + paralleled_file
        paralleled_upload_results = parallel(self.uploader.upload, files)
        success_files = []
        failed_files = []
        already_in_bucket_files = []
        for paralleled_upload_result in paralleled_upload_results:
            paralleled_success_files, paralleled_failed_files, paralleled_already_in_bucket_files = (
                paralleled_upload_result
            )
            success_files = success_files + paralleled_success_files
            failed_files = failed_files + paralleled_failed_files
            already_in_bucket_files = (
                already_in_bucket_files + paralleled_already_in_bucket_files
            )
        create_record = parallel(self._create, success_files) + parallel(
            self._create, already_in_bucket_files
        )
        return create_record

    def _check_version(self, files):
        model_name = self.__class__.__name__.lower()
        bar = tqdm(desc="checking files version", total=len(files))
        for file in files:
            err, result = self.queryer.data_model_lastest(
                model_name=model_name,
                file=file,
                metadata=turn_metadata(file["metadata"]),
            )
            if err:
                log.error({"_check_version_err": err})
                raise Exception(
                    "Error to file check version, cancel upload session, no file uploaded"
                )
            datas = result["data"]["data_{}".format(model_name)]
            if datas:
                lastest = datas[0]
                if (
                    lastest["metadata"] != file["metadata"]
                    or lastest["md5"] != file["md5"]
                ):
                    file["version"] = lastest["version"] + 1
                else:
                    file["version"] = lastest["version"]
            else:
                file["version"] = 0
            bar.update(1)
        log.debug({"_check_version_files": files})
        return files

    def query(
        self, where='{metadata: {_contains: {tag: "latest"}}}', qeury_string=None
    ):
        model_name = self.__class__.__name__.lower()
        if qeury_string:
            return self.queryer.query(qeury_string)

        err, models = self.queryer.data_where(model_name=model_name, where=where)
        if not err:
            return err, models["data"]["data_{}".format(model_name)]
        else:
            return err, None

    def _create(self, files):
        model_name = self.__class__.__name__.lower()
        results = []
        bar = tqdm(desc="create files recordings", total=len(files))
        for file in files:
            err, result = self.queryer.remove_tag_insert_data(
                model_name=model_name,
                file=file,
                metadata=turn_metadata(file["metadata"]),
            )
            if not err:
                results.append(
                    result["data"]["insert_data_{}".format(model_name)]["returning"][0]
                )
            else:
                if err[0]["extensions"]["code"] == "constraint-violation":
                    log.debug({"constraint-violation": file["name"]})
            bar.update(1)
        return results


class Model(Resource):
    pass


class Weight(Resource):
    pass


class Attachment(Resource):
    pass


class Raw(Resource):
    pass
