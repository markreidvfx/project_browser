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
from collections import defaultdict
import time
import ffmpeg
import imagemagick
import sequence
from project_browser import utilities

def return_none():
    return None

class File_Model_Item(object):
    def __init__(self,Content_Item=None,parent=None):
        self.parent_item = parent
        
        self.content =  Content_Item
        
        self.column_names = ['Path','Frames','Resolution','Kind','Created']
        
        self.data_loaded = ['Path','Kind']
        self.data_loading = []
        self.data_queued = []
        self._stop = False
        self.lock = None
        
        self.properties = defaultdict(return_none)

        self.children = []
        
        if isinstance(self.content,File):
            if not isinstance(self.content,VideoFile):
                self.data_loaded.append('Frames')
        
        if isinstance(self.content,FileSequence):
            self.data_loaded.append('Frames')
            for item in self.content:
                f = File_Model_Item(item,self)
                self.addChild(f)
                
    def stop(self):
        return self._stop
    
    def addChild(self,item):
        self.children.append(item)

    def parent(self):
        return self.parent_item
    
    def child(self, row):
        return self.children[row]

    def row(self):
        if self.parent_item:
            return self.parent_item.children.index(self)

        return 0
    
    def columnCount(self):
        return len(self.column_names)
    
    def childCount(self):
        
        if self.children:
            
            return len(self.children)
        
        return 0
    
    def dataReady(self,key):
        
        if key in self.data_loaded:
            return True
        return False
    def dataLoading(self,key):
        if key in self.data_queued:
            return True
        if key in self.data_loading:
            return True
        
        
        
        return False
    
    def data(self, column):
 
        key = self.column_names[column]
        d = self.get_data(key)
        return d
  
    def get_data(self,key):
        if self.content:
            if not self.properties[key]:
                
                if key == 'Path':
                    self.properties[key] = self.content.nice_name()
                    
                elif key == 'Kind':
                    self.properties[key] = self.content.mimetype()[0]
                    
                elif key == 'Frames':
                    self.properties[key] = self.content.frames()
                    
                elif key == 'Blame':
                    self.properties[key] = self.content.blame()
                    
                elif key == 'Resolution':
                    self.properties[key] = self.content.resolution()
                
                elif key == 'Created':
                    clean_time = time.strftime("%Y-%m-%d %H:%M",self.content.create_time())
                    self.properties[key] = clean_time
                    
                elif key == 'Url':
                    self.properties[key] = self.content.url()

        
        return self.properties[key]

    def sort_by(self,key,reverse=False):
        
        def sort_key(item):
            item.children.sort(key=sort_key,reverse=reverse)
            
            return item.get_data(key)
        
        self.children.sort(key=sort_key, reverse=reverse)
    


def get_create_time(path):
    return time.gmtime(os.path.getctime(path))

def get_owner(path):
    return 'Not Implemented'


class File(object):
    
    def __init__(self,dirname,basename,mimetype=None):
        self._dirname = dirname
        self._basename = basename
        self._mimetype= mimetype
        self._create_time = None
        self._blame = None
        self._common_prefix = None
        self._frames = 1
        self._properties = None
        self._size = None
        
    def __str__(self):
        return str(os.path.join(self.dirname(),self.basename()))
     
    def mimetype(self):
        return self._mimetype
        
    def basename(self):
        return self._basename
    
    def url(self):
        
        url = 'file://' + os.path.join(self._dirname,self._basename)
        return url
    
    def dirname(self):
        return self._dirname
    
    def range(self):
        return 1
    
    def size(self):
        
        return os.path.getsize(self.path())
    def pretty_size(self):
        
        return utilities.pretty_filesize(self.size())
    def resolution(self):
        return str(self.pretty_size())
    
    def pretty_range(self):
        return str(self.range())
    
    def frames(self):
        
        return int(self._frames)
    
    def nice_name(self):
        path = str(self.path())
        
        nice_name = path.replace(self.common_prefix(), '')
        
        nice_name = str(nice_name.lstrip(os.sep))
        #print '"%s"' % path
        #print '"%s"' % nice_name
        return nice_name
    
    def nice_path(self):
        return self.path()
    
    def path(self):
        return str(os.path.join(self.dirname(),self.basename()))
    def blame(self):
        if not self._blame:
            self._blame = get_owner(self.path())
        
        return self._blame
    
    
    def shake_path(self):
        return self.path()
        
        
    def create_time(self):
        if not self._create_time:
            self._create_time = get_create_time(self.path())
            
        return self._create_time
    
    def common_prefix(self):
        return self._common_prefix
    
    def set_common_prefix(self,path):
        self._common_prefix = str(path)
        
        
    def frame_num(self):
        
        
        seq = sequence.SeqString(self.basename())
        
        nums = seq.getNums()
        
        
        if nums:
            return nums[-1]
        
        else:
        
            return 1
    
        
    
        
        
