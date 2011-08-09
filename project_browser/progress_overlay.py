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

import traceback

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *

import traceback




class Progress_Overlay_Painter(QObject):
    def __init__(self,parent=None):
        pass
        #super(Progress_Overlay_Painter,self).__init__(parent)
        
        self.message = ''
        self.details = ''
        
        self.progress_min = 0
        self.progress_max = 100
        
        self.progress_value = 0
        
        self.last_progress_range = [0,0]
        
        #self.continus  = False
        
        self.angle = 0
        
        self.textColor = QColor(255,255,255,255)
        
        self.progressColor = QColor(125,161,200)
        
        self.bgColor = QColor(0,0,0,60)
        self.spinner_color = QColor(39,144,255)
        self.progressColor = self.spinner_color
        
        self.visible = False
        
        
    def set_message(self,message,details=''):
        self.message = message
        self.details = details
    
    def set_progress(self,progress_min,progress_max,progress_value):
        self.progress_min = float(progress_min)
        self.progress_max = float(progress_max)
        self.progress_value = float(progress_value)
        
        if not [self.progress_min,self.progress_max] == self.last_progress_range:
            self.last_progress_range =  [self.progress_min,self.progress_max]
            self.set_angle(0)
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def set_angle(self,value):
        self.angle = value
        
    def get_angle(self):
        return self.angle
    
    def get_progress_percent(self):
        
        if self.progress_min == 0 and self.progress_max == 0:
            return None
        
        else:
            percent = (self.progress_value - self.progress_min) / (self.progress_max - float(self.progress_min))
            return int(100 * percent)


    def set_paint_device(self,paint_device):
        
        self.paint_device = paint_device
        
    def draw_center(self,rect):
        self.painter.drawLine(rect.center().x(),rect.top(),
                         rect.center().x(),rect.bottom())
        
        self.painter.drawLine(rect.left(),rect.center().y(),
                         rect.right(),rect.center().y())
        
    def fit_font(self,rect,font,string):
        if not string:
            string = ' '
        
        width = rect.width()
        height = rect.height()
        
        font.setPixelSize(float(height))
        
        fm = QFontMetricsF(font)
        
        text_width = fm.width(string)
        
        factor = width / float(text_width)
        #print factor
        if text_width > width:
            font.setPixelSize(font.pixelSize() * factor)
        
        return font
    
    def draw_shadow(self,draw_cmd,args,pen=False):
        
        self.painter.save()
        
        
        self.painter.save()
        
        shadow_color = QColor(0,0,0,128)
        if pen:
            self.painter.setPen(shadow_color)
            
        else:
            self.painter.setPen(Qt.NoPen)
            
        self.painter.setBrush(shadow_color)
        
        self.painter.translate(QPointF(1,1))
        draw_cmd(*args)
        
        self.painter.restore()
        
        draw_cmd(*args)
        
        self.painter.restore()
        
        
    def draw_percent(self):
        percent = self.get_progress_percent()
        
        if percent != None:
            self.painter.save()
            
            self.painter.setPen(self.progressColor)
            self.painter.setBrush(self.progressColor)
            
    
            percent_value = str(percent) + '%'
 
            font = QFont("Helvetica",25,QFont.Bold)
            self.painter.setFont(self.fit_font(self.percent_rect, font, percent_value))
            
            
            
            self.draw_shadow(self.painter.drawText,(self.percent_rect, Qt.AlignCenter,percent_value),pen=True)
            #self.painter.drawText(self.percent_rect, Qt.AlignCenter,percent_value)
            
            
            
            self.painter.restore()
   
    def draw_message(self):
        self.painter.save()
        
        
        self.painter.setPen(self.textColor)
        self.painter.setBrush(self.textColor)
        
        title_font = QFont("Helvetica",25,QFont.Bold)
        
        title_height = self.message_rect.height() * .1
        
        details_height = self.message_rect.height() * .25
        
        
        
        title_rect = QRectF(0,0,self.message_rect.width(),title_height)
        
        title_text = self.message
        
        title_font = self.fit_font(title_rect, title_font, title_text)
        
        details_height_font = self.message_rect.width() * .05
        

        details_font = QFont("Helvetica",details_height_font,QFont.Normal,)
        
        info = QFontInfo(details_font)
        
        
        
        details_font.setPointSizeF(details_height_font)
        
        details_font.setPixelSize(details_height_font)
        #title_rect.moveCenter(QPointF(self.message_rect.center()))
        
        details_rect = QRectF(0,0,self.message_rect.width(),details_height)
        
        details_text = self.details
        
        self.painter.setFont(details_font)
        
        
        new_details_rect = self.painter.boundingRect(details_rect, Qt.TextWordWrap, details_text)
        #print new_rect,details_rect
        
        
        new_details_rect.moveCenter(QPointF(self.message_rect.center()))
        
        new_details_rect.translate(0,title_rect.height())
        
        
        title_center_x = self.message_rect.center().x()
        
        title_center_y = new_details_rect.top() - title_rect.height()
        
        
        title_rect.moveCenter(QPointF(title_center_x,title_center_y))
        #title_rect
        
        #self.painter.scale(.5,.5)
        
        #self.painter.drawText(new_details_rect, Qt.TextWordWrap,details_text)
        
        args = (new_details_rect, Qt.TextWordWrap,details_text)
        self.draw_shadow(self.painter.drawText, args, pen=True)

        self.painter.setFont(title_font)
        
        
        #self.painter.scale(.5,.5)
        
        #self.painter.drawText(title_rect, Qt.AlignCenter,title_text)
        
        args = (title_rect, Qt.AlignCenter,title_text)
        
        self.draw_shadow(self.painter.drawText, args, pen=True)
        
        self.painter.restore()
        
    def draw_progress_spinner(self):
        self.painter.save()
        
        width = self.spinner_rect.width()
        outerRadius = (width-1)*0.5
        innerRadius = (width-1)*0.5*0.38
        
        capsuleHeight = outerRadius - innerRadius
        if width > 32:
            capsuleWidth  =  capsuleHeight *.23 
        else: 
            capsuleWidth = capsuleHeight *.35
        
        capsuleRadius = capsuleWidth/2.0
        
        
        
        
        for i in xrange(12):
            color = QColor(self.spinner_color)
            
            color_bg = QColor(100,110,115)
            
            
            percent = self.get_progress_percent()
            
            if percent != None:
                
                current_angle_precent = (i * 30.0) / 360.0
                
                current_value = percent / 100.0
                
                if current_angle_precent > current_value:
                    color = color_bg
                
            else:
                
                mix =  i/12.0
                
                color.setRedF((color.redF() * mix) + ( color_bg.redF() * (1-mix)) )
                color.setGreenF((color.greenF() * mix) + ( color_bg.greenF() * (1-mix)) )
                color.setBlueF((color.blueF() * mix) + ( color_bg.blueF() * (1-mix)) )
            #item(1.0 - (i/12.0))
            #color.setAlphaF(1.0 - (i/12.0))
            
            self.painter.setPen(Qt.NoPen)
            
            self.painter.setBrush(color)
            self.painter.save()
            
            self.painter.translate(self.spinner_rect.center())
            self.painter.rotate(self.angle + i*30.0)
            
            #self.painter.drawRoundedRect(-capsuleWidth*0.5, 
            #                       -(innerRadius+capsuleHeight),
            #                         capsuleWidth, capsuleHeight, 
            #                         capsuleRadius, capsuleRadius)
            
            args = (-capsuleWidth*0.5, 
                    -(innerRadius+capsuleHeight),
                     capsuleWidth, capsuleHeight, 
                     capsuleRadius, capsuleRadius)
            
            self.draw_shadow(self.painter.drawRoundedRect, args, pen=False)
            
            self.painter.restore()
            
        
        self.painter.restore()
    
    def paint_overlay(self):
        
        if self.visible:
            self.draw()
        
    def draw(self):
        
        self.painter = QPainter()
        
        
        if hasattr(self.paint_device, 'viewport'): # if drowing on any vew widget 
            self.painter.begin(self.paint_device.viewport())
        
        else:
            self.painter.begin(self.paint_device)
        
        self.painter.save()
        
        self.painter.setRenderHint(QPainter.Antialiasing)
        
        
        device_rect = self.paint_device.rect()
        
        
        aspect = 9.0/16.0
        
        overlay_width = device_rect.width() *.66
        
        overlay_height = overlay_width * aspect
        
        
        #overlay_height = overlay_height * device_rect.height() 
        
        
        vertical_spacing = .15
        
        if device_rect.height() - overlay_height < device_rect.height() * vertical_spacing:
            difference = device_rect.height() - overlay_height
            factor = vertical_spacing - difference/float(device_rect.height())
            
            overlay_width *= 1- factor
            overlay_height *= 1- factor
            
            
        if overlay_width < 100 or overlay_width < 100:
            self.painter.restore()
        
            self.painter.end()
            return None
            
        
        x_space = max((device_rect.width() * .25) * .5,(device_rect.height() * .25) * .5)
        y_space = x_space
        
        
        center = QPointF(self.paint_device.rect().center().x(),self.paint_device.rect().height() * .42)

        
        self.overlay_rect  = QRectF(0,0,overlay_width,overlay_height)
        self.overlay_rect.moveCenter(center)
    
        
        
        
        x_overlay_boarder = self.overlay_rect.width() * .02
        y_overlay_boarder = self.overlay_rect.height() * .02
        
        progress_message_ratio = .33
        
        p_width = (self.overlay_rect.width() * (1.0-progress_message_ratio)) - (x_overlay_boarder *2.0)
        
        
        
        progress_rect = self.overlay_rect.adjusted(x_overlay_boarder,y_overlay_boarder,
                                              -p_width,-y_overlay_boarder)
        
        
        
        p_width = (self.overlay_rect.width() * progress_message_ratio) + (x_overlay_boarder *3.0)
        #p_topR = progress_rect.topRight()
        
        
        self.message_rect = self.overlay_rect.adjusted(p_width,y_overlay_boarder,
                                             -x_overlay_boarder,-y_overlay_boarder)
        
        
        progress_spiner_ratio = .75
        
        ps_height = (progress_rect.height() * (1.0 -progress_spiner_ratio) - y_overlay_boarder)
        
        progress_spiner_center_rect = progress_rect.adjusted(x_overlay_boarder,y_overlay_boarder,
                                                      -x_overlay_boarder,-ps_height)
        
        
        spiner_radius = min(progress_spiner_center_rect.width(),progress_spiner_center_rect.height()) * .5
        
        
        #print spiner_radius
        spinner_center = progress_spiner_center_rect.center()
        
        
        self.spinner_rect = QRectF(0,0,spiner_radius*2,spiner_radius*2)
        
        self.spinner_rect.moveCenter(QPointF(progress_spiner_center_rect.center()))
        
        
        percent_border = 5
        
        
        
        y_pspace = progress_rect.bottom() - self.spinner_rect.bottom() - percent_border
        #print y_pspace
        
        
        percent_center_y = self.spinner_rect.bottom() + (y_pspace * .5) + percent_border
        
        self.percent_rect = QRectF(0,0,progress_rect.width(),y_pspace)

        percent_center = QPointF(self.spinner_rect.center().x(),percent_center_y)
        
        self.percent_rect.moveCenter(percent_center)
        
        
        self.painter.setPen(Qt.NoPen)
        self.painter.setBrush(self.bgColor)
        self.painter.drawRoundedRect(self.overlay_rect, 20, 20,)
        
        #self.painter.drawRoundedRect(progress_rect, 15, 15,)
        

        #self.painter.drawEllipse(self.spinner_rect)
        
        
        #self.painter.drawRoundedRect(self.message_rect,15,15)
        
        #self.painter.drawRoundedRect(self.percent_rect,15,15)
        
        #self.draw_center(self.message_rect)
        #self.draw_center(self.spinner_rect)
        
        self.draw_percent()
        self.draw_message()
        self.draw_progress_spinner()
        
        self.painter.restore()
        
        self.painter.end()



