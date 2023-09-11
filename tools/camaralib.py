from simple_pyspin import Camera
from tools.stokeslib import polarization_full_dec_array, calcular_stokes
import numpy as np
import sys

#Esta librería cuenta con algoritmos para obtener información de la cámara. 

#Captura una imagen de intensidad 

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
        img_mean = 1/N*(sum(imgs)).astype(float)
    
    return imgs[0]

#Captura un tensor que representa el vector de Stokes observado.

def take_stokes(exposure_time, N):
    # Dimension sensor
    dim = (2048,2448)      

    # Vector de Stokes
    S = np.zeros((dim[0]//2,dim[1]//2,3,3), dtype=float)
   
    #Toma la foto
    image_data = take_photo(exposure_time, N)
    
    # Decodifica
    I90, I45, I135, I0 = polarization_full_dec_array(image_data)
    
    # Calcula Stokes
    S[:,:,:,0], S[:,:,:,1], S[:,:,:,2] = calcular_stokes(I90, I45, I135, I0)

    return S

def main():
  return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
