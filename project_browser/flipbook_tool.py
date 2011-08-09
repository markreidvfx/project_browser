import sys
import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *


import flipbook

DEFAULT_FLIPBOOK='Shake'
DEFAULT_PROXY='Base'


def get_proxy_levels():
    
    return ['Base','P1','P2']

class Flipbook_Tool_Widget(QDialog):  
    def __init__(self,parent=None):
        
        super(Flipbook_Tool_Widget,self).__init__(parent)
        
        
        self.setWindowTitle("Flipbook Tool")
        
        self.range_label = QLabel("Range:")
        self.range_lineEdit = QLineEdit()
        
        proxy_levels = get_proxy_levels()
        self.proxy_comboBox = QComboBox()
        self.proxy_comboBox.addItems(proxy_levels)
        self.proxy_comboBox.setCurrentIndex(proxy_levels.index( DEFAULT_PROXY))
        
        flipbooks = flipbook.get_avaible_flipbooks()
        
        
        self.flipbook_comboBox = QComboBox()
        self.flipbook_comboBox.addItems(flipbooks)
        
        self.flipbook_comboBox.setCurrentIndex(flipbooks.index(DEFAULT_FLIPBOOK))
        #self.flipbook_comboBox.setcu(DEFAULT_FLIPBOOK)
        
        self.flipbook_button = QPushButton('Flipbook')
        self.cancel_button = QPushButton('Cancel')
        
        
        self.connect(self.flipbook_button, SIGNAL('clicked()'),self.accept)
        self.connect(self.cancel_button, SIGNAL('clicked()'),self.reject)
        
        self.connect(self.flipbook_comboBox, SIGNAL('currentIndexChanged (const QString&)'),self.flipbook_change)
        self.connect(self.proxy_comboBox, SIGNAL('currentIndexChanged (const QString&)'),self.proxy_change)
        
        main_layout =  QHBoxLayout()
        main_layout.addWidget(self.range_label)
        main_layout.addWidget(self.range_lineEdit)
        main_layout.addWidget(QLabel("Proxy:"))
        main_layout.addWidget(self.proxy_comboBox)
        main_layout.addWidget(QLabel("Using:"))
        main_layout.addWidget(self.flipbook_comboBox)
        
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.flipbook_button)
        button_layout.addWidget(self.cancel_button)
        
        layout = QVBoxLayout()
        layout.addLayout(main_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def flipbook_change(self,current):
        
        DEFAULT_FLIPBOOK = str(current)
        
        if str(current) == 'RV':
           
            self.range_lineEdit.setEnabled(False)
        else:
            self.range_lineEdit.setEnabled(True)
    
    def proxy_change(self,current):
        DEFAULT_PROXY = str(current)
    
        
    def set_file_item(self,file_item):
        
        self.range_lineEdit.setText(str(file_item.content.pretty_range()))
    
    
    def get_options(self):
        
        
        options = {'flipbook':str(self.flipbook_comboBox.currentText()),
                   'range':str(self.range_lineEdit.text()),
                   'proxy':str(self.proxy_comboBox.currentText())
                   }
        
        return options
                   


        
        
def launch_flipbook_tool(file_items):
    
    dialog = Flipbook_Tool_Widget()
    first_item = file_items[0]
    dialog.set_file_item(first_item)
    
    if dialog.exec_():
        launch_flipbook(file_items,dialog.get_options())
        
    
def launch_flipbook(file_items,options):
    reload(flipbook)
    
    first_item = file_items[0]
    if options['flipbook'] == 'Shake':
        flipbook.shake_flipbook(first_item, options)
        
    elif options['flipbook'] == 'RV':
        flipbook.rv_flipbook(file_items, options)
        
        
        
        
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    

    main_widget = Flipbook_Tool_Widget()

    main_widget.show()
    main_widget.raise_()
    sys.exit(app.exec_())
    