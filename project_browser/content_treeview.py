#Copyright (C) 2011 Mark Reid <mindmark@gmail.com>

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

import traceback
import content_finder
import content_types

import utilities
import tool_actions
from gui_utilities import draw_with_shadow,fit_font
from progress_overlay import Progress_Overlay_Painter

from information_finder import Information_Finder_Manager

class Content_Model(QAbstractItemModel):
    def __init__(self, parent=None):
        super(Content_Model, self).__init__(parent)
        self.root_item= content_finder.create_model_root()
        
        self.default_icon = QIcon.fromTheme('image')
        
        self.rejected= []
        
        self.rejected_timer = False
        
        self.requested_data = []
        self.data_change_queue = []
        
        self.current_item = None
    
    def set_model_data(self,model_data):
        self.root_item = model_data
        
    def startAnimation(self):
        
        if not self.timer_id:
            self.timer_id = self.startTimer(self.busy_delay)
            
        
    def stopAnimation(self):
        
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None
        
    def timerEvent(self,event):
        pass
        #self.loading_pixmap = self.busy_pixmaps[self.busy_index]
        #self.busy_index = (self.busy_index + 1 ) % len(self.busy_pixmaps)
        
        #if self.selected_item:
    
            #self.update_item_view(self.selected_item)
                
    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.root_item.columnCount()
        
        
    def set_current_item(self,item):
        self.current_item = item
        
    def request_children_data_loaded(self,index):
        
        if index:
            item_data = index.internalPointer()
        else:
            item_data = self.root_item
        
        requests = []
        if not item_data:
            item_data = self.root_item
            
        for child in item_data.children:
            columns = []
            
            columns.extend(child.column_names)
            
            columns.insert(0,'Thumbnail')
            
            for key in columns:
                requests.append((child,key))
                    
        #if not self.requested_data:
           # QTimer.singleShot(50,self._data_request)
            
        #self.requested_data.extend(requests)
        
        requests.reverse()
        self._data_request(requests,priority=True)
        
    def priority_data_request(self,index,preview=False):
        
        if index:
            item_data = index.internalPointer()
        else:
            item_data = self.root_item
            
        columns = []
            
        columns.extend(item_data.column_names)
        columns.append('Thumbnail')
        
        requests = []
        
        for key in columns:
            if item_data.dataReady(key):
                pass
            else:
                requests.append((item_data,key))
        
        preview_keys = ['Preview_0','Preview_1','Preview_2','Preview_3']
        preview_keys.reverse()
        for key in preview_keys:
            requests.append((item_data,key))
        
        requests.reverse()
        #print 'sending priority request',requests
        self._data_request(requests,priority=True)

        
    def data_request(self,item,key):
        
        if item:
            #print 'requesting',item.properties['name'], key
            
            #item.data_queued.extend(keys)
            if not self.requested_data:
                #pass
                QTimer.singleShot(10,self._data_request)
                 
            
            
            if (item,key) in self.requested_data:
                pass
            else:
                self.requested_data.append((item,key))
            
            
            
            
    def _data_request(self,request=None,priority=False):
        
        if not request:
            request = self.requested_data
            
        
        self.emit(SIGNAL("data_request"),request,priority)
        
    def remove_data_request(self,index):
        item_data = index.internalPointer()
        
        removal_list =[]
        
        
        removal_list.extend( item_data.children)
         
        
        self.emit(SIGNAL("remove_data_request"),removal_list)

            
    
            
    def needsLoading(self,item,key):
        if item.dataReady(key):
            return False
        elif item.dataLoading(key):
            return False
        
        else:
            return True
           
           
    def data_failed(self,item,key):
        
        preview_keys = ['Preview_0','Preview_1','Preview_2','Preview_3']
        
        if key in preview_keys:
        
            if item == self.current_item:
                print 'Failed'
                index = preview_keys.index(key)
                self.emit(SIGNAL('preview_ready'),{'status':'failed','preview_index':index,'preview':None})
        
    def data_ready(self,item,key):
        #print '***',key,'loaded!'
        self.update_item_view_column(item,key)
        #self.update_item_view(item)

    def data(self, index, role):
        if not index.isValid():

            v = QVariant()
            v.clear()
            return v
        
        item = index.internalPointer()
        
        
        
        if role == Qt.DecorationRole:
            
            if index.column() == 0:
                key = 'Thumbnail'
                if item.dataReady(key):
                    
                    icon = item.get_data(key)
                    
                    if icon:
                        return QIcon(QPixmap.fromImage(icon))
                
                elif not item.dataLoading(key):
                    self.data_request(item, key)
                    
                return self.default_icon
            
            else:
                v = QVariant()
                v.clear()
                return v

        if role != Qt.DisplayRole:

            v = QVariant()
            v.clear()
            return v
        
        

        key = item.column_names[index.column()]
        
        item_data = None
        
        if item.dataReady(key):
            item_data = item.get_data(key)
        
        elif not item.dataLoading(key):
            #print key,index,role
            self.data_request(item, key)
        
        if item_data:
            return QVariant(item_data)
        
        
        return item_data

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled

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
            item_data = self.root_item
        
        
        if item_data.children:
            return True
        
        return False

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
        
 
        childcount = parent_item.childCount()
        return childcount
    
    
    def sort(self, column,order):
        
        
        column_name = self.root_item.column_names[column]
        reverse = False
        
        if order == Qt.AscendingOrder:
            reverse = True
            
            
        self.emit(SIGNAL("layoutAboutToBeChanged ()"))
            
        self.root_item.sort_by(column_name, reverse)
        
        
        self.emit(SIGNAL("layoutChanged()"))
        
        #for item in self.root_item.children:
        
            #self.update_item_view(item)
        #self.reset()
    def mimeTypes(self):
        
        return ['application/x-qabstractitemmodeldatalist',"text/uri-list"]
    
    def mimeData(self,indexes):
        
        
        mimeData = QMimeData()
        #encodedData = QByteArray()
        
       
        #stream = QDataStream(encodedData,QIODevice.WriteOnly)
        urls = []
        text = ''
        for index in indexes:
            if index.isValid():
                
                if index.column() == 0:
                    path = index.internalPointer().content.path()
                    url = QUrl.fromLocalFile(path)
                    urls.append(url)
                    
                    #text += '%s\n' % (path)
                #stream.writeQString(url)
                #stream.writeString(text)
        
        #mimeData.setData("text/uri-list", encodedData)
        mimeData.setUrls(urls)
        mimeData.setData('application/x-qabstractitemmodeldatalist',QByteArray())
        
        #mimeData.setText(text)
        return mimeData
            
    
    def update_item_view(self,item):
        """send a dataChanged signal to the view"""
        index_start = self.createIndex(item.row(), 0, item)
        index_end = self.createIndex(item.row(), item.columnCount(), item)
        
        self._dataChanged(index_start, index_end)
        
    def update_item_view_column(self,item,key):
        if key in ['Thumbnail']:
            index = self.createIndex(item.row(), 0, item)
            self._dataChanged(index,index)
            
        elif key in ['Preview_0','Preview_1','Preview_2','Preview_3']:
            
            if item == self.current_item:
                self.emit(SIGNAL('preview_ready'),item.properties[key])
        
        else:
            column = item.column_names.index(key)
            left = max(0,column-1)
            right = min(column+1,item.columnCount())
            
            index_start = self.createIndex(item.row(), left, item)
            index_end = self.createIndex(item.row(), right, item)
        
            self._dataChanged(index_start, index_end)
            
            
        
    def _dataChanged(self,index_start,index_end):
        
        
        if not self.data_change_queue:
            QTimer.singleShot(10,self._emitDataChanged)
            
        #print 'sending update'
        self.data_change_queue.append((index_start,index_end))
        
    
    def _emitDataChanged(self):
        
        while self.data_change_queue:
            index_start,index_end = self.data_change_queue.pop(0)
            self.emit(SIGNAL('dataChanged(const QModelIndex &, const QModelIndex &)'), index_start, index_end)
    

        
    def set_modal_data(self,data):
        
        self.root_item= data
        #self.emit(SIGNAL('layoutChanged ()'))
        #self.update_item_view(self.root_item)