class ImageFile(File):
    def __init__(self,dirname,basename,mimetype=None):
        super(ImageFile,self).__init__(dirname,basename,mimetype)
        self._width = None
        self._height = None
        self._depth = None
        
        
    def properties(self):
        if not self._properties:
            p = imagemagick.get_image_properties(self.path())
            self._properties = p
            self._width = p['width']
            self._height = p['height']
            self._depth = p['depth']
            
            
        return self._properties
    
    def resolution(self):
        
        return '%ix%i %ibit %s' % (self._width,self._height,self._depth,str(self.pretty_size()))
    
    
    def thumbnail(self,width=None,height=None,frame=None,indexF=None):
        return imagemagick.make_thumbnail(self.path(),width,height)

            
        
        
        
        


class VideoFile(File):
    def __init__(self,dirname,basename,mimetype=None):
        super(VideoFile,self).__init__(dirname,basename,mimetype)
        
        
        self._frames = 0
        self._rate = None
        self._duration = None
        
        self._size = None
        
        self._width = None
        self._height = None
        self._depth = 8
        
    def properties(self):
        
        if not self._properties:
            p = ffmpeg.get_video_properties(self.path())
            self._properties = p
            self._rate = p['rate']
            self._duration = p['duration']
            self._width = p ['width']
            self._height = p['height']
            self._frames = p['frames']

        
        return self._properties
    
    def resolution(self):
        fps = '%.2ffps' % (self._rate)
        return '%ix%i %s %s' % (self._width,self._height,fps,str(self.pretty_size()))
    
    def frames(self):
  
        return self._frames
    
    def pretty_range(self):
        return '1-%i' % self.frames()
    
    def thumbnail(self,width=None,height=None,frame=None,indexF=None):
        
        if indexF != None:
            percent= indexF
            
        elif frame != None:
            percent = frame / float(self.properties()['frames'])
        
        else:
            percent=.5
        
        image = ffmpeg.frame_grab_percent(self.path(), percent=percent, properties=self.properties())
        scaled_image = imagemagick.make_thumbnail(image,width=width,height=height,use_stdin=True)
        return scaled_image
        
        
    def frameF(self,indexF):
        
        return int(self.properties()['frames'] * indexF) + 1
        


class AudioFile(File):
    
    pass


class FileSequence(object):
    def __init__(self,dirname,sequence_object,mimetype=None):
        
        self._dirname = dirname
        
        self._sequence_object = sequence_object
        self._mimetype = mimetype
        
        basename,range = self._sequence_object.sequenceName()
        self._basename = basename
        self._range = range
        self._create_time = None
        self._blame = None
        self._common_prefix = ''
        
        self._width = None
        self._height= None
        self._depth = None
        
        self._properties = None
        #self._range = self._sequence_object.
        
    def __str__(self):
        return os.path.join(self.dirname(),str(self._sequence_object))
    
    def __len__(self):
        return self._sequence_object.__len__()
   
    def __getitem__(self,idx):
        return self._sequence_object[idx]
        
    def mimetype(self):
        return self._mimetype
        
    def dirname(self):
        return self._dirname
    
    def basename(self):
        return self._basename
    
    def range(self):
        return self._range
    
    def frames(self):
        return len(self._sequence_object)
    
    def indexF(self,value):
        
        index = int(len(self) * value)
        
        return self[index]
    
    def frameF(self,indexF):
        
        item = self.indexF(indexF)
        return item.frame_num()
    
    def resolution(self):
        return self.indexF(.5).resolution()
    
    
    def properties(self):
        
        if not self._properties:
            
            test_file = self.indexF(.5)
            
            p = test_file.properties()
            
            self._properties = p
            self._properties['frames'] = len(self)
            
        return self._properties
    
    def thumbnail(self,width=None,height=None,frame=None,indexF=None):
        
        if indexF != None:
            image = self.indexF(float(indexF))
        elif frame != None:
            
            image = self[frame]
        else:
            image = self.indexF(.5)
        
        return image.thumbnail(width=width,height=height)

    def nice_name(self):
        
        path = str(self.path())
        
        nice_name = path.replace(self.common_prefix(), '')
        
        nice_name = nice_name.lstrip(os.sep)
        
   
        return nice_name
    
    def pretty_range(self):
        
        return ','.join(self.range())
    
    def url(self):
        #print type(self._range)
        url = 'file://' + self.path()
        return url
    
    def nice_path(self):
        return self[0].nice_path()
    
    def path(self):
        
        #return self.shake_path()
        return os.path.join(self.dirname(),str(self._basename) + ' ' + self.pretty_range()  )
    
    def shake_path(self):
        
        padder = None
        for pad_item in ['#','@','*']:
            
            if self.basename().count(pad_item):
                padder = pad_item * self.basename().count(pad_item)
                break
                
        if padder:
            range = self.pretty_range()
            shake_padder = '@' * len(padder)
            shake_basename  = self.basename().replace(padder,range + shake_padder)
            
            return os.path.join(self.dirname(),shake_basename)
            
        else:
            return self.path()
    
    def blame(self):
        if not self._blame:
            test_file = self[0]
            self._blame = test_file.blame()
        
        return self._blame
    

        
    def create_time(self):
        if not self._create_time:
            test_file = self[0]
            self._create_time = test_file.create_time()
            
        return self._create_time
    
    def common_prefix(self):
        return self._common_prefix
    
    def set_common_prefix(self,path):
        self._common_prefix = str(path)
        


class ImageSequence(FileSequence):
    pass



