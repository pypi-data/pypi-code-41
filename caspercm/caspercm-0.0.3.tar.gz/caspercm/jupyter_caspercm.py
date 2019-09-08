#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from enum import Enum
from datetime import datetime
import pytz
import json
import io
import base64
import mimetypes
import logging

from notebook.services.contents.manager import ContentsManager
import nbformat
from notebook.services.contents.checkpoints import (
    Checkpoints,
    GenericCheckpointsMixin,
)

from traitlets import (
    Unicode,
)
from tornado.web import HTTPError as HTTPServerError

import oci

class FileType(Enum):
    NOTEBOOK    = 'notebook'
    DIRECTORY   = 'directory'
    FILE        = 'file'


class FileFormat(Enum):
    JSON        = 'json'
    TEXT        = 'text'
    BASE64      = 'base64'


class FileExtension(Enum):
    NOTEBOOK    = '.ipynb'
    CHECKPOINT  = '.checkpoint'

CHECKPOINT_ID = 'checkpoint'

class MimeType(Enum):
    TEXT_PLAIN          = 'text/plain'
    APP_OCT_STREAM      = 'application/octet-stream'

class OciFileObject(object):
    # this wraps r.data.objects's element in list_objects api
    def __init__(self, name, time_created, mount_path):
        self.name = name
        self.time_created = time_created
        self.mount_path = mount_path

class MountPoint(object):
    def __init__(self, mount_voci_path, mountpoint_config):
        if mount_voci_path != '' and not mount_voci_path.endswith('/'):
            self.mount_voci_path = mount_voci_path + '/'
        else:
            self.mount_voci_path = mount_voci_path

        self.prefix = mountpoint_config['prefix']
        self.namespace = mountpoint_config['namespace']
        self.bucket = mountpoint_config['bucket']
        self.api_config = mountpoint_config['api_config']
        # TODO: make it lazy
        oci_config = oci.config.from_file(self.api_config)
        self.os_client = oci.object_storage.ObjectStorageClient(oci_config)


