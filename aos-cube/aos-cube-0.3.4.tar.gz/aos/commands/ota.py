import os, sys
import shutil
import hashlib
import json
import threading
import time
import progressbar
import requests
import click
import paho.mqtt.client as mqtt
import base64

from aos.constant import OTA_SERVER, OTA_EMQ_PORT, OTA_WEBSERVER_PORT, OTA_UDEBUG_LIB
from aos.util import log, error, cd_aos_root, is_domestic, popen
from aos.program import *

first_progress = 0
bar = None
timer = {}

# ota command
@click.command("ota", short_help="upload firmware to board over ota, e.g. aos ota helloworld@starterkit")
@click.argument("targets", required=False, nargs=-1, metavar="[TARGETS...]")
@click.option("-d", "--device-name", prompt=True, metavar="[DEVICENAME]")
@click.option("-p", "--product-key", prompt=True, metavar="[PRODUCTKEY]")
@click.option("-f", "--upload-file", default="none", metavar="[FILE]")

def cli(targets, device_name, product_key, upload_file):
    """ upload firmware to board over ota """
    from aos import __version__
    click.echo("aos-cube version: %s" % __version__)
    click.echo("deviceName: %s" % device_name)
    click.echo("productKey: %s" % product_key)

    ota_target = ' '.join(targets)

    udebug_lib = None
    if upload_file != "none":
        # check file type (must be *.bin)
        if not upload_file.endswith(".bin"):
            error("file must be *.bin")

        click.echo("You specified the upload file: %s\n" % upload_file)

        if os.path.isfile(upload_file) == False:
            error("Uploading file not exist")
    else:
        #cd to aos root_dir
        ret, original_dir = cd_aos_root()
        if ret != 'success':
            log("[INFO]: Not in AliOS-Things source code directory")
            log("[INFO]: Current directory is: '%s'\n" % original_dir)
            if os.path.isdir(original_dir):
                os.chdir(original_dir)
            aos_path = Global().get_cfg(AOS_SDK_PATH)
            if aos_path == None:
                error("[ERRO]: Not in aos_sdk_path, aos_sdk unavailable as well!")
            else:
                log("[INFO]: Config Loading OK, use '%s' as sdk path\n" % aos_path)
        else:
            aos_path = os.getcwd()
            log("[INFO]: Currently in aos_sdk_path: '%s'\n" % os.getcwd())

        # read app & board from .config
        if ota_target == '':
            # check AliOS Things version
            if os.path.exists(os.path.join(aos_path, 'build', 'Config.in')) == False:
                error('Target invalid')

            board = None
            app = None
            log("[INFO]: Not set target, read target from .config\n")

            config_file = os.path.join(aos_path, '.config')
            if os.path.exists(config_file) == False:
                error('Config file NOT EXIST: %s\n' % config_file)

            board = get_config_value('AOS_BUILD_BOARD', config_file)
            app = get_config_value('AOS_BUILD_APP', config_file)

            if not app and not board:
                error('None target in %s\n' % config_file)
            ota_target = '%s@%s' % (app, board)

        elif '@' not in ota_target or len(ota_target.split('@')) != 2:
            error('Target invalid')
            return

        click.secho("[INFO]: Target: %s\n" % ota_target, fg="green")

        _ota_bin = os.path.join(aos_path, "out", "%s" % ota_target, "binary", "%s.ota.bin" % ota_target)
        _bin = os.path.join(aos_path, "out", "%s" % ota_target, "binary", "%s.bin" % ota_target)

        # check *.bin or *.ota.bin
        if os.path.isfile(_ota_bin) == True:
            upload_file = _ota_bin
        elif os.path.isfile(_bin) == True:
            upload_file = _bin
        else:
            error("Uploading file not exist(%s.bin or %s.ota.bin)" % (ota_target, ota_target))

        click.echo("[INFO]: Get Uploading file: %s" % upload_file)
        udebug_lib = os.path.join(aos_path, "out", "%s" % ota_target, "libraries", "%s" % OTA_UDEBUG_LIB)
        # check is binary including udebug components
        if os.path.isfile(udebug_lib) == False:
            log("[WARN]: Uploading binary seems not including udev components(%s not exist), maybe you can't upload firmware over ota next time\n" % udebug_lib)
            if not click.confirm(click.style('Do you want to continue?', fg="red"), abort=True):
                error("Cancel upload")
    check_device_online(device_name, product_key)
    return ota_upload(upload_file, device_name, product_key)

