import sys
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use("Qt5Agg")
from pathlib import Path
from PyQt5 import QtCore
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget,QPushButton,QTreeWidget,
                            QTreeWidgetItem, QHBoxLayout, QTextEdit,QAction, QInputDialog,QLineEdit, QFileDialog)
from PyQt5.QtGui import QCursor,QMouseEvent
from CoreWidgets import *
import numpy as np
from yxspkg import tecfile,plot3d
import json
import time
import one2one
import RSCal
#whatsThis explication
'''
blocks:(Blocks)
    block1:(block1)
        surface:I0:(surface:1I0)
Zones:(Zones)
    in:(Zones_child)
        block1:surface:Ke:(zone_surf:surface1Ke)
Rotor and Stator:(RotorStator)
    stator:(Zones_child_stator)
    rotor:(Zones_child_rotor)
        block1:(rs_block)
'''
def ExpandTo3d(key,result,shape):
    #因为face2face返回的结果是针对一个二维的平面，并不包含第三个轴，所以需要转换到和Ogrid_check的结果一样的结果
    idim,jdim,kdim = shape 
    r1,r2,index1,index2 = result
    if key[0] == 'I':
        if key[1] == '0':
            result0 = (1,1), r1, r2, index1+1,index2+1
        else:
            result0 = (idim,idim), r1, r2, index1+1,index2+1
    elif key[0] == 'J':
        if key[1] == '0':
            result0 = r1, (1,1), r2, index1,index2+1
        else:
            result0 = r1, (jdim,jdim), r2, index1,index2+1
    elif key[0] == 'K':
        if key[1] == '0':
            result0 = r1,r2, (1,1),index1,index2
        else:
            result0 = r1,r2, (kdim,kdim),index1,index2
    else:
        raise Exception('key is an error variables x ,y,z not in key.')
    return result0
class YxsQTreeWidgetItem(QTreeWidgetItem):
    def __init__(self,*d,**k):
        super().__init__(*d,**k)
        self.yxsData = dict()
    def GetYxsData(self):
        return self.yxsData
    def AppendYxsData(self,data,key):
        self.yxsData[key] = data
    def GetDataString(self):
        return json.dumps(self.yxsData)
    def setDataFromString(self,dataString):
        self.yxsData = json.loads(dataString)


