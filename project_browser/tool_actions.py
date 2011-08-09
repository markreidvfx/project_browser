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

import utilities
import flipbook_tool

def content_treeview_contextmenu_actions():
    
    
    actions =[]
    
    actions.append({'name':"Show in %s" % utilities.filebrowser_name().capitalize(),'func':show_content_in_file_browser})
    actions.append(None)
    actions.append({'name':"Copy",'func':copy_content_path})
    actions.append(None)
    actions.append({'name':"Flipbook",'func':flipbook})
    
    
    
    return actions

def show_content_in_file_browser(project_item,file_items):
    print 'showing in finder'
    print project_item,file_items
    
    path = file_items[0].content.nice_path()
    utilities.show_file_in_folder(path)

def copy_content_path(project_item,file_items):
    import gui_utilities
    
    paths = []
    
    string = ""
    
    for item in file_items:
        
        path = item.content.path()
        
        paths.append(path)
        #string += '%s\n' % path
        #paths.append(path)
    
    print 'copying content path to clipboard'
    print string
    
    gui_utilities.copy_string_to_clipboard('\n'.join(paths))
    
    
def flipbook(project_item,file_items):
    
    print 'flipbooking'
    #reload(flipbook_tool)
    flipbook_tool.launch_flipbook_tool(file_items)
    