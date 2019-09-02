import sys
import logging
import os


########################################################################
class Service:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, name, path=None):
        """Constructor"""
        self.name = name
        self.path = path

    # ----------------------------------------------------------------------
    def stop(self):
        """"""
        os.system(f"systemctl stop {self.name}")

    # ----------------------------------------------------------------------
    def start(self):
        """"""
        os.system(f"systemctl start {self.name}")

    # ----------------------------------------------------------------------
    def restart(self):
        """"""
        os.system(f"systemctl restart {self.name}")

    # ----------------------------------------------------------------------
    def enable(self):
        """"""
        os.system(f"systemctl enable {self.name}")

    # ----------------------------------------------------------------------
    def reload(self):
        """"""
        os.system("systemctl --user daemon-reload")

    # ----------------------------------------------------------------------
    def remove(self):
        """"""
        if self.path is None:
            logging.error("No path specified.")
            # sys.exit()
        else:
            os.remove(f"/etc/systemd/system/{self.name}.service")
            # os.system(f"rm /etc/systemd/system/{self.name}.service")

    # ----------------------------------------------------------------------
    def create(self):
        """"""
        systemd_script = f"""[Unit]
Description={name}

[Service]
Type=simple
ExecStart={self.path}
Restart=always

[Install]
WantedBy=multi-user.target"""

        self.stop()
        self.remove()
        with open(f"/etc/systemd/system/{self.name}.service") as file:
            file.write(systemd_script)
        self.reload()