# upload binary file to oss for ota download
def ota_upload(upload_file, device_name, product_key):
    try:
        (url, size, md5) = _upload(upload_file, device_name, product_key)
        payload = {
            "url": url,
            "size": size,
            "md5": md5
        }

        mqtt_operation(device_name, product_key, json.dumps(payload))
    except KeyboardInterrupt as e:
        click.secho("User aborted!", fg="red")
        timer.cancel()
        return
    except Exception as e:
        # traceback.print_exc(file=sys.stdout)
        error("Unknown Error: %s" % e)
        return -1

# check device online/offline
def check_device_online(device_name, product_key):
    try:
        r = requests.get("http://%s:%d/client?deviceName=%s&productKey=%s" % (OTA_SERVER, OTA_WEBSERVER_PORT, device_name, product_key))
        if r.status_code != 200:
            error("can not check device online/offline")

        r = r.json()
        if len(r['result']['objects']) == 0:
            click.secho("ERROR: device: %s.%s offline" % (device_name, product_key), fg="red")
            sys.exit(-1)
        click.secho("device: %s.%s online" % (device_name, product_key), fg="green")

    except Exception as e:
        error("Unknown Error: %s" % e)

# get file md5sum
def _get_file_md5(filename):
    _FILE_SLIM = (10*1024*1024) # 100MB
    hmd5 = hashlib.md5()
    f_size = os.stat(filename).st_size
    with open(filename,"rb") as fp:
        if f_size>_FILE_SLIM:
            while(f_size>_FILE_SLIM):
                hmd5.update(fp.read(_FILE_SLIM))
                f_size/=_FILE_SLIM
            if(f_size>0) and (f_size<=_FILE_SLIM):
                hmd5.update(fp.read())
        else:
            hmd5.update(fp.read())
        return hmd5.hexdigest()

# upload binary to OSS
def _upload(file, dn, pk):
    upload_file = os.path.abspath(file)
    size = os.path.getsize(upload_file)
    md5 = _get_file_md5(upload_file).upper()
    #print "local file md5: " + md5

    try:
        data = {
            "deviceName": dn,
            "productKey": pk
        }
        files = {
            "field1": open(upload_file, "rb")
        }
        click.echo("uploading file: %s ..." % file)
        r = requests.post("http://%s:%d/upload" %(OTA_SERVER, OTA_WEBSERVER_PORT), data=data, files=files).json()

    except Exception as e:
        error(e)

    if r['res']['headers']['etag'] != ("\"%s\"" % md5):
        error("verify error, remote md5: %s" % r['res']['headers']['etag'])

    click.echo("upload success, verify ok")

    return (r['url'], size, md5)

# The callback when connect to mqtt broker
def on_connect(client, (dn, pk, payload), flags, rc):
    global bar
    # print userdata
    topic_upgrade = "/%s/%s/upgrade" % (pk, dn)
    topic_progress = "/%s/%s/progress" % (pk, dn)

    click.echo("connected mqtt broker, waiting to finish erasing flash...")

    client.publish(topic_upgrade, payload, qos=1)
    client.subscribe(topic_progress, qos=1)

# The callback for when a PUBLISH message is received from the mqtt broker.
def on_message(client, (dn, pk, payload), msg):
    global first_progress, bar, timer

    #print "on message"
    timer.cancel()
    timer = threading.Timer(5, mqtt_timeout, [client])
    timer.damon = True
    timer.start()

    # print userdata
    # click.echo("%s %s" % (msg.topic, str(msg.payload)))
    payload = json.loads(str(msg.payload))

    if bar == None:
        widgets=[
            progressbar.Percentage(),
            progressbar.Bar(),
            ' (', progressbar.ETA(), ') ',
        ]
        bar = progressbar.ProgressBar(max_value=100, widgets=widgets, redirect_stdout=True)
        bar.start()
    bar.update(payload["progress"])
    if payload["progress"] == 100:
        bar.finish()
        click.secho("Congratulations!! upgrade done", fg="green")
        timer.cancel()
        sys.exit(0)

# start mqtt client
def mqtt_operation(dn, pk, payload):

    global timer
    client = mqtt.Client(userdata=(dn, pk, payload))
    client.on_connect = on_connect
    client.on_message = on_message
    token = base64.b64decode(OTA_EMQ_TOKEN).split('|')
    if len(token) != 2:
        error("wrong EMQ token")
    client.username_pw_set(username=token[0], password=token[1])

    client.connect(OTA_SERVER, OTA_EMQ_PORT, 60)
    timer = threading.Timer(15, mqtt_timeout, [client])
    timer.damon = True
    timer.start()
    client.loop_forever()

# exit when timeout
def mqtt_timeout(client):
    global timer
    timer.cancel()
    client.disconnect()
    error("mqtt timeout")
