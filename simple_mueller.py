import PySpin
import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
from tools.camaralib import take_photo
from PIL import Image 
from simple_pyspin import Camera
from motor_control_ssh import ejecutar_comando_ssh
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

IMG_LOAD_PATH = 'stokes/'            
IMG_SAVE_PATH = 'mueller/'

def main(name = None):

    # Configuracion de la camara
    
    # Exposicion
    exposure_time = 5000
    
    # Numero de promedios
    N = 1

    #Decimador 
    decimador = 1
    
    # Dimension sensor
    dim = (2048,2448)         

    # Magnificación
    Mag = 22
    
    #Angulos de polarizacion de entrada
    thetas_list = [0,60,120]  
    N_datos = len(thetas_list)

    #Matrices de estadísticas	
    with open(IMG_LOAD_PATH + 'Sin.npy', 'rb') as f:
        print("Cargando Stokes de entrada...")
        S_in_stat_inv = np.load(f)[::decimador,::decimador]           
    
    S_out_stat = np.zeros((dim[0]//2,dim[1]//2,3,3,N_datos))[::decimador,::decimador]
    
    #Captura vectores de Stokes
    for i, theta in enumerate(thetas_list):
    	#Toma la foto
        image_data = take_photo(exposure_time, N)
        print("Tomando Foto...")

        #  Decodifica
        I90, I45, I135, I0 = stokeslib.polarization_full_dec_array(image_data)    
        
        # Stokes        
        S_out_stat[:,:,:,0,i], S_out_stat[:,:,:,1,i], S_out_stat[:,:,:,2,i]  = stokeslib.calcular_stokes(I90, I45, I135, I0, decimador = decimador)

        #Mueve el motor
        if theta != thetas_list[-1]:
            print("Moviendo T en direccion F...")
            comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T F"
            ejecutar_comando_ssh(comando)

    # Volver a posicion original
    for _ in range(len(thetas_list)-1):
        print("Moviendo T en direccion B...")
        comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T B"
        ejecutar_comando_ssh(comando)

    #Calcula Mueller
    print("Calculando Matriz de Mueller...")
    M = stokeslib.calcular_mueller_inv(S_in_stat_inv,S_out_stat)

    #Guarda numpy array
    print("Guardando...")
    with open(IMG_SAVE_PATH + 'mueller.npy', 'wb') as f:
        np.save(f, M)
        
    #Guarda Mueller img
    M_B = stokeslib.acoplar_mueller(M[:,:,0,:,:])
    M_G = stokeslib.acoplar_mueller(M[:,:,1,:,:])
    M_R = stokeslib.acoplar_mueller(M[:,:,2,:,:])
    M_img = [M_B, M_G, M_R]
        
    for color, matriz in enumerate(M_img):
        codigo=["B","G","R"]
        fig = plt.figure()
        ax = fig.add_subplot()
        im = ax.imshow(matriz, cmap='jet')
        ax.set_title('Matriz de Mueller',fontsize = 20)
        scalebar = AnchoredSizeBar(ax.transData, Mag*50/3.45 , '50 μm', 'lower right', pad=0.2, 
                                    color='white', frameon=False, size_vertical=1,
                                    fontproperties=fm.FontProperties(size=12))
        ax.add_artist(scalebar)
        cbar = fig.colorbar(im, shrink = 0.8)
        plt.savefig(IMG_SAVE_PATH + "Mueller_"+codigo[color]+".png")

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
