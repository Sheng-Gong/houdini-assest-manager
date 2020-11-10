#coding: utf-8

from PySide2.QtWidgets import *
from PySide2.QtGui import QIcon
from PySide2.QtGui import *
from PySide2.QtCore import *
#from pykeyboard import *
import os
import sys
import time 
import shutil
import xml.dom.minidom
import hou
import webbrowser
#from win32com.shell import shell,shellcon

class ProjectManager(QWidget):
    def __init__(self):
        super(ProjectManager, self).__init__()
        self.init_UI()
    def init_UI(self):
        # 窗体设置
        self.setWindowTitle("Project Manager 1.0")
        self.setGeometry(0, 0, 850, 600)
        self.text=QLineEdit()
        self.text.setPlaceholderText('资产区路径') 
        self.text1=QLineEdit()
        self.text1.setPlaceholderText('筛选 *代表显示所有')
        self.text1.setClearButtonEnabled(1)
        self.text2=QTextEdit()
        self.text2.setFixedHeight(122)
        self.text2.setPlaceholderText('文件描述') 
        self.btn0 = QPushButton("选择资产区")
        self.btn1 = QPushButton("载入")
        self.table1=QListWidget()
        self.table1.setViewMode(QListView.IconMode)
        self.table1.setIconSize(QSize(100,100))
        self.table1.setMovement(QListView.Static)
        self.listwidget = QTreeView()
        self.listwidget.setIndentation(20)
        self.listwidget.setFixedWidth(250)
        self.listwidget.setHeaderHidden(1)
        self.btn5 = QPushButton("清理")
        self.btn2 = QPushButton("保存当前场景的设置")
        self.btn4 = QPushButton("保存文件描述")
        self.btn3 = QPushButton("创建")

        layout=QVBoxLayout() 
        h_layout=QHBoxLayout()
        v_layout=QVBoxLayout()
        h_layout1=QHBoxLayout()
        h_layout2=QHBoxLayout()
        h_layout3=QHBoxLayout()
        v_layout1=QVBoxLayout()

        h_layout.addWidget(self.btn0)
        h_layout.addWidget(self.text)
        h_layout.addWidget(self.btn1)

        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.text1)

        h_layout1.addLayout(v_layout)
        h_layout1.addWidget(self.text2)

        h_layout2.addWidget(self.listwidget)
        h_layout2.addWidget(self.table1)

        h_layout3.addWidget(self.btn5)
        h_layout3.addWidget(self.btn2)
        h_layout3.addWidget(self.btn4)
        h_layout3.addWidget(self.btn3)
        
        layout.addLayout(h_layout1)
        layout.addLayout(h_layout2)
        layout.addLayout(h_layout3)
        self.setLayout(layout)
        


        self.btn0.clicked.connect(self.set_asset_path_event)
        self.btn1.clicked.connect(self.load_asset_data_event)
        self.text1.textChanged.connect(self.filter_event)
        self.btn2.clicked.connect(self.save_event)
        self.btn3.clicked.connect(self.create_event)
        self.btn4.clicked.connect(self.save_text_event)
        self.btn5.clicked.connect(self.clean_back_up)
        self.text2.textChanged.connect(self.text_change)
        self.table1.doubleClicked.connect(self.load_hip)
        self.table1.clicked.connect(self.show_file_documentation)
        self.table1.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table1.customContextMenuRequested.connect(self.generate_menu_event)
        self.listwidget.clicked.connect(self.show_tree)
        #self.listwidget.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.listwidget.customContextMenuRequested.connect(self.generate_listwidget_menu_event)
        try :
            open("D:/houdini_project_path.txt","r")
        except:
            pass
        else:
            _f = open("D:/houdini_project_path.txt","r")
            _text = _f.read()
            _f.close()
            if len(_text)==0:
                pass
            else:
                self.text.setText(_text)
                self.set_item()
                self.btn1.setText("刷新")
                self.set_tree_view(_text)
    def closeEvent(self,event):
        self.setParent(None)


    def clean_back_up(self):
        _data_list = self.get_data()
        _index = self.table1.currentRow()

        if _index!=-1:
            _hip_path = _data_list[_index][3]
            _path = _hip_path[:-len(_hip_path.split("/")[-1])]
        else:
            _path = self.text.text()
        _dir_choose=QFileDialog().getExistingDirectory(self,("选择需要清理的文件夹"),_path)

        for root, dirs, files in os.walk(_dir_choose):
            for name in files:
                _path = os.path.join(root, name)
                _path = _path.replace('\\','/')
                if 'backup' in _path:
                    os.remove(_path)
                    #shell.SHFileOperation((0,shellcon.FO_DELETE,filename,None, shellcon.FOF_SILENT | shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION,None,None))
                    #shell.SHFileOperation((0,shellcon.FO_DELETE,_path,None,/shellcon.FOF_SILENT | /shellcon.FOF_ALLOWUNDO | /shellcon.FOF_NOCONFIRMATION,None,None))
            #for name in dirs:
                #if name=='backup':
                    #print(os.path.join(root, name,))

    def set_tree_view(self,_path):
        self.listwidget._model = QFileSystemModel()
        _path = _path
        self.listwidget._model.setRootPath(_path)
        self.listwidget._model.setNameFilters(["back"])
        self.listwidget._model.setNameFilterDisables(0)

        self.listwidget.setModel(self.listwidget._model)
        self.listwidget.setRootIndex(self.listwidget._model.index(_path))
        for i in [1,2,3]:
            self.listwidget.setColumnHidden(i, True)
        
            
    def show_tree(self,Qmodelidx):
        _current_catalog = self.listwidget._model.filePath(Qmodelidx)
        self.catalog_filter_event(_current_catalog)
        #print self.listwidget._model.fileName(Qmodelidx)
    def create_event(self):
        _current_catalog_index_list = self.listwidget.selectedIndexes()
        Dialog = childWindow() 
        Dialog.text.setText(self.text.text())
        if len(_current_catalog_index_list) !=0:
            _current_catalog_index = _current_catalog_index_list[0]
            _path =  self.listwidget._model.filePath(_current_catalog_index)
            _floder = _path[(len(self.text.text())+1):]
            Dialog.text1.setText(_floder)
        else:
            _path = self.text.text()

        Dialog.setParent(hou.qt.mainWindow(),Qt.Window)
        Dialog.show()

    def save_text_event(self):
        _documentation_text = self.text2.toPlainText()
        _color = self.text2.textColor().rgb()
        if _color==4294901760:
            _data_list = self.get_data()
            _index = self.table1.currentRow()
            _hip_path = _data_list[_index][3]
            _path = _hip_path.split('.')[0]
            _documentation_path = _path+".txt"
            _documentation_text = self.text2.toPlainText()
            _f = open(_documentation_path, 'w')
            _f.write(_documentation_text)
            _f.close()
            #print('ddd')
        else:
            pass

    def catalog_filter_event(self,_current_catalog):
        _filter_text = self.text1.text()
        _count = self.table1.count()
        _data_list = self.get_data()
        for k in range(_count):
            self.table1.setItemHidden(self.table1.item(k),1)
        _current_catalog_list = _current_catalog.split('/')
        _index_list = []
        if len(_filter_text) ==0:
            iter = 0
            for i in _data_list:
                _sub_level = i[5].replace('\\','/')
                _sub_list = _sub_level.split('/')
                #if set(_sub_list).issubset(set(_current_catalog_list)):
                if set(_current_catalog_list).issubset(set(_sub_list)):
                    _index_list.append(iter)
                else:
                    pass
                iter+=1
        else:
            iter = 0
            for i in _data_list:
                _sub_level = i[5].replace('\\','/')
                _sub_list = _sub_level.split('/')
                if set(_current_catalog_list).issubset(set(_sub_list)):
                ##if set(_sub_list).issubset(set(_current_catalog_list)):
                    for m in i:
                        if _filter_text.lower() in m.lower():
                            _index_list.append(iter)
                        else:
                            pass
                else:
                    pass
                iter+=1
            _index_list = list(set(_index_list))
        for l in _index_list:
            self.table1.setItemHidden(self.table1.item(l),0)



    # 过滤事件
    def filter_event(self):
        #print self.listwidget._model.file
        _current_catalog_index_list = self.listwidget.selectedIndexes()
        _filter_text = self.text1.text()
        _count = self.table1.count()
        _data_list = self.get_data()
        if len(_filter_text) !=0:
            for k in range(_count):
                self.table1.setItemHidden(self.table1.item(k),1)
            _index_list = []
            if _filter_text =='*':
                for k in range(_count):
                    self.table1.setItemHidden(self.table1.item(k),0)
            else:
                if len(_current_catalog_index_list) ==0:
                    iter = 0
                    for i in _data_list:
                        for m in i:
                            if _filter_text.lower() in m.lower():
                                _index_list.append(iter)
                            else:
                                pass
                        iter+=1
                    _index_list = list(set(_index_list))
                else:
                    _current_catalog_index = _current_catalog_index_list[0]
                    _current_catalog =  self.listwidget._model.filePath(_current_catalog_index)
                    _current_catalog_list = _current_catalog.split('/')
                    ##print(_current_catalog)
                    iter = 0
                    for i in _data_list:
                        _sub_level = i[5].replace('\\','/')
                        _sub_list = _sub_level.split('/')
                        if set(_current_catalog_list).issubset(set(_sub_list)):
                        ##if set(_sub_list).issubset(set(_current_catalog_list)):
                            for m in i:
                                if _filter_text.lower() in m.lower():
                                    _index_list.append(iter)
                                else:
                                    pass
                        else:
                            pass
                        iter+=1
                    _index_list = list(set(_index_list))

                for l in _index_list:
                    self.table1.setItemHidden(self.table1.item(l),0)
        else:
            if len(_current_catalog_index_list) ==0:
                for j in range(_count):
                    self.table1.setItemHidden(self.table1.item(j),0)
            else:
                _current_catalog_index = _current_catalog_index_list[0]
                _current_catalog =  self.listwidget._model.filePath(_current_catalog_index)
                _index_list = []
                _current_catalog_list = _current_catalog.split('/')
                iter = 0
                for i in _data_list:
                    _sub_level = i[5].replace('\\','/')
                    _sub_list = _sub_level.split('/')
                    if set(_current_catalog_list).issubset(set(_sub_list)):
                    ##if set(_sub_list).issubset(set(_current_catalog_list)):
                        _index_list.append(iter)
                    else:
                        pass
                    iter+=1
                for l in _index_list:
                    self.table1.setItemHidden(self.table1.item(l),0)

       
        
    def text_change(self):
        self.text2.setTextColor(QColor(255,0,0))
        

    #  设置资产区
    def set_asset_path_event(self):
        _dir_choose=QFileDialog().getExistingDirectory(self,("选取资产区文件夹"))
        _project_dir = self.text.setText(_dir_choose)
        _project_file_path = "D:/houdini_project_path.txt"
        _f = open(_project_file_path, 'w')
        _f.write(_dir_choose)
        _f.close()

    # 获得资产区的文件数据
    # 路径 文件名 icon 文件描述
    def generate_menu_event(self,_pos):
        _menu = hou.qt.Menu()
        _item4 = _menu.addAction(u"打开")
        _item2 = _menu.addAction(u"合并")
        _item1 = _menu.addAction(u"重命名")
        _item = _menu.addAction(u"在资源管理器中显示")
        #_item3 = _menu.addAction(u"文件另存为")

        _action = _menu.exec_(self.table1.mapToGlobal(_pos))
        if _action == _item:
            self.open_folder_menu_event()    
        if _action == _item1:
            self.rename_menu_event()
        if _action == _item2:
            self.merge_menu_event()
        if _action == _item4:
            self.open_hip_new_houdini()

    def generate_listwidget_menu_event(self,_pos):
        _menu = hou.qt.Menu()
        _item = _menu.addAction(u"创建子文件夹")
        _action = _menu.exec_(self.listwidget.mapToGlobal(_pos))

    def open_hip_new_houdini(self):
        _data_list = self.get_data()
        _index = self.table1.currentRow()
        _hip_file_path = _data_list[_index][3]
        os.system(_hip_file_path)

    def open_folder_menu_event(self):
        _data_list = self.get_data()
        _index = self.table1.currentRow()
        _hip_path = _data_list[_index][3]
        _dir = _hip_path[:-len(_hip_path.split("/")[-1])]
        _dir =_dir.replace("/","\\")
        os.startfile(_dir)

    def rename_menu_event(self):
        _text, _okPressed = QInputDialog.getText(self, "重命名","文件名:", QLineEdit.Normal, "")
        if _okPressed and _text != '':
            _data_list = self.get_data()
            _index = self.table1.currentRow()
            _hip_path = _data_list[_index][3]
            _jpg_path = _data_list[_index][1]
            _documentation_path = _data_list[_index][4]
            _dst_hip_name = _text +'.hip'
            _path = _hip_path[:-len(_hip_path.split("/")[-1])]
            _dst_hip_path = os.path.join(_path,_dst_hip_name)
            os.rename(_hip_path,_dst_hip_path)
            if len(_jpg_path) !=0:
                _dst_jpg_name = _text +'.jpg'
                _dst_jpg_path = os.path.join(_path,_dst_jpg_name)
                os.rename(_jpg_path,_dst_jpg_path)
            else:
                pass
            if len(_documentation_path) !=0:
                _dst_doc_name = _text +'.txt'
                _dst_doc_path = os.path.join(_path,_dst_doc_name)
                os.rename(_documentation_path,_dst_doc_path)
            else:
                pass
    def merge_menu_event(self):
        _data_list = self.get_data()
        _index = self.table1.currentRow()
        _hip_path = _data_list[_index][3]
        hou.hipFile.merge(_hip_path)


    def load_asset_data_event(self):
        if self.table1.count()==0:
            self.set_item()
            _project_dir = self.text.text()
            self.set_tree_view(_project_dir)
            self.btn1.setText("刷新")
        else:
            if self.btn1.text() == "刷新":
                self.refresh_event()
            else:
                pass
    def load_hip(self):
        _data_list = self.get_data()
        _index = self.table1.currentRow()
        _hip_file_path = _data_list[_index][3]
        hou.hipFile.load(_hip_file_path)

    def get_data(self):
        _project_dir = self.text.text()
        _data_list = []
        for _root,_dirs,_files in os.walk(_project_dir):
            for _filename in _files:
                _backup_file = _root[-6:]
                if _backup_file =="backup":
                    pass
                else:
                    if _filename.endswith(".hip"):
                        _name = _filename.split(".")[0]
                        _hip_path = os.path.join(_root,_filename)
                        _hip_path = _hip_path.replace('\\','/')
                        _current_list = os.listdir(_root)
                        _jpg_name = _name+".jpg"
                        _documentation_name = _name+".txt"
                        if _jpg_name in _current_list:
                            _icon_jpg = os.path.join(_root,_jpg_name)
                            _icon_jpg = _icon_jpg.replace('\\','/')
                        else:
                            _icon_jpg = ""
                        
                        if _documentation_name in _current_list:
                            _documentation_path = os.path.join(_root,_documentation_name)
                            _documentation_path = _documentation_path.replace('\\','/')
                            _f = open(_documentation_path, 'r')
                            _documentation = _f.read()
                            _f.close()
                        else:
                            _documentation = ""
                            _documentation_path = ""
                        
                        _data_sub_list =[_name,_icon_jpg,_documentation,_hip_path,_documentation_path,_root]
                        _data_list.append(_data_sub_list)
        return _data_list
    # 设置列表
    def set_item(self):
        _data_list = self.get_data()
        for i in _data_list:
            if len(i[1])!=0:
                _jpg=QPixmap(i[1]).scaled(200, 200)
                _icon = QIcon(_jpg)
                #_icon = hou.qt.createIcon(i[1])
            else:
                _icon = hou.qt.createIcon("NETVIEW_error_badge",200,200)
            _item = QListWidgetItem(_icon, "")
            _item.setText(i[0])
            self.table1.addItem(_item)
        

    # 显示文件的说明文档
    def show_file_documentation(self):
        self.text2.blockSignals(1)
        _data_list = self.get_data()
        _index = self.table1.currentRow()
        _documentation = _data_list[_index][2]
        if len(_documentation) == 0:
            _documentation_text = "该文件没有描述"
        else:
            _documentation_text = _documentation
        self.text2.setText(_documentation_text)
        self.text2.setTextColor(QColor(255,255,255))
        self.text2.blockSignals(0)

        
    def get_floder_list(self):
        pass

    # 刷新事件
    def refresh_event(self):
        self.table1.clear()
        self.set_item()
    # 保存修改
    def save_event(self):
        _res = QMessageBox.information(self, "提示", "是否保存", QMessageBox.Yes | QMessageBox.No)
        if (QMessageBox.Yes == _res):
            self.save_edit()
        elif (QMessageBox.No == _res):
            pass

    def save_edit(self):
        _current_hip = hou.hipFile.name()
        if len(_current_hip.split("/")) ==0:
            pass
        else:
            # 截图功能
            _current_desktop = hou.ui.curDesktop()
            _scene_viewer = _current_desktop.paneTabOfType(hou.paneTabType.SceneViewer)

            _current_frame = hou.frame()
            _jpg_path = hou.hipFile.name().split(".")[0]
            _jpg_file_path = _jpg_path+".jpg"

            #getFlipbook
            _flip_options = _scene_viewer.flipbookSettings().stash()

            #SetFlipbook
            _flip_options.frameRange((_current_frame,_current_frame))
            _flip_options.outputToMPlay(0)
            _flip_options.useResolution(1)
            _flip_options.resolution((500,500))
            _flip_options.output(_jpg_file_path)

            #RunFlipbook
            _scene_viewer.flipbook(_scene_viewer.curViewport(), _flip_options)

            if self.text2.textColor().rgb()==4294901760:
                _documentation_path = _jpg_path+".txt"
                _documentation_text = self.text2.toPlainText()
                _f = open(_documentation_path, 'w')
                _f.write(_documentation_text)
                _f.close()
            else:
                pass
        

