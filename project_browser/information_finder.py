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
import time

from collections import defaultdict

from multiprocessing import cpu_count

import content_types


def return_none():
    return None

def return_none_defaultdict():
    return defaultdict(return_none)

Info_Cache = defaultdict(return_none_defaultdict)
Info_Cache_Key_Order = []

def add_to_cache(cach_key,key,value):
    if not Info_Cache[cach_key][key]:
        Info_Cache[cach_key][key] = value
        
        Info_Cache_Key_Order.append(cach_key)
        #print len(Info_Cache_Key_Order),'cached items'
        
            
            
        
        
class Information_Finder_Thread(QThread):
    def __init__(self,mutex = None,parent=None):
        
        super(Information_Finder_Thread, self).__init__(parent)
        self.current_item = None
        self.current_key = None
        self.work = []
        self.start_time = None
        self.mutex = mutex
        
    def set_stop(self,value=True):
        if self.current_item:
            self.current_item.set_stop(value)
        
    def clear(self):
        work_items = [] 
        while self.work:
            work_items.append(self.work.pop())
            
        return work_items
    
    def add_work(self,job):
        
        item = job[0]
        
        key = job[1]
        item.data_loading.append(key)
        item.data_queued.remove(key)
        
        self.work.append((item,key))
        
    
    def run(self):
        
        while self.work:
            item, key =self.work.pop(0)
            self.current_item = item
            self.current_key = key
            self.start_time = time.time()
            
            try:
                self.func()
                
                if self.current_item.stop():
                    self.work_stoped()
                    
                else:
                    self.work_done()
                    
            except:
                trace = traceback.format_exc()
                self.work_error(trace)
                
        self.current_item = None
        
    def check_time(self):
        
        dur = time.time() -self.start_time
        
        if dur < .2:
            self.msleep(15)
         
    def work_error(self,trace):
        self.emit(SIGNAL("work_error"),trace,self.current_item,self.current_key)
        self.check_time()
    def work_done(self):
        self.emit(SIGNAL("work_done"),self.current_item,self.current_key)
        #self.msleep(500)
        self.check_time()
    def key_ready(self):
        self.emit(SIGNAL("key_ready"),self.current_item,self.current_key)
        
    def func(self):
        
        key = self.current_key
        item = self.current_item
        
        item.lock.lock()
        try:
            
            item.content.properties()
        except:
            item.content._properties = None
            item.lock.unlock()
            
            raise
        item.lock.unlock()
            
       
        
        
        if key in ['Path','Kind','Blame','Frames','Created']:
            
            item.get_data(key)
            add_to_cache(item.content.path(),key,item.properties[key])
            
            
        if key in ['Thumbnail']:
            thumbnail = None
            
            #item.lock.lock()
            try:
               
                    
                image_data = item.content.thumbnail()
                image = QImage()
                if image.loadFromData(image_data):
                    thumbnail = image
                        
                    item.properties[key] = thumbnail
                else:
                    raise Exception("Failed to create Thumbnail")
            except:
                #item.lock.unlock()
                item.properties[key] = None
                raise
            
            add_to_cache(item.content.path(),key,item.properties[key])
            
            #item.lock.unlock()
        
        preview_keys = []
        
        for i in range(4):
            preview_keys.append('Preview_%d' % i)
            
            
        if key in preview_keys:
            
            try:
                
                index = preview_keys.index(key)
                indexF = index/4.0
                scale = .19
                width = int(1920*scale)
                height = int(1080*scale)
                
                frame = 0
                
                if isinstance(item.content, content_types.ImageFile):

                    item.lock.lock()
                    data = None
                    for preview_key in preview_keys:
                        if item.properties.has_key(preview_key):
                            if item.properties[preview_key]:
                                data = item.properties[preview_key].copy()
                                
                    if data:
                        data['preview_index'] = index
                        item.properties[key] = data
                        item.lock.unlock()
                    else:
                        try:
                            frame = item.content.frame_num()
                            
                            image = QImage()
                            image_data = item.content.thumbnail(width,height)
                            if image.loadFromData(image_data):
                                item.properties[key] = {'preview':image,'frame':frame,'preview_index':index,'key':key,'status':'loaded'}
                                item.lock.unlock()
                            else:
                                raise Exception("Failed to create preview")
                        except:
                            item.lock.unlock()
                            raise

                else:
                    
                    frame  = item.content.frameF(indexF)
                    image = QImage()
                    image_data = item.content.thumbnail(width,height,indexF=indexF)
                    #raise Exception()
                    if image.loadFromData(image_data):
                        item.properties[key] = {'preview':image,'frame':frame,'preview_index':index,'key':key,'status':'loaded'}
                    else:
                        raise Exception("Failed to create preview")
 
            
            except:
                item.properties[key] = None
                raise

            add_to_cache(item.content.path(),key,item.properties[key])
            
        
            
  