class BTreeWidget(QTreeWidget):
    def __init__(self,*d):
        super().__init__(*d)
        self.setContextMenuPolicy(Qt.CustomContextMenu)  
        self.customContextMenuRequested.connect(self.show_right_menu)  
  
        self.surface_menu = QMenu(self)  
        self.addtozone_menu = self.surface_menu.addMenu('Added to zone')

        self.zone_surf_menu = QMenu(self)
        action = self.zone_surf_menu.addAction('Delete')
        action.triggered.connect(self.delete_zone_surf)

        self.zones_menu = QMenu(self)
        action = self.zones_menu.addAction('Create')
        action.triggered.connect(self.create_zone)

        self.rotor_menu = QMenu(self)
        action2 = self.rotor_menu.addAction('Create a rotor')
        action2.triggered.connect(self.create_zone_rotor)
        action3 = self.rotor_menu.addAction('Create a stator')
        action3.triggered.connect(self.create_zone_stator)
        self.rotor_menu.addSeparator()
        action4 = self.rotor_menu.addAction('Auto detect boundary')
        action4.triggered.connect(self.AutoDetectBoundary)

        self.zone_menu = QMenu(self)
        action = self.zone_menu.addAction('Delete')
        action.triggered.connect(self.delete_zone)

        self.zone_rotor_menu = QMenu(self)
        action = self.zone_rotor_menu.addAction('Delete')
        action.triggered.connect(self.delete_zone)

        self.block_menu = QMenu(self)
        self.addfacestozone_menu = self.block_menu.addMenu('Added faces to')
        self.addblocktozone_menu = self.block_menu.addMenu('Added block to')


        self.selected_item = None
        self.pressed_state = None
    def mousePressEvent(self,e):
        item = self.itemAt( e.pos())
        if item:
            self.pressed_state = item.checkState(0)
        super().mousePressEvent(e)
    def AutoDetectBoundary(self):
        #自动检测边界
        def One2OneSurf(onedata):
            #将数据转化为[(blockid,'Ke'),,]的形式 blockid从0开始  onedata 的id是从1开始的
            ijk_list = ['I','J','K']
            ijks = [None]*3
            bid,(ijks[0],ijks[1],ijks[2],vdim1,vdim2) = onedata
            vdim = 6 - vdim1 - vdim2
            topBot = '0' if ijks[vdim-1][0] == 1 else 'E'
            return bid - 1, ijk_list[vdim-1]+topBot
        rotor_head = self.father.rotor_head
        zons_set = set([self.father.zones_head.child(i).text(0) for i in range(self.father.zones_head.childCount()) ])
        blocks_head = self.father.blocks_head
        block_find_face = dict(zip(('I0','IE','J0','JE','K0','KE'),range(6)))
        for i in range(rotor_head.childCount()):
            shead = rotor_head.child(i)
            block_ids = [int(shead.child(j).text(0)[5:])-1 for j in range(shead.childCount())]
            if not block_ids:
                continue
            blocks = [self.father.blocks[k] for k in block_ids]
            
            one2oneBlocks = one2one.one2one(blocks)
            #将数据网格块的坐标转化为从1开始的坐标
            one2oneBlocks = [(block_ids[ti-1]+1,tiv,block_ids[tj-1]+1,tjv) for ti,tiv,tj,tjv in one2oneBlocks]
            oneOneSurf = set([One2OneSurf((i[j],i[k])) for i in one2oneBlocks for j,k in [(0,1),(2,3)]])

            


            bound = RSCal.RotorStatorCal(blocks)
            bound = {key:[(block_ids[i],j,k) for i,j,k in v if (block_ids[i],j) not in oneOneSurf] for key,v in bound.items()}
            for mm in bound.items():
                print(mm)

            rotor_name = shead.text(0)
            for bound_key,value in bound.items():
                zname = rotor_name+'-'+bound_key
                if zname not in zons_set:
                    zons_set.add(zname)
                    child = YxsQTreeWidgetItem()
                    child.setText(0,zname)
                    child.setWhatsThis(0,'Zones_child')
                    child.setCheckState(0,Qt.Unchecked)
                    self.father.zones_head.addChild(child)
                for i,j,_ in value:
                    bl = blocks_head.child(i)
                    self.selected_item = bl.child(block_find_face[j])
                    self.addsurf_to_zone(sender_text = zname)
                #把周期面添加到oneoneblock中
                if bound_key == 'periodic':
                    blockId1, faceId1 = value[0][0:2]
                    blockId2, faceId2 = value[1][0:2]
                    face1 = self.father.GetBlockFace(blockId1, faceId1)
                    face2 = self.father.GetBlockFace(blockId2, faceId2)
                    t = one2one.get_rotated_periodic_faces(face1,face2)
                    print('periodic Face',blockId1, faceId1,blockId2, faceId2,t)
                    if t is not None:
                        t1,t2 = [ExpandTo3d(idn,tt,self.father.blocks[blockId1]['X'].shape) for idn,tt in zip((faceId1,faceId2),t)]
                        one2oneBlocks.append( (blockId1+1,t1,blockId2+1,t2) )
            for ii in one2oneBlocks:
                print(ii)
            shead.AppendYxsData(str(one2oneBlocks),'One2One')
        odata = []
        for i in range(rotor_head.childCount()):
            shead = rotor_head.child(i)
            t = shead.GetYxsData()['One2One']
            t = eval(t)
            odata.extend(t)
        m = one2one.transfer_one2one_str(odata)
        print(m)


            
    
    def delete_zone(self):
        self.selected_item.parent().removeChild(self.selected_item)
    def create_zone(self,e,title='Create a zone',label = 'zone name', whatsThis = 'Zones_child',head=None):
        text, assure = QInputDialog.getText(self,title, label, QLineEdit.Normal,"")
        if assure:
            if head is None:
                head = self.father.zones_head
            child = YxsQTreeWidgetItem()
            child.setText(0,text)
            child.setWhatsThis(0,whatsThis)
            child.setCheckState(0,Qt.Unchecked)
            head.addChild(child)
    def create_zone_rotor(self):
        self.create_zone(True,title='Create a rotor', label='rotor name', whatsThis='Zones_child_rotor',head=self.father.rotor_head)
    def create_zone_stator(self):
        self.create_zone(True,title='Create a stator', label='stator name', whatsThis='Zones_child_stator',head=self.father.rotor_head)
    def delete_zone_surf(self):
        #删除zone里面的surface
        self.selected_item.parent().removeChild(self.selected_item)
    def setFather(self,p):
        self.father = p
    def show_right_menu(self,pos):
        father = self.father
        item = self.itemAt(pos)
        if item is None:
            return
        whatsThis = item.whatsThis(0)
        pos = QCursor.pos()
        pos.setX(pos.x()+2)
        pos.setY(pos.y()+2)
        self.selected_item = item
        if whatsThis.startswith('surface'):
            self.addtozone_menu.clear()
            zone_head = father.zones_head
            for i in range(zone_head.childCount()):
                text = zone_head.child(i).text(0)
                action = self.addtozone_menu.addAction(text)
                action.triggered.connect(self.addsurf_to_zone)
            
            self.surface_menu.exec_(pos)
        elif whatsThis.startswith('zone_surf'):
            #右键点击的是zone里面的surface
            self.zone_surf_menu.exec_(pos)
        elif whatsThis == 'Zones':
            #右键点击的是Zones标签
            self.zones_menu.exec_(pos)
        elif whatsThis == 'Zones_child':
            #右键点击的是zone标签
            self.zone_menu.exec_(pos)
        elif whatsThis.startswith('block'):
            #右键点击的是某个block
            self.addfacestozone_menu.clear()
            zone_head = father.zones_head
            for i in range(zone_head.childCount()):
                text = zone_head.child(i).text(0)
                action = self.addfacestozone_menu.addAction(text)
                action.triggered.connect(self.addsurfs_to_zone)
            self.addblocktozone_menu.clear()
            zone_head = father.rotor_head
            for i in range(zone_head.childCount()):
                text = zone_head.child(i).text(0)
                action = self.addblocktozone_menu.addAction(text)
                action.triggered.connect(self.AddBlockToRotor)
            self.block_menu.exec_(pos)
        elif whatsThis == 'RotorStator':
            self.rotor_menu.exec_(pos)
        elif whatsThis == 'Zones_child_rotor' or whatsThis == 'Zones_child_stator':
            self.zone_rotor_menu.exec_(pos)
    def AddBlockToRotor(self):
        text = self.sender().text()
        block_item = self.selected_item
        head = self.father.rotor_head
        for i in range(head.childCount()):
            rotor = head.child(i)
            if rotor.text(0) == text:
                child = YxsQTreeWidgetItem()
                tt = block_item.text(0) 
                child.setText(0,tt)
                child.setWhatsThis(0,'rs_block')
                child.setCheckState(0,QtCore.Qt.Unchecked)
                rotor.addChild(child)
                break
    def addsurf_to_zone(self,*d,**kargs):
        #将blocks中的面添加到zone中，为了以后设置边界条件使用
        zone_head = self.father.zones_head
        surf_item = self.selected_item
        sender_text = kargs.get('sender_text',self.sender().text())
        for i in range(zone_head.childCount()):
            zone = zone_head.child(i)
            text = zone.text(0)
            if text == sender_text:
                zone_surf_whatsThis_set = [zone.child(i).whatsThis(0) for i in range(zone.childCount())]
                this_surf_whatsThis =  'zone_surf:'+surf_item.whatsThis(0)
                if this_surf_whatsThis not in zone_surf_whatsThis_set:
                    child = YxsQTreeWidgetItem()
                    tt = surf_item.parent().text(0) +':' + surf_item.text(0)
                    child.setText(0,tt)
                    child.setWhatsThis(0,this_surf_whatsThis)
                    child.setCheckState(0,QtCore.Qt.Unchecked)
                    zone.addChild(child)
                break
    def addsurfs_to_zone(self):
        block_item = self.selected_item
        for i in range(block_item.childCount()):
            self.selected_item = block_item.child(i)
            self.addsurf_to_zone()
