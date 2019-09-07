import os
import sys
import json
import time
import fire
import signal
import emoji
import pyfiglet
import requests
import asyncio
import copy
import pathlib
import yaml
from colorama import Fore, Back, Style, init
from termcolor import colored, cprint
from .utils import net
from loguru import logger
from tenacity import retry, wait_fixed
from .lib.process import process_data
from .utils.runtime import load_runtime, write_runtime
from .utils.process import Process, is_alive, ErrorCollector
from .utils.kafka import KafkaMonitor, KafkaSender
from .utils.task import task_divide, Task
from .lib.trigger import Trigger, custom_process, event_process, time_process
from flask import Flask, request, jsonify
from multiprocessing import Queue
from pygments import highlight
from pygments.lexers.data import YamlLexer

init()
DEFAULT_CONFIG = {
    "type": "Executor_Type",
    "tags": [],
    "meta": {
        "version": "0.0.1",
        "description": "test"
    },
    "controller_url": "http://127.0.0.1:5917",
    "host": "127.0.0.1",  # 自身IP，用于控制器健康检查
    "log_level": "DEBUG",
    "log_file_path": os.getcwd()
}


def initialize_logger(log_file_path=os.getcwd(), log_file_name=None, file_log_level="INFO", stderr_log_level="DEBUG"):
    """
    Get logging handler

    :param log_file_path: the path of logging file
    :param log_file_name: the filename of logging file
    :param file_log_level: the file logging level 
    :param stderr_log_level: the stderr logging level 
    :returns: loguru.logger
    """
    log_file_name = log_file_name or "app.log"
    logger.remove()
    logger.add("%s/%s" % (log_file_path, log_file_name), backtrace=True, rotation="00:00",
               retention="30 days", compression="zip", enqueue=True, level=file_log_level)
    logger.add(sys.stderr, level=stderr_log_level)
    return logger


