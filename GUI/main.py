import sys
import os
import cv2
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QLibraryInfo

sys.path.append('../')
from tools.camaralib import take_stokes


os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)

exposure_time = 5000
N = 1
class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        
        # Carga GUI diseñado
        loadUi('gui.ui',self)       
        
        #Muestra imagen
        self.start_recording(self) 

        #Muestra GUI
        self.show()
    
    def start_recording(self, label):
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_image)
        timer.start(500)
        self.update_image()    

    def update_image(self):
        #Capturar Stokes
        S = take_stokes(exposure_time, N)

        #S0 normalizacion
        S0 = (S[:,:,:,0]//2).astype(np.uint8)

        #Formato Array to PixMap
        h,w,_ = S0.shape
        S0QIMG = QImage(S0, w, h, 3*w, QImage.Format_RGB888)
        pixmap = QPixmap(S0QIMG)
        self.S0.setPixmap(pixmap) 

def main():
    app = QApplication(sys.argv)
    instance = Ui()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()        
