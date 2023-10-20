import sys
from tools.camaralib import take_mueller_stokes, guardar_stokes
import numpy as np
import gzip

# Ruta carpeta en dónde guardar
IMG_SAVE_PATH = 'stokes/'  

# Exposicion
exposure_time = 5000

# Numero de promedios
N = 1

#Decimador 
decimador = 1

#Angulos de polarizacion de entrada
thetas_list = ['0','60','120']  

def main():

    #Nombre
    name = 'Sin_inv.npy.gz'

    #Toma vectores de Stokes
    S_in_stat = take_mueller_stokes(exposure_time, N, thetas_list)
        
    #Guarda cada vector de Stokes
    #for i in range(3):
    #    guardar_stokes(S_in_stat[:,:,:,:,i], IMG_SAVE_PATH, name + thetas_list[i])

    #Guarda numpy stokes comprimido
    print("Guardando array...")
    f = gzip.GzipFile(IMG_SAVE_PATH + name, 'wb')
    np.save(f, np.linalg.pinv(S_in_stat))

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
