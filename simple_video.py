import sys
import numpy as np
import cv2
from simple_pyspin import Camera
from tools.stokeslib import polarization_full_dec_array, calcular_stokes
from tools.camaralib import digitalizar

# Tamaño ventana
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

        #Exposicion
        cam.ExposureAuto = 'Off'
        cam.ExposureTime = exposure_time # microseconds
    	
        #Formato
        #cam.PixelFormat = "BayerRG8"

    	#Toma las fotos
        cam.start() # Start recording
    	
        while update:    
            #Capturar Stokes
            img = cam.get_array()

            #Medibles
            I90, I45, I135, I0 = polarization_full_dec_array(img)

            #Stokes
            S0, S1, S2 = calcular_stokes (I90, I45, I135, I0)

            #S0 normalizacion
            S0 = digitalizar(S0, 'S0')

            # Actualiza imagen
            cv2.imshow("img", S0)

            #Espera comando
            k = cv2.waitKey(1)
            
            if k == ord("q"):
                cv2.destroyAllWindows()
                update = False

        cam.stop() # Stop recording

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
