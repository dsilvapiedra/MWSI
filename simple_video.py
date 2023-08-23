import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
from PIL import Image 
from simple_pyspin import Camera
from tools.camaralib import take_photo

#Tamaño ventana
hsize = 900
vsize = 700
hoffset = 40
voffset = 20
prop = 0.75

#Exposicion
exposure_time = 5000

# Numero de promedios
N = 1

#Ventana
cv2.namedWindow('img', cv2.WINDOW_NORMAL)
cv2.moveWindow('img', hoffset, voffset)
cv2.resizeWindow('img', int(prop*int(1.25*hsize)), int(prop*int(1.25*vsize)))
cv2.setWindowTitle('img', 'S0')	

def main():
    
    #Continua actualizando
    update = True
    		
    with Camera() as cam: # Acquire and initialize Camera
    	
        while update:    
            #Toma foto
            image_data = take_photo(exposure_time, N)   
            
            #Decodifica la imagen
            I90, I45, I135, I0 = stokeslib.polarization_full_dec_array(image_data)
        
            # Calcula Stokes 	
            S0, S1, S2 = stokeslib.calcular_stokes(I90, I45, I135, I0)
        
            # Actualiza imagen
            cv2.imshow("img", I90.astype(np.uint8))
            
            #Espera comando
            k = cv2.waitKey(1)
            
            if k == ord("q"):
                cv2.destroyAllWindows()
                update = False
        
    return None

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
