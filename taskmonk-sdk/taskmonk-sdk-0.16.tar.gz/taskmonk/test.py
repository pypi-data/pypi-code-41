from TaskMonkClient import *
import json
import logging
from utils import urlConfig, apiCall, argumentlist, utilities

############ For logging to a file and console at the same time 
############ This will work for the whole code

#logging.basicConfig(level=logging.DEBUG)
level    = logging.DEBUG
format   = '  %(message)s'
handlers = [logging.FileHandler('logger.log'), logging.StreamHandler()]

logging.basicConfig(level = level, format = format, handlers = handlers)

class Test:

    def main(self):
        project_id = "456"
        #logging.debug(access_token_response.status_code)
        # Initialize the taskmonk client witht he oauth credentials and projectId


        client = TaskMonkClient("http://localhost:9000", project_id, 'uIUSPlDMnH8gLEIrnlkdIPRE6bZYhHpw','zsYgKGLUnftFgkASD8pndMwn3viA0IPoGKAiw6S7aVukgMWI8hGJflFs0P2QYxTg')

        batch_id = client.create_batch("batchName")
        logging.debug('Created batch %s', batch_id)

        upload_job_id = client.upload_tasks(batch_id, '/home/dang/Downloads/Primenow_Excel_50.xlsx', 'Excel')
        logging.debug("upload job_id = %s", upload_job_id)

        upload_job_progress = client.get_job_progress(upload_job_id)
        logging.debug("Job Progess = %s", upload_job_progress)

        # upload_tasks_without_batchId = client.uploadTasksWithoutBatchId(projectId, "batch", '/home/dang/Downloads/DataTurks.xlsx', 'Excel')
        # logging.debug(upload_tasks_without_batchId)

        # getBatch = client.get_batch(projectId)
        # logging.debug(getBatch)

        # project_info = client.getProjectInfoByID(projectId)
        # logging.debug(project_info)

        # project_users = client.getProjectUsers(projectId)
        # logging.debug(project_users)

        

        # batch_status = client.getBatchStatus(projectId,10)
        # logging.debug(batch_status)

        

        # import_task_url = client.importTasksUrl(projectId=projectId)
        # logging.debug(import_task_url)




logging.debug('Hello')
test = Test()
test.main()
