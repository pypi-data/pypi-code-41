import os
import logging

from bmcsf.services.ssh import SshService

BACKUP_LOCATION = os.path.expanduser(
    os.path.join(
        '~',
        '.config',
        'bmcsf',
        'data'
    )
)


class BackupService:
    def __init__(self, alias: str, ssh: SshService):
        assert ssh is not None
        assert alias is not None
        assert len(alias) > 0

        self.alias = alias
        self.ssh = ssh

        if not os.path.isdir(BACKUP_LOCATION):
            os.makedirs(BACKUP_LOCATION)

    def _get_ftp_client(self):
        return self.ssh.sftp()

    def backup(self):
        sftp = self._get_ftp_client()

        logging.info('Compressing server data ...')
        self.ssh.exec('zip -9r {}.zip .'.format(self.alias))
        logging.info('Copying server backup ...')
        sftp.get('{}.zip'.format(self.alias), self.get_backup_location())

        sftp.close()

    def restore(self):
        if not self.has_backup():
            return False

        sftp = self._get_ftp_client()

        logging.info('Copying server data ...')
        sftp.put(self.get_backup_location(), 'backup.zip')
        logging.info('Extracting backup archive ...')
        self.ssh.exec('unzip -o backup.zip')
        logging.info('Deleting backup on the server ...')
        self.ssh.exec('rm -rf backup.zip')

        sftp.close()

        return True

    def has_backup(self):
        return os.path.isfile(self.get_backup_location())

    def get_backup_location(self):
        return os.path.join(
            BACKUP_LOCATION,
            '{}.zip'.format(self.alias)
        )
