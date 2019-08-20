# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 21:50:38 2018

@author: Sébastien Weber
"""
import sys
import os
from pathlib import Path
import codecs
path_here = os.path.split(__file__)[0]
sys.path.append(path_here)



from dateutil.parser import parse
import csv
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pyqtgraph.dockarea import DockArea, Dock
from pyqtgraph.parametertree import Parameter, ParameterTree
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph import ColorMap
import custom_parameter_tree as custom_tree

import tables
import numpy as np
import datetime
from enum import Enum
from pathlib import Path
from icons import QtDesigner_ressources_rc
from yawrap import Doc
import webbrowser
#%%

#colorder=['idnumber','day','task_type','name','time_start','time_end','N_needed','N_filled','remarqs','stuff_needed','affected_volunteers']
col_task_header=['Task Id','day','type','name','time start','time end','N needed','N filled','remarqs','stuff needed','affected volunteers']
col_volunteer_header=['Vol. Id', 'name', 'remarqs','affected tasks']


def select_file(start_path=None, save=True, ext=None):
    """
        Save or open a file with Qt5 file dialog, to be used within an Qt5 loop.

        =============== ======================================= ===========================================================================
        **Parameters**     **Type**                              **Description**

        *start_path*       Path object or str or None, optional  the path Qt5 will open in te dialog
        *save*             bool, optional                        * if True, a savefile dialog will open in order to set a savefilename
                                                                 * if False, a openfile dialog will open in order to open an existing file
        *ext*              str, optional                         the extension of the file to be saved or opened
        =============== ======================================= ===========================================================================

        Returns
        -------
        Path object
            the Path object pointing to the file



    """
    if ext is None:
        ext = '*'
    if not save:
        if type(ext) != list:
            ext = [ext]

        filter = "Data files ("
        for ext_tmp in ext:
            filter += '*.' + ext_tmp + " "
        filter += ")"
    if start_path is not None:
        if type(start_path) is not str:
            start_path = str(start_path)
    if save:
        fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Enter a .' + ext + ' file name', start_path,
                                                      ext + " file (*." + ext + ")")
    else:
        fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a file name', start_path, filter)

    fname = fname[0]
    if fname != '':  # execute if the user didn't cancel the file selection
        fname = Path(fname)
        if save:
            parent = fname.parent
            filename = fname.stem
            fname = parent.joinpath(filename + "." + ext)  # forcing the right extension on the filename
    return fname  # fname is a Path object


class TimeLineView(QtWidgets.QTableView):

    def __init__(self,task_view=None):
        super(TimeLineView, self).__init__()
        self.task_view=task_view
        self.menu = QtWidgets.QMenu()
        show_tasks = self.menu.addAction('Show These Tasks')

        show_tasks.triggered.connect(self.show_tasks)
        self.doubleClicked.connect(self.show_tasks)


    def show_tasks(self):
        index = self.currentIndex()
        target_time_stamp=int(parse(index.model().headerData(index.column(), QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole),
                  dayfirst=True).timestamp())
        day=index.model().headerData(index.row(),QtCore.Qt.Vertical,QtCore.Qt.DisplayRole)
        self.task_view.model().setDayFilter(day)
        self.task_view.model().setTimeStampFilter(target_time_stamp)


    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())



class TimeLineModel(QtCore.QAbstractTableModel):
    def __init__(self,h5file=None,time_step=30,view_type='N_needed'):
        super(TimeLineModel,self).__init__()
        self.colors=ColorMap([0,1],[[0,255,0],[255,0,0]])
        self.view_type=view_type #could be 'N_needed', 'N_filled' or a volunteer name
        self.time_step=time_step
        self.Nsteps=None
        self.days=None
        if h5file is None:
            raise Exception('No valid pytables file')
        elif type(h5file)==str or type(h5file)==Path:
            self.h5file=tables.open_file(str(h5file),mode='a',title='List of Tasks and volunteers for RTA 2018')
        elif type(h5file)==tables.File:
            self.h5file=h5file

        self.update_steps()

    def update_view_type(self,view_type):
        self.view_type = view_type
        self.update()

    def update(self,*args,**kwargs):
        self.update_steps()
        index_ul=self.createIndex(0,0)
        index_br=self.createIndex(len(self.days)-1,self.Nsteps-1)
        self.dataChanged.emit(index_ul,index_br,[QtCore.Qt.DisplayRole for ind in range(self.Nsteps*len(self.days))])

        
        
    def update_steps(self):
        try:
            self.task_table = self.h5file.get_node('/tasks/tasks_table')
            self.days = list(set(self.task_table[:]['day']))
            day_datetime = datetime.datetime.fromtimestamp(min(self.days))

            self.time_start=min([datetime.datetime.fromtimestamp(x).replace(year=day_datetime.year,month=day_datetime.month,day=day_datetime.day)for x in self.task_table[:]['time_start']]).timestamp()
            self.time_end = max([datetime.datetime.fromtimestamp(x).replace(year=day_datetime.year,month=day_datetime.month,day=day_datetime.day)for x in self.task_table[:]['time_end']]).timestamp()

            self.Nsteps=int((self.time_end-self.time_start)/(self.time_step*60)+1)
            self.time_steps=np.linspace(self.time_start,self.time_end,self.Nsteps).astype('int')
            self.names=self.task_table.colnames

            self.N_needed=np.zeros((len(self.days),self.Nsteps)).astype('int')
            self.N_filled = np.zeros((len(self.days), self.Nsteps)).astype('int')
            for ind_day,day in enumerate(self.days):
                for ind_time in range(len(self.time_steps)):
                    time_s=self.time_steps[ind_time]
                    if time_s==self.time_steps[-1]:
                        time_e=time_s
                    else:
                        time_e=self.time_steps[ind_time+1]
                    day_datetime=datetime.datetime.fromtimestamp(day)
                    time_s_datetime=datetime.datetime.fromtimestamp(time_s)
                    time_s=int(time_s_datetime.replace(year=day_datetime.year,month=day_datetime.month,day=day_datetime.day).timestamp())
                    time_e_datetime=datetime.datetime.fromtimestamp(time_e)
                    time_e=int(time_e_datetime.replace(year=day_datetime.year,month=day_datetime.month,day=day_datetime.day).timestamp())
                    self.N_needed[ind_day,ind_time] = int(np.sum([ x['N_needed'] for x in self.task_table.where("""(day == {:0d}) & (time_start <= {:0d}) & (time_end >= {:0d})""".format(day,time_s,time_e)) ]))
                    self.N_filled[ind_day,ind_time] = int(np.sum([ x['N_filled'] for x in self.task_table.where("""(day == {:0d}) & (time_start <= {:0d}) & (time_end >= {:0d})""".format(day,time_s,time_e)) ]))
        except:
            pass
        
    def close(self):
        self.h5file.close()
        
    def rowCount(self,index):
        if self.days is not None:
            return len(self.days)
        else: return 0
    
    def columnCount(self,index):
        if self.Nsteps is not None:
            return self.Nsteps
        else: return 0

    def data(self,index=QtCore.QModelIndex(),role=QtCore.Qt.DisplayRole):
        try:
            self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
            self.task_table = self.h5file.get_node('/tasks/tasks_table')

            if role==QtCore.Qt.DisplayRole:
                if self.view_type == 'N_needed':
                    return int(self.N_needed[index.row(),index.column()])
                elif self.view_type == 'N_filled':
                    return int(self.N_filled[index.row(), index.column()])
                elif self.view_type == '':
                    return QtCore.QVariant()
                else:
                    return QtCore.QVariant()




            elif role==QtCore.Qt.BackgroundRole:
                Nneeded = self.N_needed[index.row(), index.column()]
                Nfilled = self.N_filled[index.row(), index.column()]



                brush=QtGui.QBrush(QtCore.Qt.SolidPattern)
                if self.view_type == 'N_needed':
                    Ntot = np.max(self.N_needed[index.row(), :])
                    if Ntot==0:
                        Ntot=1
                    brush.setColor(self.colors.map(Nneeded/Ntot,mode='qcolor'))
                elif self.view_type == 'N_filled':
                    if Nneeded == 0:
                        Nneeded=1
                        Nfilled = 1
                        ratio = 0
                    else:
                        if Nfilled < Nneeded:
                            ratio = 1
                        else:
                            ratio = 0
                    brush.setColor(self.colors.map(ratio, mode='qcolor'))
                elif self.view_type == '':
                    return QtCore.QVariant()
                else:
                    vol_row = self.volunteer_table.get_where_list("""(name == {:})""".format(self.view_type.encode()))[
                        0]
                    tasks_row = [self.task_table.get_where_list("""(idnumber == {:})""".format(id))[0] for id in
                                 self.volunteer_table[vol_row]['affected_tasks'] if id != -1]
                    ts = []
                    te = []
                    flag = False
                    time_step = QtCore.QDateTime().fromSecsSinceEpoch(self.time_steps[index.column()]).addDays(
                        index.row()).toSecsSinceEpoch()
                    for row in tasks_row:
                        # self.time_steps are properly defined only for the first day, to do add a loop on the number of days adding a day to all time_steps

                        if time_step >= self.task_table[row]['time_start'] and time_step < self.task_table[row]['time_end']:
                            flag = True
                            break
                    if  not(time_step >= self.volunteer_table[vol_row]['time_start'][index.row()] and time_step <= self.volunteer_table[vol_row]['time_end'][index.row()]):
                        flag = True
                    if flag:
                        brush.setColor(QtGui.QColor(255,0,0))
                    else:
                        brush.setColor(QtGui.QColor(0,255,0))


                return brush
            else:
                return QtCore.QVariant()
        except Exception as e:
            return QtCore.QVariant()

    def headerData(self,section,orientation,role):
        if role==QtCore.Qt.DisplayRole:
            if orientation==QtCore.Qt.Horizontal:
                d=datetime.datetime.fromtimestamp(self.time_start+60*section*self.time_step)
                return d.strftime('%H:%M')
            else:
                d=datetime.datetime.fromtimestamp(self.days[section])
                return d.strftime('%A')
        else:
            return QtCore.QVariant()

# class VolunteerItemDelegate(QtWidgets.QStyledItemDelegate):
#
#     def __init__(self):
#         super(VolunteerItemDelegate,self).__init__()
#
#
#     def paint(self, painter, option, index):
#         if index.column()>1:
#             data_list=QtWidgets.QListWidget()
#             data_list.addItems([str(d) for d in index.data()])
#
#             data_list.render(painter)
#
#         else:
#             super(VolunteerItemDelegate,self).paint(painter,option,index)




class VolunteerModel(QtCore.QAbstractTableModel):
    update_signal=pyqtSignal()

    def __init__(self,h5file=None,Ndays=1,list_ids=None):
        super(VolunteerModel,self).__init__()
        self.list_ids = list_ids
        self.Ndays = Ndays
        self.day_list=[QtCore.QDateTime().fromSecsSinceEpoch(h5file.root._v_attrs['event_day']).addDays(day) for day in range(Ndays)]
        if h5file is None:
            raise Exception('No valid pytables file')
        elif type(h5file)==str or type(h5file)==Path:
            self.h5file=tables.open_file(str(h5file),mode='a',title='List of Tasks and volunteers for RTA 2018')
        elif type(h5file)==tables.File:
            self.h5file=h5file


    def close(self):
        try:
            self.h5file.close()
        except:
            pass

    def rowCount(self, index):
        if self.list_ids is not None:
            return len(self.list_ids)
        else:
            self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
            return self.volunteer_table.nrows

    def columnCount(self, index):
        if self.list_ids is not None:
            return self.Ndays+2
        else:
            return self.Ndays+4


    def data(self, index=QtCore.QModelIndex(), role=QtCore.Qt.DisplayRole):
        self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
        if role == QtCore.Qt.DisplayRole:

            if self.list_ids is not None:
                if index.column() == 1:
                    return self.volunteer_table[self.list_ids[index.row()]][index.column()].decode()

                elif index.column() == 0:  # idnumber
                    return int(self.volunteer_table[self.list_ids[index.row()]][index.column()])

                else:
                    ind_time = index.column() - 2
                    start = self.volunteer_table[index.row()]['time_start'][ind_time]
                    stop = self.volunteer_table[index.row()]['time_end'][ind_time]
                    if not (start == -1 or stop == -1):
                        s = datetime.datetime.fromtimestamp(start).strftime(
                            '%H:%M') + ' -> ' + datetime.datetime.fromtimestamp(stop).strftime('%H:%M')
                        return s
                    else:
                        return QtCore.QVariant()
            else:

                if index.column() == 1 or index.column() == 2:  # name or remarqs
                    dat = self.volunteer_table[index.row()][index.column()]
                    return dat.decode()

                elif index.column() == 0: # idnumber
                    dat = self.volunteer_table[index.row()][index.column()]
                    return int(dat)

                elif index.column() == 3: #affected tasks
                    return str([val for val in self.volunteer_table[index.row()]['affected_tasks'] if val != -1])

                else:
                    ind_time=index.column()-4
                    start=self.volunteer_table[index.row()]['time_start'][ind_time]
                    stop=self.volunteer_table[index.row()]['time_end'][ind_time]
                    if not(start ==-1 or stop==-1):
                        s=datetime.datetime.fromtimestamp(start).strftime('%H:%M')+' -> '+datetime.datetime.fromtimestamp(stop).strftime('%H:%M')
                        return s
                    else:
                        return QtCore.QVariant()
        else:
            return QtCore.QVariant()

    def headerData(self,section,orientation,role):
        self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
        if role==QtCore.Qt.DisplayRole:
            if orientation==QtCore.Qt.Horizontal:
                if self.list_ids is not None:
                    if section <= 1:
                        return col_volunteer_header[section]
                    else:
                        try:
                            return 'Day {:02d}:'.format(section - 2)
                        except:
                            return QtCore.QVariant()
                else:
                    if section<=3:
                        return col_volunteer_header[section]
                    else:
                        try:
                            return 'Day {:02d}:'.format(section-4)
                        except:
                            return QtCore.QVariant()
            else:
                return QtCore.QVariant()
        else:
            return QtCore.QVariant()

    def edit_data(self,index):
        self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
        vol_id=index.sibling(index.row(),self.volunteer_table.colnames.index('idnumber')).data()
        vol_row=self.volunteer_table.get_where_list("""(idnumber == {:})""".format(vol_id))[0]
        mapper=VolunteerWidgetMapper(self.h5file,vol_row)
        res=mapper.show_dialog()
        if res is not None:
            self.task_param_to_row(res,vol_row)

    def task_param_to_row(self,param,row_index=None):
        self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
        try:

            row_data=dict()
            row_data['idnumber'] =int( param.child('volunteer_settings', 'id').value())
            row_data['name'] = param.child('volunteer_settings', 'name').value().encode()
            row_data['remarqs'] = param.child('volunteer_settings', 'remarqs').value().encode()
            row_data['present'] = np.array([par.child(('present')).value() for par in param.child('volunteer_settings','day_list').children()],dtype='bool')

            row_data['time_start'] = np.array([int(QtCore.QDateTime(self.day_list[ind].date(),par.child(('time_start')).value()).toMSecsSinceEpoch()/1000) if par.child(('present')).value() else -1 for ind,par in enumerate(param.child('volunteer_settings','day_list').children()) ],dtype='int32')
            row_data['time_end'] = np.array([int(QtCore.QDateTime(self.day_list[ind].date(),par.child(('time_end')).value()).toMSecsSinceEpoch()/1000) if par.child(('present')).value() else -1 for ind,par in enumerate(param.child('volunteer_settings','day_list').children())],dtype='int32')

            try:
                row_data['affected_tasks'] = self.volunteer_table[row_index]['affected_tasks']
            except:
                row_data['affected_tasks'] = np.ones((50,),dtype='int64')*(-1)

            if row_index is None:
                row_index = self.volunteer_table.nrows+1
                row = self.volunteer_table.row
                for k in self.volunteer_table.colnames:
                    row[k]=row_data[k]
                row.append()
                self.volunteer_table.flush()


            else:


                dat=[tuple([row_data[k] for k in self.volunteer_table.colnames if k in row_data]) ]
                self.volunteer_table.modify_rows(start=row_index,stop=row_index+1,step=1,rows=dat)
                index_ul=self.createIndex(row_index,0)
                index_br=self.createIndex(row_index,9)
                self.dataChanged.emit(index_ul,index_br,[QtCore.Qt.DisplayRole for ind in range(10)])
                self.volunteer_table.flush()

            self.update_signal.emit()
            pass

        except Exception as e:
            print(e)

    def remove_data(self,index,rows_ids):
        self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
        self.task_table = self.h5file.get_node('/tasks/tasks_table')
        msgBox=QtWidgets.QMessageBox()
        msgBox.setText("You are about to delete rows!")
        msgBox.setInformativeText("Are you sure you want to delete rows with ids: {:}".format([row[1] for row in rows_ids]))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        res = msgBox.exec()

        if res==QtWidgets.QMessageBox.Ok:
            for row,id in rows_ids:
                if len([task for task in self.volunteer_table[row]['affected_tasks'] if task != -1]) == 0:
                    self.beginRemoveRows(index.parent(),row,row)
                    self.volunteer_table.remove_row(self.volunteer_table.get_where_list("""(idnumber == {:})""".format(id))[0])
                    self.endRemoveRows()
                else:
                    msgBox = QtWidgets.QMessageBox()
                    msgBox.setText("Volunteer with id: {:} is affected to tasks.".format(id))
                    msgBox.setInformativeText("Do you still want to remove him/her?")
                    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                    msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                    res = msgBox.exec()
                    if res == QtWidgets.QMessageBox.Ok:
                        self.remove_task(self.createIndex(row,0),select= False)
                        self.beginRemoveRows(index.parent(), row, row)
                        self.volunteer_table.remove_row(self.volunteer_table.get_where_list("""(idnumber == {:})""".format(id))[0])
                        self.endRemoveRows()
                self.update_signal.emit()


    def append_row(self,index):
        self.insertRows(self.rowCount(index),1,index.parent())
        index_ul = self.createIndex(index.row()+1, 0)
        index_br = self.createIndex(index.row()+1, 9)
        self.dataChanged.emit(index_ul, index_br, [QtCore.Qt.DisplayRole for ind in range(10)])
        self.update_signal.emit()


    def insertRows(self, row: int, count: int, parent):
        self.beginInsertRows(parent,row-1,row-1)
        mapper=VolunteerWidgetMapper(self.h5file)
        res=mapper.show_dialog()
        if res is not None:
            self.task_param_to_row(res)
        self.endInsertRows()

        return True

    def add_task(self,index):
        self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
        self.task_table = self.h5file.get_node('/tasks/tasks_table')
        vol_id = index.sibling(index.row(), self.volunteer_table.colnames.index('idnumber')).data()
        vol_row = self.volunteer_table.get_where_list("""(idnumber == {:})""".format(vol_id))[0]
        time_start=self.volunteer_table[vol_row]['time_start']
        time_end=self.volunteer_table[vol_row]['time_end']


        list=ListPicker(vol_row,time_start,time_end,"task",self.h5file)

        ids=list.pick_dialog()


        idvol = self.volunteer_table[vol_row]['idnumber']
        for task_id in ids:
            task_row=self.task_table.get_where_list("""(idnumber == {:})""".format(task_id))[0]

            for ind_vol, vol_id in enumerate(self.task_table[task_row]['affected_volunteers']):
                if vol_id == -1:
                    break
            vols = self.task_table.cols.affected_volunteers[task_row]
            vols[ind_vol] = idvol
            self.task_table.cols.affected_volunteers[task_row]=vols
            self.task_table.cols.N_filled[task_row]+=1
            self.task_table.flush()

            for ind_task, task_id_tmp in enumerate(self.volunteer_table[idvol]['affected_tasks']):
                if task_id_tmp == -1:
                    break
            tasks = self.volunteer_table.cols.affected_tasks[idvol]
            tasks[ind_task] = task_id
            self.volunteer_table.cols.affected_tasks[idvol] = tasks
            self.volunteer_table.flush()
        self.update_signal.emit()

        index_ul = self.createIndex(index.row(), 0)
        index_br = self.createIndex(index.row(), len(self.volunteer_table.colnames)-1)
        self.dataChanged.emit(index_ul, index_br, [QtCore.Qt.DisplayRole for ind in range(len(self.volunteer_table.colnames))])

    def remove_task(self,index,select=True):
        """
        Remove tasks from the affected ones to a given volunteer
        Parameters
        ----------
        index (QtCore.QIndex): index pointing to the selected volunteer
        select (bool): if True, the user can select which task to remove else all are removed

        Returns
        -------

        """
        self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
        self.task_table = self.h5file.get_node('/tasks/tasks_table')
        idvol = int(index.sibling(index.row(), 0).data())
        row_vol= self.volunteer_table.get_where_list("""(idnumber == {:})""".format(idvol))[0]
        tasks=[task for task in  self.volunteer_table[row_vol]['affected_tasks'] if task != -1]

        if select:
            list = ListPicker(picker_type="task", h5file=self.h5file, ids=tasks)
            ids = list.pick_dialog(connect=False)
        else:
            ids = tasks

        for task_id in ids:
            task_row = self.task_table.get_where_list("""(idnumber == {:})""".format(task_id))[0]


            vols = self.task_table.cols.affected_volunteers[task_row]
            #find the index corresponding to the picked name
            for ind_vol, vol_id in enumerate(self.task_table[task_row]['affected_volunteers']):
                if vol_id == idvol:
                    break
            vols[ind_vol] = -1
            self.task_table.cols.affected_volunteers[task_row]=vols
            self.task_table.cols.N_filled[task_row]-=1
            self.task_table.flush()

            for ind_task, task_id_tmp in enumerate(self.volunteer_table[idvol]['affected_tasks']):
                if task_id_tmp == task_id:
                    break
            tasks = self.volunteer_table.cols.affected_tasks[idvol]
            tasks[ind_task] = -1
            self.volunteer_table.cols.affected_tasks[idvol] = tasks
            self.volunteer_table.flush()
            self.update_signal.emit()

            index_ul = self.createIndex(index.row(), 0)
            index_br = self.createIndex(index.row(), len(self.task_table.colnames)-1)
            self.dataChanged.emit(index_ul, index_br, [QtCore.Qt.DisplayRole for ind in range(10)])

    def export_csv(self):
        self.task_table = self.h5file.get_node('/tasks/tasks_table')
        path = os.path.split(os.path.abspath(self.h5file.filename))[0]
        filename = select_file(path, ext='csv')
        if filename != '':
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for vol in self.volunteer_table:
                    row = []
                    for name in self.volunteer_table.colnames:
                        if isinstance(vol[name], bytes):
                            row.append(vol[name].decode())
                        elif name == "day":
                            row.append(QtCore.QDateTime().fromSecsSinceEpoch(vol[name]).toString('dddd'))
                        elif 'time' in name:
                            row.append(QtCore.QDateTime().fromSecsSinceEpoch(vol[name][0]).toString('hh:mm'))
                            row.append(QtCore.QDateTime().fromSecsSinceEpoch(vol[name][1]).toString('hh:mm'))
                        elif isinstance(vol[name], int):
                            row.append(str(vol[name]))
                        elif isinstance(vol[name], np.ndarray):
                            names = []
                            for id in vol[name]:
                                if id != -1:
                                    task_row = self.task_table.get_where_list("""(idnumber == {:})""".format(id))[0]
                                    names.append('[{:d}, {:s}]'.format(id, self.task_table[task_row]['name'].decode()))
                            row.append(str(names))
                    #print(row)
                    writer.writerow(row)

    def export_html(self,index=None, export_all=False):

        self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
        self.task_table = self.h5file.get_node('/tasks/tasks_table')
        if index is not None:
            vol_id = int(index.sibling(index.row(), self.volunteer_table.colnames.index('idnumber')).data())
            vol_row = self.volunteer_table.get_where_list("""(idnumber == {:})""".format(vol_id))[0]
            vol = self.volunteer_table[vol_row]
            self.create_html(vol, vol_id)
        elif export_all:
            for ind_vol, vol in enumerate(self.volunteer_table):
                self.create_html(vol, ind_vol)

    def create_html(self,vol, vol_id):
        path = os.path.split(os.path.abspath(self.h5file.filename))[0]
        doc, tag, text = Doc().tagtext()
        doc.asis('<!DOCTYPE html>')
        with tag('html', lang='fr'):
            with tag('head'):
                doc.asis('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>')
                with tag('title'):
                    text('fiche bénévole')
                with tag('style'):
                    doc.asis('.task {background-color: black;color: white;margin: 20px;padding: 20px;}')
                    doc.asis('.container {}')
                    doc.asis('.row {line-height:24pt;}')
                    doc.asis('div.container > div:nth-of-type(odd) {background: #cce0ff;}')
                    doc.asis('div.container > div:nth-of-type(even) {background: #ffff80;}')
            with tag('body'):
                with tag('div', style=''):
                    with tag('h1'):
                        text(self.h5file.root._v_attrs['event_name'])
                    with tag('h2'):
                        text('du {:} au {:} à {:}'.format(
                            QtCore.QDateTime().fromSecsSinceEpoch(self.h5file.root._v_attrs['event_day']).toString(
                                'dd/MM/yyyy'),
                            QtCore.QDateTime().fromSecsSinceEpoch(self.h5file.root._v_attrs['event_day']).addDays(
                                self.h5file.root._v_attrs['Ndays']).toString('dd/MM/yyyy'),
                            self.h5file.root._v_attrs['event_place']))
                    with tag('h3'):
                        doc.asis('Fiche bénévole pour: {:}'.format(vol['name'].decode()))
                tasks = []
                for task_id in [v for v in vol['affected_tasks'] if v != -1]:
                    task_row = self.task_table.get_where_list("""(idnumber == {:})""".format(task_id))[0]
                    task = self.task_table[task_row]
                    tasks.append(task)
                tasks.sort(key=lambda t: t['time_start'])
                with tag('div', klass='container'):
                    for task in tasks:
                        with tag('div', klass='row'):
                            with tag('h3'):
                                text(task['name'].decode())
                            with tag('p'):
                                text('{:} de {:} à {:}'.format(
                                    QtCore.QDateTime().fromSecsSinceEpoch(task['time_start']).toString(
                                        'dddd dd/MM/yyyy'),
                                    QtCore.QDateTime().fromSecsSinceEpoch(task['time_start']).toString('hh:mm'),
                                    QtCore.QDateTime().fromSecsSinceEpoch(task['time_end']).toString('hh:mm')))
                            with tag('p'):
                                vols = []
                                for id_tmp in [v for v in task['affected_volunteers'] if v != -1 and v != vol_id]:
                                    vol_row_tmp = \
                                    self.volunteer_table.get_where_list("""(idnumber == {:})""".format(id_tmp))[0]
                                    vols.append(self.volunteer_table[vol_row_tmp]['name'].decode())
                                text('Autres volontaires: {:}'.format(vols))
                            with tag('p'):
                                text('Choses à emmener: {:}'.format(task['stuff_needed'].decode()))
                            with tag('p'):
                                text('Remarques: {:}'.format(task['remarqs'].decode()))

        path = os.path.join(path,'{:}.html'.format(vol['name'].decode()))
        url = 'file://' + path
        with codecs.open(path, 'wb', 'utf-8') as f:
            f.write(doc.getvalue())
        webbrowser.open(url)

class TaskModel(QtCore.QAbstractTableModel):

    update_signal=pyqtSignal()

    def __init__(self,h5file=None,list_ids=None):
        super(TaskModel,self).__init__()
        self.list_ids=list_ids
        if h5file is None:
            raise Exception('No valid pytables file')
        elif type(h5file)==str or type(h5file)==Path:
            self.h5file=tables.open_file(str(h5file),mode='a',title='List of Tasks and volunteers for RTA 2018')
        elif type(h5file)==tables.File:
            self.h5file=h5file
            
        self.task_table=self.h5file.get_node('/tasks/tasks_table')
        self.volunteer_table=self.h5file.get_node('/volunteers/volunteer_table')
        self.names=self.task_table.colnames

    def close(self):
        try:
            self.h5file.close()
        except:
            pass

    def rowCount(self,index):
        if self.list_ids is not None:
            return  len(self.list_ids)
        else:
            return self.task_table.nrows

    
    def columnCount(self,index):
        if self.list_ids is not None:
            return 6
        else:
            return len(self.task_table.colnames)

    def data(self,index=QtCore.QModelIndex(),role=QtCore.Qt.DisplayRole):
        if role==QtCore.Qt.DisplayRole:

            if index.isValid():
                ind_col = self.names[index.column()]
                if self.list_ids is not None:
                    dat = self.task_table[self.list_ids[index.row()]][ind_col]
                else:
                    dat = self.task_table[index.row()][ind_col]
                dat_type = self.task_table.coltypes[self.task_table.colnames[index.column()]]

                if index.column()==1:#day
                    d=datetime.datetime.fromtimestamp(dat)
                    return d.strftime('%A')

                if dat_type=='int8' or dat_type=='int64':
                    if type(dat)==np.ndarray:
                        try:
                            return str([self.volunteer_table[ind]['name'].decode() for ind in dat if ind != -1 ])
                        except:
                            return ''
                    else:
                        return int(dat)
                elif dat_type=='string':
                    return dat.decode()
                elif dat_type=='time32':
                    d=datetime.datetime.fromtimestamp(dat)
                    return d.strftime('%H:%M')
                elif dat_type=='enum':
                    return self.task_table.get_enum('task_type')(dat)
            else:
                return ''

        elif role==QtCore.Qt.BackgroundRole:
            if index.column() == self.task_table.colnames.index('N_filled'):
                Nneeded = self.task_table[index.row()]['N_needed']
                Nfilled = self.task_table[index.row()]['N_filled']



                brush=QtGui.QBrush(QtCore.Qt.SolidPattern)
                if Nfilled < Nneeded:
                    brush.setColor(QtGui.QColor(255,0,0))
                else:
                    brush.setColor(QtGui.QColor(0,255,0))
                return brush
            else:
                return QtCore.QVariant()
        else:
            return QtCore.QVariant()


    def edit_data(self,index):
        task_id=index.sibling(index.row(),self.task_table.colnames.index('idnumber')).data()
        task_row=self.task_table.get_where_list("""(idnumber == {:})""".format(task_id))[0]
        mapper=TaskWidgetMapper(self.h5file,task_row)
        res=mapper.show_dialog()
        if res is not None:
            if res.child('task_settings','time_start').value() !=\
                QtCore.QDateTime().fromSecsSinceEpoch(self.task_table[task_row]['time_start']).time() or\
                    res.child('task_settings', 'time_end').value() !=\
                    QtCore.QDateTime().fromSecsSinceEpoch(self.task_table[task_row]['time_end']).time():  #means time_start or time_end has been changed, so maybe not consistent anymore with affected tasks to other volunteers
                consistent, messg = self.check_consistency(res, task_row)
            else:
                consistent, messg = True, ''
            if consistent:
                self.task_param_to_row(res,task_row)
            else:
                messgbox = QtWidgets.QMessageBox()
                messgbox.setText(messg)
                messgbox.exec()

    def check_consistency(self,res,task_id):
        """
        Will check if the modified task times are still compatible with affected volunteers
        Returns
        -------
        (bool, str): tuple with a bool: True if consistent otherwise False, if False, returns also a message with the volunteer id for who the consistency is wrong
        """

        task_row = self.task_table[task_id]

        vols = [vol for vol in task_row['affected_volunteers'] if vol != -1]

        time_start = QtCore.QDateTime(res.child('task_settings', 'day').value(),res.child('task_settings', 'time_start').value()).toSecsSinceEpoch()
        time_end = QtCore.QDateTime(res.child('task_settings', 'day').value(),
                                      res.child('task_settings', 'time_end').value()).toSecsSinceEpoch()
        for vol_id in vols:
            affected_tasks_ids = [task for task in self.volunteer_table[vol_id]['affected_tasks'] if task != -1]
            affected_tasks_ids.pop(affected_tasks_ids.index(task_id)) #do not includ the one that has just been modified
            affected_tasks_times = [(task['time_start'], task['time_end']) for task in self.task_table if
                                    task['idnumber'] in affected_tasks_ids]
            for ind in range(len(affected_tasks_times)):

                if affected_tasks_times[ind][1]>time_start or affected_tasks_times[ind][0]>time_end: #test if this task (time_start,time_send) is compatible with volunteer presence
                    return False, 'The new times are not compatible with vol {:d}: {:s} and its other task : {:d}'.format(vol_id, self.volunteer_table[vol_id]['name'].decode(),
                                                                             affected_tasks_ids[ind])

        return True, ''


    def add_volunteer(self,index):
        task_id = index.sibling(index.row(), self.task_table.colnames.index('idnumber')).data()
        task_row = self.task_table.get_where_list("""(idnumber == {:})""".format(task_id))[0]
        time_start=self.task_table[task_row]['time_start']
        time_end=self.task_table[task_row]['time_end']

        list=ListPicker(task_row,time_start,time_end,"volunteer",self.h5file)

        volunteers=list.pick_dialog()

        for idvol in volunteers:
            row=self.volunteer_table.get_where_list("""(idnumber == {:})""".format(idvol))[0]

            for ind_vol, vol_id in enumerate(self.task_table[task_row]['affected_volunteers']):
                if vol_id == -1:
                    break
            vols = self.task_table.cols.affected_volunteers[task_row]
            vols[ind_vol] = idvol
            self.task_table.cols.affected_volunteers[task_row]=vols
            self.task_table.cols.N_filled[task_row]+=1
            self.task_table.flush()

            for ind_task, task_id_tmp in enumerate(self.volunteer_table[idvol]['affected_tasks']):
                if task_id_tmp == -1:
                    break
            tasks = self.volunteer_table.cols.affected_tasks[idvol]
            tasks[ind_task] = task_id
            self.volunteer_table.cols.affected_tasks[idvol] = tasks
            self.volunteer_table.flush()
        self.update_signal.emit()

        index_ul = self.createIndex(index.row(), 0)
        index_br = self.createIndex(index.row(), len(self.task_table.colnames)-1)
        self.dataChanged.emit(index_ul, index_br, [QtCore.Qt.DisplayRole for ind in range(len(self.task_table.colnames))])

    def remove_volunteer(self,index,select=True):
        """
        Remove volunteers from the affected ones to a given task
        Parameters
        ----------
        index (QtCore.QIndex): index pointing to the selected task
        select (bool): if True, the user can select which volunteer to remove else all are removed

        Returns
        -------

        """
        task_id = index.sibling(index.row(), self.task_table.colnames.index('idnumber')).data()
        task_row = self.task_table.get_where_list("""(idnumber == {:})""".format(task_id))[0]
        volunteers=[ind for ind in self.task_table[task_row]['affected_volunteers'] if ind != -1]

        if select:
            list = ListPicker(picker_type="volunteer", h5file=self.h5file, ids=volunteers)
            ids = list.pick_dialog(connect=False)
        else:
            ids = volunteers
        for idvol in ids:
            row=self.volunteer_table.get_where_list("""(idnumber == {:})""".format(idvol))[0]
            vols = self.task_table.cols.affected_volunteers[task_row]
            #find the index corresponding to the picked name
            for ind_vol, vol_id in enumerate(self.task_table[task_row]['affected_volunteers']):
                if vol_id == idvol:
                    break
            vols[ind_vol] = -1
            self.task_table.cols.affected_volunteers[task_row]=vols
            self.task_table.cols.N_filled[task_row]-=1
            self.task_table.flush()

            for ind_task, task_id_tmp in enumerate(self.volunteer_table[idvol]['affected_tasks']):
                if task_id_tmp == task_id:
                    break
            tasks = self.volunteer_table.cols.affected_tasks[idvol]
            tasks[ind_task] = -1
            self.volunteer_table.cols.affected_tasks[idvol] = tasks
            self.volunteer_table.flush()
            self.update_signal.emit()

        index_ul = self.createIndex(index.row(), 0)
        index_br = self.createIndex(index.row(), len(self.task_table.colnames)-1)
        self.dataChanged.emit(index_ul, index_br, [QtCore.Qt.DisplayRole for ind in range(10)])

    def remove_data(self,index,rows_ids):
        msgBox=QtWidgets.QMessageBox()
        msgBox.setText("You are about to delete rows!")
        msgBox.setInformativeText("Are you sure you want to delete rows with ids: {:}".format([row[1] for row in rows_ids]))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        res = msgBox.exec()

        if res==QtWidgets.QMessageBox.Ok:
            for row,id in rows_ids:
                if self.task_table[row]['N_filled'] == 0:
                    self.beginRemoveRows(index.parent(),row,row)
                    self.task_table.remove_row(self.task_table.get_where_list("""(idnumber == {:})""".format(id))[0])
                    self.endRemoveRows()
                else:
                    msgBox = QtWidgets.QMessageBox()
                    msgBox.setText("Task with id: {:} has affected volunteers".format(id))
                    msgBox.setInformativeText("Do you still want to remove it?")
                    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                    msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                    res = msgBox.exec()
                    if res == QtWidgets.QMessageBox.Ok:
                        self.remove_volunteer(self.createIndex(row,0),select= False)
                        self.beginRemoveRows(index.parent(), row, row)
                        self.task_table.remove_row(self.task_table.get_where_list("""(idnumber == {:})""".format(id))[0])
                        self.endRemoveRows()
                self.update_signal.emit()

    def append_row(self,index):
        self.insertRows(self.rowCount(index),1,index.parent())
        self.update_signal.emit()

    def insertRows(self, row: int, count: int, parent):
        if row == 0:
            row = 1
        self.beginInsertRows(parent,row-1,row-1)
        mapper=TaskWidgetMapper(self.h5file)
        res=mapper.show_dialog()
        if res is not None:
            self.task_param_to_row(res)
        self.endInsertRows()

        return True

    def task_param_to_row(self,param,row_index=None):
        try:

            row_data=dict()
            row_data['idnumber'] =int( param.child('task_settings', 'id').value())
            row_data['day'] = int(QtCore.QDateTime(param.child('task_settings', 'day').value()).toMSecsSinceEpoch()/1000)
            row_data['time_start'] = int(QtCore.QDateTime(param.child('task_settings', 'day').value(),
                                                     param.child('task_settings',
                                                                 'time_start').value()).toMSecsSinceEpoch()/1000)
            row_data['time_end'] = int(QtCore.QDateTime(param.child('task_settings', 'day').value(),
                                                   param.child('task_settings',
                                                               'time_end').value()).toMSecsSinceEpoch()/1000)
            row_data['task_type'] = self.task_table.get_enum('task_type')[
                param.child('task_settings', 'task_type').value()]
            row_data['name'] = param.child('task_settings', 'name').value().encode()
            row_data['N_needed'] = int(param.child('task_settings', 'N_needed').value())
            row_data['N_filled'] = int(param.child('task_settings', 'N_filled').value())
            row_data['remarqs'] = param.child('task_settings', 'remarqs').value().encode()
            row_data['stuff_needed'] = param.child('task_settings', 'stuff').value().encode()
            try:
                row_data['affected_volunteers'] = self.task_table[row_index]['affected_volunteers']
            except:
                row_data['affected_volunteers'] = np.ones((50,),dtype='int64')*(-1)

            if row_index is None:
                row_index = self.task_table.nrows+1
                row = self.task_table.row
                for k in self.task_table.colnames:
                    row[k]=row_data[k]
                row.append()
                self.task_table.flush()


            else:
                dat=[tuple([row_data[k] for k in self.task_table.colnames])]
                self.task_table.modify_rows(start=row_index,stop=row_index+1,step=1,rows=dat)
                index_ul=self.createIndex(row_index,0)
                index_br=self.createIndex(row_index,9)
                self.dataChanged.emit(index_ul,index_br,[QtCore.Qt.DisplayRole for ind in range(10)])
                self.task_table.flush()

            self.update_signal.emit()

        except Exception as e:
            print(e)



    def headerData(self,section,orientation,role):
        if role==QtCore.Qt.DisplayRole:
            if orientation==QtCore.Qt.Horizontal:
                return col_task_header[section]
            else:
                return QtCore.QVariant()
        else:
            return QtCore.QVariant()

    def export_csv(self):
        path = os.path.split(os.path.abspath(self.h5file.filename))[0]
        filename = select_file(path, ext='csv')
        if filename != '':
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                for task in self.task_table:
                    row = []
                    for name in self.task_table.colnames:
                        if isinstance(task[name], bytes):
                            row.append(task[name].decode())
                        elif name == "day":
                            row.append(QtCore.QDateTime().fromSecsSinceEpoch(task[name]).toString('dddd'))
                        elif 'time' in name:
                            row.append(QtCore.QDateTime().fromSecsSinceEpoch(task[name]).toString('hh:mm'))
                        elif isinstance(task[name], int):
                            row.append(str(task[name]))
                        elif isinstance(task[name], np.ndarray):
                            names = [self.volunteer_table[ind_row]['name'].decode() for ind_row in task[name] if
                                     ind_row != -1]
                            row.append(str(names))
                    print(row)
                    writer.writerow(row)

    def export_html(self):
        path = os.path.split(os.path.abspath(self.h5file.filename))[0]
        self.volunteer_table = self.h5file.get_node('/volunteers/volunteer_table')
        self.task_table = self.h5file.get_node('/tasks/tasks_table')

        doc, tag, text = Doc().tagtext()
        doc.asis('<!DOCTYPE html>')
        with tag('html', lang='fr'):
            with tag('head'):
                doc.asis('<meta charset="UTF-8"/>')
                with tag('title'):
                    text('Liste des tâches')
                with tag('style'):
                    text('table, th, td{border: 1px solid black;border-collapse: collapse;}')
            with tag('body'):
                with tag('div', style=''):
                    with tag('h1'):
                        text(self.h5file.root._v_attrs['event_name'])
                    with tag('h2'):
                        text('du {:} au {:} à {:}'.format(
                            QtCore.QDateTime().fromSecsSinceEpoch(self.h5file.root._v_attrs['event_day']).toString(
                                'dd/MM/yyyy'),
                            QtCore.QDateTime().fromSecsSinceEpoch(self.h5file.root._v_attrs['event_day']).addDays(
                                self.h5file.root._v_attrs['Ndays']).toString('dd/MM/yyyy'),
                            self.h5file.root._v_attrs['event_place']))
                with tag('table'):
                    with tag('tr'):
                        for name in self.task_table.colnames:
                            with tag('th'):
                                text(name)
                    for task in self.task_table:
                        with tag('tr'):
                            for name in self.task_table.colnames:
                                with tag('td'):
                                    if isinstance(task[name], bytes):
                                        text(task[name].decode())
                                    elif name == "day":
                                        text(QtCore.QDateTime().fromSecsSinceEpoch(task[name]).toString('dddd'))
                                    elif 'time' in name:
                                        text(QtCore.QDateTime().fromSecsSinceEpoch(task[name]).toString('hh:mm'))
                                    elif isinstance(task[name], int):
                                        text(str(task[name]))
                                    elif isinstance(task[name], np.ndarray):
                                        names = [self.volunteer_table[ind_row]['name'].decode() for ind_row in task[name] if ind_row!=-1]
                                        text(str(names))

        path = os.path.join(path,'tasks.html')
        url = 'file://' + path
        with codecs.open(path, 'wb', 'utf-8') as f:
            f.write(doc.getvalue())
        webbrowser.open(url)



class ListPicker(QtCore.QObject):

    def __init__(self,row=None,ts=None,te=None,picker_type='task',h5file=None, ids=None):
        super(ListPicker,self).__init__()
        self.picker_type = picker_type #either 'task' or 'volunteer'
        self.h5file = h5file
        self.selected_ids = []
        self.row=row
        self.ts=ts
        self.te=te

        if h5file is not None:
            self.task_table=self.h5file.get_node('/tasks/tasks_table')
            self.volunteer_table=self.h5file.get_node('/volunteers/volunteer_table')
        else:
            raise Exception('No valid h5 file')
        if row is not None and ts is not None and te is not None:
            self.list_ids = self.check_availlable(row,ts,te)
        else:
            self.list_ids = ids



    def check_availlable(self,vol_row,time_start,time_end,selected_ids=[]):

        id_list=[]
        if self.picker_type == 'task':
            affected_tasks_ids=[task for task in self.volunteer_table[vol_row]['affected_tasks'] if task!=-1]+selected_ids
            affected_tasks_times=[(task['time_start'],task['time_end']) for task in self.task_table if task['idnumber'] in affected_tasks_ids]

            for task_row in self.task_table:
                if task_row['N_filled']<task_row['N_needed']:

                    test = []
                    for ind in range(len(time_start)):
                        test.append([time_start[ind]<=task_row['time_start'],time_end[ind]>=task_row['time_end']]) #test if this task (time_start,time_send) is compatible with volunteer presence

                    test = np.any(np.all(test, 1))  # there is one slot available (but ùaybe other tasks collide....
                    if test:
                        flag = False
                        for atime in affected_tasks_times:
                            if task_row['time_start']<atime[1] and task_row['time_end']>atime[0]:
                                flag = True
                        if not flag:
                            id_list.append(task_row['idnumber'])
        else:
            for vol_row in self.volunteer_table:
                affected_tasks_ids = [task for task in vol_row['affected_tasks'] if task != -1]
                affected_tasks_times = [(task['time_start'], task['time_end']) for task in self.task_table if
                                        task['idnumber'] in affected_tasks_ids]

                test = np.stack((time_start >= vol_row['time_start'], time_end <= vol_row[
                    'time_end']))  # test if this task (time_start,time_send) is compatible with volunteer presence
                test = np.any(np.all(test, 0))  # there is one slot available (but ùaybe other tasks collide....

                test_other_tasks = [test]
                for atime in affected_tasks_times:
                    test_other_tasks.append(not (time_start >= atime[0] and time_end <= atime[1]))

                if np.all(np.array(test_other_tasks)):
                    id_list.append(vol_row['idnumber'])

        return id_list

    def update_table(self,index):
        if self.picker_type == 'task':
            selected_indexes=self.table_view.selectedIndexes()
            selected_ids = [ind.data() for ind in selected_indexes if ind.column()==0]

            valid_tasks_ids=self.check_availlable(self.row,self.ts,self.te,selected_ids)+selected_ids
            valid_tasks_ids.sort()
            model = TaskModel(self.h5file, valid_tasks_ids)
            self.table_view.setModel(model)

            for row in range(len(valid_tasks_ids)):
                if int(self.table_view.model().createIndex(row,0).data()) in selected_ids:
                    self.table_view.selectRow(row)



        elif self.picker_type == 'volunteer':
            pass

        else:
            raise Exception('invalid picker type')



    def pick_dialog(self,connect=True):
        self.dialog = QtWidgets.QDialog()
        self.dialog.setMinimumWidth(500)
        vlayout = QtWidgets.QVBoxLayout()



        self.table_view=QtWidgets.QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        if self.picker_type == 'task':
            model = TaskModel(self.h5file, self.list_ids)
        else:
            model = VolunteerModel(self.h5file, self.h5file.root._v_attrs['Ndays'], self.list_ids)

        sortproxy = QtCore.QSortFilterProxyModel()
        sortproxy.setSourceModel(model)
        self.table_view.setModel(sortproxy)
        self.table_view.setSortingEnabled(True)

        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        if connect:
            self.table_view.clicked.connect(self.update_table)


        vlayout.addWidget(self.table_view, 10)
        self.dialog.setLayout(vlayout)

        buttonBox = QtWidgets.QDialogButtonBox();
        buttonBox.addButton('Apply', buttonBox.AcceptRole)
        buttonBox.accepted.connect(self.dialog.accept)
        buttonBox.addButton('Cancel', buttonBox.RejectRole)
        buttonBox.rejected.connect(self.dialog.reject)

        vlayout.addWidget(buttonBox)
        if self.picker_type == 'task':
            self.dialog.setWindowTitle('Select available tasks')
        else:
            self.dialog.setWindowTitle('Select available volunteers')
        res = self.dialog.exec()

        pass
        if res == self.dialog.Accepted:
            # save preset parameters in a xml file
            return  [int(ind.data()) for ind in self.table_view.selectedIndexes() if ind.column()==0]
        else:
            return []


class VolunteerWidgetMapper(QtWidgets.QWidget):

    day_params=[
        {'title': 'Present?:', 'name': 'present', 'type': 'bool', 'value': False},
        {'title': 'Time Start:', 'name': 'time_start', 'type': 'time', 'value': QtCore.QTime(), 'minutes_increment': 1},
        {'title': 'Time End:', 'name': 'time_end', 'type': 'time', 'value': QtCore.QTime(), 'minutes_increment': 1},
    ]

    params = [{'title': 'Volunteer Settings:', 'name': 'volunteer_settings', 'type': 'group', 'children': [
                {'title': 'Id:', 'name': 'id', 'type': 'int', 'value': -1, 'readonly': True},
                {'title': 'Name:', 'name': 'name', 'type': 'str', 'value': ''},
                {'title': 'Remarqs:', 'name': 'remarqs', 'type': 'str', 'value': ''},

                {'title': 'Days','name': 'day_list', 'type': 'group'}

    ]}]


    def __init__(self, h5file=None, row=None):
        super(VolunteerWidgetMapper, self).__init__()
        self.h5file = h5file
        self.vol_table = h5file.get_node('/volunteers/volunteer_table')
        self.row = row

    def show_dialog(self):
        if not not self.vol_table and self.row is not None:
            names = self.vol_table.colnames
            dat = self.vol_table[self.row]

            name = dat[names.index('name')].decode()
            idval = dat['idnumber']
            remarqs = dat[names.index('remarqs')].decode()
            tss=[]
            tes=[]
            present=[]
            ts_s=dat[names.index('time_start')]
            te_s=dat[names.index('time_end')]

            for ind_day in range(self.h5file.root._v_attrs['Ndays']):
                if ts_s[ind_day] != -1:
                    present.append(True)
                    daytmp = QtCore.QDateTime()
                    daytmp.setSecsSinceEpoch(ts_s[ind_day])
                    tss.append(daytmp)
                    daytmp = QtCore.QDateTime()
                    daytmp.setSecsSinceEpoch(te_s[ind_day])
                    tes.append(daytmp)
                else:
                    present.append(False)
                    tss.append(QtCore.QDateTime())
                    tes.append(QtCore.QDateTime())




        else:
            try:
                idval = int(np.max(self.vol_table[:]['idnumber']) + 1)
            except:
                idval = 0
            name = ''
            remarqs = ""
            tss=[]
            tes=[]
            present=[True for ind in range(self.h5file.root._v_attrs['Ndays'])]
            for ind in range(self.h5file.root._v_attrs['Ndays']):
                day_tmp=QtCore.QDateTime()
                day_tmp.setSecsSinceEpoch(self.h5file.root._v_attrs['event_day'])
                day_tmp.setTime(QtCore.QTime(6,0))
                tss.append(day_tmp)
                day_tmp = QtCore.QDateTime()
                day_tmp.setSecsSinceEpoch(self.h5file.root._v_attrs['event_day'])
                day_tmp.setTime(QtCore.QTime(22, 0))
                tes.append(day_tmp)




        self.settings = Parameter.create(name='task_settings', type='group', children=self.params)
        self.settings.child('volunteer_settings','id').setValue(idval)
        self.settings.child('volunteer_settings','name').setValue(name)
        self.settings.child('volunteer_settings','remarqs').setValue(remarqs)

        for ind_day in range(self.h5file.root._v_attrs['Ndays']):
            new_par = Parameter.create(title='Day {:02d}:'.format(ind_day), name='day_{:02d}:'.format(ind_day), type='group', children=self.day_params)
            new_par.child(('present')).setValue(present[ind_day])
            new_par.child(('time_start')).setValue(tss[ind_day].time())
            new_par.child(('time_end')).setValue(tes[ind_day].time())
            self.settings.child('volunteer_settings','day_list').addChild(new_par)

        dialog = QtWidgets.QDialog(self)
        vlayout = QtWidgets.QVBoxLayout()
        self.settings_tree = ParameterTree()
        vlayout.addWidget(self.settings_tree, 10)
        self.settings_tree.setMinimumWidth(300)

        self.settings_tree.setParameters(self.settings, showTop=False)
        dialog.setLayout(vlayout)

        buttonBox = QtWidgets.QDialogButtonBox(parent=self);
        buttonBox.addButton('Apply', buttonBox.AcceptRole)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.addButton('Cancel', buttonBox.RejectRole)
        buttonBox.rejected.connect(dialog.reject)

        vlayout.addWidget(buttonBox)
        self.setWindowTitle('Fill in information about this Volunteer')
        res = dialog.exec()

        if res == dialog.Accepted:
            # save preset parameters in a xml file
            return self.settings
        else:
            return None


class TaskWidgetMapper(QtWidgets.QWidget):
    """ Widget presenting a Tree structure representing a task. If loaded from 
    a row in a task table then use entries from task_table, could be used to 
    update the task. Otherwise initialize and can be used to enter a new task
    
    ============== ========================================================================
    **Arguments:**
    task_table     Table type from pytables module containing tasks for this event
    row            Row index within the table. Used to initialize data of
                   the widget.

    """
    
    def __init__(self,h5file=None,row=None):

        
        super(TaskWidgetMapper,self).__init__()
        self.h5file = h5file
        self.task_table=h5file.get_node('/tasks/tasks_table')
        self.row=row
    
    def show_dialog(self):
        if not not self.task_table and self.row is not None:
            names=self.task_table.colnames
            dat=self.task_table[self.row]
            idval=dat['idnumber']
            day=datetime.datetime.fromtimestamp(dat[names.index('day')])
            day=QtCore.QDate(day.year,day.month,day.day)
            ts=datetime.datetime.fromtimestamp(dat[names.index('time_start')])
            ts=QtCore.QTime(ts.hour,ts.minute)
            te=datetime.datetime.fromtimestamp(dat[names.index('time_end')])
            te=QtCore.QTime(te.hour,te.minute)
            name=dat[names.index('name')].decode()
            task_type=self.task_table.get_enum('task_type')(dat[names.index('task_type')])
            N_needed=dat[names.index('N_needed')]
            N_filled=dat[names.index('N_filled')]
            remarqs=dat[names.index('remarqs')].decode()
            stuff=dat[names.index('stuff_needed')].decode()
            
        else:
            try:
                idval=int(np.max(self.task_table[:]['idnumber']) + 1)
            except:
                idval = 0
            if self.row is not None:
                day=datetime.datetime.fromtimestamp(np.min(self.task_table[:]['day']))
                day = QtCore.QDate(day.year, day.month, day.day)
                ts=datetime.datetime.fromtimestamp(np.min(self.task_table[:]['time_start']))
                ts=QtCore.QTime(ts.hour,ts.minute)
                te=datetime.datetime.fromtimestamp(np.min(self.task_table[:]['time_end']))
                te=QtCore.QTime(te.hour,te.minute)
            else:
                day=datetime.datetime.fromtimestamp(self.h5file.root._v_attrs['event_day'])
                day = QtCore.QDate(day.year, day.month, day.day)
                ts=QtCore.QTime(6,0)
                te=QtCore.QTime(22,0)

            name=''
            task_type=list(self.task_table.get_enum('task_type')._names.keys())[0]
            N_needed=0
            N_filled=0
            remarqs=""
            stuff=""
            
            
        
        self.params = [{'title': 'Task Settings:','name': 'task_settings','type': 'group','children':[
                    {'title': 'Id:', 'name': 'id', 'type': 'int', 'value': idval, 'readonly': True},
                    {'title': 'Day:','name': 'day', 'type': 'date', 'value': day},
                    {'title': 'Time Start:','name': 'time_start', 'type': 'time', 'value': ts, 'minutes_increment':30},
                    {'title': 'Time End:','name': 'time_end', 'type': 'time', 'value': te, 'minutes_increment':30},
                    {'title': 'Task Type:','name': 'task_type', 'type': 'list', 'value':task_type, 'values': list(self.task_table.get_enum('task_type')._names.keys())},
                    {'title': 'Name:','name': 'name', 'type': 'str', 'value': name},
                    
                    {'title': 'N needed:','name': 'N_needed', 'type': 'int', 'value': N_needed, 'min': 0},
                    {'title': 'N filled:','name': 'N_filled', 'type': 'int', 'value': N_filled, 'min': 0, 'readonly': True},
                    
                    {'title': 'Remarqs:','name': 'remarqs', 'type': 'str', 'value': remarqs},
                    {'title': 'Stuffs:','name': 'stuff', 'type': 'str', 'value': stuff},
                    ]}]

    
        dialog=QtWidgets.QDialog(self)    
        vlayout=QtWidgets.QVBoxLayout()
        self.settings_tree = ParameterTree()
        vlayout.addWidget(self.settings_tree,10)
        self.settings_tree.setMinimumWidth(300)
        self.settings=Parameter.create(name='task_settings', type='group', children=self.params)
        self.settings_tree.setParameters(self.settings, showTop=False)
        dialog.setLayout(vlayout)
        
        
        
        
        buttonBox = QtWidgets.QDialogButtonBox(parent=self);
        buttonBox.addButton('Apply',buttonBox.AcceptRole)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.addButton('Cancel',buttonBox.RejectRole)
        buttonBox.rejected.connect(dialog.reject)

        vlayout.addWidget(buttonBox)
        self.setWindowTitle('Fill in information about this task')
        res=dialog.exec()

        if res==dialog.Accepted:

            return self.settings
        else:
            return None

class TaskWidget(QtWidgets.QTableView):
    
    def __init__(self):
        super(TaskWidget,self).__init__()
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.menu=QtWidgets.QMenu()
        add_new=self.menu.addAction('Add new task')
        edit_task=self.menu.addAction('Edit current row')
        remove_task=self.menu.addAction('Remove selected rows')
        self.menu.addSeparator()
        add_volunteer = self.menu.addAction('Affect volunteers')
        remove_volunteer = self.menu.addAction('Remove volunteers')
        self.menu.addSeparator()
        self.import_action = self.menu.addAction('Import from csv')
        self.export_action = self.menu.addAction('Export to html')
        self.export_csv_action = self.menu.addAction('Export to csv')
        self.export_action.triggered.connect(self.export_html)
        self.export_csv_action.triggered.connect(self.export_csv)

        add_new.triggered.connect(self.add_new)
        edit_task.triggered.connect(self.edit_task)
        remove_task.triggered.connect(self.remove_task)
        add_volunteer.triggered.connect(self.add_volunteer)
        remove_volunteer.triggered.connect(self.remove_volunteer)

        self.doubleClicked.connect(self.edit_task)

    def export_csv(self):
        self.model().sourceModel().export_csv()



    def export_html(self):
        self.model().sourceModel().export_html()

    def add_new(self):
        index = self.currentIndex()
        if index.row() != -1:
            index_source = index.model().mapToSource(index)
        else:
            index_source = index
        self.model().sourceModel().append_row(index_source)
    

    def edit_task(self):
        index=self.currentIndex()
        index_source=index.model().mapToSource(index)
        index_source.model().edit_data(index_source)
    
    def remove_task(self):
        indexes=self.selectedIndexes()
        rows_ids=[(index.model().mapToSource(index).row(),index.data()) for index in indexes if index.column()==0]
        indexes[0].model().mapToSource(indexes[0]).model().remove_data(indexes[0].model().mapToSource(indexes[0]),rows_ids)

    def add_volunteer(self):
        index = self.currentIndex()
        index_source = index.model().mapToSource(index)
        index_source.model().add_volunteer(index_source)

    def remove_volunteer(self):
        index = self.currentIndex()
        index_source = index.model().mapToSource(index)
        index_source.model().remove_volunteer(index_source)

    def contextMenuEvent(self,event):
        self.menu.exec(event.globalPos())


class VolunteerWidget(QtWidgets.QTableView):
    index_changed_signal=pyqtSignal(QtCore.QModelIndex)

    def currentChanged(self, current: QtCore.QModelIndex, previous: QtCore.QModelIndex):
        self.index_changed_signal.emit(current)

    def __init__(self):
        super(VolunteerWidget, self).__init__()
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.menu = QtWidgets.QMenu()
        add_new = self.menu.addAction('Add new volunteer')
        edit_task = self.menu.addAction('Edit current row')
        remove_volunteer = self.menu.addAction('Remove selected rows')
        self.menu.addSeparator()
        add_task = self.menu.addAction('Affect tasks')
        remove_task= self.menu.addAction('Remove tasks')
        self.menu.addSeparator()
        self.import_action = self.menu.addAction('Import from csv')
        self.export_action = self.menu.addAction('Export to html')
        self.export_all_action = self.menu.addAction('Export all to html')
        self.export_csv_action = self.menu.addAction('Export all to csv')

        add_new.triggered.connect(self.add_new)
        edit_task.triggered.connect(self.edit_task)
        remove_volunteer.triggered.connect(self.remove_volunteer)
        add_task.triggered.connect(self.add_task)
        remove_task.triggered.connect(self.remove_task)
        self.export_action.triggered.connect(self.export_html)
        self.export_all_action.triggered.connect(lambda: self.export_html(True))
        self.export_csv_action.triggered.connect(self.export_csv)

        self.doubleClicked.connect(self.edit_task)

    def export_csv(self):
        self.model().sourceModel().export_csv()

    def export_html(self, export_all=False):
        if export_all:
            self.model().sourceModel().export_html(export_all=export_all)
        else:
            indexes = self.selectedIndexes()
            for index in indexes:
                if index.column() == 0:
                    if index.row() != -1:
                        index_source = index.model().mapToSource(index)
                    else:
                        index_source = index
                    self.model().sourceModel().export_html(index_source)

    def add_new(self):
        index = self.currentIndex()
        if index.row() != -1:
            index_source = index.model().mapToSource(index)
        else:
            index_source = index
        self.model().sourceModel().append_row(index_source)

    def edit_task(self):
        index = self.currentIndex()
        index_source = index.model().mapToSource(index)
        index_source.model().edit_data(index_source)

    def remove_volunteer(self):
        indexes = self.selectedIndexes()
        rows_ids = [(index.model().mapToSource(index).row(), index.data()) for index in indexes if index.column() == 0]
        indexes[0].model().mapToSource(indexes[0]).model().remove_data(indexes[0].model().mapToSource(indexes[0]),
                                                                       rows_ids)
    def add_task(self):
        index = self.currentIndex()
        index_source = index.model().mapToSource(index)
        index_source.model().add_task(index_source)

    def remove_task(self):
        index = self.currentIndex()
        index_source = index.model().mapToSource(index)
        index_source.model().remove_task(index_source)

    def contextMenuEvent(self, event):
        self.menu.exec(event.globalPos())


class FilterProxyDayTypeCustom(QtCore.QSortFilterProxyModel):

    def __init__(self,parent=None):
        super(FilterProxyDayTypeCustom,self).__init__(parent)

        self.target_timestamp=None

        self.dayRegExp=QtCore.QRegExp()
        self.typeRegExp=QtCore.QRegExp()

        self.dayRegExp.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.dayRegExp.setPatternSyntax(QtCore.QRegExp.Wildcard)

        self.typeRegExp.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.typeRegExp.setPatternSyntax(QtCore.QRegExp.Wildcard)

    def filterAcceptsRow(self,sourceRow, parent_index):
        dayIndex= self.sourceModel().index(sourceRow, 1, parent_index)
        typeIndex= self.sourceModel().index(sourceRow, 2, parent_index)
        id_index= self.sourceModel().index(sourceRow, 0, parent_index)
        ts_index= self.sourceModel().index(sourceRow, 4, parent_index)
        te_index = self.sourceModel().index(sourceRow, 5, parent_index)
        try:
            day= self.sourceModel().data(dayIndex)
            type_task= self.sourceModel().data(typeIndex)
            ts=int(parse(self.sourceModel().data(ts_index),dayfirst=True).timestamp())
            te = int(parse(self.sourceModel().data(te_index), dayfirst=True).timestamp())
            if self.target_timestamp is not None:
                return self.dayRegExp.pattern() in day and self.typeRegExp.pattern() in type_task and self.target_timestamp >= ts and self.target_timestamp < te
            else:
                return self.dayRegExp.pattern() in day and self.typeRegExp.pattern() in type_task
        except:
            return True

    def setTimeStampFilter(self,target_timestamp=None):
        self.target_timestamp=target_timestamp
        self.invalidateFilter()

    def setDayFilter(self,regexp):
        self.dayRegExp.setPattern(regexp)
        self.invalidateFilter()

    def setTypeFilter(self,regexp):
        self.typeRegExp.setPattern(regexp)
        self.invalidateFilter()


class GeVT(QtCore.QObject):
    """
    GeB: Gestion of volunteers user interface
    """


    def __init__(self,mainwindow):
        super(GeVT, self).__init__()
        cwd= os.getcwd()
        params = [{'title': 'Event Name:', 'name': 'event_name', 'type': 'str' , 'value': 'Mon_raid'},
                  {'title': 'Event Place:', 'name': 'event_place', 'type': 'str', 'value': 'Chez ouam'},
                  {'title': 'Event Start Date:', 'name': 'event_day', 'type': 'date'},
                  {'title': 'Ndays:', 'name': 'event_ndays', 'type': 'int', 'min':1, 'tooltip': 'Event duration in number of days'},
                  {'title': 'Save directory:', 'name': 'event_save_dir', 'type': 'browsepath', 'filetype': False, 'value': cwd},
        ]
        self.gev_settings = Parameter.create(name='gev_settings', type='group', children=params)



        self.mainwindow = mainwindow
        self.area = DockArea()
        self.mainwindow.setCentralWidget(self.area)

        self.mainwindow.closing.connect(self.do_stuff_before_closing)
        self.h5file = None

        res=self.show_dialog()
        if res:
            self.load_file()
        else:
            self.new_file()

        self.setup_ui()

    def show_dialog(self):
        dialog = QtWidgets.QMessageBox()
        dialog.setText("Welcome to GeVT: tasks and volunteers manager!")
        dialog.setInformativeText("Do you want to create a new file or load an existing one?");
        dialog.addButton('New File',QtWidgets.QMessageBox.AcceptRole)
        dialog.addButton('Load File',QtWidgets.QMessageBox.RejectRole)


        res = dialog.exec()
        return res

    def do_stuff_before_closing(self,event):
        if self.h5file.isopen:
            self.h5file.flush()
            self.h5file.close()
        event.setAccepted(True)

    def quit(self):
        if self.h5file.isopen:
            self.h5file.close()

        self.mainwindow.close()


    def define_models(self):
        self.volunteer_model = VolunteerModel(self.h5file, self.gev_settings.child(('event_ndays')).value())
        self.volunteer_sortproxy = QtCore.QSortFilterProxyModel()
        self.volunteer_sortproxy.setSourceModel(self.volunteer_model)
        self.volunteer_view.setModel(self.volunteer_sortproxy)
        self.volunteer_view.setSortingEnabled(True)

        self.task_model = TaskModel(self.h5file)
        self.proxymodel = FilterProxyDayTypeCustom()
        self.proxymodel.setSourceModel(self.task_model)
        self.task_view.setModel(self.proxymodel)
        self.task_view.setSortingEnabled(True)

        self.timeline_model_needed = TimeLineModel(self.h5file, view_type='N_needed')
        self.timeline_model_filled = TimeLineModel(self.h5file, view_type='N_filled')
        if self.volunteer_table.nrows != 0:
            self.vol_name=self.volunteer_table[0]['name'].decode()
        else:
            self.vol_name = ''
        self.timeline_model_vol = TimeLineModel(self.h5file, view_type=self.vol_name)


        self.timeline_needed.setModel(self.timeline_model_needed)
        self.timeline_filled.setModel(self.timeline_model_filled)
        self.timeline_vol.setModel(self.timeline_model_vol)

        self.volunteer_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.task_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.timeline_needed.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.timeline_filled.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.timeline_vol.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.volunteer_view.index_changed_signal.connect(self.update_vol_label)

        self.volunteer_model.update_signal.connect(self.timeline_model_needed.update_steps)
        self.volunteer_model.update_signal.connect(self.timeline_model_filled.update_steps)
        self.volunteer_model.update_signal.connect(self.timeline_model_vol.update_steps)
        self.task_model.update_signal.connect(self.timeline_model_needed.update_steps)
        self.task_model.update_signal.connect(self.timeline_model_filled.update_steps)
        self.task_model.update_signal.connect(self.timeline_model_vol.update_steps)


    def setup_ui(self):

        self.menubar=self.mainwindow.menuBar()
        self.create_menu(self.menubar)


        self.toolbar=QtWidgets.QToolBar()
        self.create_toolbar()
        self.mainwindow.addToolBar(self.toolbar)

        dock_time_line=Dock('TimeLine',size=(500,100))
        dock_task=Dock('List of Tasks', size=(600, 400))
        dock_volunteer=Dock('List of Volunteers', size=(400, 400))
        dock_html = Dock('Html', size=(400, 400))

        self.volunteer_view=VolunteerWidget()
        self.volunteer_view.import_action.triggered.connect(self.import_volunteer_csv)
        self.volunteer_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.volunteer_view.horizontalHeader().setMinimumWidth(50)


        self.task_view = TaskWidget()
        self.task_view.import_action.triggered.connect(self.import_task_csv)
        self.task_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.task_view.horizontalHeader().setMinimumWidth(50)
        self.timeline_needed = TimeLineView(task_view=self.task_view)
        self.timeline_filled = TimeLineView(task_view=self.task_view)
        self.timeline_vol = TimeLineView(task_view=self.task_view)

        self.define_models()



        layout=QtWidgets.QHBoxLayout()
        filter_widget=QtWidgets.QWidget()

        self.day_edit=QtWidgets.QLineEdit()
        self.day_edit.setPlaceholderText("Day filter")

        self.type_edit=QtWidgets.QLineEdit()
        self.type_edit.setPlaceholderText("Type filter")

        self.remove_filters_pb=QtWidgets.QPushButton('Reset Filters from TimeLine')

        layout.addWidget(self.day_edit)
        layout.addWidget(self.type_edit)
        layout.addWidget(self.remove_filters_pb)
        layout.addStretch(1)
        filter_widget.setLayout(layout)





        dock_task.addWidget(filter_widget)
        dock_task.addWidget(self.task_view)
        dock_volunteer.addWidget(self.volunteer_view)

        dock_time_line.addWidget(QtWidgets.QLabel('Needed Volunteers during day'))
        dock_time_line.addWidget(self.timeline_needed  )
        dock_time_line.addWidget(QtWidgets.QLabel('Filled Volunteers during day'))
        dock_time_line.addWidget(self.timeline_filled)
        self.vol_name_label=QtWidgets.QLabel(self.vol_name)
        dock_time_line.addWidget(self.vol_name_label)
        dock_time_line.addWidget(self.timeline_vol)

        #self.html=QtWebEngineWidgets.QWebEngineView()
        #
        # self.html.setHtml('temp.html')
        # self.html.show()
        #dock_html.addWidget(self.html)

        self.area.addDock(dock_time_line, 'top')
        self.area.addDock(dock_task,'bottom',dock_time_line)
        self.area.addDock(dock_volunteer,'right',dock_time_line)
        #self.area.addDock(dock_html,'below',dock_task)
        self.day_edit.textChanged.connect(self.proxymodel.setDayFilter)
        self.type_edit.textChanged.connect(self.proxymodel.setTypeFilter)
        self.remove_filters_pb.clicked.connect(lambda: self.proxymodel.setTimeStampFilter(None)) #timestamp will be set to None and will be rendered ineficient


    pyqtSlot(QtCore.QModelIndex)
    def update_vol_label(self,index):
        try:
            row = index.model().mapToSource(index).row()
            name = self.volunteer_table[row]['name'].decode()
            self.vol_name_label.setText(name)
            self.timeline_model_vol.update_view_type(name)
        except:
            pass


    def create_menu(self,menubar):
        # %% create Settings menu
        file_menu = menubar.addMenu('File')
        new_action = file_menu.addAction('New file')
        new_action.triggered.connect(self.new_file)
        load_action = file_menu.addAction('Load file')
        load_action.triggered.connect(self.load_file)
        save_action = file_menu.addAction('Save')
        save_action.triggered.connect(self.save_file)
        saveas_action = file_menu.addAction('Save as')
        saveas_action.triggered.connect(self.save_file_as)
        file_menu.addSeparator()
        import_task_action = file_menu.addAction('Import Tasks from csv')
        import_task_action.triggered.connect(self.import_task_csv)
        import_vol_action = file_menu.addAction('Import Volunteers from csv')
        import_vol_action.triggered.connect(self.import_volunteer_csv)

        file_menu.addSeparator()
        quit_action = file_menu.addAction('Quit')
        quit_action.triggered.connect(self.quit)

        settings_menu = menubar.addMenu('Settings')
        config_action= settings_menu.addAction('Event configuration')
        config_action.triggered.connect(self.update_event_settings)

    def get_task_description(self):
        return {'name': tables.StringCol(itemsize=128, shape=(), dflt=b'', pos=3),
         'day': tables.Time32Col(shape=(), dflt=0, pos=1),
         'idnumber': tables.Int64Col(shape=(), dflt=0, pos=0),
         'task_type': tables.EnumCol(enum=tables.Enum({'welcoming': 0, 'balisage': 1, 'logistics': 2, 'security': 3, 'race': 4, 'other': 5, 'unknown': 6}), dflt='welcoming', base=tables.Int32Atom(shape=(), dflt=0), shape=(), pos=2),
         'time_start': tables.Time32Col(shape=(), dflt=0, pos=4),
         'time_end': tables.Time32Col(shape=(), dflt=0, pos=5),
         'N_needed': tables.Int8Col(shape=(), dflt=0, pos=6),
         'N_filled': tables.Int8Col(shape=(), dflt=0, pos=7),
         'remarqs': tables.StringCol(itemsize=128, shape=(), dflt=b'', pos=8),
         'stuff_needed': tables.StringCol(itemsize=128, shape=(), dflt=b'', pos=9),
         'affected_volunteers': tables.Int64Col(shape=(50,), dflt=-1, pos=10)}

    def get_volunteer_description(self,Ndays):
        return {'idnumber': tables.Int64Col(shape=(), dflt=0, pos=0),
             'name': tables.StringCol(itemsize=128, shape=(), dflt=b'', pos=1),
             'remarqs': tables.StringCol(itemsize=128, shape=(), dflt=b'', pos=2),
             'affected_tasks': tables.Int64Col(shape=(50,), dflt=-1, pos=3),
             'time_start': tables.Time32Col(shape=(Ndays,), dflt=0, pos=4),
             'time_end': tables.Time32Col(shape=(Ndays,), dflt=0, pos=5)}


    def show_event_dialog(self):
        dialog = QtWidgets.QDialog()
        vlayout = QtWidgets.QVBoxLayout()
        self.settings_tree = ParameterTree()
        vlayout.addWidget(self.settings_tree, 10)
        self.settings_tree.setMinimumWidth(300)

        self.settings_tree.setParameters(self.gev_settings, showTop=True)
        dialog.setLayout(vlayout)

        buttonBox = QtWidgets.QDialogButtonBox(parent=dialog);
        buttonBox.addButton('Apply', buttonBox.AcceptRole)
        buttonBox.accepted.connect(dialog.accept)


        vlayout.addWidget(buttonBox)
        dialog.setWindowTitle('Fill in information about this Event')
        res = dialog.exec()

        if res == dialog.Accepted:
            # save preset parameters in a xml file
            return self.gev_settings
        else:
            return None

    def update_event_settings(self):
        res= self.show_event_dialog()
        if res is not None:
            event_save_dir = self.gev_settings.child(('event_save_dir')).value()
            event_name = self.gev_settings.child(('event_name')).value()
            event_place = self.gev_settings.child(('event_place')).value()
            event_day = QtCore.QDateTime(
                self.gev_settings.child(('event_day')).value()).toSecsSinceEpoch()  # stored as seconds from Epoch
            Ndays = self.gev_settings.child(('event_ndays')).value()

            self.h5file.root._v_attrs['event_save_dir'] = event_save_dir
            self.h5file.root._v_attrs['event_name'] = event_name
            self.h5file.root._v_attrs['event_place'] = event_place
            self.h5file.root._v_attrs['event_day'] = event_day
            if self.h5file.root._v_attrs['Ndays'] != Ndays:
                self.h5file.root._v_attrs['Ndays'] = Ndays



                self.h5file.remove_node('/volunteers','volunteer_table')
                self.volunteer_table = self.h5file.create_table('/volunteers', 'volunteer_table', self.get_volunteer_description(Ndays), "List of volunteers")

                self.define_models()



    def new_file(self):
        if self.h5file is not None:
            if self.h5file.isopen:
                self.h5file.close()

        res= self.show_event_dialog()
        if res is not None:
            event_save_dir = self.gev_settings.child(('event_save_dir')).value()
            event_place = self.gev_settings.child(('event_place')).value()
            event_name = self.gev_settings.child(('event_name')).value()
            event_day = QtCore.QDateTime(self.gev_settings.child(('event_day')).value()).toSecsSinceEpoch() #stored as seconds from Epoch
            Ndays = self.gev_settings.child(('event_ndays')).value()

            event_save_dir = Path(event_save_dir)


            self.h5file = tables.open_file(event_save_dir.joinpath(event_name+'.gev'), mode='w', title='List of Tasks and volunteers for RTA 2018')
            self.h5file.root._v_attrs['event_save_dir'] = event_save_dir
            self.h5file.root._v_attrs['event_name'] = event_name
            self.h5file.root._v_attrs['event_place'] = event_place
            self.h5file.root._v_attrs['event_day'] = event_day
            self.h5file.root._v_attrs['Ndays'] = Ndays
            # %%
            task_group = self.h5file.create_group('/', 'tasks', 'Tasks related stuff')
            volunter_group = self.h5file.create_group('/', 'volunteers', 'Volunteers related stuff')

            self.task_table = self.h5file.create_table(task_group, 'tasks_table', self.get_task_description(), "List of tasks")
            self.volunteer_table = self.h5file.create_table(volunter_group, 'volunteer_table', self.get_volunteer_description(Ndays), "List of volunteers")

    def load_file(self):

        if self.h5file is not None:
            if self.h5file.isopen:
                self.h5file.close()
                
        file_path = select_file(save=False, ext='gev')
        self.h5file = tables.open_file(str(file_path), mode='a', title='List of Tasks and volunteers for RTA 2018')
        self.task_table = self.h5file.get_node('/tasks/tasks_table')
        self.volunteer_table=self.h5file.get_node('/volunteers/volunteer_table')

        event_save_dir = self.h5file.root._v_attrs['event_save_dir']
        event_name = self.h5file.root._v_attrs['event_name']
        event_place = self.h5file.root._v_attrs['event_place']
        event_day = self.h5file.root._v_attrs['event_day']
        Ndays = self.h5file.root._v_attrs['Ndays'] #stored as seconds from Epoch

        self.gev_settings.child(('event_save_dir')).setValue(event_save_dir)
        self.gev_settings.child(('event_name')).setValue(event_name)
        self.gev_settings.child(('event_place')).setValue(event_place)
        day=QtCore.QDateTime()
        day.setSecsSinceEpoch(event_day)
        self.gev_settings.child(('event_day')).setValue(day.date())
        self.gev_settings.child(('event_ndays')).setValue(Ndays)

        if hasattr(self,'volunteer_view'): #this is the first step at initial load (before views are defined in init)
            self.define_models()

    def save_file(self):
        if self.h5file.isopen:
            self.h5file.flush()


    def save_file_as(self):
        try:
            fname = select_file(save=True, ext='gev')
            if fname != '':
                self.h5file.copy_file(str(fname))
        except:
            pass

    def import_task_csv(self):
        try:
            file_path = select_file(save=False, ext=['csv','txt'])
            if file_path != '':
                task = self.task_table.row

                ind = task.nrow - 1
                with codecs.open(str(file_path), 'rb', 'utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    # reader = csv.reader(tsvfile, dialect='excel-tab')
                    header = next(reader, None)
                    if len(header) != 8:
                        msgBox = QtWidgets.QMessageBox()
                        msgBox.setText(
                            "The number of columns in file is not adequate with the definition of tasks")
                        msgBox.exec()
                        return

                    for row in reader:
                        ind += 1
                        if row[3] == '':
                            d = QtCore.QDateTime()
                            row[3] = d.fromSecsSinceEpoch(self.h5file.root._v_attrs['event_day']).date().toString('dd/MM/yy')

                        task['day'] = int(parse(row[3], dayfirst=True).timestamp())
                        task['name'] = row[1].encode()
                        if row[0] == '':
                            row[0] = 'unknown'
                        task['task_type'] = self.task_table.get_enum('task_type')[row[0]]
                        task['idnumber'] = ind
                        task['time_start'] = int(parse(row[3] + ' ' + row[4], dayfirst=True).timestamp())
                        if row[2] == '':
                            row[2] = 1
                        task['N_needed'] = int(row[2])
                        if row[5] == '':
                            row[5] = '23h59'
                        task['time_end'] = int(parse(row[3] + ' ' + row[5], dayfirst=True).timestamp())
                        task['remarqs'] = row[6].encode()
                        task['stuff_needed'] = row[7].encode()
                        task.append()
                    self.task_table.flush()

                if QtCore.QDateTime(self.gev_settings.child(('event_day')).value()).toSecsSinceEpoch() != min(self.task_table[:]['day']):
                    msgBox = QtWidgets.QMessageBox()
                    msgBox.setText("The day filled in the table is not compatible with the starting date of the event")
                    msgBox.exec()
                    self.task_table.remove_rows(0,self.task_table.nrows,1)
                    return

                self.define_models()
                self.proxymodel = FilterProxyDayTypeCustom()
                self.proxymodel.setSourceModel(self.task_model)
                self.task_view.setModel(self.proxymodel)
                self.task_view.horizontalHeader().setMinimumWidth(50)
                self.task_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

        except Exception as e:
            print(e)

    def import_volunteer_csv(self):
        try:
            file_path = select_file(save=False, ext=['csv', 'txt'])
            Ndays = self.gev_settings.child(('event_ndays')).value()
            if file_path != '':
                vol = self.volunteer_table.row
                ind = vol.nrow - 1
                with codecs.open(str(file_path), 'rb', 'utf-8') as csvfile:  #data = codecs.open(..., "rb", "utf-8")
                    #reader = csv.reader(tsvfile, dialect='excel-tab')
                    reader = csv.reader(csvfile, dialect='excel',)
                    header_days = next(reader, None)
                    flag = True
                    if len(header_days)!= 2*Ndays+2:
                        flag = False
                        msgBox = QtWidgets.QMessageBox()
                        msgBox.setText("The number of columns in file is not adequate with the number of days selected for the event")
                        msgBox.exec()

                    if int(parse(header_days[2] + ' ' + '00:00:00', dayfirst=True).timestamp()) !=QtCore.QDateTime(self.gev_settings.child(('event_day')).value()).toSecsSinceEpoch():
                        flag = False
                        msgBox = QtWidgets.QMessageBox()
                        msgBox.setText("The days filled in the table are not compatible with the starting date of the event")
                        msgBox.exec()

                    if not flag:
                        return

                    next(reader, None)
                    for row in reader:
                        ind += 1
                        #print(row[0])
                        vol['name'] = row[0].encode()
                        vol['remarqs'] = row[1].encode()
                        vol['time_start'] = [self.fill_in_time(header_days[ind], row[ind], time='start') for ind in
                                             range(2, 2 * Ndays + 2, 2)]
                        vol['time_end'] = [self.fill_in_time(header_days[ind], row[ind], time='end') for ind in
                                           range(3, 2 * Ndays + 2, 2)]
                        vol['idnumber'] = ind
                        # print(vol['name'])
                        # print(vol['time_start'])
                        # print(vol['time_end'])
                        vol.append()
                self.volunteer_table.flush()

            self.define_models()
            self.volunteer_sortproxy=QtCore.QSortFilterProxyModel()
            self.volunteer_sortproxy.setSourceModel(self.volunteer_model)
            self.volunteer_view.setModel(self.volunteer_sortproxy)
            self.volunteer_view.setSortingEnabled(True)
            self.volunteer_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        except Exception as e:
            print(e)

    def fill_in_time(self,header_day, string, time='start'):
        if string.upper() == 'X':
            if time == 'start':
                return int(parse(header_day + ' ' + '00:00:00', dayfirst=True).timestamp())
            else:
                return int(parse(header_day + ' ' + '23:59:59', dayfirst=True).timestamp())
        elif string == '':
            return -1
        else:
            try:
                return int(parse(header_day + ' ' + string, dayfirst=True).timestamp())
            except:
                if time == 'start':
                    return int(parse(header_day + ' ' + '00:00:00', dayfirst=True).timestamp())
                else:
                    return int(parse(header_day + ' ' + '23:59:59', dayfirst=True).timestamp())
    # %%

    def create_toolbar(self):
        iconload = QtGui.QIcon()
        iconload.addPixmap(QtGui.QPixmap(":/Icons/Icons/Open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.loadaction=QtWidgets.QAction(iconload,"Load GeV file (.gev)",None)
        self.toolbar.addAction(self.loadaction)
        self.loadaction.triggered.connect(self.load_file)

        iconsave= QtGui.QIcon()
        iconsave.addPixmap(QtGui.QPixmap(":/Icons/Icons/Save_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveaction=QtWidgets.QAction(iconsave,"Save",None)
        self.toolbar.addAction(self.saveaction)
        self.saveaction.triggered.connect(self.save_file)

        iconsaveas= QtGui.QIcon()
        iconsaveas.addPixmap(QtGui.QPixmap(":/Icons/Icons/SaveAs_32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveasaction=QtWidgets.QAction(iconsaveas,"Save As",None)
        self.toolbar.addAction(self.saveasaction)
        self.saveasaction.triggered.connect(self.save_file_as)

class MyMainWindow(QtWidgets.QMainWindow):
    closing=QtCore.pyqtSignal(QtGui.QCloseEvent)

    def __init__(self):
        super(MyMainWindow,self).__init__()

    def closeEvent(self, event):
        self.closing.emit(event)


#%%

def start_gevt():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    win = MyMainWindow()

    prog = GeVT(win)
    win.show()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    win = MyMainWindow()

    prog = GeVT(win)
    win.show()

    # h5file = tables.open_file('RTA_2018.gev', mode='a', title='List of Tasks and volunteers for RTA 2018')
    # row=8
    # ts = np.array([1536357600, 1536444000], dtype='int32')
    # te = np.array([1536443999, 1536530399], dtype='int32')
    # list=ListPicker(row,ts,te,h5file=h5file)

    sys.exit(app.exec_())