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


import os
import mimetypes
from collections import defaultdict
import re

import sequence

import content_types

import utilities

mimetypes.knownfiles = [utilities.find_mime_types_file()]
mimetypes.init()

class Content_Finder_Object(object):
    
    def __init__(self):
        self._stop=False
        
    def stop(self):
        return self._stop
    
    def setStop(self,value=True):
        self._stop = value
        
    def progress(self,progress_min=0,progress_max=0,progress_value=0):
    
    
        pass

        
    def message(self,**kargs):
        pass
        
        
    def run(self):
        pass
    
    def start(self):
        return self.run()


def split_mimetype(file_type):
    
    return file_type.split('/')


class Content_Sorter(Content_Finder_Object):
    
    def __init__(self,path_dict=None):
        
        super(Content_Sorter,self).__init__()
        self.numPos = -1
        
        
        if isinstance(path_dict, Content_Finder):
            self.path_dict = path_dict.path_dict
            self.file_count = path_dict.file_count
            
        else:
            
            self.path_dict = path_dict
            self.file_count = 0
            self.calculate_file_count()
            
            
        self.file_index = 0
        
        self.sorted_content = {}
        
        self.mimetypes = {}
        
    def calculate_file_count(self):
        self.file_count = 0
        for filenames in self.path_dict.values():
            self.file_count += len(filenames)
            
    def add_content(self,content_dict):
        for key,value in content_dict.items():
            if self.sorted_content.has_key(key):
                self.sorted_content[key].extend(value)
                
            else:
                self.sorted_content[key] = value
         
        
    def run(self):
        
        for dirname,files in self.path_dict.items():
            sorted_files = self.sort_files(dirname, files)
            self.add_content(sorted_files)
            self.file_index += len(files)
            self.progress(0, self.file_count, self.file_index)
            
            self.message(sort_filecount=self.file_count,sort_fileindex=self.file_index)
    
            
    def sort_files(self,dirname,files):
        
        sorted_files = defaultdict(list)
        for filename in files:
            
            file_type,encoding = mimetypes.guess_type(filename)
            
            if file_type == None:
                file_type = 'unkown/unkown'
                #print file_type,filename
                
            fullpath = os.path.join(dirname,filename)
            
            main_type,subtype = split_mimetype(file_type)
            
            if main_type == 'image':
                FileItem = content_types.ImageFile(dirname,filename,mimetype=(file_type,encoding))
            elif main_type == 'video':
                FileItem = content_types.VideoFile(dirname,filename,mimetype=(file_type,encoding))
            elif main_type == 'audio':
                FileItem = content_types.AudioFile(dirname,filename,mimetype=(file_type,encoding))
            else:
                FileItem = content_types.File(dirname,filename,mimetype=(file_type,encoding))
            
            #FileItem.blame()
            #FileItem.create_time()
            
            FileItem.set_common_prefix(files.common_prefix)
            sorted_files[file_type].append(FileItem)
            
            
            
            #print files.common_prefix
            #print file_type,filename
            
        for key in sorted_files.keys():
            
            main_type,subtype = split_mimetype(key)
            
            if main_type in ['image']:
                
                files = sorted_files[key]
                content_list = self.sort_sequence(files)
                
                sorted_files[key] = content_list
                
                
        return sorted_files
                


    def sort_sequence(self,files):
        #print ''
        
        res = []
        
        currentSeq = sequence.Sequence()
        for file_item in files:
            
            name = sequence.SeqString(file_item.basename())
            
            sequenceSplit = False
            
            if not currentSeq.match(name, self.numPos):
                sequenceSplit = True
            
                
            if sequenceSplit:
                res.append(currentSeq)
                currentSeq = sequence.Sequence()
                
                
            currentSeq.append(name, file_item)
            
        if len(currentSeq) > 0:
            res.append(currentSeq)
            
        content_list = []
        
        
        for item in res:
            
            if len(item) <= 1:
                content_list.append(item[0])
                
            else:
                f = item[0]
                
                if isinstance(f, content_types.ImageFile):
                    c = content_types.ImageSequence
                else:
                    c = content_types.FileSequence
                
                content_item = c(dirname=f.dirname(),
                                 sequence_object=item,
                                 mimetype = f.mimetype())
                
                content_item.set_common_prefix(f.common_prefix())
                
                
                #print content_item[0]
                #for item in content_item:
                    #print item
                #print content_item
                
                #print item.ranges()
                #print item.sequenceName()
                
                content_list.append(content_item)
        
        return content_list


