from tableau_rest import Tools
import requests  # Contains methods used to make HTTP requests
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML
from datetime import datetime, timedelta
import time
import json


def query_schedule(authentication, name="", frequency="", type=""):
    """
      Gets the schedule info and stores it
      :param frequency:
      :param authentication: authentication object that grants user access to API calls and holds any signin info
      :param name: the name of the schedule
      :return:
      """
    done = False
    page_size = 100
    page_number = 1
    total_returned = 0

    while not (done):

        url = authentication.server + "/api/{0}/schedules".format(Tools.VERSION)
        url += "?pageSize={0}&pageNumber={1}".format(page_size, page_number)

        server_response = requests.get(url, headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 200)
        xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))
        # Get total number of records from the <pagination> element
        total_available = xml_response.find('.//t:pagination',
                                            namespaces={'t': "http://tableau.com/api"}).attrib['totalAvailable']
        # Note! Need to convert "total_available" to integer
        total_available = int(total_available)

        page_number += 1
        total_returned += page_size
        schedules = xml_response.findall('.//t:schedule', namespaces=Tools.XMLNS)
        output_schedules = []
        for s in schedules:
            if name != "":
                if s.get('name') == name:
                    schedule = Schedule(authentication, s.get('name'), s.get('id'), s.get('state'), s.get('priority'),
                                        s.get('createdAt'), s.get('updatedAt'), s.get('type'), s.get('frequency'),
                                        s.get('nextRunAt'))
                    return schedule
            if frequency != "":
                if s.get('frequency') == frequency:
                    if type != "":
                        if s.get('type') == type:
                            schedule = Schedule(authentication, s.get('name'), s.get('id'), s.get('state'),
                                                s.get('priority'),
                                                s.get('createdAt'), s.get('updatedAt'), s.get('type'),
                                                s.get('frequency'),
                                                s.get('nextRunAt'))
                    else:
                        schedule = Schedule(authentication, s.get('name'), s.get('id'), s.get('state'),
                                            s.get('priority'),
                                            s.get('createdAt'), s.get('updatedAt'), s.get('type'), s.get('frequency'),
                                            s.get('nextRunAt'))
                    output_schedules.append(schedule)
            else:
                if type != "":
                    if s.get('type') == type:
                        schedule = Schedule(authentication, s.get('name'), s.get('id'), s.get('state'),
                                            s.get('priority'),
                                            s.get('createdAt'), s.get('updatedAt'), s.get('type'), s.get('frequency'),
                                            s.get('nextRunAt'))
                        output_schedules.append(schedule)
        if total_returned >= total_available:
            done = True

    if len(output_schedules) > 0:
        return output_schedules
    error = "Schedule named '{0}' not found.".format(name)
    raise LookupError(error)


