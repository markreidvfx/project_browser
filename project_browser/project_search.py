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

import projects
import os


class Path_Finder(object):
    
    """searches set projects for a path"""
    
    def __init__(self,path,root):
        """path is the path your looking for and root is to root of all projects"""
        self.path =  path
        self.root = root
        
        properties = {'name':'Name','type':'Type','path':''}
        nearest = projects.Project_Item(properties=properties)
        
        self.nearest_item = None
        
        self.stop = False
        
        
    def get_nearest_item(self):
        """returns the nearest match to set path"""
        
        match = self.search_projects()
        
        if not match:
            return self.nearest_item
        
        self.nearest_item = match
        
        return match
        
        
    def compare_common_prefix(self,item,nearest_item):
        """compares items path to self.path and sets self.nearest path if its the neareset"""
    
        common = os.path.commonprefix([self.path,item.properties['path']])
        
        
        
    
        if os.path.exists(common):
            if len(common) > len(nearest_item.properties['path']):
                
                if self.nearest_item:
                    if len(common) > len(self.nearest_item.properties['path']):
                        self.nearest_item = item
                else:
                    self.nearest_item = item
                    
                    
            
                return common
      
        return None
        
        
    def search_projects(self,root=None,nearest=None):
        """walks projects trying to match a item to self.path 
        if you have your projects setup funky it might case a infinate loop"""

        if nearest is None:
            properties = {'name':'Name','type':'Type','path':''}
            nearest = projects.Project_Item(properties=properties)
            
        if root is None:
            root = self.root
        
        #print root.properties
        try:
            root.check_children()
            
        except:
            pass
            #return None
        
        match = None
        for item in root.children:
            if item.properties['path']:
                
                
                item_path = item.properties['path']
                new_common_prefix = self.compare_common_prefix(item,nearest)
                
                if new_common_prefix:
                    #print new_common_prefix
                    if new_common_prefix == self.path:
                        match = item
                        break
                    else:
                        match = self.search_projects(item,item)
                        if match:
                            break
                        
                        else:
                            match = None
                        
                
                else:
                    match = None
                 
            
            else:
                match = self.search_projects(item,nearest)
                if match:
                    break
                else:
                    match = None
                    
                
        return match
        
        