class VirtualCasper(object):
    log = logging.getLogger('VirtualCasper')

    def __init__(self, mount_config):
        self.mountpoints = {}
        for mount_path, mountpoint_config in mount_config.items():
            mount_voci_path = mount_path[1:]
            self.mountpoints[mount_path] = MountPoint(mount_voci_path, mountpoint_config)
    
    @classmethod
    def __match_prefix(cls, path, old_prefix, new_prefix):
        # if path match the old_prefix, the old prefix is replaced with new_prefix
        # if not match, it return None
        if not path.startswith(old_prefix):
            return None
        return new_prefix + path[len(old_prefix):]

    @classmethod
    def __get_direct_child(cls, parent_voci_path, child_voci_path):
        if parent_voci_path == '':
            possible_child = child_voci_path.split('/')[0]
            if possible_child == '':
                possible_child = None
            return possible_child
        if not child_voci_path.startswith(parent_voci_path + '/'):
            return None
        remaining = child_voci_path[len(parent_voci_path)+1]
        possible_child = remaining.split('/')[0]
        if possible_child == '':
            possible_child = None
        return possible_child

    @classmethod
    def __replace_prefix(cls, path, old_prefix, new_prefix):
        return new_prefix + path[len(old_prefix):]

    def list_objects(self, voci_path, fields=None, limit=None):
        log_prefix = 'VirtualCasper.list_objects'
        self.log.info('%s: enter, voci_path=%r, fields=%r, limit=%r', log_prefix, voci_path, fields, limit)

        objs = {}
        for mount_path, mountpoint in self.mountpoints.items():
            # mounted_oci_path is only meanful to the given mountpoint
            mounted_oci_path = self.__match_prefix(voci_path, mountpoint.mount_voci_path, mountpoint.prefix)
            if mounted_oci_path is None:
                self.log.info('%s: mount_path %r does not match', log_prefix, mount_path)
                direct_child = self.__get_direct_child(voci_path, mountpoint.mount_voci_path)
                if direct_child is not None:
                    name = mountpoint.mount_voci_path + '/' + direct_child
                    obj = OciFileObject(name, datetime.fromtimestamp(86400), None)
                    objs[name] = obj
                continue

            self.log.info('%s: mount_path %r match, converted to %r', log_prefix, mount_path, mounted_oci_path)
            r = mountpoint.os_client.list_objects(
                mountpoint.namespace, 
                mountpoint.bucket, 
                fields=fields,
                prefix=mounted_oci_path,
                limit=limit
            )
            if r.status != 200:
                raise Exception('Unable to list objects, oci error: {}'.format(r.status))
            for obj in r.data.objects:
                name = self.__replace_prefix(obj.name, mountpoint.prefix, mountpoint.mount_voci_path)
                # mount point directory, we do not want to override it
                if name not in objs or (objs[name].mount_path is not None and len(mount_path) > len(objs[name].mount_path)):
                    objs[name] = OciFileObject(name, obj.time_created, mount_path)
            # even limit is set, we should still keep searching since the same name might overwritten
            # yes, our return list might be longer than limit, caller need to deal with it
        self.log.info('%s: exit', log_prefix)
        return list(objs.values())

    def find_mountpoint(self, voci_path):
        # find a mount point that satisfied the voci_path
        # if multiple mount point matches, the deepest wins
        log_prefix = 'VirtualCasper.find_mountpoint'
        self.log.info('%s: enter, voci_path=%r', log_prefix, voci_path)

        found_mount_path = None
        found_mountpoint = None
        found_mounted_oci_path = None
        # find deepest mount point
        for mount_path, mountpoint in self.mountpoints.items():
            # mounted_oci_path is only meanful to the given mountpoint
            mounted_oci_path = self.__match_prefix(voci_path, mountpoint.mount_voci_path, mountpoint.prefix)
            if mounted_oci_path is None:
                self.log.info('%s: mount_path %r does not match', log_prefix, mount_path)
            else:
                self.log.info('%s: mount_path %r match, converted to %r', log_prefix, mount_path, mounted_oci_path)
                if found_mount_path is None or len(mount_path) > len(found_mount_path):
                    found_mount_path = mount_path
                    found_mountpoint = mountpoint
                    found_mounted_oci_path = mounted_oci_path
        
        return (found_mount_path, found_mountpoint, found_mounted_oci_path, )

    def put_object(self, voci_path, content):
        log_prefix = 'VirtualCasper.put_object'
        self.log.info(
            '%s: enter, voci_path=%r, content type=%s', 
            log_prefix, voci_path, content.__class__.__name__
        )

        found_mount_path, found_mountpoint, found_mounted_oci_path = self.find_mountpoint(voci_path)
        if found_mountpoint is None:
            raise Exception('Unable to put object: no mount point')
    
        self.log.info('%s: using mount_path %r', log_prefix, found_mount_path)
        r = found_mountpoint.os_client.put_object(
            found_mountpoint.namespace, 
            found_mountpoint.bucket, 
            found_mounted_oci_path,
            content
        )
        if r.status != 200:
            raise Exception('Unable to put object: oci error {}'.format(r.status))
        self.log.info('%s: exit', log_prefix)

    def delete_object(self, voci_path):
        log_prefix = 'VirtualCasper.delete_object'
        self.log.info('%s: enter, voci_path=%r', log_prefix, voci_path)

        found_mount_path, found_mountpoint, found_mounted_oci_path = self.find_mountpoint(voci_path)
        if found_mountpoint is None:
            raise Exception('Unable to delete object: no mount point')
    
        self.log.info('%s: using mount_path %r', log_prefix, found_mount_path)
        r = found_mountpoint.os_client.delete_object(
            found_mountpoint.namespace, 
            found_mountpoint.bucket, 
            found_mounted_oci_path
        )
        if r.status not in (200, 204):
            raise Exception('Unable to delete object: oci error {}'.format(r.status))
        self.log.info('%s: exit', log_prefix)

    def head_object(self, voci_path):
        log_prefix = 'VirtualCasper.head_object'
        self.log.info('%s: enter, voci_path=%r', log_prefix, voci_path)

        found_mount_path, found_mountpoint, found_mounted_oci_path = self.find_mountpoint(voci_path)
        if found_mountpoint is None:
            raise Exception('Unable to head object: no mount point')
    
        self.log.info('%s: using mount_path %r', log_prefix, found_mount_path)
        r = found_mountpoint.os_client.head_object(
            found_mountpoint.namespace, 
            found_mountpoint.bucket, 
            found_mounted_oci_path
        )
        self.log.info('%s: exit', log_prefix)
        return r

    def get_object(self, voci_path):
        log_prefix = 'VirtualCasper.get_object'
        self.log.info('%s: enter, oci_path=%r', log_prefix, voci_path)

        found_mount_path, found_mountpoint, found_mounted_oci_path = self.find_mountpoint(voci_path)
        if found_mountpoint is None:
            raise Exception('Unable to get object: no mount point')
    
        self.log.info('%s: using mount_path %r', log_prefix, found_mount_path)
        r = found_mountpoint.os_client.get_object(
            found_mountpoint.namespace, 
            found_mountpoint.bucket, 
            found_mounted_oci_path
        )
        self.log.info('%s: exit', log_prefix)
        return r

    def rename_object(self, src_voci_path, dst_voci_path):
        log_prefix = 'VirtualCasper.rename_object'
        self.log.info('%s: enter, src_voci_path=%r, dst_voci_path=%r', log_prefix, src_voci_path, dst_voci_path)

        src_found_mount_path, src_found_mountpoint, src_found_mounted_oci_path = self.find_mountpoint(src_voci_path)
        if src_found_mountpoint is None:
            raise Exception('Unable to rename object: no mount point')

        dst_found_mount_path, dst_found_mountpoint, dst_found_mounted_oci_path = self.find_mountpoint(dst_voci_path)
        if dst_found_mountpoint is None:
            raise Exception('Unable to rename object: no mount point')

        if src_found_mountpoint.namespace != dst_found_mountpoint.namespace:
            raise Exception('Unable to rename object: cross namespace')

        if src_found_mountpoint.bucket != dst_found_mountpoint.bucket:
            raise Exception('Unable to rename object: cross bucket')

        self.log.info('%s: using mount_path %r', log_prefix, src_found_mount_path)
        rod = oci.object_storage.models.RenameObjectDetails(
            source_name = src_found_mounted_oci_path,
            new_name = dst_found_mounted_oci_path
        )

        r = src_found_mountpoint.os_client.rename_object(
            src_found_mountpoint.namespace, 
            src_found_mountpoint.bucket, 
            rod
        )
        if r.status != 200:
            raise Exception('Unable to rename file')
        self.log.info('%s: exit', log_prefix)

