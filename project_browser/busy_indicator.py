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

import sys
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *

import utilities


def get_indicator_pixmaps(width=64,height=64,color=None):
    
    if not color:
        color = QColor(102, 205, 170)

    pixmaps = []
    
    
    for angle in xrange(0,360,30):
        #print angle
    
        image = QPixmap(width,height)
        image.fill(Qt.transparent)
        
        painter = QPainter()
        painter.begin(image)
        
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = min([image.width(),image.height()])
        
        outerRadius = (width-1)*0.5
        innerRadius = (width-1)*0.5*0.38
        
        capsuleHeight = outerRadius - innerRadius
        if width > 32:
            capsuleWidth  =  capsuleHeight *.23 
        else: 
            capsuleWidth = capsuleHeight *.35
        
        capsuleRadius = capsuleWidth/2.0
        
        
        for i in xrange(12): 
            color.setAlphaF(1.0 - (i/12.0))
            
            painter.setPen(Qt.NoPen)
            
            painter.setBrush(color)
            painter.save()
    
            painter.translate(image.rect().center())
            painter.rotate(angle - i*30.0)
            
            painter.drawRoundedRect(-capsuleWidth*0.5, 
                                    -(innerRadius+capsuleHeight),
                                     capsuleWidth, capsuleHeight, 
                                     capsuleRadius, capsuleRadius)
            painter.restore()
                
                
        painter.end()
        
        
        pixmaps.append(image)
    
    
    return pixmaps


class Busy_QEdit(QLineEdit):
    
    def __init__(self,parent=None):
        super(Busy_QEdit,self).__init__(parent)
        
        self.angle = 0
        #self.color = QColor(102, 205, 170)
        self.color = QColor(125,161,200)
        self.delay = 100 
        
        self.timer_id = None
        
        
        
    def startAnimation(self):
        
        if not self.timer_id:
            #print 'starting timer'
            self.angle = 0
            self.timer_id = self.startTimer(self.delay)
        
        
    def stopAnimation(self):
        
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None
            self.update()

        
    def timerEvent(self,event):
        
        self.angle = (self.angle + 30) % 360

        self.update()
        
        QLineEdit.timerEvent(self,event)
        
    def contextMenuEvent(self,event):
        
        
        #QMenu.actions
        
        menu = self.createStandardContextMenu()
        
        actions = menu.actions()
        
        reveal_action = QAction("Show in %s" % utilities.filebrowser_name().capitalize(),self)

        
        self.connect(reveal_action, SIGNAL('triggered()'),self.reveal_path)
        action = menu.insertAction(actions[0],reveal_action)
        menu.insertSeparator(actions[0])
        #menu.addAction("Go to Location")
        menu.exec_(event.globalPos())
        
    def reveal_path(self):
        path = str(self.text())
        
        if os.path.exists(path):
        
            utilities.show_file_in_folder(path)
        
    def paintEvent(self,event):
        
        QLineEdit.paintEvent(self,event)
        if self.timer_id:
            self.paintBusy()
            
    def paintBusy(self):
        
        painter = QPainter()
        painter.begin(self)
        
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.height()
        outerRadius = (width-1)*0.5
        innerRadius = (width-1)*0.5*0.38
        
        capsuleHeight = outerRadius - innerRadius
        if width > 32:
            capsuleWidth  =  capsuleHeight *.23 
        else: 
            capsuleWidth = capsuleHeight *.35
        
        capsuleRadius = capsuleWidth/2.0
        
        
        rect = QRectF(self.rect())
        center = rect.center()
        y = center.y()
        x = rect.right() - outerRadius
        

        rect.moveLeft(rect.width() * .5)
        
        linearGradient = QLinearGradient(rect.bottomLeft(), rect.bottomRight())
        linearGradient.setColorAt(0.0, QColor(255,255,255,0))
        linearGradient.setColorAt(0.5, QColor(176,226,255,225))
        linearGradient.setColorAt(1.0, QColor(0,0,0,0))
        
        painter.setPen(Qt.NoPen)
        
        painter.setBrush(linearGradient)
        
        painter.drawRoundedRect(rect,10,10)
        
        for i in xrange(12):
            color = self.color
            
            color.setAlphaF(1.0 - (i/12.0))
            
            painter.setPen(Qt.NoPen)
            
            painter.setBrush(color)
            painter.save()
            
            painter.translate(x,y)
            painter.rotate(self.angle - i*30.0)
            
            painter.drawRoundedRect(-capsuleWidth*0.5, 
                                    -(innerRadius+capsuleHeight),
                                     capsuleWidth, capsuleHeight, 
                                     capsuleRadius, capsuleRadius)
            painter.restore()
            
        painter.end()
    


class Busy_Indicator_Widget(QWidget):
    
    def __init__(self,parent=None):
        super(Busy_Indicator_Widget,self).__init__(parent)
        
        self.angle = 0
        self.color = QColor(102, 205, 170)
        self.delay = 100 
        
        self.timer_id = None
        #self.isRunning = False

        #self.setM
        
        #self.startTimer(self.delay)
        #self.timer = QTimer()
        #self.connect(self.timer, SIGNAL(' timeout ()'),self.timerEvent)
        #self.timer.start(300)
        
    def startAnimation(self):
        
        if not self.timer_id:
            #print 'starting timer'
            self.angle = 0
            self.timer_id = self.startTimer(self.delay)
        
        
    def stopAnimation(self):
        
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None
            self.update()

        
    def timerEvent(self,event):
        
        self.angle = (self.angle + 30) % 360

        self.update()
        
    def sizeHint(self):
        return QSize(20,20);
        
    def paintEvent(self,event):
        
        
        painter = QPainter()
        painter.begin(self)
        
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = min([self.width(),self.height()])
        
        outerRadius = (width-1)*0.5
        innerRadius = (width-1)*0.5*0.38
        
        capsuleHeight = outerRadius - innerRadius
        if width > 32:
            capsuleWidth  =  capsuleHeight *.23 
        else: 
            capsuleWidth = capsuleHeight *.35
        
        capsuleRadius = capsuleWidth/2.0
        
        
        if self.timer_id:
        
            for i in xrange(12):
                color = self.color
                
                color.setAlphaF(1.0 - (i/12.0))
                
                painter.setPen(Qt.NoPen)
                
                painter.setBrush(color)
                painter.save()
    
                painter.translate(self.rect().center())
                painter.rotate(self.angle - i*30.0)
                
                painter.drawRoundedRect(-capsuleWidth*0.5, 
                                        -(innerRadius+capsuleHeight),
                                         capsuleWidth, capsuleHeight, 
                                         capsuleRadius, capsuleRadius)
                painter.restore()
        else:
            for i in xrange(12):
                #color = self.color
                
                #color.setAlphaF(1.0 - (i/12.0))
                color = QColor(0,0,0)
                color.setAlphaF(.2)
                
                painter.setPen(Qt.NoPen)
                
                painter.setBrush(color)
                painter.save()
    
                painter.translate(self.rect().center())
                painter.rotate(self.angle - i*30.0)
                
                painter.drawRoundedRect(-capsuleWidth*0.5, 
                                        -(innerRadius+capsuleHeight),
                                         capsuleWidth, capsuleHeight, 
                                         capsuleRadius, capsuleRadius)
                painter.restore()
            
            
        painter.end()
            
            
            