import os, sys
import json
import click

from aos.util import *
from aos.repo import *
from aos.managers.comp import CompManager
import ConfigParser

@click.group(short_help="OTA firmware management tool")
def cli():
    pass

def get_extra_cmd_path():
    """ Return path of $aos_root/build/cmd """
    os_type = get_host_os().lower()

    extra_path = None
    # Get aos source root directory
    ret, original_dir = cd_aos_root()
    if ret == 'success':
        source_root = os.getcwd()
        extra_path = os.path.join(source_root, "build/cmd/%s" % os_type)

    if os.path.isdir(original_dir):
        os.chdir(original_dir)

    return extra_path

# Create diff patch
@cli.command("diff", short_help="Create diff bin base on old & new binaries")
@click.argument("old_bin", required=True, metavar="[OLD_BIN]")
@click.argument("new_bin", required=True, metavar="[NEW_BIN]")
@click.option("-o", "--output-file", required=False, metavar="DIFF_BIN", help="The name of diff binary, default as diff.bin" )
@click.option("-s", "--split-size", required=False, metavar="BYTE", help="Split size, default as 65536")
@click.option("-l", "--logfile", required=False, metavar="LOG_FILE", help="The name of log file")
def ota_diff(old_bin, new_bin, output_file, split_size, logfile):
    if not split_size:
        split_size = "65536"

    if not output_file:
        output_file = "diff.bin"

    if not os.path.isfile(old_bin):
        error("No such file %s" % old_bin)

    if not os.path.isfile(new_bin):
        error("No such file %s" % new_bin)

    # run ota_nbdiff
    extra_path = get_extra_cmd_path()
    ota_nbdiff = which("ota_nbdiff", extra_path)
    if ota_nbdiff:
        cmd = [ota_nbdiff, old_bin, new_bin, output_file, split_size]
        if logfile:
            cmd += [logfile]

        popen(cmd)
    else:
        error("Can't find command ota_nbdiff")

# Patch diff to old firmware
@cli.command("patch", short_help="Create new bin base on diff & old binaries")
@click.argument("old_bin", required=True, metavar="[OLD_BIN]")
@click.argument("new_bin", required=True, metavar="[NEW_BIN]")
@click.argument("diff_bin", required=True, metavar="[DIFF_BIN]")
def ota_patch(old_bin, new_bin, diff_bin):
    for binfile in [old_bin, new_bin, diff_bin]:
        if not os.path.isfile(binfile):
            error("No such file %s" % binfile)

    # run ota_nbpatch
    extra_path = get_extra_cmd_path()
    ota_nbpatch = which("ota_nbpatch", extra_path)
    if ota_nbpatch:
        cmd = [ota_nbpatch, old_bin, new_bin, diff_bin]
        popen(cmd)
    else:
        error("Can't find command ota_nbpatch")

@cli.command("upload", short_help="Upload firmware to board over OTA, e.g. aos ota helloworld@starterkit")
@click.argument("targets", required=False, nargs=-1, metavar="[TARGETS...]")
@click.option("-d", "--device-name", prompt=True, metavar="[DEVICENAME]")
@click.option("-p", "--product-key", prompt=True, metavar="[PRODUCTKEY]")
@click.option("-f", "--upload-file", default="none", metavar="[FILE]")
def ota_upload(targets, device_name, product_key, upload_file):
    try:
        from aos.ota_upload import upload
    except:
        pass

    upload(targets, device_name, product_key, upload_file)
