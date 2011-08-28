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

import OpenEXR
import Imath
import array
from StringIO import StringIO

class Point(object):
    """Point is a 2D point, with members *x* and *y*."""
    def __init__(self, x, y):
        self.x = x;
        self.y = y;
    def __repr__(self):
        return repr((self.x, self.y))
    
    
class Box(object):
    """Box is a 2D box, specified by its two corners *min* and *max* """
    def __init__(self, min = None, max = None):
        self.min = Point(min.x,min.y)
        self.max = Point(max.x,max.y)
        
    def width(self):
        return self.max.x - self.min.x + 1
    
    def height(self):
        return self.max.y - self.min.y + 1
    
    def __repr__(self):
        return repr(self.min) + ',' + repr(self.max)
    
class Scanline(object):
    
    def __init__(self,y,start,end,data):
        self.y = y
        self.start = start
        self.end = end
        self.data = data
        
        
    def tolist(self):
        return self.data.tolist()
    
    def firstPixel(self):
        first = Point(None,None)
        
        for i,p in enumerate(self.data):
            
            if p == 0:
                pass
            
            else:
                first.x = i  + self.start
                first.y = self.y
                
                break

        return first
    
    def lastPixel(self):
        
        last = Point(None,None)
        
        for n in xrange(len(self.data)):
            
            i = len(self.data)-1 - n
            
            p = self.data[i]
            
            if p == 0:
                pass
            else:
                last.x = i + self.start
                last.y = self.y
                
                break
        
        return last
            
    def firstLastPixel(self):
        
        first = self.firstPixel()
        last = Point(None,None)
        if first.x:
            last = self.lastPixel()
            
            
        return first,last
            
    

class Channel(object):
    """Channel is EXR Channel Data, name is the name of the channel,data is string float data, header is the exr header"""
    
    def __init__(self,name,data,header):
        
        self.name = name
        self._data =data
        self.data = None
        #self.data = array.array('f',data)
        self.data_window = Box(header['dataWindow'].min,header['dataWindow'].max)
        self.display_window = Box(header['displayWindow'].min,header['displayWindow'].max)
        
    def _convert_data_to_array(self):
        self.data = array.array('f',self._data)
        del self._data
        
    def dataWidth(self):
        return self.data_window.width()
    
    def dataHeight(self):
        return self.data_window.height()
    
    def width(self):
        return self.display_window.width()
    
    def height(self):
        return self.display_window.height()
    
    
    
    def inDataWindow(self,x,y):
        """returns True if x,y coordinate is in the data window"""
        
        if y >= self.data_window.min.y and y <= self.data_window.max.y:
            if x >= self.data_window.min.x and x <= self.data_window.max.x:
                return True
            
        return False
    
    def scanlineInDataWindow(self,y,start,end):
        """returns True if scanline intersects the data window"""
        
        if y >= self.data_window.min.y and y <= self.data_window.max.y:
            
            if start < self.data_window.max.x and end > self.data_window.min.x:
                
            
                return True
            
        return False
    
    def pixelDataIndex(self,x,y):
        """returns the data index for a pixel at a coordinate"""
        if self.inDataWindow(x, y):
            d_x =  x - self.data_window.min.x
            d_y =  y -self.data_window.min.y
            i = (self.dataWidth() * d_y) + d_x
            
            return i

        else:
            raise Exception("not in data window")
        
    def pixelAt(self,x,y):
        """returns the pixel value at a coordinate"""
        #print self.data_window,x,y
        if self.inDataWindow(x, y):
            d_x =  x - self.data_window.min.x
            d_y =  y -self.data_window.min.y
            i = (self.dataWidth() * d_y) + d_x
            
            if not self.data:
                self._convert_data_to_array()
            #print i
            return self.data[i]
        else:
            
            return 0.0
        
    def pixelScanLine(self,y,start,end):
        """returns a scanline array at y between start and end"""
        data = array.array('f',[])
        #print end - start + 1 
        if self.scanlineInDataWindow(y,start,end):
            
            head = self.data_window.min.x - start
            tail = end - self.data_window.max.x
            
            #print head,tail
            
            ds_x = self.data_window.min.x
            de_x = self.data_window.max.x

            if head < 0 :
                
                ds_x = self.data_window.min.x - head 
                
                head = 0
                
            if tail < 0:
                de_x  = self.data_window.max.x + tail
                tail = 0
                
            ds_i = self.pixelDataIndex(ds_x, y)
            de_i = self.pixelDataIndex(de_x, y)
                
            for i in xrange(head):
                data.append(0.0)
                
            if not self.data:
                self._convert_data_to_array()
            #print ds_i,de_i+1
            data.extend(self.data[ds_i:de_i+1])
                
                
            for i in xrange(tail):
                data.append(0.0)
                
        
        else:
            for i in xrange(start,end+1):
                data.append(0.0)
            
        return Scanline(y,start,end,data)
               
            
    def pixelBox(self,box):
        """returns a array of pixels the are in containing bounding box"""
        data = array.array('f',[])
        
        args = []
        for h in xrange(box.height()):
            y = h + box.min.y
            
            scanline = []
            
            scanline = self.pixelScanLine(y,box.min.x,box.max.x)

            data.extend(scanline.data)
            
        return data


