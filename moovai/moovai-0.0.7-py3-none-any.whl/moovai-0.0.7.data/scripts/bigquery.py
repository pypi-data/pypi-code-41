from google.cloud import bigquery as bq
from google.cloud.bigquery.schema import SchemaField
from google.cloud import error_reporting
import json
import pandas as pd
import pysnooper

def get_schema_from_json(schema_path):
    """
    Converts json schema to bigquery schema
    :param schema_path: path to the json file containing schema
    :return: schema to plug into job config when uploading file to bigquery: [ bigquery.SchemaField("name", "STRING"), ...]
    """
    schema = []
    try:
        with open(schema_path) as json_file:
            text = json_file.read()
            json_data = json.loads(text)

        for item in json_data:
            schema.append(SchemaField(item['name'], item['type']))
    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()

    return schema

@pysnooper.snoop()
def get_schema_from_csv(csv_file_path):
    """
    Get Bigquery compatible schema object
    :param csv_file_path: path to the csv file you want to get bigquery schema of.
    :return: list of bigquery compatible schema.
    """
    df = pd.read_csv(csv_file_path).dtypes
    bq_dtypes = ['INT64', 'NUMERIC', 'FLOAT64', 'BOOL', 'STRING', 'BYTES', 'DATE', 'TIMESTAMP', 'DATETIME', 'GEOGRAPHY',
                 'TIME', 'ARRAY', 'STRUCT']
    pandas_dtypes = ['object', 'int64', 'float64', 'bool', 'datetime64', 'timedelta[ns]', 'category']
    dtype_mapper = {
        'object': "STRING",
        'int64': "INTEGER",
        'float64': "FLOAT",
        'bool': "BOOL",
        'datetime64': "TIMESTAMP"
    }
    schema = []
    for index, value in df.iteritems():
        dict = {
            "mode": "NULLABLE"
        }
        if f"{value}" in dtype_mapper:
            value = dtype_mapper[f"{value}"]
        dict["name"] = index
        dict["type"] = value
        schema.append(dict)
    bq_schema = []
    for item in schema:
        bq_schema.append(SchemaField(item["name"], item["type"]))

    return bq_schema

def generate_sql_query(project, dataset_id, table_id, columns=None, conditions=None):
    """
    Generates SQL query for querying a BigQuery dataset table
    :param project: project id
    :param dataset_id: bigquery dataset id
    :param table_id: bigquery table id
    :param columns: Array. Columns to select
    :param conditions: Array. conditions the data to retrive needs to satisfy
    :return: STRING of sql
    """
    bq_table = f"{project}.{dataset_id}.{table_id}"
    select = ""
    where_clause = ""
    if not columns:
        select = "*"
    else:
        last_col = len(columns) - 1
        for col in columns:
            if col == columns[last_col]:
                select += f"{col}"
            else:
                select += f"{col}, "
    if conditions:
        last_cond = len(conditions) - 1
        for condition in conditions:
            where_clause = "WHERE"
            if condition == conditions[last_cond]:
                where_clause += f" {condition}"
            else:
                where_clause += f" {condition} AND"

    query_string = f"SELECT {select} FROM `{bq_table}` {where_clause}"

    return query_string

def upload_local_file_to_bq(file, dataset_id, table_id, schema_path=None, schema=None, overwrite=False):
    """
    uploads a csv file to BigQuery. App needs to have already been authenticated to google cloud.
    :param uri: file path to csv to upload in google cloud storage
    :param dataset_id: name of dataset to upload data to
    :param table_id: name of table to upload data to
    :param schema_path: OPTIONAL : if present, the schema will be used as config for Bigquery job. If not provided, schema will be auto-detected
    :param schema: OPTIONAL: exclusive from schema_path: bigquery schema object. if present, schema will be used in BigQuery job config.
    :param overwrite: Boolean: OPTIONAL : overwrites table if set to true (default is False)
    :return: None. Uploads and appends file to BigQuery dataset_id.table_id.
    """
    try:
        client = bq.Client()
        dataset_ref = client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)
        job_config = bq.LoadJobConfig()
        job_config.source_format = bq.SourceFormat.CSV
        if overwrite:
            job_config.write_disposition = bq.WriteDisposition.WRITE_TRUNCATE  # If the table already exists, BigQuery overwrites data in table
        else:
            job_config.write_disposition = bq.WriteDisposition.WRITE_APPEND  # If the table already exists, BigQuery appends the data to the table
        job_config.skip_leading_rows = 1
        if not schema_path and not schema:
            job_config.autodetect = True
        elif schema_path:
            bq_schema = get_schema_from_json(schema_path)
            job_config.schema = bq_schema
        else:
            job_config.schema = schema
        try:
            with open(file, 'rb') as source_file:
                job = client.load_table_from_file(
                    source_file,
                    table_ref,
                    location='US',
                    job_config=job_config)  # API request

            job.result()  # Waits for table load to complete.
            print('Loaded {} rows into {}:{}.'.format(
                job.output_rows, dataset_id, table_id))
        except Exception:
            error_client = error_reporting.Client()
            error_client.report_exception()

    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()


def upload_gcs_file_to_bq(gcs_uri, dataset_id, table_id, schema_path=None, schema=None, overwrite=False):
    """
    uploads a csv file located on google cloud storage to BigQuery. App needs to have already been authenticated to google cloud.
    :param uri: STRING. file path to csv to upload in google cloud storage
    :param dataset_id: STRING.  name of dataset to upload data to
    :param table_id: STRING. name of table to upload data to
    :param schema_path: OPTIONAL : if present, the schema will be used as config for Bigquery job. If not provided, schema will be auto-detected
    :param schema: OPTIONAL: exclusive from schema_path: bigquery schema object. if present, schema will be used in BigQuery job config.
    :param overwrite: Boolean: OPTIONAL : overwrites table if set to true (default is False)
    :return: None. Uploads and appends file to BigQuery dataset_id.table_id.
    """
    try:
        client = bq.Client()
        dataset_ref = client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)

        job_config = bq.LoadJobConfig()
        job_config.source_format = bq.SourceFormat.CSV
        if overwrite:
            job_config.write_disposition = bq.WriteDisposition.WRITE_TRUNCATE  # If the table already exists, BigQuery overwrites data in table
        else:
            job_config.write_disposition = bq.WriteDisposition.WRITE_APPEND  # If the table already exists, BigQuery appends the data to the table
        job_config.skip_leading_rows = 1
        if not schema_path and not schema:
            job_config.autodetect = True
        elif schema_path:
            bq_schema = get_schema_from_json(schema_path)
            job_config.schema = bq_schema
        else:
            job_config.schema = schema
        try:
            job = client.load_table_from_uri(
                gcs_uri,
                table_ref,
                job_config=job_config)  # API request

            job.result()  # Waits for table load to complete.
            print('Loaded {} rows into {}:{}.'.format(
                job.output_rows, dataset_id, table_id))
        except Exception:
            error_client = error_reporting.Client()
            error_client.report_exception()
    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()



def get_data_from_bq(sql_query, prediction=False):
    """
    Queries bigquery data
    :param sql_query: String. SQL query string.
    :return: pandas dataframe result of query
    """

    try:
        client = bq.Client()
        result = (client.query(sql_query).result().to_dataframe())
        if prediction:
            result = result.to_json(orient='records')
        return result
    except Exception:
        error_client = error_reporting.Client()
        error_client.report_exception()