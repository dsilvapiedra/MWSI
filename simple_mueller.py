import sys
import numpy as np
from tools.camaralib import guardar_mueller, take_mueller
import gzip

IMG_LOAD_PATH = 'stokes/Sin_inv.npy.gz'            
IMG_SAVE_PATH = 'mueller/'

# Exposicion
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
    M = take_mueller(S_in_stat_inv, exposure_time, N, IMG_LOAD_PATH, thetas_list)

    #Guarda numpy array
    #print("Guardando...")
    #with open(IMG_SAVE_PATH + name + ' mueller.npy', 'wb') as f:
    #    np.save(f, M)

    #Guardar matriz de Mueller
    guardar_mueller(M, IMG_SAVE_PATH, name)

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
