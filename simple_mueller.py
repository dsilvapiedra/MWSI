import PySpin
import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
from PIL import Image 
from simple_pyspin import Camera

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

    #Nombre archivo
    if name is None:
        name = sys.argv[1]
   
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
    thetas_list = [0,10,90]  
    N_datos = len(thetas_list)

    #Matrices de estadísticas	
    with open(IMG_LOAD_PATH + 'Sin.npy', 'wb') as f:
        np.load(f, S_in_stat)           
    S_out_stat = np.zeros((dim[0]//2,dim[1]//2,3,3,N_datos))[::decimador,::decimador]
    
    #Captura vectores de Stokes
    for i in range(N_datos):
    	#Toma la foto
    	image_data = take_photo(exposure_time, N)
        
        #  Decodifica
        I90, I45, I135, I0 = stokeslib.polarization_full_dec_array(image_data)    
        
        # Stokes        
        S_out_stat[:,:,:,0,i], S_out_stat[:,:,:,1,i], S_out_stat[:,:,:,2,i]  = stokeslib.calcular_stokes(I90, I45, I135, I0)

    #Calcula Mueller
    M = stokeslib.calcular_mueller(S_in_stat,S_out_stat)
    
    #Guarda Mueller
    os.makedirs(IMG_SAVE_PATH, exist_ok=True)
    im_S0.save(IMG_SAVE_PATH + "S0_" + str(theta) + ".png") 
    im.save(IMG_SAVE_PATH + name + ".png")   
    
    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
