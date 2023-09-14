import sys
import numpy as np
from tools.stokeslib import acoplar_mueller
from tools.camaralib import guardar_img, take_mueller

IMG_LOAD_PATH = 'stokes/'            
IMG_SAVE_PATH = 'mueller/'

# Exposicion
exposure_time = 5000

# Numero de promedios
N = 1

#Angulos de polarizacion de entrada
thetas_list = [0,60,120]  

def main(name = None):

    #Captura matriz de Mueller
    M = take_mueller(exposure_time, N, IMG_LOAD_PATH, thetas_list)

    #Guarda numpy array
    print("Guardando...")
    with open(IMG_SAVE_PATH + 'mueller.npy', 'wb') as f:
        np.save(f, M)

    #Mueller normalizada
    
        
    #Guarda Mueller img
    M_B = acoplar_mueller(M[:,:,0,:,:])
    M_G = acoplar_mueller(M[:,:,1,:,:])
    M_R = acoplar_mueller(M[:,:,2,:,:])
    M_img = [M_B, M_G, M_R]
        
    for color, matriz in enumerate(M_img):
        codigo=["B","G","R"]
        guardar_img(IMG_SAVE_PATH, matriz, "Mueller_"+codigo[color]+".png", cmap = 'jet')
    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