def query_tasks(authentication, task_id="", schedule_id=""):
    """
         Gets the task info and stores it
         :param schedule_id:
         :param authentication: authentication object that grants user access to API calls and holds any signin info
         :param task_id: task ID for searching for specific task
         :return:
         """
    if task_id == "":

        url = authentication.server + "/api/{0}/sites/{1}/tasks/extractRefreshes".format(Tools.VERSION,
                                                                                         authentication.site_id)
        # url += "?pageSize={0}&pageNumber={1}".format(page_size, page_number)

        server_response = requests.get(url, headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 200)
        xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))
        # Get total number of records from the <pagination> element
        # total_available = xml_response.find('.//t:pagination',
        #           namespaces={'t': "http://tableau.com/api"}).attrib['totalAvailable']
        # Note! Need to convert "total_available" to integer
        # total_available = int(total_available)

        # page_number += 1
        # total_returned += page_size
        tasks = xml_response.findall('.//t:tasks', namespaces=Tools.XMLNS)
        output_tasks = []
        if not schedule_id == "":
            for t in tasks:
                get_schedule = t.find('.//t:schedule', namespaces=Tools.XMLNS)
                if schedule_id == get_schedule.get('id'):
                    extract_refresh = t.find('.//t:extractRefresh', namespaces=Tools.XMLNS)
                    extract_id = extract_refresh.get('id')
                    extract_priority = extract_refresh.get('priority')
                    extract_fails = extract_refresh.get('consecutiveFailedCount')
                    extract_type = extract_refresh.get('type')
                    try:
                        content_id = {"datasource": t.find('.//t:datasource', namespaces=Tools.XMLNS).get('id')}
                    except AttributeError:
                        content_id = {"workbook": t.find('.//t:workbook', namespaces=Tools.XMLNS).get('id')}
                    schedule = Schedule(authentication, get_schedule.get('name'), get_schedule.get('id'),
                                        get_schedule.get('state'), get_schedule.get('priority'),
                                        get_schedule.get('createdAt'), get_schedule.get('updatedAt'),
                                        get_schedule.get('type'), get_schedule.get('frequency'),
                                        get_schedule.get('nextRunAt'))
                    task = Task(authentication, extract_id, extract_priority, extract_fails, extract_type, schedule,
                                content_id)
                    output_tasks.append(task)
        elif schedule_id == "":
            for t in tasks:
                extract_refresh = t.find('.//t:extractRefresh', namespaces=Tools.XMLNS)
                extract_id = extract_refresh.get('id')
                extract_priority = extract_refresh.get('priority')
                extract_fails = extract_refresh.get('consecutiveFailedCount')
                extract_type = extract_refresh.get('type')
                get_schedule = t.find('.//t:schedule', namespaces=Tools.XMLNS)
                schedule = Schedule(authentication, get_schedule.get('name'), get_schedule.get('id'),
                                    get_schedule.get('state'), get_schedule.get('priority'),
                                    get_schedule.get('createdAt'), get_schedule.get('updatedAt'),
                                    get_schedule.get('type'), get_schedule.get('frequency'),
                                    get_schedule.get('nextRunAt'))
                try:
                    content_id = {"datasource": t.find('.//t:datasource', namespaces=Tools.XMLNS).get('id')}
                except AttributeError:
                    content_id = {"workbook": t.find('.//t:workbook', namespaces=Tools.XMLNS).get('id')}
                task = Task(authentication, extract_id, extract_priority, extract_fails, extract_type, schedule,
                            content_id)
                output_tasks.append(task)
        # if total_returned >= total_available:
        #    done = True
    else:

        url = authentication.server + "/api/{0}/sites/{1}/tasks/extractRefreshes".format(Tools.VERSION,
                                                                                         authentication.site_id)
        # url += "?pageSize={0}&pageNumber={1}".format(page_size, page_number)

        server_response = requests.get(url, headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 200)
        xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))
        # Get total number of records from the <pagination> element
        # total_available = xml_response.find('.//t:pagination',
        #           namespaces={'t': "http://tableau.com/api"}).attrib['totalAvailable']
        # Note! Need to convert "total_available" to integer
        # total_available = int(total_available)

        # page_number += 1
        # total_returned += page_size
        tasks = xml_response.findall('.//t:tasks', namespaces=Tools.XMLNS)
        output_tasks = []
        if not schedule_id == "":
            for t in tasks:
                get_schedule = t.find('.//t:schedule', namespaces=Tools.XMLNS)
                if schedule_id == get_schedule.get('id'):
                    extract_refresh = t.find('.//t:extractRefresh', namespaces=Tools.XMLNS)
                    extract_id = extract_refresh.get('id')
                    extract_priority = extract_refresh.get('priority')
                    extract_fails = extract_refresh.get('consecutiveFailedCount')
                    extract_type = extract_refresh.get('type')
                    try:
                        content_id = {"datasource": t.find('.//t:datasource', namespaces=Tools.XMLNS).get('id')}
                    except AttributeError:
                        content_id = {"workbook": t.find('.//t:workbook', namespaces=Tools.XMLNS).get('id')}
                    schedule = Schedule(authentication, get_schedule.get('name'), get_schedule.get('id'),
                                        get_schedule.get('state'), get_schedule.get('priority'),
                                        get_schedule.get('createdAt'), get_schedule.get('updatedAt'),
                                        get_schedule.get('type'), get_schedule.get('frequency'),
                                        get_schedule.get('nextRunAt'))
                    task = Task(authentication, extract_id, extract_priority, extract_fails, extract_type, schedule,
                                content_id)
                    output_tasks.append(task)
        elif schedule_id == "":
            for t in tasks:
                if task_id == t.find('.//t:extractRefresh', namespaces=Tools.XMLNS).get('id'):
                    extract_refresh = t.find('.//t:extractRefresh', namespaces=Tools.XMLNS)
                    extract_id = extract_refresh.get('id')
                    extract_priority = extract_refresh.get('priority')
                    extract_fails = extract_refresh.get('consecutiveFailedCount')
                    extract_type = extract_refresh.get('type')
                    get_schedule = t.find('.//t:schedule', namespaces=Tools.XMLNS)
                    schedule = Schedule(authentication, get_schedule.get('name'), get_schedule.get('id'),
                                        get_schedule.get('state'), get_schedule.get('priority'),
                                        get_schedule.get('createdAt'), get_schedule.get('updatedAt'),
                                        get_schedule.get('type'), get_schedule.get('frequency'),
                                        get_schedule.get('nextRunAt'))
                    try:
                        content_id = {"datasource": t.find('.//t:datasource', namespaces=Tools.XMLNS).get('id')}
                    except AttributeError:
                        content_id = {"workbook": t.find('.//t:workbook', namespaces=Tools.XMLNS).get('id')}
                    task = Task(authentication, extract_id, extract_priority, extract_fails, extract_type, schedule,
                                content_id)
                    output_tasks.append(task)
    if len(output_tasks) > 0:
        return output_tasks
    error = "Tasks associated with '{0}{1}' were not found.".format(task_id, schedule_id)
    raise LookupError(error)


