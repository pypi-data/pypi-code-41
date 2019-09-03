import os.path
import subprocess

from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext

class prepare_tinydtls(build_ext):
    def run(self):
        def run_command(args):
            print("Running:", " ".join(args))
            subprocess.check_call(args, cwd=os.path.join(os.path.dirname(__file__), "DTLSSocket","tinydtls"))
        commands =  [
                    ["autoconf"],
                    ["autoheader"],
                    ["./configure", "--without-ecc"],
                    ]
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'DTLSSocket','tinydtls','dtls.c')):
            run_command(["git", "submodule", "update", "--init"])
        for command in commands:
            run_command(command)
        build_ext.run(self)

setup(
    name="DTLSSocket",
    version='0.1.11a1',
    description = "DTLSSocket is a cython wrapper for tinydtls with a Socket like interface",
    author      = "Jannis Konrad",
    author_email= "Jannis.Konrad@h-brs.de",
    url         = "https://git.fslab.de/jkonra2m/tinydtls-cython",
    py_modules  = [ "DTLSSocket.DTLSSocket"],
    cmdclass    = {"build_ext": prepare_tinydtls},
    setup_requires = ['setuptools>=18.0','Cython'],
    install_requires = ['Cython'],
    ext_modules = [Extension("DTLSSocket.dtls",
                [
                 "DTLSSocket/dtls.pyx",
                 "DTLSSocket/tinydtls/ccm.c",
                 "DTLSSocket/tinydtls/crypto.c",
                 "DTLSSocket/tinydtls/dtls.c",
                 "DTLSSocket/tinydtls/dtls_debug.c",
                 "DTLSSocket/tinydtls/dtls_time.c",
                 "DTLSSocket/tinydtls/hmac.c",
                 "DTLSSocket/tinydtls/netq.c",
                 "DTLSSocket/tinydtls/peer.c",
                 "DTLSSocket/tinydtls/session.c",
                 "DTLSSocket/tinydtls/aes/rijndael.c",
                 "DTLSSocket/tinydtls/sha2/sha2.c",
                 "DTLSSocket/tinydtls/platform-specific/dtls_prng_posix.c",
                 ],
                include_dirs=['DTLSSocket/tinydtls'],
                define_macros=[('DTLSv12', '1'),
                               ('WITH_SHA256', '1'),
                               ('DTLS_CHECK_CONTENTTYPE', '1'),
                               ('_GNU_SOURCE', '1'),
                                ('NDEBUG', '1'),
                              ],
#                undef_macros = [ "NDEBUG" ],
                ),]
    )
