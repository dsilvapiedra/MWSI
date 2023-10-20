import sys
import numpy as np
from tools.camaralib import guardar_mueller, take_mueller
import gzip
import cv2
from tools.camaralib import digitalizar

IMG_LOAD_PATH = 'stokes/Sin_inv.npy.gz'            
IMG_SAVE_PATH = 'mueller/'

# Exposiciona
exposure_time = 5000

# Numero de promedios
N = 1

#Decimador
decimador = 1

#Angulos de polarizacion de entrada
thetas_list = [0,60,120]  

#Matrices de estadísticas	
f = gzip.GzipFile(IMG_LOAD_PATH, 'rb')
S_in_stat_inv = np.load(f)[::decimador,::decimador]           

def main(name = None):

    #Nombre archivo
    if name is None:
        name = sys.argv[1]

    #Captura matriz de Mueller
    m00, M = take_mueller(S_in_stat_inv, exposure_time, N, IMG_LOAD_PATH, thetas_list)

    #Digitaliza intensidad
    I_dig = digitalizar(m00, 'm00')

    # Guarda imagen de intensidad
    cv2.imwrite(IMG_SAVE_PATH + name + '_intensidad.png', I_dig)

    #Guardar matriz de Mueller
    guardar_mueller(M, IMG_SAVE_PATH, name)

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