class VirtualCasperMgr(object):
    __instance = None

    @staticmethod
    def set(instance):
        VirtualCasperMgr.__instance = instance

    @staticmethod
    def get():
        return VirtualCasperMgr.__instance

class CasperCheckpoints(GenericCheckpointsMixin, Checkpoints):
    # a file's checkpoint is just another object with .checkpoint suffix
    # Example:
    #     in oci, file path is 'foo/bar.txt'
    #     then checkpoint is 'foo/bar.txt$checkpoint'
    # Note:
    #     (1) When you delete file, you MUST delete the checkpoint as well, otherwise
    #     when someone create a file with the same path, it will have a stale checkpoint
    #     (2) We only keep at most 1 checkpoint
    #     (3) checkpoint is not returned in list_file object

    log = logging.getLogger('CasperCheckpoints')

    def create_file_checkpoint(self, content, format, path):
        log_prefix = 'CasperCheckpoints.create_file_checkpoint'
        self.log.info(
            '%s: enter, content type = %r, format=%r, path=%r', 
            log_prefix, content.__class__.__name__, format, path
        )

        # normalize path
        path = '/' + path.strip('/')

        voci_path = path[1:]

        virtual_casper = VirtualCasperMgr.get()
        if format==FileFormat.TEXT.value:
            bcontent = b'\0' + content.encode('utf-8')
        elif format==FileFormat.BASE64.value:
            b64_bytes = content.encode('ascii')
            bcontent = b'\1' + base64.decodebytes(b64_bytes)

        virtual_casper.put_object(voci_path + FileExtension.CHECKPOINT.value, bcontent)
        
        checkpoint_model = {
            'id': 'checkpoint',
            'last_modified': datetime.fromtimestamp(86400)
        }
        self.log.info('%s: exit', log_prefix)
        return checkpoint_model

    def create_notebook_checkpoint(self, nb, path):
        log_prefix = 'CasperCheckpoints.create_notebook_checkpoint'
        self.log.info('%s: enter, path=%r', log_prefix, path)

        # normalize path
        path = '/' + path.strip('/')

        voci_path = path[1:]

        virtual_casper = VirtualCasperMgr.get()
        with io.StringIO('') as f:
            nbformat.write(nb, f, version=nbformat.NO_CONVERT)
            f.seek(0)
            virtual_casper.put_object(voci_path + FileExtension.CHECKPOINT.value, f.read())

        # so far we have been lying to JupyterLab, we didn't create checkpoint
        checkpoint_model = {
            'id': 'checkpoint',
            'last_modified': datetime.fromtimestamp(86400)
        }
        self.log.info('%s: exit', log_prefix)
        return checkpoint_model

    def get_file_checkpoint(self, checkpoint_id, path):
        log_prefix = 'CasperCheckpoints.get_file_checkpoint'
        self.log.info('%s: enter, checkpoint_id=%r, path=%r', log_prefix, checkpoint_id, path)

        # normalize path
        path = '/' + path.strip('/')

        voci_path = path[1:]

        if checkpoint_id != CHECKPOINT_ID:
            raise HTTPServerError(404,  'Checkpoint does not exist: {}@{}'.format(path, checkpoint_id))

        virtual_casper = VirtualCasperMgr.get()
        try:
            r = virtual_casper.get_object(voci_path + FileExtension.CHECKPOINT.value)
        except oci.exceptions.ServiceError as e:
            if e.status == 404:
                raise HTTPServerError(404,  'Checkpoint does not exist: {}@{}'.format(path, checkpoint_id))
            raise

        if r.data.content[0] == 0:
            content = r.data.content[1:].decode('utf-8')
            format = FileFormat.TEXT.value
        elif r.data.content[0] == 1:
            content = base64.b64encode(r.data.content[1:]).decode('utf-8')
            format = FileFormat.BASE64.value
        else:
            raise Exception("Checkpoint corrupted: {}".format(r.data.content))

        self.log.info('%s: exit', log_prefix)
        return {
            'type': FileType.FILE.value,
            'content': content,
            'format': format
        }

    def get_notebook_checkpoint(self, checkpoint_id, path):
        log_prefix = 'CasperCheckpoints.get_notebook_checkpoint'
        self.log.info('%s: enter, checkpoint_id=%r, path=%r', log_prefix, checkpoint_id, path)

        # normalize path
        path = '/' + path.strip('/')

        voci_path = path[1:]

        if checkpoint_id != CHECKPOINT_ID:
            raise HTTPServerError(404,  'Checkpoint does not exist: {}@{}'.format(path, checkpoint_id))

        virtual_casper = VirtualCasperMgr.get()
        try:
            r = virtual_casper.get_object(voci_path + FileExtension.CHECKPOINT.value)
        except oci.exceptions.ServiceError as e:
            if e.status == 404:
                raise HTTPServerError(404,  'Checkpoint does not exist: {}@{}'.format(path, checkpoint_id))
            raise

        with io.StringIO(r.data.text) as f:
            content = nbformat.read(f, 4)

        self.log.info('%s: exit', log_prefix)
        return {
            'type': FileType.NOTEBOOK.value,
            'content': content,
        }

    def delete_checkpoint(self, checkpoint_id, path):
        log_prefix = 'CasperCheckpoints.delete_checkpoint'
        self.log.info('%s: enter, checkpoint_id=%r, path=%r', log_prefix, checkpoint_id, path)

        # normalize path
        path = '/' + path.strip('/')

        voci_path = path[1:]

        if checkpoint_id != CHECKPOINT_ID:
            # such checkpoint should never have existed
            self.log.info('%s: exit', log_prefix)
            return

        virtual_casper = VirtualCasperMgr.get()
        try:
            r = virtual_casper.get_object(voci_path + FileExtension.CHECKPOINT.value)
        except oci.exceptions.ServiceError as e:
            if e.status == 404:
                # we are good, check point does not exist
                self.log.info('%s: exit', log_prefix)
                return
            raise

        virtual_casper.delete_object(voci_path + FileExtension.CHECKPOINT.value)
        self.log.info('%s: exit', log_prefix)

    def list_checkpoints(self, path):
        log_prefix = 'CasperCheckpoints.list_checkpoints'
        self.log.info('%s: enter, path=%r', log_prefix, path)

        # normalize path
        path = '/' + path.strip('/')

        voci_path = path[1:]

        virtual_casper = VirtualCasperMgr.get()
        try:
            r = virtual_casper.head_object(voci_path + FileExtension.CHECKPOINT.value)
        except oci.exceptions.ServiceError as e:
            if e.status == 404:
                # we are good, check point does not exist
                self.log.info('%s: exit', log_prefix)
                return []
            raise

        info = {
            'id': CHECKPOINT_ID,
            'last_modified': datetime.fromtimestamp(86400)
        }

        self.log.info('%s: exit', log_prefix)
        return [info]

    def rename_checkpoint(self, checkpoint_id, old_path, new_path):
        # since our checkpoint is saved along with the file, no need to rename checkpoint separately
        log_prefix = 'CasperCheckpoints.rename_checkpoint'
        self.log.info('%s: enter, old_path=%r, new_path=%r', log_prefix, old_path, new_path)

        # normalize path
        old_path = '/' + old_path.strip('/')
        new_path = '/' + new_path.strip('/')
        if old_path == new_path:
            self.log.info('%s: exit', log_prefix)
            return
        
        virtual_casper = VirtualCasperMgr.get()
        virtual_casper.rename_object(
            old_path[1:] + FileExtension.CHECKPOINT.value,
            new_path[1:] + FileExtension.CHECKPOINT.value
        )

        self.log.info('%s: exit', log_prefix)

