#import PySpin
import sys
import os
import cv2
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QLibraryInfo

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        
        # Carga GUI diseñado
        loadUi('gui.ui',self)       
        
        
        #Muestra GUI
        self.show()
      
def main():
    app = QApplication(sys.argv)
    instance = Ui()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()        
