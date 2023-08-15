import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
from PIL import Image 
from simple_pyspin import Camera

hsize = 900
vsize = 700
hoffset = 40
voffset = 20
prop = 0.75

def begin_stream(exposure_time, N):

    #Ventana
    cv2.namedWindow('img1', cv2.WINDOW_NORMAL)
    cv2.moveWindow('img1', hoffset, voffset)
    cv2.resizeWindow('img1', int(prop*int(1.25*hsize)), int(prop*int(1.25*vsize)))
    cv2.setWindowTitle('img1', 'S0')	
    
    #Continua actualizando
    update = True
    		
    with Camera() as cam: # Acquire and initialize Camera
    	
        while update:    
            
            #Exposicion
            cam.ExposureAuto = 'Off'
            cam.ExposureTime = exposure_time # microseconds
            
            #Toma las fotos
            cam.start() # Start recording
            imgs = [cam.get_array() for n in range(N)] # Get 10 frames
            cam.stop() # Stop recording
        
            #Promedia las fotos
            img_mean = 1/N*(sum(imgs)).astype(float)
            
            #Decodifica la imagen
            I90, I45, I135, I0 = stokeslib.polarization_full_dec_array(img_mean)
        
            # Calcula Stokes 	
            S0, S1, S2 = stokeslib.calcular_stokes(I90, I45, I135, I0)
        
            # Actualiza imagen
            cv2.imshow("img1", I90.astype(np.uint8))
            
            #Espera comando
            k = cv2.waitKey(1)
            
            if k == ord("q"):
                cv2.destroyAllWindows()
                update = False
        
    return None
    
def main():

    #Exposicion
    exposure_time = 5000
    
    # Numero de promedios
    N = 1
   
    #Toma el video
    begin_stream(exposure_time, N)
    
    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