class childWindow(QWidget):
    def __init__(self):
        super(childWindow, self).__init__()
        self.init_UI()
    def init_UI(self):
        # 窗体设置
        self.setWindowTitle("创建新工程文件")
        self.resize(600,400)
        
        self.text=QLineEdit()
        self.text.setPlaceholderText('文件区')
        self.text1=QLineEdit()
        self.text1.setPlaceholderText('子目录')
        self.text2=QLineEdit()
        self.text2.setPlaceholderText('文件名')
        self.text2.setClearButtonEnabled(1)
        self.text3=QTextEdit()
        self.text3.setPlaceholderText('文件描述信息')
        self.btn1 = QPushButton("创建")


        layout=QVBoxLayout() 
        layout.addWidget(self.text)
        layout.addWidget(self.text1)
        layout.addWidget(self.text2)
        layout.addWidget(self.text3)
        layout.addWidget(self.btn1)
        self.setLayout(layout)
        self.btn1.clicked.connect(self.create_new_hip)
    def create_new_hip(self):
        _floder = self.text1.text()
        _hip_name = self.text2.text()+'.hip'
        #_hip_text = self.text3.text()
        if len(_hip_name)!=0 and len(_floder)!=0:
            _hip_path =  os.path.join(self.text.text(),_floder,_hip_name)
            _hip_path=_hip_path.replace('\\','/')
            hou.hipFile.save(_hip_path,save_to_recent_files=False)

            # 截图功能
            _current_desktop = hou.ui.curDesktop()
            _scene_viewer = _current_desktop.paneTabOfType(hou.paneTabType.SceneViewer)

            _current_frame = hou.frame()
            _jpg_path = _hip_path.split(".")[0]
            _jpg_file_path = _jpg_path+".jpg"

            #getFlipbook
            _flip_options = _scene_viewer.flipbookSettings().stash()

            #SetFlipbook
            _flip_options.frameRange((_current_frame,_current_frame))
            _flip_options.outputToMPlay(0)
            _flip_options.useResolution(1)
            _flip_options.resolution((500,500))
            _flip_options.output(_jpg_file_path)

            #RunFlipbook
            _scene_viewer.flipbook(_scene_viewer.curViewport(), _flip_options)

            _documentation_text = self.text3.toPlainText()
            if len(_documentation_text) !=0:
                _documentation_path = _jpg_path+".txt"

                _f = open(_documentation_path, 'w')
                _f.write(_documentation_text)
                _f.close()
            else:
                pass

            self.close()
        else:
            pass

    def closeEvent(self,event):
        self.setParent(None)


            

Dialog = ProjectManager() 
Dialog.setParent(hou.qt.mainWindow(),Qt.Window)
Dialog.show()
