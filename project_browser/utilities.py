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
import sys
import platform

from timeout_process import launch_process

def find_executable_path(name):
    """search system path and included packages (if available) for executable"""
    names = [name.lower()]
    seperator=':'
    if platform.system() == 'Windows':
        names.append(name.lower() + '.exe')
        seperator = ';'
        
    executable = None
    
    executable = packaged_executable(names)
    if executable:
        return executable
    
    PATH = 'PATH'
    
    if os.environ.has_key(PATH):
        executable = search_env_variable(os.environ[PATH],names,seperator)
        
        
    
        
    return executable


def packaged_executable(names):
    """search included packages for executable"""
    
    dirs = ['Program Files/FFmpeg/bin','Program Files/ImageMagick']
    
    for path in dirs:
        if os.path.exists(path):
            executable = search_dir(path,names)
            if executable:
                return executable
            
    return None
    
    




def search_env_variable(var,names,seperator=':'):
    """search system path for executable and return it"""

    for dirname in var.split(seperator):
        if os.path.exists(dirname):
            executable =  search_dir(dirname,names)
            if executable:
                return executable
    return None

def search_dir(dirname,names):
    
    """search a directory for any item in names and return it"""
    for filename in os.listdir(dirname):
        #print filename
        if filename.lower() in names:
            return os.path.join(dirname,filename)
        
    return None
    
            
def find_mime_types_file():
    """find the included mime.types file which list file formats and their extensions"""
    default_file = os.path.join(os.path.dirname(__file__),'mime.types')
    return default_file


def find_image_dir():
    
    """find project browsers images directory"""
    default_dirs = ['images',os.path.join(os.path.dirname(__file__),'images')]
    
    for path in default_dirs:
        if os.path.exists(path):
            return path
    return None

def find_project_configuration_dirs():
    """find available project directories"""
    
    
    default_dirs = ['projects',os.path.join(os.path.dirname(__file__),'projects')]
    
    dir_list = []
    for path in default_dirs:
        if os.path.exists(path):
            
            if os.path.abspath(path) in dir_list:
                pass
            else:
                dir_list.append(os.path.abspath(path))
            
    
    return dir_list

def pretty_filesize(bytes):
    if bytes >= 1073741824:
        return str(bytes / 1024 / 1024 / 1024) + ' GB'
    elif bytes >= 1048576:
        return str(bytes / 1024 / 1024) + ' MB'
    elif bytes >= 1024:
        return str(bytes / 1024) + ' KB'
    elif bytes < 1024:
        return str(bytes) + ' bytes'


def detect_desktop_environment():
    """Detect Current Desktop Environment"""
    if platform.system() == 'Windows':
        return 'Windows'
    elif  platform.system() == "Darwin":
        return 'Darwin'
    
    elif platform.system() == 'Linux':
        
        desktop_environment = 'generic'
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            desktop_environment = 'kde'
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            desktop_environment = 'gnome'
            
        
        return desktop_environment


def show_file_in_folder_cmd(path):
    """Generate the command to launch a native file browser and select it if it can"""
    desktop_environment = detect_desktop_environment()
    
    dirname = path
    if os.path.isfile(path):
        dirname = os.path.dirname(path)
    
    if desktop_environment == 'Windows':
        cmd = ['explorer.exe','/select,', path ]
        
    elif  desktop_environment == "Darwin":
        
        cmd = ['/usr/bin/osascript']
        cmd.extend(['-e', 'tell application "Finder"'])
        cmd.extend(['-e','activate'])
        cmd.extend(['-e','select POSIX file "%s"' % path])
        cmd.extend(['-e','end tell'])
        
    elif desktop_environment == 'gnome':
        cmd = ['xdg-open',dirname]
        
    elif desktop_environment == 'kde':
        cmd = ['konqueror', '--select',path]
        
    else:
        cmd = ['xdg-open',dirname]
        
    return cmd


def filebrowser_name():
    
    """return a pretty name for the native file browser"""
    desktop_environment = detect_desktop_environment()
    
    if desktop_environment == 'Windows':
        return "explorer"
    
    elif  desktop_environment == "Darwin":
        return 'finder'
    
    elif desktop_environment == 'gnome':
        return "nautilus"
    
    elif desktop_environment == 'kde':
        return 'konqueror'
    
    else:
        return 'file browser'

def show_file_in_folder(path):
    """show file in native file browser and select it if supported"""
    cmd = show_file_in_folder_cmd(path)
    
    launch_process(cmd)
if __name__ == '__main__':
    
    print find_executable_path('ffmpeg')
    print find_executable_path('fFprobe')
    print find_executable_path('Convert')
    print find_executable_path('identify')
    
    show_file_in_folder(find_executable_path('ffmpeg'))