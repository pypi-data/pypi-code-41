# Copyright | 2019 | All rights reserved
# MIHAIL BUTNARU
"""
Ingestor, handles the operations between the mongo database and s3
The data is transformed based on the specified format, it handles aswell the
configurations for the connection to aws and mongodb
"""
from src.core import mongo_manager
from src.core import aws_manager
from src.serializers.serializer import serialize


class Ingestor:

    def start_ingesting(self, format):
        """
        Based on the format, the ingesting is starting
            Args:
                format (str): csv and json format is supported at the moment
            Returns:
                success if the data is succseful saved into S3
        """
        try:
            mongo_extract = serialize.serializer(
                mongo_manager.get_data_collection(),
                format)
            aws_manager.bucket_manager(mongo_extract, format)
        except Exception as error:
            raise ValueError(error)
