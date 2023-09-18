import sys
import numpy as np
import cv2
from simple_pyspin import Camera
from tools.camaralib import take_stokes

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
            #Capturar Stokes
            S = take_stokes(exposure_time, N)

            #S0 normalizacion
            S0 = (S[:,:,:,0]//2).astype(np.uint8)

            # Actualiza imagen
            cv2.imshow("img", S0)

            #Espera comando
            k = cv2.waitKey(1)
            
            if k == ord("q"):
                cv2.destroyAllWindows()
                update = False
        
    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
