import logging
import re
from .remotesessionbase import RemoteSessionBase
from .exceptions import (
    SessionTargetIsNotSet,
    NotImplementedInRemoteScript,
    RunnerTargetNotSet)


__copyright__ = 'Copyright (C) 2019, Nokia'

LOGGER = logging.getLogger(__name__)


class RemoteSessionTarget(RemoteSessionBase):

    re_env = re.compile('^([^.]+)\.([^.]+)$')

    def __init__(self):
        super(RemoteSessionTarget, self).__init__()
        self._engines = dict()
        self._runner_shelldicts = dict()

    def get_remoterunner_targets(self):
        """
        Get targets defined by \`Set Runner Target\` as dictionary with the
        target names as keys.
        """
        return self._remoterunner.targets

    def get_remotescript_targets(self):
        """
        Get targets defined by \`Set Target\` or by
        \`Set Target With Sshkeyfile\` as dictionary of target with the target
        names as keys.
        """
        return self._remotescript._engine.targets

    def set_target(self, host, username, password,
                   name='default', protocol='ssh/sftp'):
        """
        **RECOMMENDATION** Use \`Set Runner Target\` instead.

        Adds a target to RemoteScript Library.

        **Arguments:**

        *host*: Host name or IP address of the target host.

        *username*: User name for login to *host*.

        *password*: Password for the *username*.

        *name*: String identifier used to distinguish multiple targets.

        *protocol*: Protocol for connecting the target
        (\"telnet\", \"ssh/sftp\", \"ssh/scp\" or \"ftp\").  Value \"ssh\" is
        mapped to default \"ssh/sftp\". Value is case insensitive.

        **Returns:**

        Nothing.
        """
        self._remotescript.set_target(host, username, password,
                                      name=name, protocol=protocol)
        self._engines[name] = self._remotescript

    def set_target_with_sshkeyfile(self, host, username, sshkeyfile,
                                   name='default', protocol='ssh/sftp'):
        """
        Exactly as \`Set Target\` but instead of a password, a ssh private key
        file *sshkeyfile* is expected as input.
        """
        self._remotescript.set_target_with_sshkeyfile(host,
                                                      username,
                                                      sshkeyfile,
                                                      name=name,
                                                      protocol=protocol)
        self._engines[name] = self._remotescript

    def set_target_property(self, target_name, property_name, property_value):
        """
        Sets property *property_name* for target *target_name*.
        This keyword can be used only with targets defined by
        \`Set Target`\ or \`Set Target With Sshkeyfile\`.

        **Arguments:**

        *target_name*: Name of the individual target, whose property to set.

        *property_name*:Name of the property.

        *property_value*: Value of the property.

        **Returns:**

        Nothing.

        **Supported properties:**

        +---------------+-----------------------------------+-----------------+
        | **Name**      | **Description**                   |**Default Value**|
        +===============+===================================+=================+
        | *cleanup*     | Delete temporary directories and  | True            |
        |               | files when the keyword is exiting.|                 |
        +---------------+-----------------------------------+-----------------+
        | *connection*  | Raise exception if connection is  | True            |
        | *break is*    | lost before command is finished.  |                 |
        | *error*       | If set to False, exception is not |                 |
        |               | raised if connection is closed    |                 |
        |               | unexpectedly. The result          |                 |
        |               | exit status is *unknown*,         |                 |
        |               | stdout and stderr will be empty   |                 |
        |               | strings.                          |                 |
        +---------------+-----------------------------------+-----------------+
        | *connection*  | Raise exception if connection     | True            |
        | *failure*     | cannot be opened. If set to false,|                 |
        | *is error*    | exception is not raised if        |                 |
        |               | opening connection fails.         |                 |
        |               | The result status to *unknown*,   |                 |
        |               | stdout and stderr will be empty   |                 |
        |               | strings.                          |                 |
        +---------------+-----------------------------------+-----------------+
        | *login prompt*| Telnet login prompt regular.      |   "login:  "    |
        +---------------+-----------------------------------+-----------------+
        | *login*       | Timeout to wait loging prompt.    | 60              |
        +---------------+-----------------------------------+-----------------+
        | *max*         | Maximum number of reconnections   | 10              |
        | *connection*  | if connection is refused.         |                 |
        | *attempts*    |                                   |                 |
        +---------------+-----------------------------------+-----------------+
        | *nonzero*     | Raise NonZeroExitStatusError if   | False           |
        | *status*      | exit status of the command is not |                 |
        | *is error*    | zero. If set to 'True' and command|                 |
        |               | fails stdout and stderr are       |                 |
        |               | not returned, but they are        |                 |
        |               | included in the exception message.|                 |
        +---------------+-----------------------------------+-----------------+
        | *password*    | Telnet password prompt regular    |                 |
        | *prompt*      | expression.                       |  "Password: "   |
        +---------------+-----------------------------------+-----------------+
        | *port*        | Target port.                      | 22 for ssh and  |
        |               |                                   | 23 for telnet   |
        +---------------+-----------------------------------+-----------------+
        | *prompt*      | Target prompt.                    | "$  "           |
        +---------------+-----------------------------------+-----------------+
        | *su password* | Target su password                | None            |
        +---------------+-----------------------------------+-----------------+
        | *su username* | Target su username. If defined,   | None            |
        |               | command and script execution      |                 |
        |               | related keywords will do the      |                 |
        |               | execution under this account.     |                 |
        +---------------+-----------------------------------+-----------------+


        **property specialities:**

        .. note::

            FlexiPlatform specific keywords in *RemoteScript.FP* uses
            *su username* (if defined) in all SSH/SCP operations between CLA
            and nodes (not doing su).

        .. danger::

            If *su username* is specified, then commands may not contain single
            quotes (double quotes are ok).  Stdout and stderr are combined to
            object stdout field. Telnet protocol is not supported.
        """
        self._remotescript.set_target_property(target_name,
                                               property_name,
                                               property_value)

        self._engines[target_name] = self._remotescript

    def set_default_target_property(self, property_name, property_value):
        """This keyword can be used only with targets defined by
        \`Set Target`\ or \`Set Target With Sshkeyfile\`.

        Sets default property for all targets.
        Target specific properties override the default values. See
        \`Set Target Property\` for supported properties.

        **Arguments:**

        *property_name*: Name of the property.

        *property_value*: Value of the property.

        **Returns:**

        Nothing.
        """
        self._remotescript.set_default_target_property(property_name,
                                                       property_value)

    def set_runner_target(self, shelldicts, name='default'):
        """
        Set connection path to target as dictionaries of *Shells*. The default
        shell is *DefaultSshShell* from
        *crl.interactivesessions.shells.shellstack*.  The shell *__init__*
        arguments have to be given as keyword argument dictionary with addition
        of the *shellname* keyword. If the *shellname* argument is not given,
        the *DefaultSshShell* is instantiated.

        In the *DefaultSshShell* the *host* is the only mandatory argument
        so it supports passwordless login. The arguments *user* and *username*
        are aliases for the *SshShell* argument *ip*.

        For setting the target properties and the default properties please use
        \`Set Runner Target Property\` and
        \`Set Runner Default Target Property\` respectively.

        **Arguments:**

        *shelldicts*: Path to the target defined by the stack of *Shell*
        dictionaries.

        *name*: String identifier used to distinguish multiple targets.

        **Returns:**

        Nothing.

        **Example 1:**

        +----------------------+--------------------------------------------+
        | &{UNDERCLOUD}=       | host=10.102.227.10                         |
        +----------------------+--------------------------------------------+
        | ...                  | user=root                                  |
        +----------------------+--------------------------------------------+
        | ...                  | password=root                              |
        +----------------------+--------------------------------------------+
        | &{OVERCLOUD} =       | host=192.168.122.56                        |
        +----------------------+--------------------------------------------+
        | ...                  | user=nokiaovercloud                        |
        +----------------------+--------------------------------------------+
        | ...                  | password=overcloudpass                     |
        +----------------------+--------------------------------------------+
        | @{SHELLDCITS}=       | ${UNDERCLOUD}                              |
        +----------------------+--------------------------------------------+
        | ...                  | ${OVERCLOUD}                               |
        +----------------------+--------------------------------------------+
        | Set Target           | shelldicts=${SHELLDICTS}                   |
        +----------------------+--------------------------------------------+
        | ...                  | name=Overcloud                             |
        +----------------------+--------------------------------------------+

        **Example 2:**

        *NamespaceShell* can be used in a middle for executing commands in the
        test targets where the connection requires setting of the
        *Linux* kernel namespace.

        +----------------------+--------------------------------------------+
        | &{CONTROLLER}=       | host=10.102.227.10                         |
        +----------------------+--------------------------------------------+
        | ...                  | user=root                                  |
        +----------------------+--------------------------------------------+
        | ...                  | password=root                              |
        +----------------------+--------------------------------------------+
        | &{NAMESPACE}=        | shellname=NamespaceShell                   |
        +----------------------+--------------------------------------------+
        | ...                  | namespace=\ |namespace|                    |
        +----------------------+--------------------------------------------+
        | &{VNFNODE}=          | host=192.168.57.124                        |
        +----------------------+--------------------------------------------+
        | ...                  | user=nodeuser                              |
        +----------------------+--------------------------------------------+
        | ...                  | password=nodepassword                      |
        +----------------------+--------------------------------------------+
        | @{SHELLDCITS}=       | ${CONTROLLER}                              |
        +----------------------+--------------------------------------------+
        | ...                  | ${NAMESPACE}                               |
        +----------------------+--------------------------------------------+
        | ...                  | ${VNFNODE}                                 |
        +----------------------+--------------------------------------------+
        | Set Target           | shelldicts=${SHELLDICTS}                   |
        +----------------------+--------------------------------------------+
        | ...                  | name=vnfnode                               |
        +----------------------+--------------------------------------------+

        .. |namespace| replace:: qdhcp-d5c44716-4d11-45a6-a658-8ed97502d26b


        **Creating new shells**

        If none of the built-in shells
        (*SshShell*, *BashShell* and *NamespaceShell*) is usable
        the new shell can be created.
        The shell code can be located e.g in any test library which is
        imported e.g. via *Library* in the Robot Framework suites.

        The new shells must inherit from *Shell* and must be registered
        via *RegisterShell* decorator from
        *crl.interactivesessions.shells.registershell*

        For further information, please refer to the documentation of
        *Shell* from *crl.interactivesessions.shells.shell*.

        **Example 3**

        In this example is shown in the high level how the new
        *Shell* can he registered and used.

        Example code which has to be import e.g. by *Library*:

        .. code:: python

            @RegisterShell()
            NewShell(Shell):
                def __init__(self, newargument):
                   ...

        Example usage of the code from Robot Framework test suites:

        +----------------------+--------------------------------------------+
        | &{CONTROLLER}=       | host=10.102.227.10                         |
        +----------------------+--------------------------------------------+
        | ...                  | user=root                                  |
        +----------------------+--------------------------------------------+
        | ...                  | password=root                              |
        +----------------------+--------------------------------------------+
        | &{NEWSHELL}=         | shellname=NewShell                         |
        +----------------------+--------------------------------------------+
        | ...                  | newargument=newvalue                       |
        +----------------------+--------------------------------------------+
        | @{SHELLDCITS}=       | ${CONTROLLER}                              |
        +----------------------+--------------------------------------------+
        | ...                  | ${NEWSHELL}                                |
        +----------------------+--------------------------------------------+
        | Set Target           | shelldicts=${SHELLDICTS}                   |
        +----------------------+--------------------------------------------+
        | ...                  | name=newtarget                             |
        +----------------------+--------------------------------------------+

        The real life example could be *SuShell* which would change the user to
        the required user. Another example could be *SudoShell* which would
        e.g. start the shell with *sudo bash*.  Still one use-case could be to
        extend *BashShell* to execute source of the  required file in the shell
        start.
        """
        self._remoterunner.set_target(shelldicts, name=name)
        self._engines[name] = self._remoterunner
        self._runner_shelldicts[name] = shelldicts

    def set_runner_target_property(self, target_name,
                                   property_name, property_value):
        """
        Sets property *property_name* for target *target_name*.

        **Arguments:**

        *target_name*: Name of the individual target, whose property to set.

        *property_name*: Name of the property.

        *property_value*: Value of the property.

        **Returns:**

        Nothing.

        **Supported properties:**

        +------------------------+-------------------------------+-----------+
        | Name                   | Description                   | Default   |
        |                        |                               | value     |
        +========================+===============================+===========+
        |default_executable      | The default shell             | /bin/bash |
        |                        | executable in which the       |           |
        |                        | commands are executed.        |           |
        +------------------------+-------------------------------+-----------+
        |max_processes_in_target | Maximum number of             | 100       |
        |                        | simultaneous command execution|           |
        |                        | processes in the              |           |
        |                        | single target.                |           |
        +------------------------+-------------------------------+-----------+
        |prompt_timeout          | Timeout in seconds            | 30        |
        |                        | for getting prompt            |           |
        |                        | in the pseudo terminal.       |           |
        |                        | This mainly depends on the    |           |
        |                        | connection latency to the     |           |
        |                        | target.                       |           |
        +------------------------+-------------------------------+-----------+
        |termination_timeout     | Timeout in seconds for waiting| 10        |
        |                        | the execution process to      |           |
        |                        | gracefully shutdown after     |           |
        |                        | it is signaled with *SIGTERM*.|           |
        +------------------------+-------------------------------+-----------+
        |update_env_dict         | Dictionary of *os.environ*    | {}        |
        |                        | style environmental variables |           |
        |                        | which updates the original    |           |
        |                        | environment for all the runs. |           |
        +------------------------+-------------------------------+-----------+
        """
        self._remoterunner.set_target_property(target_name,
                                               property_name,
                                               property_value)
        self._engines[target_name] = self._remoterunner

    def set_runner_default_target_property(self,
                                           property_name,
                                           property_value):
        """
        Sets default property for all targets.

        Target specific properties override the default values. See
        \`Set Runner Target Property\` for supported properties.
        Moreover, it is possible to also create new properties.

        **Arguments:**

        *property_name*: Name of the property.

        *property_value*: Value of the property.

        **Returns:**

        Nothing.
        """
        self._remoterunner.set_default_target_property(property_name,
                                                       property_value)

    def get_target_properties(self, target):
        """
        Returns dictionary containing effective properties for *target*.
        """
        return self._get_engine(target).get_target_properties(target)

    def _get_engine(self, name):
        try:
            return self._get_engine_for_key_from_dict(
                key=name,
                enginedict=self._engines,
                msg="in target '{}'".format(name),
                exception=SessionTargetIsNotSet)
        except SessionTargetIsNotSet as e:
            return self._create_target_or_raise(name, e)

    def _create_target_or_raise(self, name, exception):
        matches = re.match(self.re_env, name)
        if self._envcreator and matches:
            target, envname = matches.groups()
            update_env_dict = self._envcreator.create(target=target,
                                                      envname=envname)

            self.set_runner_target(
                self._get_runner_shelldicts(target=target,
                                            envtarget=name),
                name=name)
            self.set_runner_target_property(target_name=name,
                                            property_name='update_env_dict',
                                            property_value=update_env_dict)
            return self._get_engine(name)

        raise exception

    def _get_runner_shelldicts(self, target, envtarget):
        try:
            return self._runner_shelldicts[target]
        except KeyError:
            if target in self._engines:
                raise NotImplementedInRemoteScript(
                    'RemoteScript target ({target}) cannot be used for creating '
                    '{envtarget}'.format(target=target,
                                         envtarget=envtarget))
            raise RunnerTargetNotSet(
                'Runner target ({target}) needed for creating {envtarget} is not set'
                '{envtarget}'.format(target=target,
                                     envtarget=envtarget))

    def _get_engine_for_key_from_dict(self, key, enginedict, msg, exception):
        try:
            engine = enginedict[key]
            self._log_engine(engine, msg)
            return engine
        except KeyError:
            raise exception(key)

    @staticmethod
    def _log_engine(engine, msg):
        LOGGER.debug("RemoteSession: running with %s %s",
                     engine.__class__, msg)
