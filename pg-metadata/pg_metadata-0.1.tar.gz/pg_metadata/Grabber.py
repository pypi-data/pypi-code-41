#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
from multiprocessing import Pool
from pg_metadata.Database import Database

class Grabber():
    def __init__(self, source_connect, target_path, exclude_schemas=[]):
        assert source_connect is not None
        assert isinstance(source_connect, dict)
        assert len(source_connect.keys()) > 0

        assert target_path is not None
        assert isinstance(target_path, str)
        assert len(target_path) > 0

        self.Connect = source_connect
        self.TargetPath = target_path
        self.ExcludeSchemas = exclude_schemas

        if os.path.exists(self.TargetPath):
            shutil.rmtree(self.TargetPath, True)
        os.mkdir(self.TargetPath)

    def GetPath(self, schema_name, folder_name, file_name):
        if not os.path.exists(self.TargetPath):
            os.mkdir(self.TargetPath)

        schema_path = '/'.join([self.TargetPath, schema_name])
        if not os.path.exists(schema_path):
            os.mkdir(schema_path)

        folder_path = '/'.join([schema_path, folder_name])
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        file_name += '.sql'
        file_name = '/'.join([folder_path, file_name])

        return file_name

    def WriteTable(self, table):
        file_name = self.GetPath(table.Schema, table.Folder, table.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(table.QueryDDL())

    def WriteFunction(self, function):
        file_name = self.GetPath(function.Schema, function.Folder, function.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(function.QueryDDL())

    def WriteView(self, view):
        file_name = self.GetPath(view.Schema, view.Folder, view.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(view.QueryDDL())

    def WriteSequence(self, sequence):
        file_name = self.GetPath(sequence.Schema, sequence.Folder, sequence.Name)
        with open(file_name, 'w', encoding='utf-8') as wf:
            wf.write(sequence.QueryDDL())

    def Grab(self):
        source_db = Database(self.Connect, self.ExcludeSchemas)
        source_db.Parse()

        pool = Pool(processes=8)

        pool.map(self.WriteTable,    [v for k,v in source_db.Tables.items()])
        pool.map(self.WriteFunction, [v for k,v in source_db.Functions.items()])
        pool.map(self.WriteView,     [v for k,v in source_db.Views.items()])
        pool.map(self.WriteSequence, [v for k,v in source_db.Sequences.items()])
