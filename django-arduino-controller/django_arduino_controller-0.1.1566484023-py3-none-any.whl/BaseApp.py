import logging
import os
import sys
import time

from arduino_controller.serialreader.serialreader import SerialReader
from logging.handlers import RotatingFileHandler
from os.path import expanduser

import coloredlogs

from json_dict import JsonDict
from plug_in_django import manage as plug_in_django_manage
from django_arduino_controller.apps import DjangoArduinoControllerConfig


class BaseApp:
    DEBUGGING = False
    BASENAME = "BaseApp"
    SNAKE_NAME = BASENAME.lower().replace(" ", "_")
    BASE_DIR = os.path.join(expanduser("~"), "." + SNAKE_NAME)
    app_configs = []
    logging_fmt = (
        "%(asctime)s %(filename)s %(lineno)d %(name)s %(levelname)-8s  %(message)s"
    )

    login_required = True

    def __init__(self):
        self.to_migrate=False
        if not os.path.exists(self.BASE_DIR):
            self.to_migrate=True
        os.makedirs(self.BASE_DIR, exist_ok=True)
        self.config = JsonDict(
            os.path.join(self.BASE_DIR, self.SNAKE_NAME + "_config.json")
        )

        logging.basicConfig(
            level=self.config.get(
                "basic",
                "logging",
                "level",
                default=logging.DEBUG if self.DEBUGGING else logging.INFO,
            ),
            format=self.logging_fmt,
            datefmt="(%H:%M:%S)",
        )

        rotating_handler = RotatingFileHandler(
            os.path.join(self.BASE_DIR, "log.log"),
            maxBytes=self.config.get("basic", "logging", "max_bytes", default=2 ** 19),
            backupCount=self.config.get("basic", "logging", "backup_count", default=10),
        )

        rotating_handler.setFormatter(logging.Formatter(self.logging_fmt))
        logging.getLogger("").addHandler(rotating_handler)

        logger = logging.getLogger(self.BASENAME)

        coloredlogs.install(level="DEBUG", fmt=self.logging_fmt)

        logger.info("Use basedir: " + os.path.abspath(self.BASE_DIR))

        # plugin to django
        plug_in_django_manage.plug_in(DjangoArduinoControllerConfig, self.config)
        plug_in_django_manage.CONFIG.put(
            "django_settings", "apps", "channels", value=True
        )

        # set site parameters
        plug_in_django_manage.CONFIG.put("public", "site", "title", value=self.BASENAME)
        plug_in_django_manage.CONFIG.put(
            "django_settings", "DEBUG", value=self.DEBUGGING
        )
        plug_in_django_manage.CONFIG.put(
            "django_settings", "BASE_DIR", value=self.BASE_DIR
        )

        if self.login_required:
            # login required
            plug_in_django_manage.CONFIG.put(
                "django_settings",
                "manual",
                "add_to_list",
                "MIDDLEWARE",
                value=[
                    #     "global_login_required.GlobalLoginRequiredMiddleware"
                ],
            )
            # if login is required accounds neet to be public
            plug_in_django_manage.CONFIG.put(
                "django_settings",
                "manual",
                "add_to_list",
                "PUBLIC_PATHS",
                value=[r"^/accounts/.*"],
            )

        for app_config in self.app_configs:
            plug_in_django_manage.plug_in(app_config, self.config)

    def migrate(self):
        plug_in_django_manage.run(sys.argv[0], "makemigrations")
        plug_in_django_manage.run(sys.argv[0], "migrate")

    def run(self, open_browser=False, open_data_dir=False):
        self.migrate()
        if self.to_migrate:
            self.migrate()
        if open_browser:
            def check_thread():
                import urllib.request

                while (
                    not urllib.request.urlopen(
                        "http://localhost:{}".format(
                            plug_in_django_manage.CONFIG.get(
                                "django_settings", "port", default=8000
                            )
                        )
                    ).getcode()
                    == 200
                ):
                    time.sleep(200)
                import webbrowser

                webbrowser.open(
                    "http://localhost:{}".format(
                        plug_in_django_manage.CONFIG.get(
                            "django_settings", "port", default=8000
                        )
                    ),
                    new=2,
                )

            import threading

            threading.Thread(target=check_thread).start()
        if open_data_dir:
            import webbrowser

            if sys.platform == "darwin":
                webbrowser.open(self.BASE_DIR)
            elif sys.platform == "linux2":
                webbrowser.open(self.BASE_DIR)
            elif sys.platform == "win32":
                webbrowser.open(self.BASE_DIR)
            else:
                webbrowser.open(self.BASE_DIR)
        plug_in_django_manage.run(
            sys.argv[0],
            "runserver",
            "--noreload",
            "0.0.0.0:"
            + str(
                plug_in_django_manage.CONFIG.get(
                    "django_settings", "port", default=8000
                )
            ),
        )
