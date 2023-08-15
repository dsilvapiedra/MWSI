import PySpin
import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
from PIL import Image 
from simple_pyspin import Camera
from motor_control_ssh import ejecutar_comando_ssh

IMG_LOAD_PATH = 'input_stokes/'            
IMG_SAVE_PATH = 'mueller/'

def take_photo(exposure_time, N):
		
    with Camera() as cam: # Acquire and initialize Camera
    	#Exposicion
        cam.ExposureAuto = 'Off'
        cam.ExposureTime = exposure_time # microseconds
    	
    	#Toma las fotos
        cam.start() # Start recording
        imgs = [cam.get_array() for n in range(N)] # Get 10 frames
        cam.stop() # Stop recording

    	#Promedia las fotos 
        #img_mean = 1/N*(sum(imgs)).astype(float)
    
    return imgs[0]
    
def main(name = None):

    # Configuracion de la camara
    
    # Exposicion
    exposure_time = 5000
    
    # Numero de promedios
    N = 1

    # Datos

    #Decimador 
    decimador = 8
    
    # Dimension sensor
    dim = (2048,2448)         
    
    #Angulos de polarizacion de entrada
    thetas_list = [0,10,90]  
    N_datos = len(thetas_list)

    #Matrices de estadísticas	
    S_in_stat = np.zeros((dim[0]//2,dim[1]//2,3,3,N_datos), dtype=float)[::decimador,::decimador]
    with open(IMG_LOAD_PATH + 'Sin.npy', 'rb') as f:
        S_in_stat = np.load(f)[::decimador,::decimador]           
    S_out_stat = np.zeros((dim[0]//2,dim[1]//2,3,3,N_datos))[::decimador,::decimador]
    
    #Captura vectores de Stokes
    for i in range(N_datos):
    	#Toma la foto
        image_data = take_photo(exposure_time, N)
        
        #  Decodifica
        I90, I45, I135, I0 = stokeslib.polarization_full_dec_array(image_data)    
        
        # Stokes        
        S_out_stat[:,:,:,0,i], S_out_stat[:,:,:,1,i], S_out_stat[:,:,:,2,i]  = stokeslib.calcular_stokes(I90, I45, I135, I0, decimador = decimador)

         #Mueve el motor
        print("Mover T en direccion F")
        comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T F"
        ejecutar_comando_ssh(comando)

    #Calcula Mueller
    M = stokeslib.calcular_mueller(S_in_stat,S_out_stat)
    M_img = cv2.normalize(stokeslib.acoplar_mueller(M), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    #Guarda Mueller
    os.makedirs(IMG_SAVE_PATH, exist_ok=True)
    im_mueller = Image.fromarray(cv2.cvtColor(M_img,cv2.COLOR_BGR2RGB))
    im_mueller.save(IMG_SAVE_PATH + "Mueller"+".png") 
    
    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
