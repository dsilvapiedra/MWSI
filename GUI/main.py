import sys
import os
import cv2
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QLibraryInfo
from PyQt5.QtMultimedia import QCameraInfo, QCamera, QCameraImageCapture

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
        
        self.cap = cv2.VideoCapture(0)
        
        #Muestra imagen
        self.start_recording(self) 

        #Muestra GUI
        self.show()
    
    def start_recording(self, label):
        #Cronómetro
        timer = QtCore.QTimer(self)
        
        #Conexión
        timer.timeout.connect(self.update_image)
        
        #Comienzo
        timer.start(0)

        #Actualización
        self.update_image()    

    def update_image(self):
        #Captura imagen
        ret, frame = self.cap.read()

        #Dimensiones imagen
        h, w, _ = frame.shape

        #Formato imagen
        S0QIMG = QImage(frame, w, h, QImage.Format_RGB888)
        pixmap = QPixmap(S0QIMG)

        #Plot
        self.S0.setPixmap(pixmap)
        

def main():
    app = QApplication(sys.argv)
    instance = Ui()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()        