class Executor(object):
    """Executor class."""
    DEFAULT_POOL_SIZE = {"loop": 1, "async": 100, "thread": 100, "process": 10}
    RETRY_INTERVAL = 3

    # --------------------  Init & Config--------------------------------------
    def __init__(self, config_file=os.getcwd() + "/template.yaml"):

        # Initialize variables
        self.config_file = config_file
        self.health_check_options = {
            "action": None,
            "path": None
        }
        self.triggers = {}
        self.preprocess_func = {}
        self.afterprocess_func = {}
        self.handle_method = None
        self.handle_func = None
        self.handle_config = {}
        self.name = None
        self.config = {}
        self.runtime = {}
        self.ready = True
        self.event_task = {}
        self.running = True
        self.kafka_arrangement = {}

    def init_runtimedump(self):
        self.runtime = load_runtime()
        if not self.runtime:
            self.runtime = {
                'name': "Unregistered",
                'type': self.config["type"],
                "tags": self.config["tags"],
                'process': {
                    "main": os.getpid(),
                    "api": "",
                    "triggers": []
                }
            }
            write_runtime(self.runtime)

    def reload_config(self):
        try:
            with open(self.config_file, "r") as f:
                self.config = yaml.safe_load(f.read())
            assert {"host", "type", "tags", "controller_url"} <= set(self.config.keys())
            if "log_level" not in self.config.keys():
                self.config["log_level"] = "INFO"

        except FileNotFoundError:
            logger.error("Config File Is Not Found")
            exit(1)
        except AssertionError:
            logger.error("Error in parse config_file or short of important keys: type, tags, controller_url")
            exit(2)
        except Exception as err:
            logger.error("Unknown Error:")
            logger.exception(err)
            exit(3)

    def reset_cmd(self):
        """
        Reset the command tool
        """
        fire.Fire({
            "start": self.start,
            "stop": self.stop,
            "restart": self.restart,
            "show_config": self.show_config,
            "init": self.init_config,
            "status": self.status,
            "config": self.edit_config
        })

    # ----------------- Data Processing ------------------------------------------------
    def preprocess(self, data_type, timeout):
        """
        preprocess wrapper
        :param name: preprocess method name
        :param timeout: preprocess timeout
        :return: wrapper
        """

        def wrapper(func):
            self.preprocess_func[data_type] = (func, timeout)

        return wrapper

    def afterprocess(self, data_type, timeout):
        """
        afterprocess wrapper
        :param name: afterprocess method name
        :param timeout: afterprocess timeout
        :return: wrapper
        """

        def wrapper(func):
            self.afterprocess_func[data_type] = (func, timeout)

        return wrapper

    def handle_each_input(self, timeout, strategy=None, pool_size=None):
        """
        Define a function to handle each single input by a wrapper
        :param timeout: the timeout for each input to run
        :param strategy: the strategy of execute, "async", "loop", "thread", "process"
        :param pool_size: the execute pool size
        :return: wrapper
        """
        if strategy is None:
            logger.warning("Unspecified execution strategy, loop for default")
            strategy = "loop"
        if strategy not in ["async", "loop", "thread", "process"]:
            raise ValueError("Unsupported strategy: %s", strategy)
        if pool_size is None:
            logger.warning(
                "Unspecified pool size, use default for %s: %d" % (strategy, self.DEFAULT_POOL_SIZE[strategy]))
            pool_size = self.DEFAULT_POOL_SIZE[strategy]
        if pool_size <= 0:
            raise ValueError("Pool size must be >=0")

        def wrapper(func):
            if self.handle_method is not None:
                logger.warning("handle function is defined repeatedly, use the last one")
            if strategy == "async" and not asyncio.iscoroutinefunction(func):
                raise TypeError("Only coroutine function can run asynchronously")
            self.handle_method = "single"
            self.handle_func = func
            self.handle_config = {
                "timeout": timeout,
                "strategy": strategy,
                "pool_size": pool_size
            }

        return wrapper

    def handle_all_inputs(self, timeout):
        """
        Define a function to handle total input by a wrapper
        :param timeout: the timeout for each input, the True Timeout is timeout*len(inputs)
        :return: wrapper
        """

        def wrapper(func):
            if self.handle_method is not None:
                logger.warning("handle function is defined repeatedly, use the last one")
            self.handle_method = "total"
            self.handle_func = func
            self.handle_config = {
                "timeout": timeout,
                "strategy": "total",
                "pool_size": 1
            }

        return wrapper

    def update_config(self):
        try:
            reboot = request.json["reboot"]
            config = request.json["config"]
        except:
            logger.error("Error in parse params:\n", exc_info=True)
            return {"state": False, "info": "error in parsing params"}, 400
        for key in config:
            self.config[key] = config[key]
        if reboot:
            self.restart()
        return {"state": True, "info": "Success"}, 200

    @retry(wait=wait_fixed(3))
    def register(self):
        """
        Register request
        :param port: api port
        """
        try:
            data = {
                "type": self.config["type"],
                "tags": self.config["tags"],
                "message": "register"
            }
            if self.name is not None:
                data["name"] = self.name

            re = requests.post(self.config["controller_url"] + "/executor/health", json=data)
            if re.status_code // 100 != 2:
                logger.error("Error in register:" + re.text)
                raise IOError("Error in register")
            response = re.json()
            self.cookie = re.headers["Set-Cookie"]
            self.name = response["name"]
            self.kafka_url = response["config"]["kafka_url"]
            self.kafka_topic = response["config"]["kafka_topic"]
            self.kafka_group = response["config"]["kafka_group"]
            if response["segment"]:
                self.kafka_arrangement = response["segment"]
                self.queue.put_nowait(response["segment"])
        except Exception as err:
            logger.exception(err)
            raise

    @retry(wait=wait_fixed(3))
    def receive_report(self, task_id, branch_id, position, input_length, partition, offset):
        """
        First report
        :param message: Structured kafka_message
        :param partition: message partition
        :param offset: message offset
        :return: whether to do this task of not
        """
        try:
            data = {
                "task_id": task_id,
                "branch_id": branch_id,
                "input_length": input_length,
                "current_position": position,
                "partition": partition,
                "offset": offset
            }
            re = requests.post(self.config["controller_url"] + "/task", json=data, headers={"Cookie": self.cookie})
            response = re.json()
            if not response["state"]:
                raise ValueError("Error in controller response: %s" % re.text)

            if response["operation"]:
                return response["operation"], response["config"]
            else:
                return response["operation"], None
        except Exception as err:
            logger.exception(err)
            raise

    @retry(wait=wait_fixed(3))
    def finish_report(self, task, output_length, events, has_output, errors):
        try:
            data = {
                "type": "finished",
                "task_id": task.task_id,
                "branch_id": task.branch_id,
                "current_position": task.position,
                "output_length": output_length,
                "event": events,
                "has_output": has_output,
                "errors": errors,
            }
            logger.debug("sending finish report")
            re = requests.put(self.config["controller_url"] + "/task", json=data, headers={"Cookie": self.cookie})
            response = re.json()
            if response["state"] is False:
                raise ValueError("Error in controller response: %s" % re.text)
            return response["next"]
        except Exception as err:
            logger.exception(err)
            raise

    @retry(wait=wait_fixed(3))
    def end_report(self, task, has_output, id, result, errors):
        try:
            data = {
                "type": "end",
                "task_id": task.task_id,
                "branch_id": task.branch_id,
                "branch_amount": id,
                "current_position": task.position,
                "has_output": has_output,
                "result": result,
                "errors": errors
            }
            re = requests.put(self.config["controller_url"] + "/task", json=data, headers={"Cookie": self.cookie})
            response = re.json()
            print(response)
            if response["state"] is False:
                raise ValueError("Error in controller response: %s" % re.text)
            if "segment" in response.keys() and response["segment"] is not None:
                self.queue.put_nowait(self.kafka_arrangement)
        except Exception as err:
            logger.exception(err)
            raise

    def emit_event(self, event: str):
        """
        Use by developer, emit a event in process
        :param event: event string
        """
        self.events.append(event)

    def data_process(self, task, data, partition=None, offset=None):
        """
        Receive input and task information and execute data processing , then output to kafka
        """
        operation, config = self.receive_report(task.task_id, task.branch_id, task.position, len(data),
                                               partition, offset)


        if not operation:
            logger.info("The controller prevents the task from executing, skip!")
            return

        # remove filter

        # handle inputs
        self.events = []
        error_collector = ErrorCollector()
        preprocess = task.data_type
        # Preprocess
        if preprocess:
            preprocessed, errors = process_data(data, config,
                                                func=self.preprocess_func[preprocess][0],
                                                timeout=self.preprocess_func[preprocess][1],
                                                mode="total")
            error_collector.add_many("preprocess", errors)
        else:
            preprocessed = data

        if len(preprocessed) == 0:
            logger.warning("No valid preprocessing result!")
            processed = []
            error_collector.add("preprocess", "No valid preprocessing result!")
        else:
            # Main process
            processed, errors = process_data(preprocessed, config,
                                             func=self.handle_func,
                                             timeout=self.handle_config["timeout"],
                                             mode=self.handle_config["strategy"],
                                             pool_size=self.handle_config["pool_size"])
            if processed is None:
                processed = []

        has_output = True
        if len(processed) == 0:
            has_output = False
        else:
            # check end condition
            if "depth" in task.end_condition["builtin"] and task.properties["builtin"]["depth"] + 1 > \
                    task.end_condition["builtin"]["depth"]:
                has_output = False
            elif "create_at" in task.end_condition["builtin"] and time.time() - task.properties["builtin"][
                "create_at"] > \
                    task.end_condition["builtin"]["create_at"]:
                has_output = False

        outputs = self.finish_report(task, len(processed), self.events, has_output, error_collector.export())

        # check externals
        # [FIX ME]

        # do output
        id = 0
        if has_output:
            task.properties["builtin"]["depth"] += 1
            sender = KafkaSender(self.kafka_url)
            for output in outputs:
                # Afterprocess
                if output["output_type"]:
                    afterprocessed, errors = process_data(processed, config,
                                                          func=self.afterprocess_func[output["output_type"]][0],
                                                          timeout=self.afterprocess_func[output["output_type"]][1],
                                                          mode="total")
                    error_collector.add_many("afterprocess", errors)
                else:
                    afterprocessed = processed
                    errors = []
                if len(afterprocessed) == 0:
                    continue
                output_data = task_divide(afterprocessed, output["granularity"])
                for data in output_data:
                    new_message = {
                        "headers": {
                            "task_id": task.task_id,
                            "branch_id": task.branch_id + "_" + str(id),
                            "properties": task.properties,
                            "tags": output["tags"],
                            "type": output["output_type"],
                            "current_position": output["position"],
                            "end_conditions": task.end_condition
                        },
                        "body": data
                    }
                    sender.add_message(output["topic"], new_message, partition=output["partition"])
                    id += 1
            result, info = sender.send_all()
            if not result:
                logger.error("Error in sending to kafka: %s" % info)
                error_collector.add("afterprocess", info)
        else:
            result = True
            info = ""

        self.end_report(task, has_output, id, result, error_collector.export())

    # ---------------------------  Process ------------------------------------------------
    def inside_kafka_process(self):
        """
        Process, listen to the inside kafka message, and handle it
        """
        self.kafka_monitor = KafkaMonitor(self)
        while True:
            try:
                msg = self.kafka_monitor.poll()
            except Exception as err:
                logger.exception(err)
                logger.error("Error in getting kafka message")
                break
            logger.info(
                "Inside Kafka: Received kafka message, partition=%d, offset=%d" % (msg.partition(), msg.offset()))
            try:
                message = json.loads(msg.value().decode())
                logger.debug(message)
                self.properties = message["headers"]["properties"]["externals"]
            except:
                logger.error("Error in json kafka message")
                continue

            try:
                headers = message["headers"]
                task = Task(task_id=headers["task_id"], branch_id=headers["branch_id"],
                            position=headers["current_position"],
                            data_type=headers["type"], properties=headers["properties"],
                            end_condition=headers["end_conditions"])
                self.data_process(task, message["body"], partition=msg.partition(), offset=msg.offset())
            except Exception as err:
                logger.exception(err)
                logger.error("Error in data processing")
                break
        self.running = False


    # --------------------------  Trigger  --------------------------------------
    def add_trigger(self, trigger):
        """
        Add a trigger to executor's triggers
        :param trigger: (Trigger) The trigger to add
        """
        if not isinstance(trigger, Trigger):
            raise TypeError("param trigger must be an instance of Trigger")
        if trigger.name in self.triggers:
            raise ValueError("This executor already have triggers with the same name")

        self.triggers[trigger.name] = trigger
        if trigger.type == "event":
            self.event_task[trigger.name] = []
        trigger.executor = self

    def trigger(self, name, type, interval=None, event=None):
        """
        Add a trigger by wrapper
        :param name: Trigger name
        :param type: Trigger type
        :param interval: Time trigger interval
        :param event: Event trigger event name
        """

        def wrapper(func):
            if name in self.triggers:
                raise ValueError("This executor already have triggers with the same name")
            temp = Trigger(name, type, interval, event)
            temp.bind(func)
            self.triggers[name] = temp
            if type == "event":
                self.event_task[temp.name] = []
            temp.executor = self

    def receive_task(self):
        try:
            task_id = request.json["task_id"]
            branch_id = request.json["branch_id"]
            task = Task(task_id=request.json["task_id"], branch_id=request.json["branch_id"],
                        position=request.json["position"], properties=request.json["properties"],
                        end_condition=request.json["end_condition"])
            triggers = request.json["trigger"]
        except:
            logger.error("Error in parse params:\n", exc_info=True)
            return {"state": False, "info": "error in parsing params"}, 400

        for trigger in triggers:
            if trigger["name"] not in self.triggers or trigger["type"] != self.triggers[trigger["name"]].type:
                logger.error("Mismatched trigger information: " + str(trigger))
                continue
            if trigger["type"] == "time":
                process = Process("time_trigger", action=time_process, args=(
                    copy.deepcopy(self.triggers[trigger["name"]]),
                    trigger["interval"] if "interval" in trigger else self.triggers[trigger["name"]].interval, task))
                process.start()
                self.runtime["process"]["trigger"].append({"task": task, "name": trigger["name"],
                                                           "interval": trigger["interval"] if "interval" in trigger else
                                                           self.triggers[trigger["name"]].interval, "pid": process.pid})
            elif trigger["type"] == "event":
                if trigger["name"] not in self.event_task:
                    logger.error("Mismatched trigger information: " + str(trigger))
                    continue
                self.event_task[trigger["name"]].append(task)



            elif trigger["type"] == "custom":
                process = Process("custom_trigger", action=custom_process,
                                  args=(copy.deepcopy(self.triggers[trigger["name"]]), task),
                                  kwargs={"callback": self.finish_trigger})
                process.start()
                self.runtime["process"]["trigger"].append({"task": task, "name": trigger["name"], "pid": process.pid})
        write_runtime(self.runtime)
        return {"state": True, "info": "Success"}, 201

    def event_emit(self):
        event = request.json.get("event", "")
        if not event:
            logger.error("Error in parse params:\n", exc_info=True)
            return {"state": False, "info": "error in parsing params"}, 400
        if event not in self.event_task:
            return {"state": True, "info": "Success"}, 200
        for task in self.event_task[event]:
            process = Process("event_trigger", action=event_process,
                              args=(copy.deepcopy(self.triggers[event]), task),
                              kwargs={"callback": self.finish_trigger})
            process.start()
            self.runtime["process"]["trigger"].append({"task": task, "name": event, "pid": process.pid})
        write_runtime(self.runtime)
        return {"state": True, "info": "Success"}, 201

    def stop_trigger(self):
        try:
            task_id = request.json["task_id"]
            branch_id = request.json["branch_id"]
            triggers = request.json["triggers"]
        except:
            logger.error("Error in parse params:\n", exc_info=True)
            return {"state": False, "info": "error in parsing params"}, 400
        for trigger in triggers:
            for item in self.runtime["process"]["trigger"]:
                if item["task"].task_id == task_id and item["task"].branch_id == branch_id and trigger["name"] == item[
                    "name"]:
                    os.kill(item["pid"])
                    self.runtime["process"]["trigger"].remove(item)
                    break
        write_runtime(self.runtime)
        return {"state": True, "info": "Success"}, 201

    def finish_trigger(self, pid):
        for item in self.runtime["process"]["trigger"]:
            if item["pid"] == pid:
                self.runtime["process"]["trigger"].remove(item)
                break

    # -------------------------  Others  -------------------------------------
    def health_report(self, queue, interval = 5):
        s = requests.Session()
        assignment = self.kafka_arrangement
        while True:
            try:
                resp = s.post(url = self.config["controller_url"] + "/executor/health",
                              json = {"message": "normal"},
                              headers={"Cookie": self.cookie})
                assert resp.status_code // 100 == 2
                
                data = resp.json()
                print(data)
                if data["segment"] != assignment:
                    print(assignment)
                    assignment  = data["segment"]
                    queue.put_nowait(data["segment"])
            except AssertionError:
                logger.error("Error in health check, code: %d, Info: %s" % (resp.status_code, resp.text))
            except Exception as err:
                logger.error("Error in health check, Error %s" % err.__repr__())
            time.sleep(interval)
        s.close()






    # ------------------------- Operation ----------------------------------
    def start(self):
        # --------- Init Config -----------

        # Reload the config
        self.reload_config()
        logger.debug(self.config)
        initialize_logger(log_file_path=self.config["log_file_path"], stderr_log_level=self.config["log_level"].upper())

        # Initialize RuntimeDump Object
        self.init_runtimedump()

        if self.runtime["process"]["main"] != os.getpid() and is_alive(self.runtime["process"]["main"]):
            logger.error("The executor is running now......")
            return

        cprint(pyfiglet.figlet_format('Autumn', font='graffiti'),
               'green', attrs=['blink', 'bold'])

        port = int(self.config["port"]) if "port" in self.config.keys() else net.get_free_port()

        # ---------- Register -----------

        self.queue = Queue(10)
        self.register()
        self.runtime["name"] = self.name

        # ---------- Start API Process -----------

        self.api_process = Process("api", action=self.health_report, args=(self.queue,))
        self.api_process.start()
        self.runtime["process"]["api"] = self.api_process.pid

        # ---------- Start Triggers Process------------

        # pass

        # ---------- Main Process set daemon
        self.ready = True
        self.runtime["process"]["main"] = os.getpid()

        write_runtime(self.runtime)
        self.inside_kafka_process()

    def restart(self):
        # get name
        self.runtime = load_runtime()
        self.name = self.runtime.get("name")
        self.mode = True
        # Reload the config
        self.stop()
        # Initialize RuntimeDump Object
        self.start()

        cprint(pyfiglet.figlet_format('Autumn', font='graffiti'),
               'green', attrs=['blink', 'bold'])
        logger.info("restart")

    def kill_other_process(self):
        os.kill(self.runtime.get("inside_kafka_pid"), signal.SIGKILL)

    def stop(self):
        self.runtime = load_runtime()
        api_pid = self.runtime["process"]["api"]
        os.kill(api_pid, signal.SIGKILL)
        main_pid = self.runtime["process"]["main"]
        os.kill(main_pid, signal.SIGKILL)

        cprint(pyfiglet.figlet_format('Autumn', font='graffiti'), 'green', attrs=['blink', 'bold'])
        logger.info("stop")

    def status(self):
        # Reload the config
        self.reload_config()
        # Initialize RuntimeDump Object
        self.runtime = load_runtime()

        cprint(pyfiglet.figlet_format('Autumn', font='graffiti'), 'green', attrs=['blink', 'bold'])
        print(colored(':: Basic', 'red', attrs=["bold"]))
        print(colored('---------------', 'red', attrs=["bold"]))
        print(Fore.GREEN + "Name: ", end="")
        print(Fore.WHITE + "%s" % (self.runtime.get("name")))
        print(Fore.GREEN + "Type: ", end="")
        print(Fore.WHITE + "%s" % (self.runtime.get("type")))

        print(Fore.GREEN + "Source Type: ", end="")
        print(Fore.WHITE + "%s\n\n" % (self.runtime.get("source_type")))

        print(colored(':: Process', 'red', attrs=["bold"]))
        print(colored('---------------', 'red', attrs=["bold"]))
        print(Fore.GREEN + "Main:", end="\n")
        print(colored('   - ', 'red', attrs=["bold"]), end="")
        print(Fore.GREEN + "PID: ", end="")
        print(Fore.WHITE + "%s  " % (self.runtime["process"]["main"]))
        print(colored('   - ', 'red', attrs=["bold"]), end="")
        print(Fore.GREEN + "Status: ", end="")

        if (is_alive(self.runtime["process"]["main"])):
            print(emoji.emojize(':rocket:') + "  running...\n")
        else:
            print(emoji.emojize(':construction:') + "  not active.\n")

        print(Fore.GREEN + "API:", end="\n")
        print(colored('   - ', 'red', attrs=["bold"]), end="")
        print(Fore.GREEN + "PID: ", end="")
        print(Fore.WHITE + "%s  " % (self.runtime.get("healthcheck_pid")))
        print(colored('   - ', 'red', attrs=["bold"]), end="")
        print(Fore.GREEN + "Status: ", end="")
        if (self.runtime["process"]["api"] and is_alive(self.runtime["process"]["api"])):
            print(emoji.emojize(':rocket:') + "  running...\n")
        else:
            print(emoji.emojize(':construction:') + "  not active.\n")

    def show_config(self):
        cprint(pyfiglet.figlet_format('Autumn', font='graffiti'),
               'green', attrs=['blink', 'bold'])
        with open(self.config_file, "r") as f:
            print(colored(':: Current Config In ' +
                          os.path.abspath(self.config_file), 'red', attrs=["bold"]))
            print(colored('---------------', 'red', attrs=["bold"]))
            print(highlight(f.read(), YamlLexer(), TerminalFormatter()))

    def init_config(self):
        cprint(pyfiglet.figlet_format('Autumn', font='graffiti'),
               'green', attrs=['blink', 'bold'])
        logger.debug(self.config_file)
        if pathlib.Path(self.config_file).exists():
            logger.warning(
                "The configuration has been initialized already before. It could be reinitialized if you delete the current one")
            return
        with open(self.config_file, "w+") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False,
                      Dumper=yaml.SafeDumper)
            logger.info("Initialized config file in {}", self.config_file)

    def edit_config(self, action, param1, param2):
        if action == "set":
            with open(self.config_file, "r") as f:
                self.config = yaml.safe_load(f.read())
            if param1 == "tags":
                param2 = param2.split(",")
            self.config[param1] = param2
            with open(self.config_file, "w+") as f:
                yaml.dump(self.config, f, default_flow_style=False, Dumper=yaml.SafeDumper)
