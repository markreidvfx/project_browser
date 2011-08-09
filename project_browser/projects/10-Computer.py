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
import platform
import string
import copy

content_dirs = [{'name':'Directory Contents','relative_paths':[{'path':'','recursive':False}],'default':True},
                {'name':'All Footage','relative_paths':[{'path':'','recursive':True}],}]

Directory ={
'name':None,
'type':'Directory',
'subdirectories':[{'path':'','properties':'self'}],
'recursive':False,
'content_dirs':content_dirs
}

RootDirectory = {
'name':None,
'type':'RootDirectory',
'ignore':['[.].*'],
'subdirectories':[{'path':'','properties':Directory}],
'content_dirs':content_dirs
}

HardDrive = {
'name':None,
'type':'HardDrive',
'ignore':['[.].*'],
'subdirectories':[{'path':'','properties':Directory}],}

Project = {
'name':"Computer",
'type':'Computer',
'paths':['/'],
'ignore':['[.].*'],   
'subdirectories':[{'path':'','properties':RootDirectory}],
'icon':'computer'
}


if platform.system() == 'Windows': #show harddrive if windows
    drives = []
    for c in string.uppercase:
        drive_path = c + ':\\'
        if os.path.isdir(drive_path):
            item_data = copy.deepcopy(HardDrive)
            item_data['name'] = drive_path
            item_data['paths'] = [drive_path]
            item_data['icon'] = 'drive-harddisk'
            drives.append(item_data)
                          
    #HardDrive['subdirs'] = drives
    
    Project['paths'] = None
    Project['subdirectories'] = None                 
    Project['children'] = drives
    
elif platform.system() == 'Darwin':#Hide yucky system files
    
    RootDirectory['ignore'].extend(['dev','cores','bin','net','private','Keyboard','Network'])
    Project['subdirectories'] = [{'path':'','properties':RootDirectory}]
                           
if __name__ == '__main__':
    print Project