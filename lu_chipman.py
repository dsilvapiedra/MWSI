import sys
import numpy as np
from tools.stokeslib import lu_chipman, mueller_mean
from tools.camaralib import guardar_mueller, png2mueller
import cv2

IMG_LOAD_PATH = 'mueller/'
IMG_SAVE_PATH = 'lu_chipman/'

def main(name = None):

    #Nombre archivo
    if name is None:
        name = sys.argv[1]

    # Abrir imagen de Mueller en el formato que sea
    M_show = cv2.imread(IMG_LOAD_PATH + name + 'Mueller_RGB.png',-1)

    # Convertir imagen en Matriz
    M = png2mueller(M_show, 'M16')
    print(mueller_mean(M[:,:,0,:,:]))
    print(M.shape)

    # Lu-Chipman
    name_list = ['MDelta','MR','MD']
    MDelta = np.zeros_like(M)
    MR = np.zeros_like(M)
    MD = np.zeros_like(M)
    m00 = np.zeros_like(M[:,:,:,0,0])
    lu_list = [MDelta, MR, MD]

    #Descomposición por canal de color
    for i in range(3):
        MDelta[:,:,i,:,:], MR[:,:,i,:,:], MD[:,:,i,:,:], m00[:,:,i] = lu_chipman(M[:,:,i,:,:])

    #Guarda cada Matriz
    for i, mueller in enumerate(lu_list):
        guardar_mueller(mueller, IMG_SAVE_PATH, name+name_list[i])

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
