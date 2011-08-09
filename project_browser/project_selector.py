#Copyright 2011 Mark Reid <mindmark@gmail.com>

#This file is part of Project Browser.

#Project Browser is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Project Browser is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Project Browser.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *

import project_search

import traceback

import projects

import busy_indicator
import gui_utilities

import time
from pprint import pprint

        
class Background_Model_Thread(QThread):
    def __init__(self,parent=None):
        
        super(Background_Model_Thread, self).__init__(parent)
        self.current_item = None
        self.work = []
        
    def set_stop(self):
        self.current_item.stop = True
        
    def clear(self):
        work_items = [] 
        while self.work:
            item = self.work.pop()
            self.clean_item(item)
            work_items.append(item)
        if self.current_item:
            self.current_item.stop = True
            
        return work_items
    
    def add_work(self,item):
        self.work.append(item)
        
    def run(self):
        
        while self.work:
            item =self.work.pop(0)
            self.current_item = item
            
            try:
                #time.sleep(2)
                if isinstance(self.current_item, projects.Project_Item):
                    self.current_item.load_children()
                    
                elif isinstance(self.current_item, project_search.Path_Finder):
                    print 'getting nearest item'
                    self.current_item.get_nearest_item()
                
                if item.stop:
                    self.work_stoped(self.current_item)
                    
                else:
                    self.work_done(self.current_item)
                    
            except:
                trace = traceback.format_exc()
                self.work_error(trace, item)
                
        self.current_item = None
        
    def clean_item(self,item):
        if isinstance(item, projects.Project_Item):
            item.loading=False
            item.loaded = False
            
            del item.children[:]
                    
    def work_error(self,trace,item):
        self.clean_item(item)
        self.emit(SIGNAL("work_error"),trace,item)
                    
    def work_stoped(self,item):
        self.clean_item(item)
        self.emit(SIGNAL("work_stoped"),item)
        
    def work_done(self,item):
        print 'work done'
        self.emit(SIGNAL("work_done"),item)
        

