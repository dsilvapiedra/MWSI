import sys
import os
import cv2
import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QLibraryInfo
from simple_pyspin import Camera

sys.path.append('../')
from tools.stokeslib import polarization_full_dec_array, calcular_stokes
from tools.camaralib import runcmd



os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)

exposure_time = 5000
N = 1
decimador = 2
class Ui(QMainWindow):
    def __init__(self, cam):
        super(Ui, self).__init__()

        #Objeto cámara
        self.cam = cam

        # Carga GUI diseñado
        loadUi('gui.ui',self)      
            
        #Inicializa Cámara
        self.start_cam(self)

        #Configura Cámara
        self.config_cam(self, exposure_time, N)

        #Muestra imagen
        self.start_recording(self) 

        #Espera teclas movimiento
        self.move_cam(self)

        #Espera boton captura
        self.capture_listen(self)

        #Muestra GUI
        self.show()

    def start_cam(self, label):

        #Exposicion
        self.cam.ExposureAuto = 'Off'
    	
        #Formato
        self.cam.PixelFormat = "BayerRG8"

        #Inicia cámara
        self.cam.start()

    def config_cam(self, label, exposure_time, N):
        
        #Tiempo de exposicion
        self.cam.ExposureTime = exposure_time # microseconds

        #Número de promedios
        self.N = N

    def start_recording(self, label):   	
        timer = QtCore.QTimer(self)
        
        #Conexión
        timer.timeout.connect(self.update_image)
        timer.start(0)
        self.update_image()    

    def update_image(self):
        #Captura imagen
        img = self.cam.get_array()

        #Medibles
        I90, I45, I135, I0 = polarization_full_dec_array(img)

        #Stokes
        S0, S1, S2 = calcular_stokes(I90, I45, I135, I0)

        #Imagen de intensidad
        S0 = (S0[::decimador,::decimador,:]//2).astype(np.uint8)
        
        #Formato Array to PixMap
        h, w, _ = S0.shape
        S0QIMG = QImage(S0, w, h, QImage.Format_RGB888)
        pixmap = QPixmap(S0QIMG)

        #Plot
        self.S0.setPixmap(pixmap)
    def move_up(self):
        runcmd("cd ../; python3 motor_control_ssh.py Y B", verbose=True)
    def move_down(self):
        runcmd("cd ../; python3 motor_control_ssh.py Y F", verbose=True)
    def move_left(self):
        runcmd("cd ../; python3 motor_control_ssh.py X B", verbose=True)
    def move_right(self):
        runcmd("cd ../; python3 motor_control_ssh.py X F", verbose=True)
   
    def move_cam(self, label):
        up_btn = self.up_btn
        up_btn.clicked.connect(self.move_up)
        
        dwn_btn = self.up_btn
        dwn_btn.clicked.connect(self.move_down)
        
        left_btn = self.up_btn
        left_btn.clicked.connect(self.move_left)
        
        right_btn = self.up_btn
        right_btn.clicked.connect(self.move_right)
    
    def auto_capture(self):
        runcmd("cd ../; python3 capturar_muestra.py", verbose=True)

    def capture_listen(self, label):
        capture_btn = self.capture_btn
        capture_btn.clicked.connect(self.auto_capture)

def main(cam):
    app = QApplication(sys.argv)
    instance = Ui(cam)
    app.exec_()

if __name__ == "__main__":

    #Inicia GUI
    with Camera() as cam:
        main(cam)      
    
    #Detener cámara
    cam.stop()  

    #Salir
    sys.exit()