class Content_Treeview(QTreeView):
    def __init__(self,parent=None):
        super(Content_Treeview,self).__init__(parent)
        
        self.overlay_painter = Progress_Overlay_Painter() 
        self.overlay_painter.set_paint_device(self)
        
        #self.overlay_painter.show()
        self.setAlternatingRowColors(True)
        scale = .045
        self.setIconSize(QSize(1920*scale,1080*scale))
        
        self.setDragEnabled(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.setSortingEnabled(True)
        
        #self.setModel(Content_Model())
        self.connect(self, SIGNAL("collapsed (const QModelIndex&)"),self.stop_loading)
        self.connect(self, SIGNAL("expanded (const QModelIndex&)"),self.start_loading)
        
        self.connect(self, SIGNAL("doubleClicked (const QModelIndex&)"),self.double_clicked)
        self.auto_size()
    def stop_loading(self,index):
        
        self.model().remove_data_request(index)
        
        
    def start_loading(self,index):
        
        self.model().request_children_data_loaded(index)

    def double_clicked(self,index):
        
        item_data = index.internalPointer()
        
        if not isinstance(item_data.content, content_types.FileSequence):
            
            url = item_data.content.url()
            QDesktopServices.openUrl(QUrl(url))
        
    def auto_size(self):
        for i in [0,1,2,3,4]:
            self.resizeColumnToContents(i)
            
        #self.setColumnWidth(0,200)
            
    def currentChanged(self,current,previous):
        
        self.emit(SIGNAL('current_changed'),current,previous)
        
        QTreeView.currentChanged(self,current,previous)

        
        self.model().set_current_item(current.internalPointer())
        if current:
            self.model().priority_data_request(current)
            
    def dataChanged(self,topLeft,bottomRight):
        
        QTreeView.dataChanged(self,topLeft,bottomRight)
        
        #for i in [1,2,3,4]:
            #self.resizeColumnToContents(i)
            
            
    def get_selected_items(self):
        

        selected_items = []
        #print self.selectedIndexes()
        
        selection_model = self.selectionModel()
        
        #print selection_model.selectedRows()
        for index in selection_model.selectedRows():
            
            item_data = index.internalPointer()
            
            selected_items.append(item_data)
            
        return selected_items
        
    def sizeHint(self):
        return QSize(800,400)
    
    def setModel(self,model):
        
        QTreeView.setModel(self,model)
        self.setSortingEnabled(True)
        self.start_loading(None)
        
    def keyPressEvent(self,event):
        
        if event == QKeySequence.Copy:
            items = self.get_selected_items()
            
            paths = []
            for item in items:
                paths.append(item.content.path())
                
            app = QApplication.instance()
            
            app.clipboard().setText("\n".join(paths))
            print paths
            event.accept()
        else:
            QTreeView.keyPressEvent(self,event)
        
    def paintEvent(self,event):
        
        QTreeView.paintEvent(self,event)
        self.overlay_painter.paint_overlay()
#Notification       
class Content_Notification_Bar_Widget(QWidget):
    def __init__(self,parent=None):
        super(Content_Notification_Bar_Widget,self).__init__(parent)
        
        
        self.progress_bar = QProgressBar()
        
        self.progress_bar.setFixedSize(QSize(150,10))
        
        self.message = QLabel()
        
        layout = QHBoxLayout()
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.message,Qt.AlignLeft)
        
        layout.setMargin(0)
        #layout.setAlignment()
        self.setLayout(layout)
        
        
    def set_progress(self,min,max,value):
        self.progress_bar.setMinimum(min)
        self.progress_bar.setMaximum(max)
        self.progress_bar.setValue(value)
        
    def set_message(self,message):
        self.message.setText(message)
       
        
