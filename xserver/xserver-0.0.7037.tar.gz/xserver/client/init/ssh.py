#coding: utf8
from __future__ import absolute_import
from xserver.utils.path import get_home_path
from xserver.client.utils.fab import make_env, put_file_content
from fabric.api import sudo, run, put, env
import os

sshd_config_content = """
# Package generated configuration file
# See the sshd_config(5) manpage for details

# What ports, IPs and protocols we listen for
Port 22
# Use these options to restrict which interfaces/protocols sshd will bind to
#ListenAddress ::
#ListenAddress 0.0.0.0
Protocol 2
# HostKeys for protocol version 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_dsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
#Privilege Separation is turned on for security
UsePrivilegeSeparation yes

# Lifetime and size of ephemeral version 1 server key
KeyRegenerationInterval 3600
ServerKeyBits 1024

# Logging
SyslogFacility AUTH
LogLevel INFO

# Authentication:
LoginGraceTime 120
PermitRootLogin without-password
# StrictModes yes

RSAAuthentication yes
PubkeyAuthentication yes
#AuthorizedKeysFile	%h/.ssh/authorized_keys

# Don't read the user's ~/.rhosts and ~/.shosts files
IgnoreRhosts yes
# For this to work you will also need host keys in /etc/ssh_known_hosts
RhostsRSAAuthentication no
# similar for protocol version 2
HostbasedAuthentication no
# Uncomment if you don't trust ~/.ssh/known_hosts for RhostsRSAAuthentication
#IgnoreUserKnownHosts yes

# To enable empty passwords, change to yes (NOT RECOMMENDED)
PermitEmptyPasswords no

# Change to yes to enable challenge-response passwords (beware issues with
# some PAM modules and threads)
ChallengeResponseAuthentication no

# Change to no to disable tunnelled clear text passwords
#PasswordAuthentication yes

# Kerberos options
#KerberosAuthentication no
#KerberosGetAFSToken no
#KerberosOrLocalPasswd yes
#KerberosTicketCleanup yes

# GSSAPI options
#GSSAPIAuthentication no
#GSSAPICleanupCredentials yes

X11Forwarding yes
X11DisplayOffset 10
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
#UseLogin no

#MaxStartups 10:30:60
#Banner /etc/issue.net

# Allow client to pass locale environment variables
#AcceptEnv LANG LC_*

Subsystem sftp /usr/lib/openssh/sftp-server

# Set this to 'yes' to enable PAM authentication, account processing,
# and session processing. If this is enabled, PAM authentication will
# be allowed through the ChallengeResponseAuthentication and
# PasswordAuthentication.  Depending on your PAM configuration,
# PAM authentication via ChallengeResponseAuthentication may bypass
# the setting of "PermitRootLogin yes".
# If you just want the PAM account and session checks to run without
# PAM authentication, then enable this but set PasswordAuthentication
# and ChallengeResponseAuthentication to 'no'.
UsePAM yes
PasswordAuthentication no

UseDNS no
"""



def enable_ssh_root_login(ip, password=None, user=None):
    # 允许 root 使用密码登陆
    if not user:
        user = 'root'
    make_env(ip, user=user, password=password)

    new_sshd_config_content = sshd_config_content.replace('PasswordAuthentication no', 'PasswordAuthentication yes')\
        .replace('PermitRootLogin without-password', 'PermitRootLogin yes')

    put_file_content(new_sshd_config_content, '/etc/ssh/sshd_config')

    try:
        sudo("kill -HUP `ps -C sshd -o pid --no-headers | tr -d ' '`")  # restart sshd
    except:
        pass

        # switch to root now
    make_env(ip, user='root')


def disable_ssh_root_login(ip, password=None, user=None):
    # 禁止 root 使用密码登陆
    if not user:
        user = 'root'
    make_env(ip, user=user, password=password)

    # by default
    put_file_content(sshd_config_content, '/etc/ssh/sshd_config')

    try:
        sudo("kill -HUP `ps -C sshd -o pid --no-headers | tr -d ' '`") # restart sshd
    except:
        pass

        # switch to root now
    make_env(ip, user='root')



def re_config_ssh(ip, password=None, user=None):
    # 将本地的 ssh key 发到服务器上并重启上面的 sshd 服务，下次不需要再用密码了
    # 但会导致连接断开，一般放在最后处理

    if not user:
        user = 'root'

    make_env(ip, user=user, password=password)

    sudo('mkdir -p /root/.ssh')
    #sshd_config_f.name = 'sshd_config'

    home_path = get_home_path()
    if not home_path:
        print('error: no home_path')
        return

    pub_key_filepath = os.path.join(home_path, '.ssh/id_rsa.pub')
    if not os.path.isfile(pub_key_filepath):
        print('error: no pub_key_filepath')


    with open(pub_key_filepath, 'rb') as f:
        pub_key_content = f.read()
    #pub_key_f.name = 'authorized_keys'
    sudo('mkdir -p /root/.ssh')
    put_file_content(pub_key_content, '/root/.ssh/authorized_keys')
    sudo('chown -R root:root /root/.ssh')
    sudo('chmod 700 /root/.ssh')
    sudo('chmod 600 /root/.ssh/authorized_keys')
    put_file_content(sshd_config_content, '/etc/ssh/sshd_config')

    try:
        sudo("kill -HUP `ps -C sshd -o pid --no-headers | tr -d ' '`") # restart sshd
    except:
        pass

    # switch to root now
    make_env(ip, user='root')

