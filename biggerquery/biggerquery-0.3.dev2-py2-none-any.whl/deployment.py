from datetime import datetime, timedelta
from zipfile import ZipFile
import os


def callable_factory(job):
    def job_callable(**kwargs):
        runtime = kwargs.get('ds')
        job.run(runtime)

    return job_callable


def workflow_to_dag(workflow, start_from, dag_id):
    operators = []
    for job in workflow:
        operators.append({
            'task_type': 'python_callable',
            'task_kwargs': {
                'task_id': job.id,
                'python_callable': callable_factory(job),
                'retries': job.retry_count,
                'retry_delay': timedelta(seconds=job.retry_pause_sec),
                'provide_context': True
            }
        })

    return {
               'dag_id': dag_id,
               'default_args': {
                   'owner': 'airflow',
                   'depends_on_past': True,
                   'start_date': datetime.strptime(start_from, "%Y-%m-%d"),
                   'email_on_failure': False,
                   'email_on_retry': False
               },
               'schedule_interval': '@daily',
               'max_active_runs': 1
           }, operators


def build_dag_file(workflow_import_path,
                   start_from,
                   dag_id):
    dag_package_name = workflow_import_path.split('.')[0]

    return '''from airflow import models
from airflow.operators import python_operator
import biggerquery as bgq
from {workflow_import_path} import {workflow_name} as workflow

dag_args, tasks = bgq.workflow_to_dag(workflow, '{start_from}', '{dag_id}')

dag = models.DAG(**dag_args)
final_task = python_operator.PythonOperator(dag=dag, **tasks[0]['task_kwargs'])
for task in tasks[1:]:
    final_task = final_task >> python_operator.PythonOperator(dag=dag, **task['task_kwargs'])

globals()['{dag_id}'] = dag'''.format(
        dag_package=dag_package_name,
        workflow_import_path='.'.join(workflow_import_path.split('.')[:-1]),
        workflow_name=workflow_import_path.split('.')[-1],
        start_from=start_from,
        dag_id=dag_id)


def upload_file_to_google_cloud_storage(file_path, project_id, bucket):
    from google.cloud import storage
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket)
    blob = bucket.blob(file_path)
    blob.upload_from_filename(file_path, content_type='application/octet-stream')


def zipdir(path, ziph, prefix_to_cut_from_filename):
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith('.pyc'):
                ziph.write(os.path.join(root, file),
                           os.path.join(root.replace(prefix_to_cut_from_filename, ''), file))


def build_dag_zip(
        package_path,
        workflow_import_path,
        start_from,
        dag_id,
        target_dir_path):
    dag_file_name = '{}.py'.format(dag_id)
    dag_file_path = os.path.join(target_dir_path, dag_file_name)
    with open(dag_file_path, 'w') as dag_file:
        dag_file.write(build_dag_file(workflow_import_path, start_from, dag_id))

    zip_path = os.path.join(target_dir_path, '{}.zip'.format(dag_id))
    with ZipFile(zip_path, 'w') as zip:
        zip.write(dag_file_path, dag_file_name)
        zipdir(package_path, zip, os.path.join(*package_path.split(os.sep)[:-1]))


def build_workflow_from_notebook(notebook_name, workflow_variable_name, start_date):
    cwd = os.getcwd()
    workflow_package = os.path.join(cwd, workflow_variable_name)
    workflow_package_init = os.path.join(workflow_package, '__init__.py')
    os.mkdir(workflow_package)
    with open(workflow_package_init, 'w') as f:
        f.write('pass')
    notebook_path = os.path.join(cwd, notebook_name)
    os.system('jupyter nbconvert --to script {}.ipynb'.format(notebook_path))
    converted_notebook_path = '{}.py'.format(notebook_path)
    converted_notebook_name = '{}.py'.format(notebook_name)
    with open(converted_notebook_path, 'r') as copy_source:
        with open(os.path.join(workflow_package, converted_notebook_name), 'w') as copy_target:
            copy_target.write(''.join(copy_source.readlines()[:-1]))
    build_dag_zip(
        workflow_package,
        '.'.join([workflow_variable_name, notebook_name, workflow_variable_name]),
        start_date,
        workflow_variable_name,
        cwd)
