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

from project_selector import Project_Selector_Widget

from content_treeview import Content_Treeview_Widget

from content_finder_manager import Content_Finder_Manager

import gui_utilities
import utilities


class Project_Browser_Widget(QWidget):
    
    def __init__(self,parent=None):
        super(Project_Browser_Widget,self).__init__(parent)
        
        self.project_selector = Project_Selector_Widget()
        
        self.content_treeview = Content_Treeview_Widget()
        
        self.content_manger = Content_Finder_Manager()
        
        
        self.connect(self.project_selector, SIGNAL("item_selected"),self.content_manger.set_context)
        self.connect(self.project_selector, SIGNAL("clear"),self.content_treeview.clear)
        self.connect(self.content_manger, SIGNAL("Footage_load_finished"),self.content_treeview.load_finished)
        self.connect(self.content_manger, SIGNAL("Footage_load_started"),self.content_treeview.load_started)
        self.connect(self.content_manger, SIGNAL("Footage_load_stoped"),self.content_treeview.load_finished)
        
        self.connect(self.content_manger,SIGNAL("work_progress"),self.content_treeview.set_progress)
        self.connect(self.content_manger,SIGNAL("work_message"),self.content_treeview.set_message)
        
        self.connect(self.content_treeview,SIGNAL("context_menu_action"),self.context_menu_action)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.project_selector)
        splitter.addWidget(self.content_treeview)
        
        splitter.setCollapsible(0,False)
        
        splitter.setStretchFactor(1,1)
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        #layout.addWidget(self.project_selector)
        
        #layout.addWidget(self.content_treeview)
        self.setAcceptDrops(True)
        self.setLayout(layout)
        
    def context_menu_action(self,description):
        
        project_item = self.project_selector.get_selected_item()
        
        try:
            description['func'](project_item,description['content'])
        except:
            
            gui_utilities.error_message(message='%s Error!' % description['name'],
                                  info="A error occured when trying to execute %s" % description['name'],
                                  details=traceback.format_exc())
        
    def dragEnterEvent(self, event):
        
        
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.ignore()
            
        else:
        
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            l = []
            for url in event.mimeData().urls():
                l.append(str(url.toLocalFile()))
            self.project_selector.set_path(os.path.abspath(l[0]))

        else:
            event.ignore()
        
        
        
 
class Project_Browser(QMainWindow):
    def __init__(self,parent=None):
        super(Project_Browser,self).__init__(parent)
        
        self.project_browser = Project_Browser_Widget()
        
        self.setCentralWidget(self.project_browser)

    
    
def run():
    app = QApplication(sys.argv)
    
    
    gui_utilities.register_resources()
    gui_utilities.set_theme()
    icon_path = os.path.join(utilities.find_image_dir(),'project_browser.png')
    app.setWindowIcon(QIcon(icon_path))
    
    main_widget = Project_Browser()
    main_widget.setWindowTitle("Project Browser")
    
    main_widget.show()
    main_widget.raise_()
    sys.exit(app.exec_())
    
    
    
    
if __name__ == '__main__':
    
    

    run()