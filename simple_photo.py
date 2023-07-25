import PySpin
import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
from PIL import Image 
from simple_pyspin import Camera
       
IMG_SAVE_PATH = 'img/'       
def take_photo(exposure_time, N):
		
    with Camera() as cam: # Acquire and initialize Camera
    	#Exposicion
    	cam.ExposureAuto = 'Off'
    	cam.ExposureTime = 10000 # microseconds
    	
    	#Toma las fotos
    	cam.start() # Start recording
    	imgs = [cam.get_array() for n in range(N)] # Get 10 frames
    	cam.stop() # Stop recording
    
    	#Promedia las fotos
    	img_mean = 1/N*(sum(imgs)).astype(float)
    
    return imgs[0]
    
def main():

    #Nombre archivo
    name = sys.argv[1]
   
    #Exposicion
    exposure_time = 5000
    
    # Numero de promedios
    N = 1
   
    #Toma la foto
    image_data = take_photo(exposure_time, N)
    
    # Decodifica
    I90, I45, I135, I0 = stokeslib.polarization_full_dec_array(image_data)
    
    
    
    # Crea objeto 
    im = Image.fromarray(I90.astype(np.uint8))
  
    # Guarda imagen
    os.makedirs(IMG_SAVE_PATH, exist_ok=True)
    im.save(IMG_SAVE_PATH + name + ".jpg")    

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
