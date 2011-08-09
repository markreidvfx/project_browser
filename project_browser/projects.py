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
import imp
import copy
import traceback

import re

from collections import defaultdict

import utilities

def default_value():
    return None

class Project_Item():
    
    def __init__(self,properties,parent=None):
        self.parent_item = parent
        self.properties = defaultdict(default_value)
        for key,value in properties.items():
            self.properties[key] = value
        self.item_data = [self.properties['name'], self.properties['type']]
        self.children = []
        
        
        self.stop = False
        self.loaded = False
        self.loading = False
        
        
    def __str__(self):
        return self.properties['name']
    def setParent(self,item):
        self.parent_item = item
        
        
    def get_index_path(self):
        
        index_path = self._get_index_path()
        
        index_path.reverse()
        
        return index_path
        
    def _get_index_path(self,index_path=None):
        
        if index_path is None:
            index_path = []
            
        index_path.append({'name':self.properties['name'],'row':self.row(),'column':0})
        
        if self.parent_item:
            self.parent_item._get_index_path(index_path)
            
        return index_path
        
        
        
    def addChild(self,item):
        item.setParent(self)
        self.children.append(item)
    
    def canLoadChildren(self):
        if self.properties['subdirectories']:
            return True
        if self.properties['children']:
            return True
        
        if self.properties['children_func']:
            
            return True
        
        return False
        
    def parent(self):
        return self.parent_item
    
    def child(self, row):
        return self.children[row]

    def row(self):
        if self.parent_item:
            return self.parent_item.children.index(self)

        return 0
    
    def columnCount(self):
        return len(self.item_data)
    
    def childCount(self):
        
        if self.children:
            
            return len(self.children)
        
        return 0
    
    
    def data(self, column):
        try:
            d = self.item_data[column]
            return d
        except IndexError:
            return None
    
    def check_children(self):
        if not self.loaded:
            if not self.loading:
                self.load_children()
    def load_children(self):
        self.loading = True
        
        if self.properties['children']:
            for item_properties in self.properties['children']:
                p = Project_Item(properties=item_properties)
                self.addChild(p)
                
        
        if self.properties['paths']:
            for item in self.properties['paths']:
                if os.path.exists(item):
                    self.properties['path'] = item
                    break
                
        if self.stop:
            return None
        
                
        if self.properties['path'] and self.properties['subdirectories']:
            for item in self.properties['subdirectories']:
                
                subdirectory = item['path']
                item_properties = item['properties']
                
                if self.stop:
                    return None
                
                if isinstance(item_properties, str):
                    if item_properties == 'self':
                        item_properties = copy.deepcopy(self.properties)
                        
               
                path = self.properties['path']
                full_subdir_path = os.path.join(path,subdirectory)
                for subdir_item in listdir_fullpath(full_subdir_path):
                    name = subdir_item[0]
                    path = subdir_item[1]
                    if check_item_rules(item_properties,path):
                        
                        item_properties['name'] = name
                        item_properties['path'] = path
                        p = Project_Item(properties=item_properties)
                        self.addChild(p)
                    
                    if self.stop:
                        return None
                            
                            
        
                
        if self.stop:
            return None
                
        if self.properties['children_func']:
            
            children = self.properties['children_func'](self.properties)
            
            if isinstance(children, list):
                for item_properties in children:
                    if self.stop:
                        return None
                    
                    p = Project_Item(properties=item_properties)
                    self.addChild(p)
                    
        self.loaded = True
        self.loading = False
    
def check_item_rules(item_type,path):
    
    if item_type.has_key('ignore'):
        for item in item_type['ignore']:
            basename = os.path.basename(path)
            p = re.compile(item)
            if p.match(basename):
                return False
    #required
    
    if item_type.has_key('required_subdirectories'):
        for subdir in item_type['required_subdirectories']:
            full_path = os.path.join(path,subdir)
            if not os.path.exists(full_path):
                #print 'bad',full_path
                return False 
            
    
            
    
    return True


def get_projects_list_dir():
    projects_dir = 'projects'
    
    return projects_dir


def read_project_file(name,path):
    
    #print path
    p = imp.load_source(name,path)

    
    if "Project" in dir(p):
        if isinstance(p.Project, dict):
            return Project_Item(properties=p.Project)
    
    return None
    


def get_projects(project_configuration_dirs=None):
    
    if not project_configuration_dirs:
        project_configuration_dirs = utilities.find_project_configuration_dirs()
    project_file_list = []
    
    #print project_configuration_dirs
    
    for dirname in project_configuration_dirs:
        for filename in os.listdir(dirname):
            
            name,ext = os.path.splitext(filename)
            fullpath = os.path.join(dirname,filename)
            if ext.lower() in ['.py']:
                project_file_list.append({'name':name,
                                          'path':fullpath})
                
                
    def sort_func(item):
        
        return item['name']        
    
    
    
    project_file_list.sort(key=sort_func)
    
    
    project_list = []
    
    for item in project_file_list:
        
        project = read_project_file(item['name'],item['path'])
        if project:
            project_list.append(project)
    

    return project_list


def validate_project_item(project_item):
    if not os.path.isdir(project_item['path']):
        return False
    
    if project_item.has_key('requred_subdirs'):
        for subdir in project_item['requred_subdirs']:
            full_path = os.path.join(project_item['path'],subdir)
            if not os.path.exists(full_path):
                #print 'bad',full_path
                return False
            
        
    return True

def lowercase(item):
    return item.lower()

def listdir_fullpath(path):
    
    try:
        paths = []
        
        file_list = os.listdir(path)
        
        file_list.sort(key=lowercase)
        
        for item in file_list:
            
            full_path = os.path.join(path,item)
            if os.path.isdir(full_path):
                paths.append((item,full_path))
            
        return paths
    except:
        return []

def try_list(path):
    try:
        return os.listdir(path)
    except:
        #print traceback.format_exc()
        return []


def walk_project_item(item):
    
    subdirs = item['subdirs']
    path = item['path']
    
    print path
    
    for subdir,item_type in subdirs:
        
        print subdir,item_type
        if isinstance(item_type, str):
            if item_type == 'self':
                item_type = copy.deepcopy(item)
                
        print os.path.join(path,subdir)
        
        for subdir_item in try_list(os.path.join(path,subdir)):
            
            full_path = os.path.join(path,subdir,subdir_item)
            
            print full_path
        
            new_item = copy.deepcopy(item_type)
            new_item['path'] = full_path
            if validate_project_item(new_item):
                
                #yield new_item
                print full_path
                walk_project_item(new_item)
            
            
            
  
        
def walk_project(project):
    assert project['type'] == 'Project'
    valid_path = None
    
    
    if isinstance(project['paths'],list):
    
        for item in project['paths']:
            if os.path.exists(item):
                project['path'] = item
                break
    else:
        project['path'] = ''
        
    print project['name'], ":"
    
    
    walk_project_item(project)
    
        
    
        
        
        
        #print item
    
    


if __name__ == '__main__':
    
    projects = get_projects()
    
    for item  in projects:
        
        print item
        #walk_project(item)
        #for project_item in walk_project(item):
            #print project_item['path']
    
    
    