def set_task_schedule(authentication, task_id, schedule_id, session, repos_url=""):
    """
    Using the vizportal API rather than the REST API change a tasks schedule. Not recommended to bypass the REST API.
    :param authentication:
    :param task_id:
    :param schedule_id:
    :param session:
    :param repos_url:
    :return:
    """
    if repos_url:
        url = repos_url + "/vizportal/api/web/v1/setExtractTasksSchedule"
    else:
        url = self.authentication.server + "/vizportal/api/web/v1/setExtractTasksSchedule"
    ET.tostring(xml_params)

    payload = "{\"method\":\"setExtractTasksSchedule\",\"params\":{\"ids\":[\"%s\"], \"scheduleId\":\"%s\"}}" % (
        task_id, schedule_id)
    xsrf_token = authentication.get_viz_token()
    # Make the request to server
    server_response = session.post(url, headers={
        'content-type': "application/json;charset=UTF-8",
        'accept': "application/json, text/plain, */*",
        'cache-control': "no-cache",
        'X-XSRF-TOKEN': xsrf_token},
                                   data=payload)
    Tools.check_status(server_response, 200)

    # ASCII encode server response to enable displaying to console
    server_response = Tools.encode_for_display(server_response.text)


class Job:
    def __init__(self, authentication):
        self.authentication = authentication


class Task(Job):
    """
    A Task object inheriting from the Job class. Tasks represent the repeating item, that is used in a job.
    """
    def __init__(self, authentication, task_id, priority, consecutive_fails, type, schedule, content_id):
        """
        Task's init function builds all the information for the object.
        :param authentication: <Auth Obj> for handling any authentication calls.
        :param task_id:
        :param priority:
        :param consecutive_fails:
        :param type:
        :param schedule:
        :param content_id:
        """
        super(Task, self).__init__(authentication)
        self.task_id = task_id
        self.priority = priority
        self.consecutive_fails = consecutive_fails
        self.type = type
        self.schedule = schedule
        self.content_id = content_id
        self.workgroup_id = ""

    def set_task_schedule(self, task_id, schedule_id, session, repos_url=""):
        """
        Again built using the vizportal API which is not recommended.
        :param task_id:
        :param schedule_id:
        :param session:
        :param repos_url:
        :return:
        """
        if repos_url:
            url = repos_url + "/vizportal/api/web/v1/setExtractTasksSchedule"
        else:
            url = self.authentication.server + "/vizportal/api/web/v1/setExtractTasksSchedule"

        payload = "{\"method\":\"setExtractTasksSchedule\",\"params\":{\"ids\":[\"%s\"], \"scheduleId\":\"%s\"}}" % (
            task_id, schedule_id)
        xsrf_token = self.authentication.get_viz_token()
        # Make the request to server
        server_response = session.post(url, headers={
            'content-type': "application/json;charset=UTF-8",
            'accept': "application/json, text/plain, */*",
            'cache-control': "no-cache",
            'X-XSRF-TOKEN': xsrf_token},
                                       data=payload)
        Tools.check_status(server_response, 200)

        # ASCII encode server response to enable displaying to console
        server_response = Tools.encode_for_display(server_response.text)

    def get_workgroup_id(self, session, repos_url=""):
        """
        for use with the vizportal API the repository(workgroup) id is required, this function gets said id.
        :param session:
        :param repos_url:
        :return:
        """
        if repos_url:
            url = repos_url + "/vizportal/api/web/v1/setExtractTasksSchedule"
        else:
            url = self.authentication.server + "/vizportal/api/web/v1/setExtractTasksSchedule"

        payload = "{\"method\":\"getExtractTasks\",\"params\":{\"filter\":{\"operator\":\"and\",\"clauses\":[{\"operator\":\"eq\",\"field\":\"siteId\",\"value\":\"4\"}]},\"order\":[{\"field\":\"targetName\",\"ascending\":true}],\"page\":{\"startIndex\":0,\"maxItems\":1000}}}"
        xsrf_token = self.authentication.get_viz_token()
        # Make the request to server
        server_response = session.post(url, headers={
            'content-type': "application/json;charset=UTF-8",
            'accept': "application/json, text/plain, */*",
            'cache-control': "no-cache",
            'X-XSRF-TOKEN': xsrf_token}, data=payload)
        response_json = json.loads(server_response.text)
        returned_task = response_json["result"]["tasks"]
        for s in returned_tasks:
            if s['name'] == self.name:
                # Todo not sure any frame of validation here, task id is the only consistent which this is identifying.
                self.workgroup_id = (s['id'])
        print(server_response)
        Tools.check_status(server_response, 200)
        # ASCII encode server response to enable displaying to console
        server_response = Tools.encode_for_display(server_response.text)

    def get_refresh(self):
        pass

    def run(self):
        pass