class SettingWidget(QWidget):
    def setFather(self,fa):
        self.father = fa
class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("程序主窗口")

        self.pwd = Path()  #设置工作路径

        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Open', self.fileOpen,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Save', self.fileSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addSeparator()
        self.file_menu.addAction('&Test', self.test_func,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_T)
        self.file_menu.addSeparator()
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        
        self.menuBar().addMenu(self.file_menu)
        self.surface_set_drawed = set()
        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QWidget(self)

        l = QVBoxLayout()
        window = MplCanvas(self.main_widget, width=10, height=7, dpi=100)
        window.setMinimumSize(100,100)
        l.addWidget(window,8)
        self.window = window
        self.shell = SongziShell()
        self.shell.setMinimumHeight(30)
        l.addWidget(self.shell,1)
        self.blocks_tree = BTreeWidget()
        self.blocks_tree.setFather(self)
        self.blocks_tree.setHeaderLabels(['Grid'])

        self.blocks_tree.setMinimumWidth(200)  # 左边栏
        h = QHBoxLayout(self.main_widget)
        h.addWidget(self.blocks_tree,1)
        self.setting_widget = SettingWidget()
        h.addWidget(self.setting_widget,1)
        self.setting_widget.setMinimumWidth(200)

        h.addLayout(l)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        # 状态条显示2秒
        self.statusBar().showMessage("welcome to cfl3d_pyui", 2000)
        self.delete_display_surface_timer = QTimer(self)
        self.delete_display_surface_timer.timeout.connect(self.delete_display_surf_time_connect)

        self.append_display_surface_timer = QTimer(self)
        self.append_display_surface_timer.timeout.connect(self.append_display_surf_time_connect)
        self.surface_set_append = set()
        self.saved_tree_list = None
        self.child_head_list = list()
        

        self.resize(1200,700)
        self.after_open(self.pwd / 'cfl3d.out')
        
    def test_func(self):
        self.after_open('/home/yxs/F/learning/CFL3D/CFL3D/cfl3d_test_case_nonin/cfl3d.out')
    def append_display_surf_time_connect(self):
        self.append_display_surface_timer.stop()
        self.surface_set_drawed.update(self.surface_set_append)
        for block_id,name,nn in self.surface_set_append:
            block = self.blocks[block_id-1]
            x, y, z = block['X'], block['Y'], block['Z']
            if name == 'I':
                surface = x[nn], y[nn], z[nn]
            elif name == 'J':
                surface = x[:, nn], y[:, nn], z[:, nn]
            elif name == 'K':
                surface = x[:, :, nn], y[:, :, nn], z[:, :, nn]
            self.draw_surface(surface)
        self.surface_set_append.clear()
        self.window.draw()
    def delete_display_surf_time_connect(self):
        self.delete_display_surface_timer.stop()
        for block_id,name,nn in self.surface_set_drawed:
            block = self.blocks[block_id-1]
            x, y, z = block['X'], block['Y'], block['Z']
            if name == 'I':
                surface = x[nn], y[nn], z[nn]
            elif name == 'J':
                surface = x[:, nn], y[:, nn], z[:, nn]
            elif name == 'K':
                surface = x[:, :, nn], y[:, :, nn], z[:, :, nn]
            self.draw_surface(surface)
        
        self.window.draw()
    def SelectedSurfaceOfBlocks(self,item):
        whatsThis = item.whatsThis(0)
        text = whatsThis[8:]
        blockId = int(text[:-2])
        faceId = text[-2:]
        block = self.blocks[blockId-1]
        idim,jdim,kdim = block['X'].shape
        print(idim,jdim,kdim)

    def TreeItemSelected(self,item):
        #树的节点 被单击选中
        whatsThis = item.whatsThis(0)
        if whatsThis.startswith('surface'):
            self.SelectedSurfaceOfBlocks(item)
    def blocks_change(self,item,column):
        def change_state(item,state,column):
            item.setCheckState(0,state)
            self.blocks_change(item,column)
        whatsThis = item.whatsThis(0)
        state = item.checkState(0)
        if item.isSelected():
            #如果是单击选中而不是勾选 则执行以下内容
            self.TreeItemSelected(item)
            if self.blocks_tree.pressed_state == state:
                return
        if whatsThis == 'Blocks' or whatsThis == 'Zones' or whatsThis.startswith('block') or whatsThis.startswith('Zones_child'):
            [change_state(item.child(i),state,column) for i in range(item.childCount())]
        elif whatsThis.startswith('surface') or whatsThis.startswith('zone_surf:'):
            if whatsThis.startswith('zone_surf:'):
                whatsThis = whatsThis[10:]
            block_id = int(whatsThis[8:-2])
            surface_name = whatsThis[-2:]
            if state == Qt.Checked:
                self.plot_add_surface(block_id,surface_name)
            else:
                self.plot_delete_surface(block_id, surface_name)

    def plot_add_surface(self,block_id,surface_name):
        """block_id:int'
           surface_name:str,'surface:I0'
        """ 
        
        if surface_name[-1] == '0':
            nn = 0
        elif surface_name[-1].upper() == 'E':
            nn = -1
        else:
            raise Exception('surface_Name Error',surface_name)
        s = block_id,surface_name[-2],nn
        if s not in self.surface_set_append and s not in self.surface_set_drawed:
            self.surface_set_append.add(s)
            if not self.append_display_surface_timer.isActive():
                self.append_display_surface_timer.start(50)
    def plot_delete_surface(self,block_id,surface_name):
        if surface_name[-1] == '0':
            nn = 0
        elif surface_name[-1].upper() == 'E':
            nn = -1
        s = block_id,surface_name[-2],nn
        self.surface_set_drawed.discard(s)
        self.ax.clear()
        if not self.delete_display_surface_timer.isActive():
            self.delete_display_surface_timer.start(50)
        
    def GetBlockFace(self,blockid,faceid):
        #blockid: int start from 0 
        #faceid : Ke
        p = 0 if faceid[1] == '0' else -1
        block = self.blocks[blockid]
        x,y,z = block['X'], block['Y'], block['Z']
        if faceid[0] == 'I':
            face = x[p],    y[p],    z[p]
        elif faceid[0] == 'J':
            face = x[:,p],  y[:,p],  z[:,p]
        elif faceid[0] == 'K':
            face = x[:,:,p],y[:,:,p],z[:,:,p]
        return face
    def set_blocks_tree(self):
        
        self.blocks_tree.itemClicked.connect(self.blocks_change)

        self.blocks_tree.clear()

        self.blocks_head = YxsQTreeWidgetItem(self.blocks_tree)
        self.blocks_head.setText(0,'Blocks')
        self.blocks_head.setWhatsThis(0,'Blocks')
        self.blocks_head.setCheckState(0,QtCore.Qt.Unchecked)

        for i,_ in enumerate(self.blocks):
            child = YxsQTreeWidgetItem()
            child.setText(0,'block'+str(i+1))
            child.setWhatsThis(0,'block'+str(i+1))
            child.setCheckState(0,QtCore.Qt.Unchecked)
            self.blocks_head.addChild(child)
            for j in ['I0','IE','J0','JE','K0','KE']:
                surf_child = YxsQTreeWidgetItem()
                surf_child.setText(0,'surface:{}'.format(j))
                surf_child.setWhatsThis(0,'surface:'+str(i+1)+j)
                surf_child.setCheckState(0,QtCore.Qt.Unchecked)
                child.addChild(surf_child)
        self.zones_head = YxsQTreeWidgetItem(self.blocks_tree)
        self.zones_head.setText(0,'Zones')
        self.zones_head.setWhatsThis(0,'Zones')
        self.zones_head.setCheckState(0,QtCore.Qt.Unchecked)

        self.rotor_head = YxsQTreeWidgetItem(self.blocks_tree)
        self.rotor_head.setText(0,'Rotor and Stator')
        self.rotor_head.setWhatsThis(0,'RotorStator')
        self.rotor_head.setCheckState(0,QtCore.Qt.Unchecked)

        self.child_head_list = [self.zones_head,self.rotor_head]

        if not self.saved_tree_list:
            for i in ['in','out']:
                child = YxsQTreeWidgetItem()
                child.setText(0,i)
                child.setWhatsThis(0,'Zones_child')
                child.setCheckState(0,QtCore.Qt.Unchecked)
                self.zones_head.addChild(child)
        else:
            for head,tree_dict in zip(self.child_head_list, self.saved_tree_list):
                self.Dict2Tree(head,tree_dict)
    
    def start_draw_plot3d_grid(self):
        self.window.fig.clear()
        axes = self.window.fig.gca(projection='3d')
        if self.plot3d_file.suffix == '.xs3d':
            fp = open(self.plot3d_file,'rb')
            tt = plot3d.read_plot3d_unfmt(fp)
            dict_str = fp.read().decode('utf8')
            self.saved_tree_list = json.loads(dict_str)
        else:
            self.saved_tree_list = None
            tt = tecfile.read(str(self.plot3d_file))

        self.blocks = tt
        self.ax = axes 
        self.is_draw_surfaces = True
        self.set_blocks_tree()
        self.window.fig.subplots_adjust(bottom = 0,left=0,top=1,right=1)
        # self.ax.get_proj = lambda: np.dot(Axes3D.get_proj(self.ax), np.diag([0.5, 1, 1, 1]))
        # x,y,z = tt[0]['X'][0],tt[0]['Y'][0],tt[0]['Z'][0]
        # self.draw_surface((x,y,z))
    def draw_surface(self,surface):
        if not self.is_draw_surfaces:
            return 
        points_n = 15
        x,y,z = surface
        h,w = x.shape
        inx = np.array(range(0, h, min(h, int(h/points_n)+1)),dtype='int32')
        iny = np.array(range(0, w, min(w, int(w/points_n)+1)), dtype='int32')
        inx[-1] = h-1
        iny[-1] = w-1
        x1 = x[inx][:, iny]
        y1 = y[inx][:, iny]
        z1 = z[inx][:, iny]
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        rgb = np.where(x,'#BFAB6EC0','#BFAB6EC0')
        self.ax.plot_surface(x1, y1, z1, rstride=1, cstride=1, facecolors=rgb,
                            linewidth=0, antialiased=True)
        self.ax.plot(x[0],y[0],z[0],linewidth = 3, color = 'k')
        self.ax.plot(x[-1],y[-1],z[-1],linewidth = 3, color = 'k')
        self.ax.plot(x[:,0],y[:,0],z[:,0],linewidth = 3, color = 'k')
        self.ax.plot(x[:,-1],y[:,-1],z[:,-1],linewidth = 3, color = 'k')
        # print(len(self.ax.lines))
    def fileOpen(self):
        fileName,_ = QFileDialog.getOpenFileName(self, "Open File")
        if fileName:
            self.after_open(fileName)
    def fileSave(self):
        fileName,ext_f= QFileDialog.getSaveFileName(self, "Save File","","plot3d ascii (*.fmt);;plot3d bin (*.g);;xs3d bin (*.xs3d)")
        if fileName:
            m,n = ext_f.find('*'), ext_f.find(')')
            ext_f = ext_f[m+1:n]
            if not fileName.endswith(ext_f):
                fileName += ext_f
            if ext_f == '.xs3d':
                self.save_xs3d(fileName)
            else:
                tecfile.write(fileName,self.blocks)
    def save_xs3d(self,fileName):
        fp = open(fileName,'wb')
        plot3d.write_plot3d_unfmt(fp,self.blocks)
        tree_dict_list = [self.Tree2Dict(head) for head in self.child_head_list]
        dict_str = json.dumps(tree_dict_list)
        fp.write(dict_str.encode('utf8'))
        fp.close()
    def Dict2Tree(self,head,children):
        for key,value in children.items():
            child = YxsQTreeWidgetItem()
            child.setText(0,key)
            child.setWhatsThis(0,value['whatsThis'])
            child.setDataFromString(value['data'])
            child.setCheckState(0,QtCore.Qt.Unchecked)
            head.addChild(child)
            if value['children']:
                self.Dict2Tree(child,value['children'])
    def Tree2Dict(self,tree):
        d = dict()
        for i in range(tree.childCount()):
            child = tree.child(i)
            text, whatsThis = child.text(0), child.whatsThis(0)
            child_dict = dict()
            child_dict['whatsThis'] = whatsThis 
            child_dict['data'] = child.GetDataString()
            child_dict['children'] = self.Tree2Dict(child)
            d[text] = child_dict 
        return d

    def after_open(self,filename):
        pname = Path(filename)
        if pname.suffix == '.out':
            self.residual_file = pname
            self.start_draw_residual()
        else:
            self.plot3d_file = pname 
            self.start_draw_plot3d_grid()
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QMessageBox.about(self, "About",
        """
        Copyright 2018 Yongxiaosong 
        """
        )
    def start_draw_residual(self):
        # return
        self.window.fig.clear()
        self.last_data_draw = dict()
        self.draw_history = True #是否绘制历史残差
        if not self.residual_file.is_file():
            return
        self.residual = Residual(self.residual_file)
        self.res_timer = QtCore.QTimer(self)
        self.res_timer.timeout.connect(self.draw_residual)
        self.res_timer.start(2000)
        self.axes = self.window.fig.add_subplot(111)
        self.window.fig.subplots_adjust(bottom = 0.05,left=0.1,top=1,right=1)
        self.need_legend = True
    def draw_residual(self):
        if self.draw_history:
            data = self.residual.get_history()
        else:
            data = np.array([])
        if not data.any():
            data = self.residual.get()
        if not data.any():return
        self.draw_history = False
        x = data[:,2]
        fp = 3
        x_last, y_last = None, None
        colors = ['k','b','y','#054E9F','g','o']
        names = ('residual','total res.')
        for i,(key,co) in enumerate(zip(names,colors)):
            #为了使图线不间断
            if key not in self.last_data_draw:
                x0 = x 
                y0 = np.abs(data[:,i+fp])
                self.last_data_draw[key] = x0[-1], y0[-1]
            else:
                x_last, y_last = self.last_data_draw[key]
                x0 = np.concatenate(([x_last],x))
                y0 = np.concatenate(([y_last],np.abs(data[:,i+fp])))
                self.last_data_draw[key] = x0[-1], y0[-1]

            self.axes.semilogy(x0,y0,label = key,color = co)

        if self.need_legend:
            self.axes.legend(loc='upper left')
            self.need_legend=False
        self.window.draw()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.setWindowTitle("CFL3D Tools")
    aw.show()
    sys.exit(app.exec_())
    # app.exec_()
