import PySpin
import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

IMG_LOAD_PATH = 'mueller/'
IMG_SAVE_PATH = 'lu_chipman/'

Mag = 22

def guardar_mueller(M, name):      
    
    #Guarda Mueller img
    M_B = stokeslib.acoplar_mueller(M[:,:,0,:,:])
    M_G = stokeslib.acoplar_mueller(M[:,:,1,:,:])
    M_R = stokeslib.acoplar_mueller(M[:,:,2,:,:])
    M_img = [M_B, M_G, M_R]
        
    for color, matriz in enumerate(M_img):
        codigo=["B","G","R"]
        fig = plt.figure()
        ax = fig.add_subplot()
        im = ax.imshow(matriz, cmap='jet')
        ax.set_title(name,fontsize = 20)
        scalebar = AnchoredSizeBar(ax.transData, Mag*50/3.45 , '50 μm', 'lower right', pad=0.2, 
                                    color='white', frameon=False, size_vertical=1,
                                    fontproperties=fm.FontProperties(size=12))
        ax.add_artist(scalebar)
        cbar = fig.colorbar(im, shrink = 0.8)
        plt.savefig(IMG_SAVE_PATH + name + codigo[color]+".png")

    return True

def main(name = None):

    #Nombre archivo
    if name is None:
        name = sys.argv[1]

    # Abrir Mueller
    with open(IMG_LOAD_PATH + name + ".npy", 'rb') as f:
        M = np.load(f)

    # Lu-Chipman
    MDelta = np.zeros_like(M)
    MR = np.zeros_like(M)
    MD = np.zeros_like(M)
    m00 = np.zeros_like(M[:,:,:,0,0])

    for i in range(1):
        MDelta[:,:,i,:,:], MR[:,:,i,:,:], MD[:,:,i,:,:], m00[:,:,i] = stokeslib.lu_chipman_3x3(M[:,:,i,:,:])
    
    lu_chipman = [MDelta, MR, MD]
    name_list = ["MDelta","MR","MD"]
    
    # Guardar Mueller
    for i, M in enumerate(lu_chipman):
        guardar_mueller(M, name_list[i])

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