class Project_Model(QAbstractItemModel):
    def __init__(self, parent=None):
        super(Project_Model, self).__init__(parent)
        
        root_properties = {'name':'Name','type':'Type'}
        self.root_item = projects.Project_Item(properties=root_properties)
        
        self.history = []
        self.history_index = 0
        
        self.background_thread = Background_Model_Thread()
        
        self.connect(self.background_thread, SIGNAL('work_done'),self.work_done)
        self.connect(self.background_thread, SIGNAL('work_stoped'),self.work_stoped)
        self.connect(self.background_thread, SIGNAL('work_error'),self.work_error)
        
           
        self.default_icon = QIcon.fromTheme('folder')
        
        pixmaps = busy_indicator.get_indicator_pixmaps(20,20)
        
        self.busy_pixmaps = []
        
        for item in pixmaps:
            self.busy_pixmaps.append(QIcon(item))
        self.busy_index = 0
        self.busy_delay = 150
        
        self.loading_pixmap = self.busy_pixmaps[self.busy_index]
        
        self.timer_id = None

        self.setup_model()
        
        self.startAnimation()
        
        self.selected_item = None
        
        
    def startAnimation(self):
        
        if not self.timer_id:
            self.timer_id = self.startTimer(self.busy_delay)
            
        
    def stopAnimation(self):
        
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None
            self.emit(SIGNAL('loaded_data'))
        
    def timerEvent(self,event):
        
        self.loading_pixmap = self.busy_pixmaps[self.busy_index]
        self.busy_index = (self.busy_index + 1 ) % len(self.busy_pixmaps)
        
        if self.selected_item:
            if isinstance(self.selected_item,projects.Project_Item):
                self.update_item_view(self.selected_item)
            

        
    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.root_item.columnCount()
        
    def get_icon(self,path):
        
        if os.path.exists(path):
            return QIcon(path)
        
        #else:
        return QIcon.fromTheme(path)

    

    def data(self, index, role):
        if not index.isValid():

            v = QVariant()
            v.clear()
            return v
        
        if role == Qt.DecorationRole:
            #print 'icon'
            item = index.internalPointer()
            
            #item_data = item.data(index.column())
            
            
            if item.loading:
                return self.loading_pixmap
            
            if item.properties['icon']:
                
                return self.get_icon(item.properties['icon'])
            
            else:
                return self.default_icon
            #v = QVariant()
            #v.clear()
            #return v

        if role != Qt.DisplayRole:
            
            
            #print role
            
            v = QVariant()
            v.clear()
            return v

        item = index.internalPointer()
        
        item_data = item.data(index.column())
        
        if item_data:
            return QVariant(item_data)
        
        
        return item_data

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root_item.data(section)

        return None
        

    def index(self, row, column, parent):
    
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()
        
    def hasChildren(self,parent):
        item_data = parent.internalPointer()
        #print 'checking for children',parent,item_data
        
 
        if not item_data:
            return True
        
        if not item_data.canLoadChildren():
            return False
        #if item_data.properties['']
        
        if item_data.loaded:
            
            if not item_data.children:
                return False
            
        
    
        return True

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
            
        if parent_item.loading:
            
            return 0
        if not parent_item.loaded:
            #self.add_work(parent_item)
            return 0
 
        childcount = parent_item.childCount()
        return childcount

    
    def load_index(self,index):
        """loads a index if it needs to be loaded, sends it to add_work"""
        
        item = index.internalPointer()
        
        if item.loading:
            pass
        elif not item.loaded:
            if item.canLoadChildren():
                self.add_work(item)
                
            else:
                item.loaded = True
                self.update_item_view(item)
                
        else:
            pass
        
        self.add_to_history(index)
        
    def reload_index(self,index):
        item = index.internalPointer()
        if item.loading:
            pass
        
        else:
            del item.children[:]
            item.loaded = False
            
            self.add_work(item)
            self.update_item_view(item)
            #self.emit(SIGNAL('index_updated'),item)
            
        
        pass
            
    def add_to_history(self,index):
        
        if self.history:
            index_data = index.internalPointer()
            last_index = self.history[self.history_index]
            
            if index == last_index:
                #print 'repeat'
                self.print_history()
                return None
        
        
        if self.history_index + 1 < len(self.history):
            del self.history[self.history_index + 1:]
        #print index
        self.history.append(index)
        self.history_index = len(self.history)-1
        
        #self.print_history()
        
        
        
    def print_history(self):
        print '****'
        for i,item in enumerate(self.history):
            data = item.internalPointer()
            if i == self.history_index:
                l = '*'
            else:
                l = ' '
            print l,i,data
            
        print '****'
        
        
        #print 'click'
    
    
    def add_work(self,item):
        cleared_items = self.background_thread.clear()
        
        print 'adding', item
        
        if isinstance(item,projects.Project_Item):
            item.loading = True
            
        self.background_thread.add_work(item)
        
        if not self.background_thread.isRunning():
            print 'starting thread'
            
            self.background_thread.start()

        
        self.startAnimation()
        self.selected_item = item
        self.emit(SIGNAL('loading_data'))
        
        for cleared_item in cleared_items:
            if isinstance(item,projects.Project_Item):
                self.update_item_view(cleared_item)
        #item.load_children()
        
    def work_done(self,work):
        print '***loaded',work
        if isinstance(work,projects.Project_Item):
            self.update_item_view(work)
            
        elif isinstance(work,project_search.Path_Finder):
            self.path_search_ready(work)
            
            
        if work == self.selected_item:
            self.selected_item = None
            
            self.stopAnimation()
        
        
    def work_error(self,traceback,item):
        print 'error'
        print traceback
        
        if item == self.selected_item:
            self.selected_item = None
            self.stopAnimation()
        
        if isinstance(item,projects.Project_Item):
            self.update_item_view(item)
            
    def work_stoped(self,item):
        print 'stoped'
        if item == self.selected_item:
            self.selected_item = None
            self.stopAnimation()
            
        if isinstance(item,projects.Project_Item):
            self.update_item_view(item)
            
    def update_item_view(self,item):
        """send a dataChanged signal to the view"""
        index_start = self.createIndex(item.row(), 0, item)
        index_end = self.createIndex(item.row(), item.columnCount(), item)
        
        self._dataChange(index_start, index_end)
        #if reload_selected:
            #self.emit(SIGNAL('index_updated'),item)
            
    def _dataChange(self,index_start,index_end):
        self.emit(SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'), index_start, index_end)
        
    
    def setup_model(self):
        
        self.root_item.loaded = True
        project_list = projects.get_projects()
        for p in project_list:
            self.root_item.addChild(p)
            
    def path_search_ready(self,item):
        
        item_data = item.nearest_item
        
        if not item_data:
            return
        
        index_path = item_data.get_index_path()
        index = self.createIndex(0, 0, self.root_item)
        
        print index_path
        
        for p in index_path[1:]:
            print p
            index =  index.child(p['row'],0)
            
        print 'path_search_ready'
        self.emit(SIGNAL("path_search_ready"),index)
        #return index
        
    def path_search(self,path):
        f = project_search.Path_Finder(path,self.root_item)
        self.add_work(f)
        


class Project_Item_Delegate(QStyledItemDelegate):
    
    def __init__(self,parent=None):
        super(Project_Item_Delegate,self).__init__(parent)
        
        
class Project_QListView(QListView):
    
    def scrollto(self,index,hint=QAbstractItemView.EnsureVisible):
        print 'scroll to'
        QListView.scrollTo(self,index,hint)
        
        #self.setFocus()
        
    
    def scrollContentsBy(self,dx,dy):
        
        #print '%%%', dx,dy
        
        QListView.scrollContentsBy(self,dx,dy)
        
        
class Project_ColumnView(QColumnView):
    def __init__(self,parent=None):
        super(Project_ColumnView,self).__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        #self.setAutoScroll(False)
        
        #print self.
        #self.setAutoScrollMargin(False)
        self.columnWidths_store = None
        
        self.columns_list = []
        
        #self.crea
        
    def setModel(self,model):
        QColumnView.setModel(self,model)
        self.connect(model, SIGNAL("path_search_ready"),self.path_search_ready)
     
    def set_navigator(self,navigator):
        
        self.connect(navigator,SIGNAL("go_back"),self.go_back)
        self.connect(navigator,SIGNAL("go_forward"),self.go_forward)
        self.connect(navigator,SIGNAL("go_up"),self.go_up)
        self.connect(navigator,SIGNAL("go_home"),self.go_home)
        
        self.connect(navigator,SIGNAL("refresh"),self.refresh)
        self.connect(navigator, SIGNAL("set_path"),self.set_path)
        
        model = self.model()
        self.connect(model,SIGNAL("loading_data"),navigator.start_animation)
        self.connect(model,SIGNAL("loaded_data"),navigator.stop_animation)
        
        
    def select_index(self,index):
        self.go_home()
        self.setCurrentIndex(index)
        self.scrollTo(index)
        self.update_size()
        
    def clean_column_list(self):
        """remove columns that have been delete by pyqt"""
        
        #clean_list  = []
        deleted_columns = []
        
        for item in self.columns_list:
            try:
                offset = item.horizontalOffset()
                #clean_list.append(item)
       
                
            except:
                
                deleted_columns.append(item)
                #print traceback.format_exc()
                pass
        for item in deleted_columns:
            self.columns_list.remove(item)
            
    def scrollTo(self,index,hint= QAbstractItemView.EnsureVisible):
        
        QColumnView.scrollTo(self,index,hint)

        parent = index.parent()
        self.clean_column_list()
        
        if parent.isValid():
            
            for item in self.columns_list:
                if item.rootIndex() == parent:
                    item.setCurrentIndex(index) #make sure that index is selected
                    #item.scrollTo( )
        

    def check_columns_pos(self):
        
        """this nasty hack fixes columns that are improperly layout, it runs before a repaint event"""
            
        self.clean_column_list()
        levels = self.levels_check()
        
        if levels:
            xpos = 0 
            for i,item in enumerate(self.columnWidths()):
                if i < len(self.columns_list):
                    list_item = self.columns_list[i]
                    
                    list_item_pos = list_item.pos()
                    list_item_xpos = list_item.pos().x()
                    list_item_ypos = list_item.pos().y()
                    correction =  xpos - list_item_xpos
                    
                    
                    #print list_item.currentIndex()
                    #print xpos,list_item_xpos,correction
                    
                    if correction < 0:
                        list_item.move(xpos,0)
                    
                    #list_item.resize(list_item.size())
    
                    xpos += item
                    
            
        
    def go_back(self):
        print 'back'
        model = self.model()
        
        if model.history_index:
            index = self.currentIndex()
            model.add_to_history(index)
            model.history_index -= 1
            
            index = model.history[model.history_index]
            
            
            model.print_history()
            self.select_index(index)

    def go_forward(self):
        print 'forward'
        model = self.model()
        
        if model.history_index < len(model.history)-1:
            model.history_index += 1
            
            index = model.history[model.history_index]
            
            model.print_history()
            self.select_index(index)
        
    def go_up(self):
        print 'up'
        
        current = self.currentIndex()
        parent = current.parent()
        
        if parent:
            self.select_index(parent)
        
    def go_home(self):
        print 'home'

        self.reset()
        self.emit(SIGNAL('reset'))
        
    def refresh(self):
        print 'refresh'
        
        self.model().reload_index(self.currentIndex())
        
    def set_path(self,path):
        
        self.model().path_search(path)
        
        #index = self.model().get_nearest_item(path)
        #if index:
            #self.select_index(index)
   
    def path_search_ready(self,index):
        self.select_index(index)
   
    def dataChanged(self,topLeft,topRight):

        QColumnView.dataChanged(self,topLeft,topRight)
            
        if self.load_check(topLeft):
            if topLeft == self.currentIndex():
                self.index_ready(topLeft)
            
        
    
    def createColumn(self,index):
        """overloaded default createColumn to have control over the listViews"""
        
        view = Project_QListView(self.viewport())
        
        self.initializeColumn(view)
        
        view.setRootIndex(index)
        
        self.columns_list.append( view)
        
        

        return view

    def currentChanged(self,current,previous):

        self.update_size()
        
        QColumnView.currentChanged(self,current,previous)
        
        self.index_changed(current, previous)
        if self.load_check(current):
            self.index_ready(current)
            
        else:
            model = self.model()
            model.load_index(current) #load current index if it's not loaded
    
    
    def index_changed(self,current,previous):
        
        self.emit(SIGNAL('index_changed'),current,previous)
        
        
    def index_ready(self,index):
        self.emit(SIGNAL('index_ready'),index)
        #print 'index selected'
        
    def load_check(self,index):
        item_data = index.internalPointer()
        
        if item_data:
            if item_data.loaded:
                return True
            
        return False
        
    def scroll_check(self,dx):
        
        if self.horizontalOffset() + dx  > 0:
            #print 'fixing offset'
            dx =   -self.horizontalOffset()
            
        return dx
        
    def levels_check(self):
        current = self.currentIndex()
        

        current_item = current.internalPointer()
        
        try:
            if current_item:
                if current_item.properties['levels']:
                    #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    #self.setResizeGripsVisible(False)
                    return current_item.properties['levels']
                
            #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            #self.setResizeGripsVisible(True)
            
        except:
            pass
        return False
    
    
    def scrollContentsBy(self,dx,dy):
 
        if self.levels_check():
            QColumnView.scrollContentsBy(self,0,dy) # disable scrolling on levels mode

        else:
            
            QColumnView.scrollContentsBy(self,self.scroll_check(dx),dy)
            
    def resizeEvent(self,event):
        #if self.levels_check():
        #if self.
            
        self.auto_size()
        QColumnView.resizeEvent(self,event)
        
        
        #self.viewport().update()
        
    def paintEvent(self,event):
        #self.auto_size()
        self.check_columns_pos()
        QColumnView.paintEvent(self,event)
 
    def fit_columns(self):
        
        
        levels = self.levels_check()
        
        QColumnView.scrollContentsBy(self,-self.horizontalOffset(),0)
        width = self.width()
        split = width/float(levels)
        columns = []
        
        for i in range(levels):
            columns.append(int(split))
            
            
        columns[-1] = columns[-1] -2 
        self.setColumnWidths(columns)
        
    def update_size(self):
        
        viewport = self.viewport()
        size = self.size()
        viewport.resize(size) 
        
        viewport.repaint()
        #viewport.update()
        self.setFocus() #if the widgets not in focus it doesn't show selections on some occasions
        
    def auto_size(self):
        
        if self.levels_check():
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setResizeGripsVisible(False)
            
            self.columnWidths_store = self.columnWidths()
            self.fit_columns()
            
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setResizeGripsVisible(True)

class Combo_Button(QPushButton):
    def __init__(self, parent=None):
        super(Combo_Button,self).__init__(parent)
        self.last_mouse_pos = None

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()
        QPushButton.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = event.pos()
        QPushButton.mouseReleaseEvent(self, event)

    def get_last_pos(self):
        if self.last_mouse_pos:
            return self.mapToGlobal(self.last_mouse_pos)
        else:
            return None
        
        
        
class Project_Navigator_Widget(QWidget):
    
    def __init__(self,parent=None):
        super(Project_Navigator_Widget,self).__init__(parent)
        
        self.homeButton  = QPushButton()
        self.upButton = QPushButton()
        self.backButton = QPushButton()
        self.forwardButton = QPushButton()
        
        
        self.path = busy_indicator.Busy_QEdit()
        
        
        self.refreshButton = QPushButton()
        self.browseButton = QPushButton()
        
        self.menuButton = Combo_Button()
        
        homeIcon = QIcon.fromTheme('go-home')
        upIcon = QIcon.fromTheme('go-up')
        backIcon =  QIcon.fromTheme('go-previous')
        fowardIcon =  QIcon.fromTheme('go-next')
        
        refreshIcon = QIcon.fromTheme('reload')
        browseIcon = QIcon.fromTheme('folder-open')
        
        menuIcon  =QIcon.fromTheme('preferences-system')
        
        self.homeButton.setIcon(homeIcon)
        self.upButton.setIcon(upIcon)
        self.backButton.setIcon(backIcon)
        self.forwardButton.setIcon(fowardIcon)
        
        self.refreshButton.setIcon(refreshIcon)
        self.browseButton.setIcon(browseIcon)
        self.menuButton.setIcon(menuIcon)
        
        
        #self.loadingIcon.setIc
        
        ButtonSize = QSize(32,32)
        IconSize = QSize(28,28)
        for item in [self.homeButton,self.upButton,self.backButton,self.forwardButton, self.refreshButton,self.browseButton,self.menuButton]:
            item.setFixedSize(ButtonSize)
            item.setIconSize(IconSize)
            
        self.path.setFixedHeight(IconSize.height())
        
        self.connect(self.homeButton, SIGNAL("clicked ()"),self.go_home)
        self.connect(self.upButton, SIGNAL("clicked ()"),self.go_up)
        self.connect(self.backButton, SIGNAL("clicked ()"),self.go_back)
        self.connect(self.forwardButton, SIGNAL("clicked ()"),self.go_forward)
        
        self.connect(self.refreshButton, SIGNAL("clicked ()"),self.refresh)
        self.connect(self.browseButton, SIGNAL("clicked ()"),self.browse)
        
        self.connect(self.menuButton, SIGNAL("clicked ()"),self.popup_menu)
        
        
        self.connect(self.path, SIGNAL("returnPressed ()"),self._set_path)

        layout = QHBoxLayout()
        layout.setMargin(5)
        
        #layout.setSpacing(0)
        layout.addWidget(self.homeButton)
        layout.addWidget(self.upButton)
        layout.addWidget(self.backButton)
        layout.addWidget(self.forwardButton)
        layout.addWidget(self.path)
        #
        layout.addSpacing(10)
        #layout.addWidget(self.loadingIcon)
        layout.addWidget(self.refreshButton)
        layout.addWidget(self.browseButton)
        #layout.addWidget(self.menuButton)
        
        
        layout.setAlignment(Qt.AlignTop)
        #layout.setStretch(0,0)
        
        #layout.add
        #self.loadingIcon.startAnimation()
        self.setLayout(layout)
        #popup.addAction(icon,'Get From Nuke')
        #popup.addAction(icon,'Get From Maya')
        #popup.addAction(icon,'Get From Shake')
        #popup.addSeparator()
        self.menu_items = [('emblem-symbolic-link','Get From Nuke'),
                           ('emblem-symbolic-link','Get From Shake'),
                           ('emblem-symbolic-link','Get From Maya'),
                           (None,None),
                           ('exit','Quit')]
        
    def browse(self):
        
        current_path = str(self.path.text())
        file_list = gui_utilities.file_directory_dialog(default_dir=current_path)
        print file_list
        if file_list:
            self.set_path(file_list[0], send_update=True)
        
    def start_animation(self):
        self.path.startAnimation()
        
    def stop_animation(self):
        self.path.stopAnimation()
        
    def go_back(self):
        self.emit(SIGNAL("go_back"))

    def go_forward(self):
        self.emit(SIGNAL("go_forward"))
    def go_up(self):
        self.emit(SIGNAL("go_up"))
    def go_home(self):
        self.emit(SIGNAL("go_home"))
        
        self.clear()
        
    def refresh(self):
        
        self.emit(SIGNAL("refresh"))
        #self.path.startAnimation()
        #self.loadingIcon.startAnimation()
    
        
    def set_path(self,path,send_update=False):
        #print QUrl().fromLocalFile(path)
        
        if os.path.isfile(path):
            path = os.path.dirname(path)
            
        self.path.setText(path)
        
        if send_update:
            self._set_path()
        
    def _set_path(self):
        
        path = self.path.text()
        self.emit(SIGNAL('set_path'),str(path))
        
    def clear(self):
        self.set_path('')
        
    def popup_menu(self):
        
        popup = QMenu()
        icon  = QIcon.fromTheme('emblem-symbolic-link')
        
        
        for icon,actionName in self.menu_items:
            
            if icon and actionName:
                popup.addAction(QIcon.fromTheme(icon),actionName)
                
            else:
                popup.addSeparator()
                
        #popup.addAction(icon,'Get From Nuke')
        #popup.addAction(icon,'Get From Maya')
        #popup.addAction(icon,'Get From Shake')
        #popup.addSeparator()
        #popup.addAction(icon,'Show in Finder')
        
        #popup.addSeparator()
        #quit  = popup.addAction(QIcon.fromTheme('exit'),'Quit')
        
        
        
        popup.exec_(self.menuButton.get_last_pos())
        #popuop
        
        #self.setFixedSize(QSize(32*4 + 10,32))
    
        
class Project_Selector(QWidget):
    
    def __init__(self,parent=None):
        super(Project_Selector,self).__init__(parent)
        
        #self.path_label = QLabel()
        
        self.view = Project_ColumnView()

        self.navigation = Project_Navigator_Widget()
        
        layout = QVBoxLayout()
        topLayout = QHBoxLayout()
        self.viewLayout = QHBoxLayout()
        
        topLayout.addWidget(self.navigation)
        #topLayout.addWidget(self.path_label)
        
        #topLayout.setAlignment(Qt.AlignLeft)
        
        self.viewLayout.addWidget(self.view)
        
        layout.addLayout(topLayout)
        layout.addLayout(self.viewLayout)
        
        layout.setMargin(0)
        
        self.setLayout(layout)
        
        model = Project_Model()
        #self.connect(self.view,SIGNAL("activated (const QModelIndex&)"),model.item_activated)
        
        self.view.setModel(model)
        
        self.view.set_navigator(self.navigation)
        self.connect(self.view, SIGNAL('index_changed'),self.clear_path_label)
        self.connect(self.view, SIGNAL("index_ready"),self.set_path_label)
        
        
        
    def get_selected_item(self):
        
        index = self.view.currentIndex()
        
        item_data = index.internalPointer()
        
        return item_data
        #self.setStyleSheet("QScrollBar:vertical{background-color:grey}")
        
    def clear_path_label(self,item,prevous):
        self.navigation.set_path("")
    
    def set_path_label(self,item):
        
        project_item = item.internalPointer()
        
        path = project_item.properties['path']
        
        if not path:
            path = ''
            
        self.navigation.set_path(path)
        
    def set_path(self,path):
        
        self.navigation.set_path(path,send_update=True)
        
    
def clean_QString(string):
    
    
    if isinstance(string, QString):
        
        return str(string)
    else:
        return string        
        
def clean_variant_data(data):
    
    if isinstance(data, dict):
        new_data = {}
        
        for key,value in data.items():
            
            new_key = clean_QString(key)
            
            if isinstance(value,list) or isinstance(value, dict):
                new_value = clean_variant_data(value)
                
            else:
                new_value = clean_QString(value)
                
            new_data[new_key] = new_value
            
        return new_data
        
    elif isinstance(data, list):
        new_data = []
        
        for value in data:
            if isinstance(value,list) or isinstance(value, dict):
                new_value = clean_variant_data(value)
                
            else:
                new_value = clean_QString(value)
                
            new_data.append(new_data)
            
        return new_data
            
        
    else:
        return data
    

class Mode_Data(object):
    
    def __init__(self,data):
        
        self._data = data
        
    def data(self):
        return self._data
        
        
        
class Project_Selector_Widget(Project_Selector):
    
    def __init__(self,parent=None):
        super(Project_Selector_Widget,self).__init__(parent)
        
        #self.project_selector = Project_Selector()
        
        self.content_modes = QListWidget()
        self.content_modes.setFixedWidth(150)
        self.last_item_name = None
        self.last_index_type = None
        
        self.viewLayout.addWidget(self.content_modes)
        
        
        self.connect(self.view, SIGNAL('index_changed'),self.index_changed)
        self.connect(self.view, SIGNAL('index_ready'),self.index_ready)
        
        self.connect(self.view,SIGNAL('reset'),self.clear)
        
        
        
        self.connect(self.content_modes, SIGNAL('currentItemChanged (QListWidgetItem *,QListWidgetItem *)'),self.content_mode_changed)
        
        
    def content_mode_changed(self,current,previous):
        

        if current:
            data_variant = current.data(Qt.UserRole)
            
            data = data_variant.toPyObject().data()

            index = self.view.currentIndex()
            
            if index:
                index_data = index.internalPointer()
                
                if index_data:
                    self.last_index_type = index_data.properties['type']
                    
                    new_data = dict(index_data.properties)
                    
                    if not new_data.has_key('children'):
                        
                    
                        new_data['children'] = []
                        
                    if not isinstance(new_data['children'], list):
                        new_data['children'] = []
                        
                    
                    for item in index_data.children:
                        
                        new_data['children'].append(dict(item.properties))
                        #new_data
                    
                    self.item_selected(new_data, data)
            
            
        
    def item_selected(self,index_data,content_mode):
        
        #print 'selected!'
        #pprint( [index_data,content_mode],)
    
        self.emit(SIGNAL("item_selected"),index_data,content_mode)
        
        
    def sizeHint(self):
        
        return QSize(700,200)
    
    
    def index_changed(self,current,previous):
        self.clear()
        
    def index_ready(self,index):
        
        #print '####',current
        self.clear()
        item_data = index.internalPointer()
        
        
        if item_data.properties['content_dirs']:
            self.set_content_dir_list(item_data.properties['content_dirs'])
        
        
    def set_content_dir_list(self,item_list):
        
        
        name_list = []
        
        default = []
        index = self.view.currentIndex()
        index_data = index.internalPointer()
        
        for item in item_list:
            
            item_name = item['name']
            
            list_item = QListWidgetItem(item_name,self.content_modes)
            #name_list.append(list_item)
            #print item
            if item.has_key('default'):
                if item['default']:
                    default = list_item
                    
            if item_name == self.last_item_name:
                if index_data.properties['type'] == self.last_index_type:
                    default = list_item
                    
            list_item.setIcon(QIcon.fromTheme('image'))
            list_item.setData(Qt.UserRole,QVariant(Mode_Data(item)))
            #if item.has_key('icon')
                
        #self.picker_list.addItems(name_list)
        if default:
            self.content_modes.scrollToItem(default)
            self.content_modes.setCurrentItem(default)
    
        
    def clear(self):
        self.emit(SIGNAL("clear"))
        
        
        current_item = self.content_modes.currentItem()
        
        if current_item:
            
            self.last_item_name = str(current_item.text())
            
        self.content_modes.clear()

        
