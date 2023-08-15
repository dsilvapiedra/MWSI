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

IMG_SAVE_PATH = 'input_stokes/'  
            
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
    decimador = 1
    
    # Dimension sensor
    dim = (2048,2448)         
    
    #Angulos de polarizacion de entrada
    thetas_list = [0,60,120]  
    N_datos = len(thetas_list)

    #Matrices de estadísticas
    S_in_stat = np.zeros((dim[0]//2,dim[1]//2,3,3,N_datos), dtype=float)[::decimador,::decimador]
    
    for i, theta in enumerate(thetas_list):
    	# Toma una foto
    	take_photo(exposure_time, N):
	print("Toma foto")
    
        #  Decodifica
        I90, I45, I135, I0 = stokeslib.polarization_full_dec_array(image_data)    
    
        # Stokes        
        S_in_stat[:,:,:,0,i], S_in_stat[:,:,:,1,i], S_in_stat[:,:,:,2,i]  = stokeslib.calcular_stokes(I90, I45, I135, I0)
        
        #Crea imagenes de de Stokes
        S0_img = cv2.normalize(S_in_stat[:,:,:,0,i], None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        S1_img = cv2.normalize(S_in_stat[:,:,:,1,i], None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        S2_img = cv2.normalize(S_in_stat[:,:,:,2,i], None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        
        im_S0 = Image.fromarray(cv2.cvtColor(S0_img,cv2.COLOR_BGR2RGB))
        im_S1 = Image.fromarray(cv2.cvtColor(S1_img,cv2.COLOR_BGR2RGB))
        im_S2 = Image.fromarray(cv2.cvtColor(S2_img,cv2.COLOR_BGR2RGB))
    
        # Guarda imagenes
        os.makedirs(IMG_SAVE_PATH, exist_ok=True)
        im_S0.save(IMG_SAVE_PATH + "S0_" + str(theta) + ".png")   
        im_S1.save(IMG_SAVE_PATH + "S1_" + str(theta) + ".png")   
        im_S2.save(IMG_SAVE_PATH + "S2_" + str(theta) + ".png")   

        # Mientras no sea el ultimo
        if theta != thetas_list[-1]:
            #Mueve el motor
            print("Mover T en direccion F")
            comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T F"
            ejecutar_comando_ssh(comando)

    # Volver a posicion original
    for _ in range(len(thetas_list)-1):
        print("Mover T en direccion B")
        comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T B"
        ejecutar_comando_ssh(comando)

    # Guarda Stokes
    with open(IMG_SAVE_PATH + 'Sin.npy', 'wb') as f:
        np.save(f, S_in_stat)
        
    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
