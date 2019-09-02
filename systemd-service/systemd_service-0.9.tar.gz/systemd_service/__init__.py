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
    def stop(self, unit='service'):
        """"""
        os.system(f"systemctl stop {self.name}.{unit}")

    # ----------------------------------------------------------------------
    def start(self, unit='service'):
        """"""
        os.system(f"systemctl start {self.name}.{unit}")

    # ----------------------------------------------------------------------
    def restart(self, unit='service'):
        """"""
        os.system(f"systemctl restart {self.name}.{unit}")

    # ----------------------------------------------------------------------
    def enable(self, unit='service'):
        """"""
        os.system(f"systemctl enable {self.name}.{unit}")

    # ----------------------------------------------------------------------
    def reload(self):
        """"""
        os.system("systemctl --user daemon-reload")

    # ----------------------------------------------------------------------
    def remove(self, unit='service'):
        """"""
        try:
            os.remove(f"/etc/systemd/system/{self.name}.{unit}")
        except Exception as e:
            logging.error(e)
            # os.system(f"rm /etc/systemd/system/{self.name}.service")

    # ----------------------------------------------------------------------
    def create_service(self):
        """"""
        systemd_script = f'''[Unit]
Description="{self.name}"

[Service]
Type=simple
ExecStart={self.path}
Restart=always

[Install]
WantedBy=multi-user.target'''

        self.stop()
        self.remove()
        with open(f"/etc/systemd/system/{self.name}.service", 'w') as file:
            file.write(systemd_script)
        self.reload()

    # ----------------------------------------------------------------------
    def create_timer(self, on_boot_sec=15):
        """"""
        systemd_script = f'''[Unit]
Description = "{self.name}"

[Timer]
OnBootSec = {on_boot_sec}s
Unit = {self.name}.service

[Install]
WantedBy = timers.target
        '''

        self.create_service()
        self.stop(unit='timer')
        self.remove(unit='timer')
        with open(f"/etc/systemd/system/{self.name}.timer", 'w') as file:
            file.write(systemd_script)
        self.reload()