class Information_Finder_Manager(QObject):
    def __init__(self,parent=None):
        super(Information_Finder_Manager, self).__init__(parent)

        self.workers = []
        self.work = []
        self.mutex = QMutex()
        self.work_buffer = 2
        
        worker_count = 2
        
        self.max_work = worker_count * 10
        
        print worker_count, 'workers!'
        
        for i in range(worker_count):
            self.add_worker()
    
    def clear(self):
        cleared_work = []
        while self.work:
            cleared_work.append(self.work.pop())
            
        
        for worker in self.workers:
            cleared_work.extend(worker.clear())
            
        return cleared_work
            
        
    def add_worker(self):
        
        worker = Information_Finder_Thread(mutex=self.mutex)
        
        self.connect(worker, SIGNAL('work_done'),self.work_done)
        self.connect(worker, SIGNAL('work_error'),self.work_error)
        self.connect(worker, SIGNAL('work_stoped'),self.work_stoped)
        
        self.workers.append(worker)
        
        
    def set_item_queued(self,item,key):
        
        if key in item.data_queued:
            pass
        else:
            item.data_queued.append(key)
        
    def add_work(self,item,key,priority=False):
        
        for i in range(self.work.count((item,key))):
            #print 'already in queue'
            index = self.work.index((item,key))
            old_item,old_key = self.work.pop(index)
    
        
        self.set_item_queued(item, key)
        
        if priority:
            #print 'adding to top',key
            self.work.insert(0,(item,key))
        
        else:
            #print 'adding to bottom'
            self.work.append((item,key))
        
        
        self.fill_workers()
        
        
    def get_work_load(self):
        
        load = 0
        for item in self.workers:
            load += len(item.work)
            
        return load
    
    def pop_work(self):
        
        while True:
            
            if not self.work:
                return None
            
            item,key = self.work.pop(0)
            
            if item.dataReady(key):
                self.data_ready(item,key)
                
            elif key in item.data_loading:
                pass
                #print 'key already Loading!!!!!!!'
        
            else:
                return (item,key)
            
    
    def fill_workers(self):

        max_work_load = len(self.workers) * self.work_buffer
        current_load = self.get_work_load()
        
        if current_load < max_work_load:
            for i in range(max_work_load-current_load):
                job = self.pop_work()
                
                if job:
        
                    self._add_work_to_workers(job)
                else:
                    break
                    
    def _add_work_to_workers(self,job,top=False):

        def work_length(item):return len(item.work)
        
        worker = min(self.workers,key=work_length) 
    
        worker.add_work(job)
    
        if not worker.isRunning():
            worker.start()
        
    def work_stoped(self,item,key):
        self.emit(SIGNAL("work_stoped"),item)
        self.fill_workers()
        self.clean_item_loading(item, key)
    def work_error(self,trace,item,key):
        self.emit(SIGNAL("data_failed"),item,key)
        
        print trace
        
        self.fill_workers()
        self.clean_item_loading(item, key)
        
    def work_done(self,item,key):
        #self.emit(SIGNAL("work_done"),item)
        
        self.data_ready(item, key)
        self.fill_workers()
    
    def clean_item_loading(self,item,key):
        
        for i in range(item.data_loading.count(key)):
            
            item.data_loading.remove(key)  
        
        
    def clean_item_queue(self,item,key):
        
        for i in range(item.data_queued.count(key)):
            
            item.data_queued.remove(key)
 
        
    def remove_data_request(self,items):
        
        #print 'removing requests'
        
            
        new_work_list = []
        
        for item,key in self.work:
            
            
            if item in items:
                
                self.clean_item_queue(item,key)
            else:
                new_work_list.append((item,key))
                
                
        self.work = new_work_list
            
    
    def check_cache(self,item,key):
        
        
        return Info_Cache[item.content.path()][key]
        
    def data_request(self,items,priority):
        
        while items:
            item,key = items.pop(0)
            
            
            cached = self.check_cache(item,key)
            
            if cached:
                print 'loading from cache',key
                item.properties[key] = cached
                self.data_ready(item, key)
                
            else:
            
        
                if item.lock is None:
                    item.lock = QMutex()
                
                self.add_work(item,key,priority)
    
    def data_ready(self,item,key):
        item.data_loaded.append(key)
        #item.data_loading.remove(key)
        
        self.clean_item_loading(item, key)
        self.emit(SIGNAL("data_ready"),item,key)
    