class Preview_Widget(QWidget):
    
    def __init__(self,parent=None):
        super(Preview_Widget,self).__init__(parent)
        
        self.preview_data = {}
        
        self.preview_count = 4
        
        self.clear()
        #layout.setSpacing(2)
        #layout.setMargin(2)
       
     
    def preview_ready(self,data):
        
        
        index = data['preview_index']
        
        self.preview_data[index] = data
        
        self.update()
        
        
    def clear(self):
        for i in range(self.preview_count):
            self.preview_ready({'preview_index':i,'preview':None,'status':'no image'})
            
        self.update()
            
    def set_loading(self):
        for i in range(self.preview_count):
            self.preview_ready({'preview_index':i,'preview':None,'status':'loading'})
            
        self.update()
        
    def set_size(self):
        width = self.width()
        
        height = (width * 9/(16*4.0)) + 26.0
        
        self.setFixedHeight(height)
    
            
    def resizeEvent(self,event):
        
        self.set_size()
        
        
    def paintEvent(self, event):
        painter = QPainter()
        
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        fullrect = QRectF(self.rect())
        
        
        
        border = 3
        
        
        bg_rect = QRectF(QPointF(border,border),QPointF(fullrect.width()-border,fullrect.height()-border,))
        
        painter.setPen(QPen(QColor(128,128,128),.5,Qt.SolidLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(bg_rect, 5, 5,)
        
        
        spacing = 4
        height = bg_rect.height()
        p_width = (bg_rect.width() * 1.0/self.preview_count) - border
        
        
        for i in xrange(self.preview_count):
            
            p_rect = QRectF(QPointF(0,spacing),QPointF(p_width-spacing,height-spacing))
            p_rect.translate((p_width*i) + (border*3) + spacing/2.0 ,border)
            
            
            image_width = p_rect.width()-8.0
            image_height = image_width *9.0/16.0
            i_rect = QRectF(QPointF(0,0),QPointF(image_width,image_height))
            
            i_rect.moveCenter(p_rect.center())
            
            
            painter.setBrush(QColor(0,0,0))
            painter.setPen(QPen(QColor(128,128,128),2,Qt.SolidLine))
            painter.drawRoundedRect(p_rect, 10, 10,)
            
            #painter.fillRect(p_rect, QColor(0,0,0))
            
            
            image = self.preview_data[i]['preview']
            
            font = QFont('Serif', 15, QFont.Light)
            font_color = QColor(255, 255, 255)

            
            if image:
                
                scaled_image = image.scaledToWidth(i_rect.width(),Qt.SmoothTransformation)
                
                painter.drawImage(i_rect, scaled_image)
                
                
                frame_num = str(self.preview_data[i]['frame'])
                
                
                f_rect  =QRectF(QPointF(i_rect.right()-40, i_rect.bottom()-15),i_rect.bottomRight())
                
                f_rect.translate(-4, -2)
                
                
                painter.setFont(fit_font(f_rect,font,frame_num))
                
                #painter.setFont(font)
                painter.setPen(font_color)
                
                draw_with_shadow(painter,painter.drawText,[f_rect,Qt.AlignRight,frame_num])
                
                #painter.drawText(i_rect.center(),str(frame_num))
            elif self.preview_data[i]['status'] == 'loading':
                painter.fillRect(i_rect, QColor(128, 128,128))
                
                painter.setFont(font)
                painter.setPen(font_color)
                
                draw_with_shadow(painter,painter.drawText,[i_rect,Qt.AlignCenter,str("Loading Image")])
                
            elif self.preview_data[i]['status'] == 'failed':
                painter.fillRect(i_rect, QColor(128, 128,128))
                
                painter.setFont(font)
                painter.setPen(QColor(255,128,128))
                
                draw_with_shadow(painter,painter.drawText,[i_rect,Qt.AlignCenter,str("Loading Failed")])
                
                
            else:
                pass
                
                painter.fillRect(i_rect, QColor(128, 128,128))
                
                painter.setFont(font)
                painter.setPen(font_color)
                
                draw_with_shadow(painter,painter.drawText,[i_rect,Qt.AlignCenter,str("No Image")])
    
        
        
        
        
        
        painter.end()
        
    
        #self.repaint()
        
        #self.setFixedSize(QSize(width,height))

class Content_Treeview_Widget(QWidget):
    
    def __init__(self,parent=None):
        super(Content_Treeview_Widget,self).__init__(parent)
        
        self.view = Content_Treeview()
        self.preview = Preview_Widget()
        self.context_menu = None
        
        
        
        self.information_finder = Information_Finder_Manager()
        
        self.connect(self, SIGNAL("clear"),self.information_finder.clear)
        self.connect(self.view, SIGNAL('current_changed'), self.current_changed)
        
        
        
        self.notification_bar = Content_Notification_Bar_Widget()
        self.notification_bar.hide()
        self.timer_id = None
        self.delay = 100
        
        self.overlay_timeout = 0
        self.show_overlay_delay = 500
        
        #self.notification_bar.hide()
        
        layout = QVBoxLayout()
        layout.setMargin(0)
        
        viewPreviewSplitter = QSplitter(Qt.Vertical)
        
        #sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        #viewPreviewSplitter.setSizePolicy(sizePolicy)
        
        
        viewPreviewSplitter.addWidget(self.view)
        viewPreviewSplitter.addWidget(self.preview)
        
        
        layout.addWidget(viewPreviewSplitter)
        #layout.addWidget(self.view)
        #layout.addWidget(self.preview)
        #layout.addWidget(self.notification_bar)
        #layout.setAlignment(Qt.AlignLeft)
        
        
        
        self.setLayout(layout)
        self.preview.set_size()
        #self.information_finder.start()
        self.clear()
        
        self.setup_context_menu()
        #self.update()
        
    def current_changed(self,current,prevous):
        
        if current:
            self.preview.set_loading()
        else:
        
            self.preview.clear()
        
    def connect_to_information_finder(self,new_model,old_model):
        sig = 'data_request'
        if old_model:
            self.disconnect(old_model, SIGNAL(sig),self.information_finder.data_request)
        self.connect(new_model, SIGNAL(sig),self.information_finder.data_request)
        
        
        sig = 'remove_data_request'
        if old_model:
            self.disconnect(old_model, SIGNAL(sig),self.information_finder.remove_data_request)
        self.connect(new_model, SIGNAL(sig),self.information_finder.remove_data_request)


        sig = 'data_ready'
        if old_model:
            self.disconnect(self.information_finder, SIGNAL(sig),old_model.data_ready)
        self.connect(self.information_finder, SIGNAL(sig),new_model.data_ready)
        
        sig = 'data_failed'
        if old_model:
            self.disconnect(self.information_finder, SIGNAL(sig),old_model.data_failed)
        self.connect(self.information_finder, SIGNAL(sig),new_model.data_failed)
        
        sig = 'preview_ready'
        if old_model:
            self.disconnect(old_model, SIGNAL(sig),self.preview.preview_ready)
        self.connect(new_model, SIGNAL(sig),self.preview.preview_ready)
        
        
    def context_menu_action(self,description):
        description['content'] = self.view.get_selected_items()        
        self.emit(SIGNAL("context_menu_action"),description)
        
        
        
        #print description
        
    def setup_context_menu(self):
        
        menu = QMenu()
        
        #actions = menu.actions()
        action_list = tool_actions.content_treeview_contextmenu_actions()
        
        
        for item in action_list:
            
            if item:
                action = QAction(item['name'],self)
                self.connect(action, SIGNAL('triggered()'),
                             lambda description=item:self.context_menu_action(description))
                menu.addAction(action)
                
            else:
                menu.addSeparator()
        
        self.context_menu = menu
        
    def contextMenuEvent(self,event):
        if self.view.get_selected_items():
            self.context_menu.exec_(event.globalPos())
        
    def clear(self):
        
        self.emit(SIGNAL('clear'))
        old_model = self.view.model()
        new_model = Content_Model()
        
        self.connect_to_information_finder(new_model, old_model)
        self.view.setModel(new_model)
        
        #self.preview.preview_ready(None)
        self.preview.clear()
        #self.preview.set_size()
        
        del old_model
        #self.view.setEnabled(False)
        
    def show_overlay(self):
        #self.view.overlay_painter.set_angle(0)
        self.view.overlay_painter.show()
        
    
    def hide_overlay(self):
        self.view.overlay_painter.hide()
        self.stop_animation()
        
    def set_progress(self,progress_min,progress_max,progress_value):

        self.view.overlay_painter.set_progress(progress_min, progress_max, progress_value)
    
    
    def set_message(self,message,details=''):
        self.view.overlay_painter.set_message(message, details)
    
    
    def show_progress(self):
        pass
        
    
    def hide_progress(self):
        self.hide_overlay()
        
    def set_modal_data(self,modal_data):
        self.view.setEnabled(True)
        
        old_model = self.view.model()
        new_model = Content_Model()
        self.connect_to_information_finder(new_model, old_model)
        
        new_model.set_model_data(modal_data)
        self.view.setModel(new_model)
        
        del old_model
        
        self.view.auto_size()
        
    def load_started(self,item=None):
        self.clear()
        self.show_progress()
        self.start_animation()
        
    def load_finished(self,item=None):
        self.hide_overlay()
        if item:
            self.set_modal_data(item)
        
    def load_error(self,item=None):
        self.hide_overlay()
        
    def loading_stop(self,item=None):
        self.hide_overlay()
        
        
        
    def start_animation(self):
        
        if not self.timer_id:
            self.timer_id = self.startTimer(self.delay)
            
            
    def stop_animation(self):
        
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None
            self.overlay_timeout = 0

    def timerEvent(self,event):
        
        self.overlay_timeout += self.delay
        
        if self.overlay_timeout > self.show_overlay_delay:
            self.show_overlay()
        
        percent = self.view.overlay_painter.get_progress_percent()
        
        if percent == None:
            angle = self.view.overlay_painter.get_angle()
            self.view.overlay_painter.set_angle(angle + 30 )
        
        self.view.viewport().update()
        
    #def sizeHint(self):
        
        #return QSize(500,500)

        
        