class Overaly_Test_Widget(QListWidget):
    
    def __init__(self,parent=None):
        super(Overaly_Test_Widget,self).__init__(parent)
        
        self.progress_overlay = Progress_Overlay_Painter()
        
        self.setAlternatingRowColors(True)
        
        self.progress_overlay.set_paint_device(self)
        
        for i in range(30):
            self.addItem(str(i+10000000000000000000))
        
        
    def paintEvent(self,event):
        super(Overaly_Test_Widget,self).paintEvent(event)
        
        
        self.progress_overlay.paint_overlay()
        
        
class Test_Widget(QWidget):
    
    
    def __init__(self,parent=None):
        super(Test_Widget,self).__init__(parent)
        
        self.overlayWidget = Overaly_Test_Widget()
        
        self.start_progressButton = QPushButton("start progress")
        self.start_busyindicatorButton = QPushButton("start Busy indicator")
        self.stop_button = QPushButton("stop")
        
        message = "Message Title"
        details = "This is a message of what the Progress Overlay is doing,lots of text is suppose to be able to go here so I'm typing alot just for fun, lets see if this will fit"
        self.overlayWidget.progress_overlay.set_message(message=message, details=details)
        layout = QVBoxLayout()
        
        buttonLayout = QHBoxLayout()
        
        layout.addWidget(self.overlayWidget)
        
        buttonLayout.addWidget(self.start_progressButton)
        buttonLayout.addWidget(self.start_busyindicatorButton)
        
        buttonLayout.addWidget(self.stop_button)
        
        
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
        
        self.timer_id = None
        self.delay = 200
        
        
        self.connect(self.start_progressButton, SIGNAL('clicked ()'),self.start_progress)
        self.connect(self.start_busyindicatorButton, SIGNAL('clicked ()'),self.start_busyindicator)
        self.connect(self.stop_button, SIGNAL('clicked ()'),self.stop_progress)
        
        self.busy = False
                     
                     
    def start_progress(self):
        self.overlayWidget.progress_overlay.show()
        self.overlayWidget.progress_overlay.angle = 0
        self.overlayWidget.progress_overlay.set_progress(0, 100, 0)
        self.busy = False
        self.startAnimation()
        
    def start_busyindicator(self):
        self.overlayWidget.progress_overlay.show()
        self.overlayWidget.progress_overlay.angle = 0
        self.overlayWidget.progress_overlay.set_progress(0, 0, 0)
        self.busy = True
        
        self.startAnimation()
        
    def stop_progress(self):
        self.overlayWidget.progress_overlay.hide()
        self.stopAnimation()
        viewport= self.overlayWidget.viewport()
        viewport.update()
        
    def startAnimation(self):
        
        if not self.timer_id:
            self.timer_id = self.startTimer(self.delay)
            
            
    def stopAnimation(self):
        
        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None

    def timerEvent(self,event):
        
        if self.busy:
            angle = self.overlayWidget.progress_overlay.angle
            self.overlayWidget.progress_overlay.angle = (angle + 30) % 360
        else:
            progress_value = self.overlayWidget.progress_overlay.progress_value
            self.overlayWidget.progress_overlay.set_progress(0, 100, ( progress_value + 1) % 100)
            
     

        
        
        #self.overlayWidget.repaint()
        #self.overlayWidget.update()
        #self.overlayWidget.setUpdatesEnabled(True)
        #self.overlayWidget.repaint(self.overlayWidget.rect())
        viewport= self.overlayWidget.viewport()
        viewport.update()
        
        #self.overlayWidget.repaint()



        #self.overlayWidget.t




def run_test():
    
    
    QResource.registerResource('images/themes.rcc')
    
    
    QIcon.setThemeSearchPaths([':/themes/tango'])
        
    QIcon.setThemeName('Tango')
    app = QApplication(sys.argv)
    main = Test_Widget()
    
    main.show()
    main.raise_()
    
    sys.exit(app.exec_())
    
    
if __name__ == '__main__':
    
    

    run_test()