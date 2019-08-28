import logging

import paramiko


class SshService:
    def __init__(self, ip_address: str):
        assert ip_address is not None

        self.ssh = paramiko.client.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.load_system_host_keys()

        while True:
            logging.info('Trying to connect ...')

            try:
                self.ssh.connect(
                    hostname=ip_address,
                    username='root'
                )
            except TimeoutError:
                continue

            break

    def exec(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.channel.recv_exit_status()

    def sftp(self):
        return self.ssh.open_sftp()
