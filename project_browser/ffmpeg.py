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


def get_ffprobe():
    ffprobe = utilities.find_executable_path('ffprobe')
    
    assert ffprobe
    return ffprobe

def get_ffmpeg():
    ffmpeg = utilities.find_executable_path('ffmpeg')
    assert ffmpeg
    return ffmpeg

def parse_ffmpeg_stderr_duration(output):     
    d = ''
    for line in output.splitlines():
        if line.count('Duration:'):
            d = line.replace('Duration:','')
            d = d.split('start:')
            d = d[0].replace(',','')
            d = d.rstrip().lstrip()
            break
    d = d.split(':')

    time = 0.0
    if d[0]:
        time += float(d[0]) * 60 * 60
    if d[1]:
        time += float(d[1]) *60
    if d[2]:
        time += float(d[2]) 
    return time

def decode_fraction(string):
    
    
    try:
        a,b = string.split('/')
        result = float(a) / float(b)
        return result
    
    except:    
        return None 

def decode_value(key,value):
    
    if value == 'N/A':
        return None
    
    elif key in ['height','width','nb_frames','index']:
        return int(value)
    
    elif key in ['duration','start_time']:
        return float(value)
    
    elif key in ['codec_time_base','time_base','r_frame_rate','avg_frame_rate']:
        
        return decode_fraction(value)
    
    else:
    
        return value
    
def parse_ffprobe_output(output):
    
    assert output
    pattern = re.compile("[[].*?[]].*?[[][/].*?[]]",re.DOTALL)
    
    section_list = pattern.findall(output)
    
    
    sections = []
    
    for item in section_list:
        key_list = item.splitlines()
        
        section = {}
        
        section['SECTION'] =  key_list[0].replace('[','').replace(']','')
        
        for line in key_list[1:-1]:
            key,value = line.split('=')
            
            section[key] = decode_value(key,value)
            
        sections.append(section)
        
    #pprint(sections)
       
    return sections
    
            
            
def get_video_stream(path):
    
    streams = get_streams(path)
    
    for stream in streams:
        
        if stream['codec_type'] == 'video':
            return stream
        
    else:
        return None

def slow_durations(path):
    
    cmd = [get_ffmpeg(),'-i',path,'-f','null',os.devnull]
    
    stdout,stderr = timeout_process(cmd,timeout=60)
    
    print stdout
    print stderr
    
    
def check_key(section,key):
    
    if section.has_key(key):
        if section[key] == None:
            pass
        else:
            return section[key]
    return None
  

def get_video_properties(path):
    
    """get all sorts of details about a video file, rate,duration,frames and resolution. also much much more"""
    video_stream = get_video_stream(path)
    
    rate = None
    duration = None
    frames = None
    size = (None,None)
    
    width = None
    height = None
    
    if not video_stream:
        return (rate,duration,frames,size)
    
    rate = check_key(video_stream,'r_frame_rate')
    duration = check_key(video_stream,'duration')
    frames = check_key(video_stream,'nb_frames')
    
    width = check_key(video_stream,'width')
    height = check_key(video_stream,'height')
    
    
    if width and height:
        size = (width,height)
        
        
    if not duration:
        output = get_ffmpeg_details(path)
        duration = parse_ffmpeg_stderr_duration(output)
        
        
    if not frames:
        if rate and duration:
            frames = int(duration*rate)
    
    
    video_stream['rate'] = rate
    video_stream['duration']  = duration
    video_stream['frames'] = frames
    video_stream['width'] = width
    video_stream['height'] = height
    
    
    return video_stream
    
    
def get_streams(path):
    
    cmd = [get_ffprobe(), '-show_streams',path]
    
    stdout,stderr = timeout_process(cmd,timeout=12)
    
    return parse_ffprobe_output(stdout)

def get_ffmpeg_details(path):
    
    cmd = [get_ffprobe(),path]
    
    stdout,stderr = timeout_process(cmd,timeout=12)
    
    return stderr


def frame_grab(path,frame,properties=None,format='png'):
    """grabs a still image form the video file at 'path' at specified frame.
    'properties' are the video file properites (from get_video_properties) if 
    you pass them in it won't recalculate them.
    'format' is the image format, options are ppm,png and mjpeg (for jpeg)"""
    
    if not properties:
        properties = get_video_properties(path)
        
    percent = frame / float(properties['frames'])
    
    
    return frame_grab_percent(path,percent,properties=properties,format=format)

def frame_grab_percent(path,percent=.5,properties=None,format='png'):
    """grabs a still image form the video file at 'path' at specified 'percent' (between 0-1).
    'properties' are the video file properites (from get_video_properties) if 
    you pass them in it won't recalculate them.
    'format' is the image format, options are ppm,png and mjpeg (for jpeg)"""
    
    if not properties:
        properties = get_video_properties(path)
    

    seconds = properties['duration'] * float(percent)
    
    return  frame_grab_seconds(path,seconds,format)

    
def frame_grab_seconds(path,seconds=0,format='png'):
    """grabs a still image from the video file at 'path' at specified 'seconds' in. 
    'format' is the image format, options are ppm,png and mjpeg (for jpeg)"""

    cmd = [get_ffmpeg(),'-ss',str(seconds),'-vframes','1','-i',path,'-f','image2','-vcodec', format,'-']
    
    
    stdout,stderr = timeout_process(cmd,timeout=12)
    
    
    return stdout
    
    
    
    