def create_channel(item):
    
    name = item[0]
    data = item[1]
    header = item[2]
    
    
    c = Channel(name,data,header)
    
    return c

def box_check(box):
    
    
    new_box = Box(box.min,box.max)
    
    for item in [new_box.min,new_box.max]:
        if item.x is None:
            item.x = 0
        if item.y is None:
            item.y = 0
            
    return new_box
  
        
    
    
    
    
              

class ExrImage(object):
    
    def __init__(self,fileIn=None):
        
        self.header = None
        self.data_window = None
        self.display_window = None
        
        self.channels = {}
        self.layers = {}
        
        if fileIn:
            self.read(fileIn)
        
        
        
        
        
    def read(self,fileIn):
        f = OpenEXR.InputFile(fileIn)
        header = f.header()

        self.setHeader(header)
        
        self.readAllChannels(f)
            
            
    def readAllChannels(self,inputFile):
        """Read all Exr channels and load them into channels and layers"""
        channels = self.header['channels'].keys()
        pt = Imath.PixelType(Imath.PixelType.FLOAT)
        
        data = inputFile.channels(channels,pt)
        
        for name,chan_data in zip(channels,data):
            
            c = Channel(name,chan_data,dict(self.header))
            
            self.addChannel(c)

         
    def addChannel(self,channel):
        """create a channel object for exr data and load them into channels and layers"""
        

        name =  channel.name
          
        self.channels[name] = channel
        
        if name in ['R','G','B','A']:
            if self.layers.has_key('RGBA'):
                self.layers['RGBA'].append(name)
                
            else:
                self.layers['RGBA'] = [name]                
        else:
            
            if name.count('.'):
                split_name = name.split('.')
                
                layer_name = '.'.join(split_name[:-1])
                
                if self.layers.has_key(layer_name):
                    self.layers[layer_name].append(name)
                else:
                    self.layers[layer_name] = [name]
            else:
                self.layers[name] = [name]
             
    def setHeader(self,header):
        
        self.header = header
        self.data_window = Box(header['dataWindow'].min,header['dataWindow'].max)
        self.display_window = Box(header['displayWindow'].min,header['displayWindow'].max)
        
        
    def width(self):
        return self.display_window.width()
    
    def height(self):
        return self.display_window.height()
    
    def dataWidth(self):
        return self.data_window.width()
    
    def dataHeight(self):
        
        return self.data_window.height()
            
            
    def write(self,fileOut,channels=None,displayWindow=None,dataWindow=None,half_float=True):
        
        new_channels = {}
        
        new_header = dict(self.header)
        new_header['channels'] = {}
        
        
        if dataWindow:
            roi = box_check(dataWindow)
        else:
            roi = box_check(self.data_window)
            
        if not channels:
            channels = self.channels.keys()
        
        for name in channels:
            chan = self.channels[name]
            
            new_channels[name] = chan.pixelBox(roi).tostring()
            
            new_header['channels'][name] = Imath.Channel(Imath.PixelType(OpenEXR.FLOAT))
            
            
        new_header['dataWindow'] = Imath.Box2i(Imath.point(roi.min.x,roi.min.y), Imath.point(roi.max.x,roi.max.y))
        
        
        o = fileOut
        if half_float:
            o = StringIO()
        
        out = OpenEXR.OutputFile(o,new_header)
        
        out.writePixels(new_channels)
        
        out.close()
        
        if half_float:
            o.seek(0)

            f = OpenEXR.InputFile(o)
    
            h = f.header()
            channels = h['channels'].keys()
            pt = Imath.PixelType(Imath.PixelType.HALF)
            
            data = f.channels(channels,pt)
            data_dict ={}
            for i,name in enumerate(channels):
                h['channels'][name] = Imath.Channel(Imath.PixelType(OpenEXR.HALF))
                data_dict[name] = data[i]

            out =  OpenEXR.OutputFile(fileOut,h)
    
            out.writePixels(data_dict)
            out.close()
            
    def getOptimzeRoi(self,channels=None):
        """returns optimal Roi Box object for channels specified 
        Note: this can be quite slow if you have a large image"""
        
        if not channels:
            channels = self.channels.keys()
        
        
        min_x,min_y = None,None
        max_x,max_y = None,None    
        box = self.data_window
        

        for h in xrange(self.dataHeight()):
            
            y = h  + self.data_window.min.y 

            for name in channels:
                chan = self.channels[name]
                scanline = chan.pixelScanLine(y,box.min.x,box.max.x)
                
                first,last = scanline.firstLastPixel()
                if first.x is None:
                    pass
                else:
                    #print first.x
                    if min_y is None:
                        min_x = first.x
                        min_y = y
                        
                        max_x = last.x
                        max_y = y
                        
                    else:
                        min_x = min(min_x,first.x)
                        max_x = max(last.x,max_x)
                        max_y = y
                        
                        
                    break
                        
            
                        
        return Box(Point(min_x,min_y),Point(max_x,max_y))
            
    
