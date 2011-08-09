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

import time
from collections import defaultdict

class Work_Item(object):
    
    def __init__(self,data,mode):
        
        self._stop = False
        self.data = data
        self.mode = mode
        
        
        self.work = None
        
    def stop(self):
        
        return self._stop
    
    def set_stop(self,value=True):
        self._stop = True

class Content_Finder_Thread(QThread):
    def __init__(self,parent=None):
        
        super(Content_Finder_Thread, self).__init__(parent)
        self.current_item = None
        self.work = []
        self.details = ''
        
    def set_stop(self,value=True):
        if self.current_item:
            self.current_item.set_stop(value)
        
    def clear(self):
        work_items = [] 
        while self.work:
            item = self.work.pop()
            self.clean_item(item)
            work_items.append(item)
        
        self.set_stop()
            
        return work_items
    
    def add_work(self,data,mode):
        
        
        self.work.append(Work_Item(data,mode))
        
    def run(self):
        
        while self.work:
            item =self.work.pop(0)
            self.current_item = item
            
            try:
                #time.sleep(2)
                self.func()
                
                if self.current_item.stop():
                    self.work_stoped(self.current_item)
                    
                else:
                    self.work_done(self.current_item)
                    
            except:
                trace = traceback.format_exc()
                self.work_error(trace, item)
                
        self.current_item = None
        
    def func(self):
        
        
        
        if self.current_item.mode['context'] == 'Footage':
            
            self.load_footage()
        #content = content_finder.run_test()
    
    def load_footage(self):
        
        self.message(message="Loading Footage")
        self.work_progress(0, 0, 0)
        
        item_data = self.current_item.data
        
        description = self.current_item.mode

        content_dirs = content_finder.description_to_content_dirs(item_data,description)
        
        if not content_dirs:
            model = content_finder.create_model_root()
            self.current_item.work = model
            return None
        
        if self.current_item.stop():
            return None
        
        self.details = item_data['name']
    
        cf = content_finder.Content_Finder(search_dirs=content_dirs)
        cf.progress = self.work_progress
        cf.message = self.message
        cf.common_prefix = item_data['path']
        
        cf.stop = self.current_item.stop
        
        cf.start()
        
        if self.current_item.stop():
            return None
        
        cs = content_finder.Content_Sorter(cf)
        cs.progress = self.work_progress
        cs.message = self.message
        
        cs.stop = self.current_item.stop
        
        cs.start()
        
        if self.current_item.stop():
            return None
        
        self.message(message='Loading into View')
        self.work_progress(progress_min=0, progress_max=0, progress_value=0)
        
        model = content_finder.create_model_data(cs.sorted_content)
        
        if self.current_item.stop():
            return None
        
        self.current_item.work = model
        
        
        
        
        
    def clean_item(self,item):

        pass
    
    def message(self,**kargs):
        details = ''
        
        if self.current_item:
            item_data = self.current_item.data
            mode = self.current_item.mode
            details = 'Item: %s Mode: %s' % (item_data['name'],mode['name'])
        
        if kargs.has_key('message'):
            message = kargs['message']
        
        if kargs.has_key('listing'):
            
            message = 'Listing Files: %i' % (kargs['listing'])
            
            
        if kargs.has_key('sort_filecount'):
            message = 'Sorting Files: %i/%i' % (kargs['sort_fileindex'],kargs['sort_filecount'])
            
            
        
        
        
        self.emit(SIGNAL("work_message"),message,details)
        
    def work_progress(self,progress_min=0,progress_max=0,progress_value=0):
        
        self.emit(SIGNAL("work_progress"),progress_min,progress_max,progress_value)
                    
    def work_error(self,trace,item):
        self.clean_item(item)
        self.emit(SIGNAL("work_error"),trace,item)
                    
    def work_stoped(self,item):
        self.clean_item(item)
        self.emit(SIGNAL("work_stoped"),item)
        
    def work_done(self,item):
        print 'work done'
        self.emit(SIGNAL("work_done"),item)