class JupyterCasperCM(ContentsManager):
    checkpoints_class = CasperCheckpoints

    # with this, you can define c.NotebookApp.JupyterCasperCM.fstab
    # in config file and able to access it latter in __init__ method

    fstab   = Unicode(config=True)

    __DEBUG_API = True

    def __print_ret(self, ret):
        if self.__DEBUG_API:
            print('>> API Return')
            for k, v in ret.items():
                if k == 'content':
                    if v is None:
                        v = 'None'
                    else:
                        v = 'Not none, {}'.format(v.__class__.__name__)
                print('{}: {}'.format(k, v))
            print('-------------')

    def __get_format_for_file(self, model, path):
        if model is None:
            format = None
        else:
            format = model.get('format')
        if format is None:
            if mimetypes.guess_type(path)[0] == MimeType.TEXT_PLAIN.value:
                format = FileFormat.TEXT.value
            else:
                format = FileFormat.BASE64.value
        return format


    def __init__(self, *args, **kwargs):
        log_prefix = 'JupyterCasperCM.__init__'
        self.log.info('%s: enter', log_prefix)
        super(ContentsManager, self).__init__(*args, **kwargs)

        with open(self.fstab, 'r') as f:
            mount_config = json.load(f)

        virtual_casper = VirtualCasper(mount_config)
        VirtualCasperMgr.set(virtual_casper)

        self.log.info('%s: exit', log_prefix)


    def __get_notebook(self, path, content, format):
        log_prefix = 'JupyterCasperCM.__get_notebook'
        self.log.info(
            '%s: enter, path=%r, content=%r, format=%r', 
            log_prefix, path, content, format
        )

        # path is always starts with '/'
        voci_path = path[1:]
        virtual_casper = VirtualCasperMgr.get()
        objs = virtual_casper.list_objects(voci_path, fields='md5,timeCreated,size', limit=1)
        if len(objs) != 1 or objs[0].name != voci_path:
            raise Exception(
                'Unable to get notebook: len = {}, name = {}'.format(
                    len(objs),
                    objs[0].name if len(objs)>0 else None
                )
            )
        time_created = objs[0].time_created.astimezone(pytz.utc).replace(tzinfo=None)

        if content:
            r = virtual_casper.get_object(voci_path)
        else:
            r = virtual_casper.head_object(voci_path)
        if r.status != 200:
            raise Exception('Unable to get notebook')
        last_modified_str = r.headers['last-modified'].split(',')[1].strip()
        last_modified = datetime.strptime(last_modified_str, '%d %b %Y %H:%M:%S GMT')


        ret = {
            'created': time_created,
            'last_modified': last_modified,
            'mimetype': None,
            'name': path.split('/')[-1],
            'path': path,
            'type': FileType.NOTEBOOK.value,
            'writable': True,
        }

        if not content:
            ret['content'] = None
            ret['format'] = None
            self.__print_ret(ret)
            self.log.info('%s: exit', log_prefix)
            return ret

        with io.StringIO(r.data.text) as f:
            ret['content'] = nbformat.read(f, 4)
            ret['format'] = FileFormat.JSON.value
            self.__print_ret(ret)
            self.log.info('%s: exit', log_prefix)
            return ret

    def __get_file(self, path, content, format):
        log_prefix = 'JupyterCasperCM.__get_file'
        self.log.info(
            '%s: enter, path=%r, content=%r, format=%r', 
            log_prefix, path, content, format
        )

        # path is always starts with '/'
        voci_path = path[1:]
        virtual_casper = VirtualCasperMgr.get()
        objs = virtual_casper.list_objects(voci_path, fields='md5,timeCreated,size', limit=1)
        if len(objs) != 1 or objs[0].name != voci_path:
            raise Exception('Unable to get file')
        time_created = objs[0].time_created.astimezone(pytz.utc).replace(tzinfo=None)

        if content:
            r = virtual_casper.get_object(voci_path)
        else:
            r = virtual_casper.head_object(voci_path)
        last_modified_str = r.headers['last-modified'].split(',')[1].strip()
        last_modified = datetime.strptime(last_modified_str, '%d %b %Y %H:%M:%S GMT')

        ret = {
            'created': time_created,
            'last_modified': last_modified,
            'name': path.split('/')[-1],
            'path': path,
            'type': FileType.FILE.value,
            'writable': True,
        }

        if not content:
            ret['content'] = None
            ret['format'] = None
            ret['mimetype'] = None
            self.__print_ret(ret)
            self.log.info('%s: exit', log_prefix)
            return ret

        if content:
            if format is None:
                format = self.__get_format_for_file(None, path)
                self.log.info('%s: guess format is :%r', log_prefix, format)
            if format==FileFormat.TEXT.value:
                ret['content'] = r.data.text
                ret['mimetype'] = MimeType.TEXT_PLAIN.value
                ret['format'] = format
            elif format==FileFormat.BASE64.value:
                ret['content'] = base64.b64encode(r.data.content).decode('utf-8')
                ret['mimetype'] = MimeType.APP_OCT_STREAM.value
            else:
                raise Exception('Uncognized format: {}'.format(format))
            ret['format'] = format
        self.__print_ret(ret)
        self.log.info('%s: exit', log_prefix)
        return ret

    def __get_directory(self, path, content, format):
        log_prefix = 'JupyterCasperCM.__get_directory'
        self.log.info(
            '%s: enter, path=%r, content=%r, format=%r', 
            log_prefix, path, content, format
        )

        # path is always starts with '/'
        # TODO: deal with directory for large files
        if path == '/':
            voci_path = ''
        else:
            voci_path = path[1:].strip('/') + '/'

        virtual_casper = VirtualCasperMgr.get()
        limit = 1 if content else None
        objs = virtual_casper.list_objects(voci_path, fields='md5,timeCreated,size')
        # casper does not really has directory
        time_created  = datetime.fromtimestamp(86400)
        last_modified = datetime.fromtimestamp(86400)

        if not content:
            self.log.info('%s: exit', log_prefix)
            return {
                'content': None,
                'created': time_created,
                'format': None,
                'last_modified': last_modified,
                'mimetype': None,
                'name': path.split('/')[-1],
                'path': path,
                'type': FileType.DIRECTORY.value,
                'writable': True,
            }

        children = set()
        contents = []

        for obj in objs:
            remaining_name = obj.name[len(voci_path):]
            if len(remaining_name) == 0:
                continue
            if remaining_name == '__dir__':
                continue
            if remaining_name.endswith(FileExtension.CHECKPOINT.value):
                # do not show checkpoint to user
                continue
            if '/' in remaining_name:
                children.add(remaining_name.split('/')[0])
            else:
                # this is a file
                if path.endswith(FileExtension.NOTEBOOK.value):
                    type = FileType.NOTEBOOK.value
                else:
                    type = FileType.FILE.value
                content = {
                    'type': type,
                    'name': remaining_name,
                    'path': '/' + obj.name
                }
                contents.append(content)
        
        for child in children:
            contents.append({
                'type': FileType.DIRECTORY.value,
                'name': child,
                'path': path + '/' + child
            })

        self.log.info('%s: exit', log_prefix)

        return {
            'content': contents,
            'created': time_created,
            'format': FileFormat.JSON.value,
            'last_modified': last_modified,
            'mimetype': None,
            'name': path.split('/')[-1],
            'path': path,
            'type': FileType.DIRECTORY.value,
            'writable': True,
        }

    def __save_notebook(self, model, path):
        log_prefix = 'JupyterCasperCM.__save_notebook'
        self.log.info('%s: enter, path=%r', log_prefix, path)
        voci_path = path[1:]
        with io.StringIO('') as f:
            nb = nbformat.from_dict(model['content'])
            self.check_and_sign(nb, path)
            nbformat.write(nb, f, version=nbformat.NO_CONVERT)
            f.seek(0)
            virtual_casper = VirtualCasperMgr.get()
            virtual_casper.put_object(voci_path, f.read().encode('utf-8'))
        self.log.info('%s: exit', log_prefix)


    def __save_file(self, model, path):
        log_prefix = 'JupyterCasperCM.__save_file'
        self.log.info('%s: enter, path=%r', log_prefix, path)
        format = self.__get_format_for_file(model, path)
        self.log.info('%s: fromat is:%r', log_prefix, format)
        if format==FileFormat.TEXT.value:
            bcontent = model['content'].encode('utf-8')
        elif format==FileFormat.BASE64.value:
            b64_bytes = model['content'].encode('ascii')
            bcontent = base64.decodebytes(b64_bytes)
        else:
            raise Exception('{} is unrecognized file format'.format(format))
        voci_path = path[1:]
        virtual_casper = VirtualCasperMgr.get()
        virtual_casper.put_object(voci_path, bcontent)
        self.log.info('%s: exit', log_prefix)


    def __save_directory(self, model, path):
        log_prefix = 'JupyterCasperCM.__save_directory'
        self.log.info('%s: enter, path=%r', log_prefix, path)
        voci_path = path[1:] + '/__dir__'
        virtual_casper = VirtualCasperMgr.get()
        virtual_casper.put_object(voci_path, b'')
        self.log.info('%s: exit', log_prefix)


    def get(self, path, content=True, type=None, format=None):
        log_prefix = 'JupyterCasperCM.get'
        self.log.info(
            '%s: path=%r, content=%r, type=%r, format=%r', 
            log_prefix, path, content, type, format
        )

        asking_for_dir = path.endswith('/')

        # normalize path
        path = '/' + path.strip('/')

        # guess type and formatf
        if type is None:
            # in sync with save method??
            if path.endswith(FileExtension.NOTEBOOK.value):
                type = FileType.NOTEBOOK.value
            elif asking_for_dir or path == '/':
                type = FileType.DIRECTORY.value
            elif self.__dir_exists(path):
                type = FileType.DIRECTORY.value
            else:
                type = FileType.FILE.value
            self.log.info('%s: guess type is:%r', log_prefix, type)
        
        if type == FileType.NOTEBOOK.value:
            ret = self.__get_notebook(path, content, format)
            self.log.info('%s: exit', log_prefix)
            return ret
        elif type == FileType.FILE.value:
            ret = self.__get_file(path, content, format)
            self.log.info('%s: exit', log_prefix)
            return ret
        elif type == FileType.DIRECTORY.value:
            ret = self.__get_directory(path, content, format)
            self.log.info('%s: exit', log_prefix)
            return ret
        else:
            raise Exception('Invalid type: {}'.format(type))

    
    def save(self, model, path=''):
        log_prefix = 'JupyterCasperCM.save'
        self.log.info('%s: enter, path=%r', log_prefix, path)

        # normalize path
        path = '/' + path.strip('/')

        type = model.get('type')
        self.log.info('%s: type from model is:%r', log_prefix, type)
        if type is None:
            if path.endswith(FileExtension.NOTEBOOK.value):
                type = FileType.NOTEBOOK.value
            elif self.__dir_exists(path):
                type = FileType.DIRECTORY.value
            else:
                type = FileType.FILE.value
            self.log.info('%s: guess type is:%r', log_prefix, type)

        if type == FileType.NOTEBOOK.value:
            self.__save_notebook(model, path)
        elif type == FileType.FILE.value:
            self.__save_file(model, path)
        elif type == FileType.DIRECTORY.value:
            self.__save_directory(model, path)
        else:
            raise Exception('Invalid type: {}'.format(type))
        
        model_ret = self.get(path, content=False)
        self.log.info('%s: exit', log_prefix)
        return model_ret
    
    def delete_file(self, path):
        log_prefix = 'JupyterCasperCM.delete_file'
        self.log.info('%s: enter, path=%r', log_prefix, path)

        virtual_casper = VirtualCasperMgr.get()

        # normalize path
        path = '/' + path.strip('/')

        voci_path = path[1:]
        if not self.__dir_exists(path):
            # we are deleting file, not directory
            r = virtual_casper.delete_object(voci_path)
            self.log.info('%s: exit', log_prefix)
            return

        # we are deleting directory
        # BUG: if mount point has overlap, some file file may not get deleted
        #      because they might be hidden by another mount point
        objs = virtual_casper.list_objects(voci_path + '/')
        for obj in objs:
            if self.__DEBUG_API:
                print('deleting file: {}'.format(obj.name))
            virtual_casper.delete_object(obj.name)
        self.log.info('%s: exit', log_prefix)


        
    
    def rename_file(self, old_path, new_path):
        log_prefix = 'JupyterCasperCM.delete_file'
        self.log.info('%s: enter, old_path=%r, new_path=%r', log_prefix, old_path, new_path)

        old_path = '/' + old_path.strip('/')
        new_path = '/' + new_path.strip('/')
        if old_path == new_path:
            return
        
        virtual_casper = VirtualCasperMgr.get()
        
        if not self.__dir_exists(old_path):
            # assuming the old_path is a file
            virtual_casper.rename_object(old_path[1:], new_path[1:])
            self.log.info('%s: exit', log_prefix)
            return
        
        # old_path is a directory
        objs = virtual_casper.list_objects(old_path[1:] + '/')
        old_path_len = len(old_path[1:])
        for obj in objs:
            old_voci_path = obj.name
            new_voci_path = new_path[1:] + obj.name[old_path_len:]
            if self.__DEBUG_API:
                print('rename: from {} to {}'.format(old_voci_path, new_voci_path))
            virtual_casper.rename_object(old_voci_path, new_voci_path)
        self.log.info('%s: exit', log_prefix)



        
    
    def file_exists(self, path):
        log_prefix = 'JupyterCasperCM.file_exists'
        self.log.info('%s: enter, path=%r', log_prefix, path)

        # normalize path
        path = '/' + path.strip('/')

        voci_path = path[1:]
        
        if not voci_path:
            # root is always a directory, not a file
            self.log.info('%s: ret = %r', log_prefix, False)
            self.log.info('%s: exit', log_prefix)
            return False

        virtual_casper = VirtualCasperMgr.get()
        try:
            virtual_casper.head_object(voci_path)
            self.log.info('%s: ret = %r', log_prefix, True)
            self.log.info('%s: exit', log_prefix)
            return True
        except oci.exceptions.ServiceError as e:
            if e.status == 404:
                self.log.info('%s: ret = %r', log_prefix, False)
                self.log.info('%s: exit', log_prefix)
                return False
            raise
    
    def __dir_exists(self, path):
        log_prefix = 'JupyterCasperCM.__dir_exists'
        self.log.info('%s: enter, path=%r', log_prefix, path)

        # normalize path
        path = '/' + path.strip('/')

        if path == '/':
            voci_path = ''
        else:
            voci_path = path[1:].strip('/') + '/'
        
        if not voci_path:
            # root is always a directory, not a file
            self.log.info('%s: ret = %r', log_prefix, True)
            self.log.info('%s: exit', log_prefix)
            return True

        virtual_casper = VirtualCasperMgr.get()
        # scan for mount points, they are considered as directory
        ret = None
        for mount_path, mountpoint in virtual_casper.mountpoints.items():
            if mountpoint.mount_voci_path.startswith(voci_path):
                self.log.info('%s: ret = %r', log_prefix, True)
                self.log.info('%s: exit', log_prefix)
                return True

        
        objs = virtual_casper.list_objects(voci_path, fields='md5,timeCreated,size', limit=1)
        ret = len(objs) > 0
        self.log.info('%s: ret = %r', log_prefix, ret)
        self.log.info('%s: exit', log_prefix)
        return ret

    def dir_exists(self, path):
        log_prefix = 'JupyterCasperCM.dir_exists'
        self.log.info('%s: enter, path=%r', log_prefix, path)
        ret = self.__dir_exists(path)
        self.log.info('%s: exit', log_prefix)
        return ret

    def is_hidden(self, path):
        return False