class File_Path_List(list):
    
    def __init__(self):
        
        super(File_Path_List,self).__init__()
        
        self.common_prefix = None


class Content_Finder(Content_Finder_Object):
    
    def __init__(self,search_dirs=None):
        
        super(Content_Finder,self).__init__()
        self.file_count = 0
        self.path_dict = {}
        self.fname_ignore = ['[.].*']
        self.recursive = True
        self.common_prefix = ''
        if search_dirs:
            self.search_dirs = search_dirs
    
    def set_search_dirs(self,paths):
        
        self.search_dirs = paths
    
    def run(self):
        
        
        for item in self.search_dirs:
            
            item_dict = description_to_dict(item)
            self.recursive = item_dict['recursive']
     
            p_dict = self.get_path_dict(item_dict['path'])
            
            if self.stop():
                return None
            self.path_dict.update(p_dict)
            
            
            if self.stop():
                return None
            
        
        
        return self.path_dict
        
        #for key,value in self.path_dict 
        
        pass
    


    def get_path_dict(self,path):
        
        if os.path.isfile(path):
            dirname = os.path.dirname(path)
        else:
            dirname = path
            
        def get_file_path_list():
            p= File_Path_List()
            p.common_prefix = self.common_prefix 
            return p
        
        path_dict = defaultdict(get_file_path_list)
        
        for root,dirs,files in os.walk(dirname):
                for filename in files:
                    #full_path = os.path.join(root,filename)
                    
                    if self.path_dict.has_key(root):
                        pass
                    elif self.ignore_file(root, filename):
                        pass
                    else:
                        path_dict[root].append(filename)
                        self.file_count += 1
                        
                        self.message(message='',listing=self.file_count)
                        #self.progress(progress_value=self.file_count)
                    if self.stop():
                        return None
                if self.stop():
                    return None
                
                if not self.recursive:
                    break
                    
        return path_dict
    
    def ignore_file(self,dirname,filename):
        
        for item in self.fname_ignore:
            p = re.compile(item)
            if p.match(filename):
                #print 'ignoring', filename
                return True
            
        return False
    
    

def description_to_dict(item):
    
    if isinstance(item, dict):
        item_path = item['path']
        item_dict = item.copy()
        if not item_dict.has_key('recursive'):
            item_dict['recursive'] = True
    else:
        item_dict = {'recursive':True,'path':item}
        

    return item_dict



def description_to_content_dirs(item_data,description):
    

    content_description = defaultdict(list)
    content_description.update(description)   
    assert item_data['path']
    
    base_path = item_data['path']
    
    
    content_dirs = []
    

    for item in content_description['relative_paths']:
        
        item_dict = description_to_dict(item)
        
        rel_path = os.path.join(base_path,item_dict['path'])
        
        if os.path.exists(rel_path):
            item_dict['path'] = rel_path
            content_dirs.append(item_dict)
        
    for item in content_description['child_relative_paths']:
        
        item_dict = description_to_dict(item)
        
        for child in item_data['children']:
            child_path = child['path']
            rel_path = os.path.join(child_path,item_dict['path'])
            if os.path.exists(rel_path):
                
                new_item_dict = item_dict.copy()
                new_item_dict['path'] = rel_path
                content_dirs.append(new_item_dict)
                
            
    return content_dirs

    
    
    
    
    

def get_content(paths):
    
    
    cf = Content_Finder(paths)
    cf.start()
    
    cs = Content_Sorter(cf)
    cs.start()
    
    return cs.sorted_content

def create_model_root():
    
    root = content_types.File_Model_Item()
    for item in root.column_names:
        root.properties[item] = item
        root.data_loaded.append(item)
        
    root.data_loaded.append('Thumbnail')
        
    return root

def create_model_data(content):

    root = create_model_root()
    
    
        
    for key,value in content.items():
        main_type,sub_type = split_mimetype(key)
        
        if main_type in ['image','video']:
            #print value
            for item in value:
                c = content_types.File_Model_Item(item,root)
                
                root.addChild(c)
            

    root.sort_by('Path')
    return root
        

