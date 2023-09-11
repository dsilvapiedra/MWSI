import PySpin
import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
from PIL import Image 
from simple_pyspin import Camera
from tools.camaralib import take_stokes
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

IMG_SAVE_PATH = 'img/'              
    
def guardar_img(img, name, color = 'white', clim = None):
    # Magnificacion
    Mag = 22

    # Guarda figura
    fig = plt.figure()
    ax = fig.add_subplot()
    im = ax.imshow(img, cmap='gray')
    ax.set_title(name,fontsize = 20)
    scalebar = AnchoredSizeBar(ax.transData, 0.5*Mag*50/3.45 , '50 μm', 'lower right', pad=0.2, 
                                color=color, frameon=False, size_vertical=6,
                                fontproperties=fm.FontProperties(size=14))
    ax.add_artist(scalebar)
    if clim != None:
        cbar = plt.colorbar(im)
        im.set_clim(vmin=clim[0],vmax=clim[1])
    plt.savefig(IMG_SAVE_PATH + name + ".png")
    plt.close()
    return None

def main(name = None):

    #Nombre archivo
    if name is None:
        name = sys.argv[1]
   
    #Exposicion
    exposure_time = 5000
    
    # Numero de promedios
    N = 1

    #Capturar Stokes
    S = take_stokes(exposure_time, N)
       
    # Guarda imagenes
    color = ['450','550','650']
    
    #S0 en color
    im_S0 = cv2.cvtColor(S[:,:,:,0].astype(np.uint8),cv2.COLOR_BGR2RGB)
    guardar_img(im_S0, name + ' S0')
    S0_max = np.max(S[:,:,0,0])

    #S0 S1 y S2 en grises con colorbar
    for i in range(3):
        for j in range(3):
            im = cv2.cvtColor(cv2.normalize(S[:,:,i,j], None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1),cv2.COLOR_BGR2RGB)
            lim = [np.min(S[:,:,i,j])/S0_max,np.max(S[:,:,i,j])/S0_max]
            guardar_img(im, name + ' S' + str(j) + ' ('+color[i]+' nm)', color = 'red', clim=lim)
    
    #Guarda Array
    #with open(IMG_SAVE_PATH + name + ".npy", 'wb') as f:
    #    np.save(f, S)

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
