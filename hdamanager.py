#coding: utf-8

from PySide2.QtWidgets import *
from PySide2.QtGui import QIcon
from PySide2.QtGui import *
from PySide2.QtCore import *

import os
import sys
import time 
import shutil
import xml.dom.minidom
import hou
import webbrowser
    
class HDAManager(QWidget):
    def __init__(self):
        super(HDAManager, self).__init__()
        self.init_UI()
    def init_UI(self):
        # 窗体设置
        self.setWindowTitle("HDA Manager 1.4")
        self.setGeometry(0, 0, 700, 600) 
        # UI属性设置 
        #设置icon
        #help_icon= hou.qt.createIcon("opdef:/labs::Sop/destruction_cleanup::2.0?IconSVG", 128, 128)
        #self.setWindowIcon(help_icon) 
        # 过滤器设置
        self.filter=QLineEdit()
        self.filter.setPlaceholderText('筛选')
        self.filter.setClearButtonEnabled(1)
        # 切换列表设置
        self.cb = QComboBox()
        # 按钮设置
        self.btn0 = QPushButton("刷新列表")
        self.btn1 = QPushButton("保存修改")
        self.btn2 = QPushButton("过滤修改项")
        self.btn2.setCheckable(True)
        self.btn3 = QPushButton("打开目录")
        # self.btn2.toggle() 设置为初始按下
        # 表格设置
        self.table=QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels(['HDA Label Name','Tab','描述'])        # 设置表头标签
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)    # 自适应的伸缩模式
        ####self.table.setSortingEnabled(1)#目前有元素丢失问题
        QTableWidget.resizeColumnsToContents(self.table)        # TODO 优化 5 将行与列的高度设置为所显示的内容的宽度高度匹配
        QTableWidget.resizeRowsToContents(self.table)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        # 设置部署布局
        layout=QVBoxLayout() 
        v_layout=QVBoxLayout()
        h_layout=QHBoxLayout()
        v_layout1=QVBoxLayout()
        v_layout.addWidget(self.filter)
        v_layout.addWidget(self.cb)
        h_layout.addWidget(self.btn0)
        h_layout.addWidget(self.btn1)
        h_layout.addWidget(self.btn2)
        h_layout.addWidget(self.btn3)
        v_layout1.addWidget(self.table)
        layout.addLayout(v_layout)
        layout.addLayout(h_layout)
        layout.addLayout(v_layout1)
        self.setLayout(layout)
        # 初始执行数据
        self.get_cb_data()
        self.add_data()
        # 触发设置
        self.filter.textChanged.connect(self.filter_event)
        self.cb.currentIndexChanged.connect(self.switch_event)
        self.btn0.clicked.connect(self.refresh_event)
        self.btn1.clicked.connect(self.save_event)
        self.btn2.clicked.connect(self.filter_changed_event) # 点击信号与槽函数进行连接，实现的目的：输入安妞的当前状态，按下还是释放
        self.btn3.clicked.connect(self.open_resource_directory_event)
        self.table.cellChanged.connect(self.table_cell_change)
        self.table.customContextMenuRequested.connect(self.generate_menu_event)
    
    # #界面按键触发事件

    # 检测按键按下事件
    def keyPressEvent(self, event):
        if(event.key() == Qt.Key_Escape):
            self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        if(event.key() == Qt.Key_F1):
            self.open_help_event()
    # 检测按键释放事件
    def keyReleaseEvent(self, event):
        if(event.key() == Qt.Key_Escape):
            self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
    # 关闭事件
    def closeEvent(self,event):
        _list = self.get_table_change_list()
        if len(_list)>0:
            _res = QMessageBox.information(self, "提示", "尚有修改未保存，是否关闭", QMessageBox.Yes | QMessageBox.No)
            if (QMessageBox.Yes == _res):
                event.accept()
                self.setParent(None)
            elif (QMessageBox.No == _res):
                event.ignore()
        else:
            event.accept()
            self.setParent(None)
    # 过滤事件
    def filter_event(self):
        _filter_text = self.filter.text()
        _row_count = self.table.rowCount()
        if len(_filter_text) !=0:
            for k in range(_row_count):
                self.table.setRowHidden(k,1)
            _items = self.table.findItems(_filter_text,Qt.MatchContains)
            _index_list = []
            for i in _items:
                _index_list.append(i.row())
            _index_list= list(set(_index_list))
            for l in _index_list:
                self.table.setRowHidden(l,0)
        else:
            for j in range(_row_count):
                self.table.setRowHidden(j,0)
    # 切换列表事件
    def switch_event(self): 
        _list = self.get_table_change_list()
        if len(_list)>0:
            _res = QMessageBox.information(self, "提示", "尚有修改未保存，是否切换", QMessageBox.Yes | QMessageBox.No)
            if (QMessageBox.Yes == _res):
                self.refresh_table()
                self.btn2.setChecked(0)
            elif (QMessageBox.No == _res):
                pass
        else:
            self.refresh_table()
            self.btn2.setChecked(0)    
    # 列表刷新事件       
    def refresh_event(self):
        _list = self.get_table_change_list()
        if len(_list)>0:
            _res = QMessageBox.information(self, "提示", "尚有修改未保存，是否刷新", QMessageBox.Yes | QMessageBox.No)
            if (QMessageBox.Yes == _res):
                self.refresh_table()
                self.btn2.setChecked(0)
            elif (QMessageBox.No == _res):
                pass
        else:
            self.refresh_table()
            self.btn2.setChecked(0)
    # 保存事件
    def save_event(self):
        _list = self.get_table_change_list()
        if len(_list)>0:
            _res = QMessageBox.information(self, "提示", "是否保存,请确认一下", QMessageBox.Yes | QMessageBox.No)
            if (QMessageBox.Yes == _res):
                self.save_changes()
                self.btn2.setChecked(0)
            elif (QMessageBox.No == _res):
                pass
        else:
            pass
    # 过滤修改项事件
    def filter_changed_event(self):
        _filterlist = self.get_table_change_list()
        _row_count = self.table.rowCount()
        if self.btn2.isChecked():
            if len(_filterlist) !=0:
                self.set_disable_all_items(1)
                for i in _filterlist:
                    self.table.setRowHidden(i,0) 
            else:
                self.btn2.setChecked(0)
        else:
            for k in range(_row_count):
                self.table.setRowHidden(k,0)
    # 列表修改触发事件
    def table_cell_change(self,_row,_col):
        self.table.blockSignals(1)
        _select_items_list =self.get_select_items_list()
        _item = self.table.item(_row,_col)
        _txt = _item.text()
        #item.setForeground(QBrush(QColor(255,0,0)))
        _item.setTextColor(QColor(255,0,0))
        if len(_select_items_list) <2:
            pass
        else:
            for i in _select_items_list:
                if i[1] != 0:
                    _change_item = QTableWidgetItem(_txt)
                    self.table.setItem(i[0],i[1],_change_item)
                    self.table.item(i[0],i[1]).setTextColor(QColor(255,0,0))
                else:
                    pass
        self.table.blockSignals(0)
    # 右键菜单触发生成事件           
    def generate_menu_event(self,_pos):
        _menu = hou.qt.Menu()
        _item1 = _menu.addAction(u"还原")
        _item2 = _menu.addAction(u"保存修改")
        _item3 = _menu.addAction(u"导入")

        _action = _menu.exec_(self.table.mapToGlobal(_pos))
        if _action == _item1:
            self.refresh_menu_event()
        elif _action == _item2:
            self.save_menu_event()      
        elif _action == _item3:
            self.import_menu_event() 
    # 右键菜单：还原事件       
    def refresh_menu_event(self):
        _list = self.filter_select_items_list()
        if len(_list)>0:
            _res = QMessageBox.information(self, "提示", "是否还原", QMessageBox.Yes | QMessageBox.No)
            if (QMessageBox.Yes == _res):
                self.refresh_select_items()
                _change_list = self.get_table_change_list()
                if len(_change_list) >0:
                    pass  
            elif (QMessageBox.No == _res):
                pass 
        else:
            pass
    # 右键菜单：保存事件
    def save_menu_event(self):
        _list = self.filter_select_items_list()
        if len(_list)>0:
            _res = QMessageBox.information(self, "提示", "是否保存修改", QMessageBox.Yes | QMessageBox.No)
            if (QMessageBox.Yes == _res):
                self.save_select_items()
            elif (QMessageBox.No == _res):
                pass           
        else:
            pass
    # 右键菜单：引入事件
    def import_menu_event(self): 
        _select_list = self.get_select_row_list() 
        _hda_list = self.get_hda_data()
        _import_hda_list=[]
        _houdini_level_list = {"Chop":"ch",
        "Cop2":"img",
        "Vop":["mat","attribvop","shop"],
        "Object":"obj",
        "Sop":"geo",
        "Dop":"dopnet",
        "Driver":"out",
        "Lop":"stage",
        "Top":"topnet"
        }
        for j in _select_list:
            _import_hda_name = _hda_list[j][4]
            _import_hda_level = _hda_list[j][6]
            _imoprt_hda_sub_list = [_import_hda_name,_import_hda_level]
            _import_hda_list.append(_imoprt_hda_sub_list)
        _pane_list =hou.ui.paneTabs()
        for i in _pane_list:
            if "NetworkEditor" == i.type().name():
                _current = i.currentNode()
                _Current_level = _current.type().name()
                for k in _import_hda_list:
                    _hda_level = k[1]
                    if _hda_level !="Vop":
                        if _houdini_level_list[_hda_level] ==_Current_level:
                            _current.createNode(k[0])
                        elif _houdini_level_list[_hda_level] ==_current.parent().type().name():
                            _current.parent().createNode(k[0])
                        else:
                            print("创建层级错误,请转到%s层级\n" % _houdini_level_list[_hda_level])
                    else:
                        if _Current_level in _houdini_level_list[_hda_level]:
                            _current.createNode(k[0])
                        elif _current.parent().type().name() in _houdini_level_list[_hda_level]:
                            _current.parent().createNode(k[0])
                        else:
                            print("创建层级错误,请转到%s层级\n" % _houdini_level_list[_hda_level])
                
            else:
                pass
                #print "不存在节点编辑面板，请创建"
    # F1打开帮助文档事件
    def open_help_event(self):
        _select_list = self.get_select_row_list() 
        _hda_list = self.get_hda_data()
        for i in _select_list:
            if len(_hda_list[i][3]) !=0:
                _hda_name = _hda_list[i][4]
                if "::" in _hda_name:
                    _name_list=_hda_name.split("::")
                    _hda_name = _name_list[0]+"--"+_name_list[1]+"-"+_name_list[-1]
                else:
                    _hda_name=_hda_name
                _import_hda_level = _hda_list[i][6]
                _import_hda_level_lower=_import_hda_level.lower()
                _dir = "http://127.0.0.1:48626/nodes/"
                _web_path = os.path.join(_dir,_import_hda_level_lower,_hda_name)
                webbrowser.open(_web_path)
            else:
                print("%s没有对应的帮助文档\n" % _hda_list[i][1])

    # 在资源管理器中显示
    def open_resource_directory_event(self):
        _assest_lib_list = self.get_hda_path_list()
        _current_tab = self.cb.currentText()
        for j in _assest_lib_list:
            if _current_tab in j:
                _dir= j
        _dir =_dir.replace("/","\\")
        #os.system("explorer %s" %(dir))
        #old
        os.startfile(_dir)

    # 获取资产库路径列表
    def get_hda_path_list(self):
        _assest_lib_list = hou.getenv('HOUDINI_PATH').split(";")
        _assest_lib_list.pop(-1)
        return _assest_lib_list
    # 获得hda数据
    # 数据格式：hda路径，hdaLabel名称，TAB名称，help,命名空间，icon,层级
    # 去除帮助hda 多版本只获取最新版本 有问题的定义清除
    def get_hda_data(self):
        _current_tab = self.cb.currentText()
        _hda_list=hou.hda.loadedFiles()
        _hda_data =[]
        for j in _hda_list:
            # 全列表循环
            if _current_tab in j:
                # 筛选出当前标签的列表
                _hda_file_list = hou.hda.definitionsInFile(j)
                _version_definition_dict = {}
                for y in _hda_file_list:
                    # 逐文件筛选定义
                    try:
                        # 剔除存在问题的定义
                        y.sections()
                    except:
                        # 存在问题进行标注
                        _path = j
                        _label_name = j
                        _tab_submenu = " "
                        _help = "此资产存在问题:ObjectWasDeleted: Attempt to access an object that no longer exists in Houdini."
                        _hda_name_space = " "
                        _icon = "NETVIEW_error_badge"
                        _level = "None"
                        _list_data = [_path,_label_name,_tab_submenu,_help,_hda_name_space,_icon,_level]
                    else:
                        if 'EXAMPLE_FOR' in y.sections():
                        #if y.sections().has_key('EXAMPLE_FOR'): py2.7
                            # 剔除是帮助的定义
                            pass
                        else:
                            _name_space = y.nodeType().name()
                            if "::" in _name_space:
                                # 筛选具有版本信息的定义
                                _version_num=_name_space.split("::")[-1]
                                _name_spaces=_name_space[:-len(_version_num)]
                                if _name_spaces in _version_definition_dict:
                                #if _version_definition_dict.has_key(_name_spaces): py 2.7
                                    if _version_definition_dict[_name_spaces]>_version_num:
                                        pass
                                    else:
                                        _version_definition_dict[_name_spaces]=_version_num
                                else:
                                    _version_definition_dict[_name_spaces] = _version_num 
                                continue
                            else:
                                # 筛选非以上条件的定义
                                _path = j
                                _label_name = y.description()
                                _help = y.sections()["Help"].contents()
                                _tab_submenu = self.get_tab_submenu(y)
                                _hda_name_space = y.nodeTypeName()
                                _icon = y.icon()
                                _level = y.nodeTypeCategory().name()
                                _list_data = [_path,_label_name,_tab_submenu,_help,_hda_name_space,_icon,_level]
                    _hda_data.append(_list_data)
                # 比较多版本的资产信息 筛选出最新版本
                # 目前比较卡顿
                if len(_version_definition_dict)==0:
                    pass
                else:
                    for k,v in _version_definition_dict.items():
                        i=k+v
                        for _each in dir(hou):
                            if "NodeType" in _each:
                                try:
                                    _node_type="hou.%s().nodeTypes()" % _each
                                    _version_hda_data = eval(_node_type)[i]
                                except:
                                    continue
                        _version_hda = _version_hda_data.definition()
                        _path = j
                        _label_name =_version_hda.description()
                        _tab_submenu = self.get_tab_submenu(_version_hda)
                        _help = _version_hda.sections()["Help"].contents()
                        _hda_name_space = _version_hda.nodeTypeName()
                        _icon = _version_hda.icon()
                        _level = _version_hda.nodeTypeCategory().name()
                        _list_data = [_path,_label_name,_tab_submenu,_help,_hda_name_space,_icon,_level]
                        _hda_data.append(_list_data)  
            else:
                pass
        return _hda_data
    # 获得标签数据
    def get_cb_data(self):
        _assest_lib_list = self.get_hda_path_list()
        _cb_list =[]
        _iter = 0
        for l in _assest_lib_list:
            _cb_Item = l.split("/")[-1]
            _cb_list.append(_cb_Item)
            if "GsLib" in _cb_Item:
                _iter_num = _iter
            else:
                pass
            _iter+=1
        self.cb.addItems(_cb_list)
        self.cb.setCurrentIndex(_iter_num) 
    #添加数据到表格
    def add_data(self):
    #添加数据 
        _iter=0
        for z in self.get_hda_data():
            _row_num = self.table.rowCount()
            self.table.setRowCount(_row_num + 1)  
            #print z[1]
            try:
                hou.qt.createIcon(z[5])
            except:
                _icon = hou.qt.createIcon("NETVIEW_warning_badge")
            else:
                _icon= hou.qt.createIcon(z[5])
            #_icon= hou.qt.createIcon("SOP_subnet", 64, 64)
            _new_item=QTableWidgetItem(_icon,z[1])
            self.table.setItem(_iter,0,_new_item)
            _new_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            _new_item=QTableWidgetItem(z[2])
            self.table.setItem(_iter,1,_new_item)   
            _new_item=QTableWidgetItem(z[3])
            self.table.setItem(_iter,2,_new_item)
            _iter+=1
    # 初始化表格      
    def init_table(self):  
        self.table.clearContents() 
        self.table.setRowCount(0)
    # 刷新表格      
    def refresh_table(self):
        self.table.blockSignals(1)
        self.init_table()
        self.add_data()
        self.filter_event()
        self.table.blockSignals(0)
    # 获取发生修改的表格行索引列表 
    def get_table_change_list(self):
        _table_change_list=[]
        _row_count = self.table.rowCount()
        for i in range(_row_count):
            if self.table.item(i,1).textColor().rgb() == 4294901760 or self.table.item(i,2).textColor().rgb() == 4294901760:
                _table_change_list.append(i)
            else:
                pass
        return _table_change_list
    # 获得改变的表格列表
    def get_change_items_list(self):
        _change_items_list = []
        _row_count = self.table.rowCount()
        for i in range(_row_count):
            if self.table.item(i,1).textColor().rgb() == 4294901760:
                _item = [i,1]
                _change_items_list.append(_item)
            else:
                pass

            if self.table.item(i,2).textColor().rgb() == 4294901760:
                _item = [i,2]
                _change_items_list.append(_item)
            else:
                pass
        return _change_items_list
    #获得hda文件的修改内容字典
    def get_hda_modify_dict(self):
        _all_hda_list = self.get_hda_data()
        _index_list = self.get_table_change_list()
        _hda_modify_dict = []
        for i in _index_list:
            _path = _all_hda_list[i][0]
            _tab_submenu = self.table.item(i,1).text()
            _help = self.table.item(i,2).text()
            _hda_name_space = _all_hda_list[i][4]
            _list = [_path,_tab_submenu,_help,_hda_name_space]
            _hda_modify_dict.append(_list)
        return _hda_modify_dict 
    # 保存修改   
    def save_changes(self):
        _save_changes_list = self.get_hda_modify_dict()
        #删除，减少，增加，修改，
        for i in _save_changes_list:
            _hda_definition_list = hou.hda.definitionsInFile(i[0]) 
            for k in _hda_definition_list:
                if k.nodeTypeName() == i[3]:
                    self.back_up_hda_file(i[0])
                    _tab_submenu_data=k.sections()["Tools.shelf"].contents()
                    _xml_data = xml.dom.minidom.parseString(_tab_submenu_data)
                    _tab_submenu = _xml_data.documentElement.getElementsByTagName('toolSubmenu')[0].firstChild.data
                    _modify_tab_submenu = i[1]
                    if len(_modify_tab_submenu)==0:
                        _modify_tab_submenu="Digital Assets"
                    else:
                        _modify_tab_submenu = _modify_tab_submenu
                    _help = i[2]
                    _tab_submenu_data = _tab_submenu_data.replace("<toolSubmenu>"+_tab_submenu+"</toolSubmenu>","<toolSubmenu>"+_modify_tab_submenu+"</toolSubmenu>")
                    k.sections()["Tools.shelf"].setContents(_tab_submenu_data)
                    k.sections()["Help"].setContents(_help)
        self.refresh_table()
    # 获得选择的行索引列表
    def get_select_row_list(self):
        _Item_list = self.table.selectedItems()
        _select_row_list = []
        for i in _Item_list:
            _select_row_list.append(i.row())
        _select_row_list = list(set(_select_row_list))
        _select_row_list.sort()
        return _select_row_list
    #过滤选择的行索引列表
    def filter_select_row_list(self):
        _select_list =self.get_select_row_list()
        _change_list =self.get_table_change_list()
        _select_change_list = [item for item in _select_list if item in set(_change_list)]
        return _select_change_list
    #  获得选择的单元格列表
    def get_select_items_list(self):
        _Item_list = self.table.selectedItems()
        _select_row_list = []
        for i in _Item_list:
            _Item=[i.row(),i.column()]
            _select_row_list.append(_Item)
        _select_row_list.sort()
        return _select_row_list
    # 过滤选择的单元格列表
    def filter_select_items_list(self):
        _select_items_list =self.get_select_items_list()
        _change_items_list =self.get_change_items_list()
        _select_change_items_list = []
        for i in _select_items_list:
            if i in _change_items_list:
                _select_change_items_list.append(i)
        return _select_change_items_list
    # 获得选择的变化的单元格数据
    def get_select_change_items_hda_data(self):
        _index_list = self.filter_select_items_list()
        _all_hda_list = self.get_hda_data()
        _items_hda_data = []
        for i in _index_list:
            _index = i[0]
            _index_y = i[1]+1
            _data = _all_hda_list[_index][_index_y]
            _items_hda_data.append(_data)
        return _items_hda_data
    # 刷新选择的单元格
    def refresh_select_items(self):
        self.table.blockSignals(1)
        _select_items_list = self.get_select_change_items_hda_data()
        _index_list = self.filter_select_items_list()
        _iter=0
        for i in _index_list:
            _refresh_Item = QTableWidgetItem(_select_items_list[_iter])
            self.table.setItem(i[0],i[1],_refresh_Item)
            _iter+=1
        self.table.blockSignals(0)
    # 保存选择的单元格
    def save_select_items(self):
        self.table.blockSignals(1)
        _index_list = self.filter_select_items_list()
        _all_hda_list = self.get_hda_data()
        for i in _index_list:
            _index = i[0]
            _index_y = i[1]
            _file_path = _all_hda_list[_index][0]
            _hda_definition_list = hou.hda.definitionsInFile(_file_path) 
            for k in _hda_definition_list:
                if k.nodeTypeName() == _all_hda_list[_index][4]:
                    self.back_up_hda_file(_file_path)
                    _tab_submenu_data=k.sections()["Tools.shelf"].contents()
                    _xml_data = xml.dom.minidom.parseString(_tab_submenu_data)
                    _tab_submenu = _xml_data.documentElement.getElementsByTagName('toolSubmenu')[0].firstChild.data
                    if _index_y == 1:
                        _modify_tab_submenu = self.table.item(_index,_index_y).text()
                        if len(_modify_tab_submenu)==0:
                            _modify_tab_submenu="Digital Assets"
                        else:
                            _modify_tab_submenu = _modify_tab_submenu
                        _tab_submenu_data = _tab_submenu_data.replace("<toolSubmenu>"+_tab_submenu+"</toolSubmenu>","<toolSubmenu>"+_modify_tab_submenu+"</toolSubmenu>")
                        k.sections()["Tools.shelf"].setContents(_tab_submenu_data)
                    elif _index_y == 2:
                        _help = self.table.item(_index,_index_y).text()           
                        k.sections()["Help"].setContents(_help)
                    self.table.item(_index,_index_y).setTextColor(QColor(255,255,255))
                    
        self.table.blockSignals(0)
    # 设置全部单元的显示与隐藏
    def set_disable_all_items(self,_dis):
        _row_count = self.table.rowCount()
        for k in range(_row_count):
            self.table.setRowHidden(k,_dis)
    # 设置给定列表的显示与隐藏
    def set_disable_items_by_list(self,_items_list,_dis):
        for i in _items_list:
            self.table.setRowHidden(k,_dis)
    # 保存备份功能，当确定修改后，将修改的hda文件在backup 中复制一份 后缀使用日期   
    # 似乎官方有这个功能了
    def back_up_hda_file(self,_file_path):
        _hda_file_name = _file_path.split("/")[-1]
        _folder = "backup"
        _file_dir = os.path.join(_file_path[:-len(_hda_file_name)],_folder)
        _hda_name = _hda_file_name.split(".")[0]
        _bak_time = time.strftime('_%Y_%m_%d_%H_%M',time.localtime(time.time()))
        _bak_name = "_bak"+_bak_time
        _hda_type_name = "."+_hda_file_name.split(".")[-1]
        _bak_hda_name = _hda_name+_bak_name+_hda_type_name
        _new_file = os.path.join(_file_dir,_bak_hda_name)
        _new_file = _new_file.replace("\\","/")
        if os.path.exists(_file_dir):
            pass
        else:
            os.mkdir(_file_dir)
        shutil.copy(_file_path,_new_file)
    # 获得hda的tab列表标签
    def get_tab_submenu(self,_definition):
        _tab_submenu_data=_definition.sections()["Tools.shelf"].contents()
        _xml_data = xml.dom.minidom.parseString(_tab_submenu_data) 
        _tool_submenu_num= len(_xml_data.documentElement.getElementsByTagName('toolSubmenu'))
        if _tool_submenu_num !=0:
            _tab_submenu= ""
            for i in range(_tool_submenu_num):
                _tab= _xml_data.documentElement.getElementsByTagName('toolSubmenu')[i].firstChild.data
                if i >0:
                    _tab_submenu+=";"+_tab
                else:
                    _tab_submenu+=_tab
        else:
            _tab_submenu= ""
        
        return _tab_submenu

