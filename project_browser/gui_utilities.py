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

def register_resources():
    theme_resource = os.path.join(utilities.find_image_dir(),'themes.rcc')
    
    resources = [theme_resource]
    
    for item in resources:

        QResource.registerResource(item)
    
def set_theme():
    
    if not QIcon.themeName():
    
        QIcon.setThemeSearchPaths([':/themes/tango'])
        QIcon.setThemeName('Tango')
        
        
def draw_with_shadow(painter,paint_cmd,args,pen=True):
    painter.save()
    painter.save()
    
    shadow_color = QColor(0,0,0,128)
    if pen:
        painter.setPen(shadow_color)
        
    else:
        painter.setPen(Qt.NoPen)
        
    painter.setBrush(shadow_color)
    
    painter.translate(QPointF(1,1))
    paint_cmd(*args)
    painter.restore()
    paint_cmd(*args)
    painter.restore()
    
def fit_font(rect,font,string):
    if not string:
        string = ' '
    
    width = rect.width()
    height = rect.height()
    
    font.setPixelSize(float(height))
    
    fm = QFontMetricsF(font)
    text_width = fm.width(string)
    
    factor = width / float(text_width)
    if text_width > width:
        font.setPixelSize(font.pixelSize() * factor)
    return font

def message(message,title="Information",info=None,details=None):
    dialog = QMessageBox()
    
    dialog.setWindowTitle(title)
    dialog.setText(message)

    dialog.setIcon(QMessageBox.Information)
    if info:
        dialog.setInformativeText(info)
    if details:
        dialog.setDetailedText(details)
    
    
    
    dialog.exec_()
    
def error_message(message,title="Error Occurred",info=None,details=None):
    
    dialog = QMessageBox()
    
    dialog.setWindowTitle(title)
    dialog.setText(message)

    dialog.setIcon(QMessageBox.Critical)
    if info:
        dialog.setInformativeText(info)
    if details:
        dialog.setDetailedText(details)
        
        print details
    dialog.exec_()

def file_directory_dialog(default_dir=None):
    
    
    
    if not default_dir:
        default_dir = os.path.expanduser('~')
        
    elif not os.path.exists(default_dir):
        default_dir = os.path.expanduser('~')
        
        
    
    dialog = QFileDialog()
    
    
    dialog.setDirectory(default_dir)
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setViewMode(QFileDialog.Detail)
    
    if dialog.exec_():
        
        selected_files = []
        
        for item in dialog.selectedFiles():
            selected_files.append(str(QDir.toNativeSeparators(item)))
        return selected_files
    
    return None


def copy_string_to_clipboard(string):
    
    data = QMimeData()
    data.setText(string)
    app = QApplication.instance()
    
    app.clipboard().setMimeData(data)

    
    
if __name__ == '__main__':
    
    register_resources()
