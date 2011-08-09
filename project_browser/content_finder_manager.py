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

import traceback

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *

from content_finder_thread import Content_Finder_Thread

class Content_Finder_Manager(QObject):
    
    def __init__(self, parent=None):
        super(Content_Finder_Manager, self).__init__(parent)
        
        self.content_finder = Content_Finder_Thread()
        
        
        self.connect(self.content_finder, SIGNAL("work_done"),self.work_done)
        self.connect(self.content_finder, SIGNAL("work_stoped"),self.work_stoped)
        self.connect(self.content_finder, SIGNAL("work_error"),self.work_error)
        
        self.connect(self.content_finder, SIGNAL("work_message"),self.work_message)
        self.connect(self.content_finder, SIGNAL("work_progress"),self.work_progress)
        
        
    def connect_to_view(self,view):
        pass
        #self.connect(self, SIGNAL("work_progress"),view.
        
    def set_context(self,data,mode):
        #print "&&& CONTEXT"
        print data
        
        print mode
        
        
        
        
        if not mode.has_key('context'):
            
            mode['context'] = 'Footage'
            
            
        self.emit(SIGNAL(mode['context'] + "_load_started"))
        self.add_work(data, mode)
    
    
    def work_progress(self,progress_min,progress_max,progress_value):
        
        self.emit(SIGNAL("work_progress"),progress_min,progress_max,progress_value)
    
    
    def work_message(self,message,details=''):
        self.emit(SIGNAL("work_message"),message,details)
        
    def add_work(self,data,mode):
        self.content_finder.clear()
        
        self.content_finder.add_work(data,mode)
        
        if not self.content_finder.isRunning():
            self.content_finder.start()
        
        
    def work_done(self,item):
        
        mode = item.mode

        self.emit(SIGNAL(mode['context'] + "_load_finished"),item.work)
        
     
        
        
    
    
    def work_error(self,trace,item):
        print trace
        
    def work_stoped(self,work):
        
        print 'stoped'
    
    
    
    

        