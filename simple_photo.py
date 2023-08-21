import PySpin
import sys
import numpy as np
import keyboard
import os
import cv2
from tools import stokeslib
from PIL import Image 
from simple_pyspin import Camera
from tools.camaralib import take_photo
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

IMG_SAVE_PATH = 'img/'              
    
def main(name = None):

    #Nombre archivo
    if name is None:
        name = sys.argv[1]
   
    #Exposicion
    exposure_time = 5000
    
    # Numero de promedios
    N = 1

    # Magnificacion
    Mag = 22

    # Dimension sensor
    dim = (2048,2448)      

    # Vector de Stokes
    S = np.zeros((dim[0]//2,dim[1]//2,3,3), dtype=float)
   
    #Toma la foto
    image_data = take_photo(exposure_time, N)
    
    # Decodifica
    I90, I45, I135, I0 = stokeslib.polarization_full_dec_array(image_data)
    
    # Calcula Stokes
    S[:,:,:,0], S[:,:,:,1], S[:,:,:,2] = stokeslib.calcular_stokes(I90, I45, I135, I0)
       
    # Crea objeto 
    im = cv2.cvtColor(S[:,:,:,0].astype(np.uint8),cv2.COLOR_BGR2RGB)
  
    # Guarda imagen
    fig = plt.figure()
    ax = fig.add_subplot()
    im = ax.imshow(im)
    ax.set_title(name,fontsize = 20)
    scalebar = AnchoredSizeBar(ax.transData, Mag*50/3.45 , '50 μm', 'lower right', pad=0.2, 
                                color='white', frameon=False, size_vertical=1,
                                fontproperties=fm.FontProperties(size=12))
    ax.add_artist(scalebar)
    plt.savefig(IMG_SAVE_PATH + name + ".png")

    #Guarda Array
    with open(IMG_SAVE_PATH + name + ".npy", 'wb') as f:
        np.save(f, S)

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