if __name__ == '__main__':
    import time
    
    fileIn1 = 'test_files/MultiChannel.singleTK.0001.exr_temp.exr'
    
    #fileIn = 'test_files/BA_046_001_Light_v0001_r0005.singleTK.0001.exr'
    start = time.time()
    exr1 = ExrImage(fileIn1)
    print 'File 1',time.time()-start,'secs'
    fileIn2 = 'test_files/MultiChannel.singleTK.0001.exr'
    start = time.time()
    exr2 = ExrImage(fileIn2)
    print 'File 2',time.time()-start,'secs'
    
    
    print exr1.channels['R'].pixelAt(1000,570)
    print exr2.channels['R'].pixelAt(1000,570)
    
    print len(exr1.channels['R'].pixelScanLine(570,0,1919).tolist())
    print len(exr1.channels['R'].pixelScanLine(570,1000,1919).tolist())
    print len(exr1.channels['R'].pixelScanLine(570,0,1000).tolist())
    print len(exr1.channels['R'].pixelScanLine(570,0,200).tolist())
    print 'testing roi'
    #for layer in ['RGBA']:
        #print layer,exr1.data_window,exr2.getOptimzeRoi2(exr2.layers[layer].keys()),exr2.getOptimzeRoi(exr2.layers[layer].keys())
    chans = ['R','G','B','A']
    start = time.time()
    roi = exr1.getOptimzeRoi(chans)
    print roi,time.time()-start,'secs'
    start = time.time()
    roi2 = exr2.getOptimzeRoi(chans)
    print roi2,time.time()-start,'secs'
    
    print 'testing roi on', len(exr2.channels.keys()),'channels'
    start = time.time()
    roi = exr2.getOptimzeRoi()
    print roi,time.time()-start,'secs'
        
        
    
    exr1.write(fileIn1 + '_test.exr',channels=['R','G','B','A'])
    exr2.write(fileIn2 + '_test.exr',channels=['R','G','B','A'])

    
    