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
import re

from pprint import pprint

from timeout_process import timeout_process

import utilities


def get_convert():
    executable = utilities.find_executable_path('convert')
    
    assert executable
    return executable

def get_identify():
    executable = utilities.find_executable_path('identify')
    
    assert executable
    return executable


def format_info(source,format,use_stdin=False):
    
    if use_stdin:
        path = '-'
        stdin = source
    else:
        path = source
        stdin = None

    cmd = [get_convert(),'-ping',path,'-format' , format, 'info:-']
    stdout,stderr = timeout_process(cmd, stdin=stdin)
    
    
    
    
    
    return stdout,stderr
    
    
def get_image_properties(source,use_stdin=False):

    format = '%[width] %[height] %[depth] %[colorspace] %[channels] %C %Q\n%[*]'
    
    stdout,stderr = format_info(source,format,use_stdin=use_stdin)
    
    
    if not stdout:
        raise Exception("failed to get Image Properties")
    
    p = {}
    
    splitlines = stdout.splitlines()
    p['width'],p['height'],p['depth'],p['colorspace'],p['channels'],p['compression_type'],p['compression_quality'] = splitlines[0].split()
    
    
    for line in splitlines[1:]:
        if line:
        
            split = line.split('=')
            
            key = split[0]
            
            value = '='.join(split[1:])
            p[key] = value
            
            
    for key in ['width','height','depth']:
        if p.has_key(key):
            p[key] = int(p[key])
    
    
    return p


def make_thumbnail(source,width=None,height=None,use_stdin=False):
    
    scale = .05
    
    default_width = int(1920 * scale)
    default_height = int(1080 * scale)
    
    
    if not width:
        width = default_width
        
    if not height:
        height = default_height
        
    if use_stdin:
        path = '-'
        stdin = source
        ext = None
        
    else:
        
        name,ext = os.path.splitext(source)
        ext = ext.lower()
        path = source
        stdin = None
        
    
    
    resize = '%dx%d' % (width,height)
    
    
    cmd = [get_convert(),path,'-gravity', 'Center','-background','black',
           '-thumbnail', resize,'-strip','-extent',resize,'-colorspace','RGB',  'png:-']
    
    
    if ext in ['.dpx']:
        cmd = [get_convert(),path,'-gravity', 'Center','-background','black',
           '-thumbnail', resize,'-strip','-extent',resize,'-set','colorspace','RGB',  'png:-']
        
    
    
    stdout,stderr = timeout_process(cmd, stdin=stdin)
    
    return stdout
           