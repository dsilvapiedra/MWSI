import PySpin
import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
from PIL import Image 
from simple_pyspin import Camera
from tools.camaralib import take_photo
from motor_control_ssh import ejecutar_comando_ssh
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

IMG_SAVE_PATH = 'stokes/'  
            
def main(input = None):

    # Bandera entrada
    if input is None:
        input = sys.argv[1]

    # Configuracion de la camara
    
    # Exposicion
    exposure_time = 5000
    
    # Numero de promedios
    N = 1

    #Decimador 
    decimador = 1

    #Magnificacion
    Mag = 22

    #Bandera de entrada
    name = "Sin.npy" if input else "S.npy"
    
    # Dimension sensor
    dim = (2048,2448)         
    
    #Angulos de polarizacion de entrada
    thetas_list = [0,60,120]  
    N_datos = len(thetas_list)

    #Matrices de estadísticas
    S_in_stat = np.zeros((dim[0]//2,dim[1]//2,3,3,N_datos), dtype=float)[::decimador,::decimador]
    
    for i, theta in enumerate(thetas_list):
        # Toma una foto
        print("Tomando foto...") 
        image_data = take_photo(exposure_time, N)   

        #Decodifica
        I90, I45, I135, I0 = stokeslib.polarization_full_dec_array(image_data)    
    
        #Stokes        
        S_in_stat[:,:,:,0,i], S_in_stat[:,:,:,1,i], S_in_stat[:,:,:,2,i] = stokeslib.calcular_stokes(I90, I45, I135, I0)
        
        # Guarda imagenes
        print("Guardando imagen...")
        im_S0 = cv2.cvtColor(cv2.normalize(S_in_stat[:,:,:,0,i], None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1),cv2.COLOR_BGR2RGB)
        im_S1 = cv2.cvtColor(cv2.normalize(S_in_stat[:,:,:,1,i], None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1),cv2.COLOR_BGR2RGB)
        im_S2 = cv2.cvtColor(cv2.normalize(S_in_stat[:,:,:,2,i], None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1),cv2.COLOR_BGR2RGB)
        im_S = [im_S0,im_S1,im_S2]

        for componente, stokes in enumerate(im_S):
            fig = plt.figure()
            ax = fig.add_subplot()
            im = ax.imshow(stokes)
            ax.set_title("S"+str(componente),fontsize = 20)
            scalebar = AnchoredSizeBar(ax.transData, Mag*50/3.45 , '50 μm', 'lower right', pad=0.2, 
                                        color='white', frameon=False, size_vertical=1,
                                        fontproperties=fm.FontProperties(size=12))
            ax.add_artist(scalebar)
            plt.savefig(IMG_SAVE_PATH +"S"+str(componente)+"_"+str(theta)+".png")

        # Mientras no sea el ultimo
        if theta != thetas_list[-1]:
            #Mueve el motor
            print("Moviendo T en direccion F...")
            comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T F"
            ejecutar_comando_ssh(comando)

    # Volver a posicion original
    for _ in range(len(thetas_list)-1):
        print("Moviendo T en direccion B...")
        comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T B"
        ejecutar_comando_ssh(comando)

    # Guarda Stokes
    print("Guardando array...")
    with open(IMG_SAVE_PATH + name, 'wb') as f:
        np.save(f, S_in_stat)
        
    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
