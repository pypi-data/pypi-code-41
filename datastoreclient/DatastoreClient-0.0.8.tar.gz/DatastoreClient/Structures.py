from jinja2 import Template
from DatastoreClient.utils import turn_metadata
from functools import partial


class DataSet(object):
    def __init__(self, queryer=None):
        self.queryer = queryer
        for model_name in ["model", "raw", "attachment", "weight"]:
            add_func_name = "add_" + model_name + "s"
            remove_func_name = "remove_" + model_name + "s"
            setattr(self, add_func_name, partial(self.add_xs, model_name))
            setattr(self, remove_func_name, partial(self.remove_xs, model_name))

    def check_metadata(self, metadata):
        protoype = self.protoype[self.__class__.__name__.lower()]
        protoype_keys = protoype.keys()
        metadata_keys = metadata.keys()
        if protoype_keys != metadata_keys:
            log.error({"your metadata should catains all kyes: ": protoype})
            raise Exception({"your metadata should catains all kyes: ": protoype})

    def create(self, name, metadata):
        err, result = self.queryer.insert_data_dataset(
            name=name, metadata=turn_metadata(metadata)
        )
        return (
            err,
            result["data"]["insert_data_dataset"]["returning"][0] if not err else None,
        )

    def update(self, name, metadata, where):
        err, result = self.queryer.update_data_dataset(
            where=where, name=name, metadata=turn_metadata(metadata)
        )
        return err, result

    def query(self, where):
        err, result = self.queryer.data_dataset(where=where)
        return err, result["data"]["data_dataset"] if not err else None

    def delete(self, where):
        err, result = self.queryer.delete_data_dataset(where=where)
        return err, result

    def add_xs(self, model_name, resources, dataset):
        results = []
        errs = []
        for resource in resources:
            err, result = self.queryer.insert_data_dataset_xx(
                model_name=model_name, dataset_id=dataset["id"], id=resource["id"]
            )
            errs.append(err)
            results.append(result)
        return errs, results

    def remove_xs(self, model_name, resources, dataset):
        err, result = self.queryer.delete_data_dataset_xx(
            model_name=model_name,
            dataset_id=dataset["id"],
            ids=[resource["id"] for resource in resources],
        )
        return err, result