class Schedule(Job):
    """
    Object designed to hold all information and functions regarding Schedules.
    """
    def __init__(self, authentication, name, schedule_id="", state="", priority="", created_at="", updated_at="",
                 type="", frequency="", next_run_at=""):
        """
        Build the object
        :param authentication:
        :param name:
        :param schedule_id:
        :param state:
        :param priority:
        :param created_at:
        :param updated_at:
        :param type:
        :param frequency:
        :param next_run_at:
        """
        super(Schedule, self).__init__(authentication)
        self.name = name
        self.schedule_id = schedule_id
        self.state = state
        self.priority = priority
        self.created_at = created_at
        self.updated_at = updated_at
        self.type = type
        self.frequency = frequency
        if not next_run_at == "":
            self.next_run_at = datetime.strptime(next_run_at, '%Y-%m-%dT%H:%M:%SZ')
        self.workgroup_id = 0

    def create(self, type, start_time, frequency, interval="", end_time="", execution_order="Parallel", priority="50"):
        url = self.authentication.server + "/api/{0}/schedules".format(Tools.VERSION)
        # Builds the request
        xml_payload = ET.Element('tsRequest')
        schedule_element = ET.SubElement(xml_payload, 'schedule', name=self.name, priority=priority, type=type,
                                         frequency=frequency, executionOrder=execution_order)
        fd = ET.SubElement(schedule_element, 'frequencyDetails', start=start_time, end=end_time)

        if frequency != "Daily":
            intervals_element = ET.SubElement(fd, 'intervals')
            if frequency == "Hourly":
                ET.SubElement(intervals_element, 'interval', hours=interval, minutes=interval)
            elif frequency == "Weekly":
                ET.SubElement(intervals_element, 'interval', weekDay=interval)
            elif frequency == "Monthly":
                ET.SubElement(intervals_element, 'interval', monthDay=interval)
        xml_payload = ET.tostring(xml_payload)
        # Make the request to server
        server_response = requests.post(url, headers={'x-tableau-auth': self.authentication.get_token()},
                                        data=xml_payload)
        Tools.check_status(server_response, 201)

        # ASCII encode server response to enable displaying to console
        server_response = Tools.encode_for_display(server_response.text)

        # Reads and parses the response
        parsed_response = ET.fromstring(server_response)

    def delete(self):
        url = self.authentication.server + "/api/{0}/schedules/{1}".format(Tools.VERSION, self.schedule_id)

        server_response = requests.delete(url, headers={'x-tableau-auth': self.authentication.get_token()})
        Tools.check_status(server_response, 204)

    def update(self, name="", type="", start_time="", frequency="", interval="", end_time="",
               execution_order="Parallel", priority=""):
        if name == "":
            name = self.name

        if type == "":
            type = self.type

        if frequency == "":
            frequency = self.frequency

        if start_time == "":
            # (YYYY-MM-DDTHH:MM:SSZ) needs HH:MM:SS
            start_time = self.next_run_at  # datetime.strptime(self.next_run_at, '%Y-%m-%dT%H:%M:%SZ')
            if time.localtime().tm_isdst == 1:
                start_time += timedelta(hours=1)

            start_time = start_time.strftime('%H:%M:%S')

        if priority == "":
            priority = self.priority

        url = self.authentication.server + "/api/{0}/schedules/{1}".format(Tools.VERSION, self.schedule_id)
        # Builds the request
        xml_payload = ET.Element('tsRequest')
        schedule_element = ET.SubElement(xml_payload, 'schedule', name=name, priority=priority, type=type,
                                         frequency=frequency, executionOrder=execution_order)
        fd = ET.SubElement(schedule_element, 'frequencyDetails', start=start_time, end=end_time)

        if frequency != "Daily":
            intervals_element = ET.SubElement(fd, 'intervals')
            if frequency == "Hourly":
                ET.SubElement(intervals_element, 'interval', hours=interval, minutes=interval)
            elif frequency == "Weekly":
                ET.SubElement(intervals_element, 'interval', weekDay=interval)
            elif frequency == "Monthly":
                ET.SubElement(intervals_element, 'interval', monthDay=interval)
        xml_payload = ET.tostring(xml_payload)
        # Make the request to server
        server_response = requests.put(url, headers={'x-tableau-auth': self.authentication.get_token()},
                                       data=xml_payload)
        Tools.check_status(server_response, 200)

        # ASCII encode server response to enable displaying to console
        server_response = Tools.encode_for_display(server_response.text)

        # Reads and parses the response
        parsed_response = ET.fromstring(server_response)

    def get_workgroup_id(self, session, repos_url=""):
        if repos_url:
            url = repos_url + "/vizportal/api/web/v1/getSchedules"
        else:
            url = self.authentication.server + "/vizportal/api/web/v1/getSchedules"

        payload = "{\"method\":\"getSchedules\",\"params\":{\"filter\":{\"operator\":\"and\",\"clauses\":[{\"operator\":\"eq\", \"field\":\"siteId\", \"value\":\"4\"}]},\"order\":[{\"field\":\"name\",\"ascending\":true}],\"page\":{\"startIndex\":0,\"maxItems\":1000}}}"
        xsrf_token = self.authentication.get_viz_token()
        # Make the request to server
        server_response = session.post(url, headers={
            'content-type': "application/json;charset=UTF-8",
            'accept': "application/json, text/plain, */*",
            'cache-control': "no-cache",
            'X-XSRF-TOKEN': xsrf_token}, data=payload)
        response_json = json.loads(server_response.text)
        returned_schedules = response_json["result"]["schedules"]
        for s in returned_schedules:
            if s['name'] == self.name:
                self.set_workgroup_id(s['id'])
        Tools.check_status(server_response, 200)
        # ASCII encode server response to enable displaying to console
        server_response = Tools.encode_for_display(server_response.text)

    def set_workgroup_id(self, id):
        self.workgroup_id = int(id)

    def query_tasks(self):
        done = False
        page_size = 100
        page_number = 1
        total_returned = 0

        while not (done):
            url = self.authentication.server + "/api/{0}/sites/{1}/schedules/{2}/extracts".format(Tools.VERSION,
                                                                                                  self.authentication.site_id,
                                                                                                  self.schedule_id)
            url += "?pageSize={0}&pageNumber={1}".format(page_size, page_number)

            server_response = requests.get(url, headers={'x-tableau-auth': self.authentication.get_token()})
            Tools.check_status(server_response, 200)
            xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))
            # Get total number of records from the <pagination> element
            total_available = xml_response.find('.//t:pagination',
                                                namespaces={'t': "http://tableau.com/api"}).attrib['totalAvailable']
            # Note! Need to convert "total_available" to integer
            total_available = int(total_available)

            page_number += 1
            total_returned += page_size
            tasks = xml_response.findall('.//t:extract', namespaces=Tools.XMLNS)
            output_tasks = []
            for t in tasks:
                content_id = ""
                try:
                    content_id = {"datasource": t.find('.//t:datasource', namespaces=Tools.XMLNS).get('id')}
                    print("Datasource {}".format(content_id))
                except AttributeError:
                    content_id = {"workbook": t.find('.//t:workbook', namespaces=Tools.XMLNS).get('id')}
                    print("Workbook {}".format(content_id))
                # extract_refresh = t.find('.//t:extractRefresh', namespaces=Tools.XMLNS)
                extract_id = t.get('id')
                extract_priority = t.get('priority')
                # extract_fails = extract_refresh.get('consecutiveFailedCount')
                extract_type = t.get('type')
                schedule = self
                task = Task(self.authentication, extract_id, extract_priority, 0, extract_type,
                            schedule, content_id)
                output_tasks.append(task)

            if total_returned >= total_available:
                done = True

        if len(output_tasks) > 0:
            return output_tasks
        error = "Tasks for the schedule '{0}' not found.".format(self.name)
        raise LookupError(error)
