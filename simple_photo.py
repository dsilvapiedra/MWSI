import sys
import cv2
import numpy as np
from tools.camaralib import take_stokes, guardar_img, digitalizar
from tools.stokeslib import calcular_dolp, calcular_aolp

IMG_SAVE_PATH = 'img/'              

#Exposicion
exposure_time = 5000

# Numero de promedios
N = 1

def main(name = None):

    #Nombre archivo
    if name is None:
        name = sys.argv[1]

    #Capturar Stokes
    S = take_stokes(exposure_time, N)
       
    # Codigo de colores
    color = ['650','550','450']
    
    #DoLP y AoLP
    dolp = calcular_dolp(S[:,:,:,0],S[:,:,:,1],S[:,:,:,2])
    aolp = calcular_aolp(S[:,:,:,1],S[:,:,:,2])

    #Digitaliza intensidad
    S0_norm = digitalizar(S[:,:,:,0], 'S0')
    dolp_norm = digitalizar(dolp, 'dolp')
    aolp_norm = digitalizar(aolp, 'aolp')
    
    #Color
    S0_RGB = cv2.cvtColor(S0_norm,cv2.COLOR_BGR2RGB)
    dolp_RGB = cv2.cvtColor(dolp_norm,cv2.COLOR_BGR2RGB)
    aolp_RGB = cv2.cvtColor(aolp_norm,cv2.COLOR_BGR2RGB)

    #Guarda imagen en color
    guardar_img(IMG_SAVE_PATH, S0_RGB, name + ' S0')

    #S0 en grises con colorbar
    for i in range(3):

        #Colormap
        im = cv2.cvtColor(cv2.applyColorMap(S0_RGB[:,:,i], cv2.COLORMAP_BONE),cv2.COLOR_BGR2RGB)
        dolp_im = cv2.cvtColor(cv2.applyColorMap(dolp_RGB[:,:,i], cv2.COLORMAP_JET),cv2.COLOR_BGR2RGB)
        aolp_im = cv2.cvtColor(cv2.applyColorMap(aolp_RGB[:,:,i], cv2.COLORMAP_JET),cv2.COLOR_BGR2RGB)

        #Guardar
        guardar_img(IMG_SAVE_PATH, im, name + ' S0 ('+color[i]+' nm)', color = 'red', clim=[0,2])
        guardar_img(IMG_SAVE_PATH, dolp_im, name + ' DoLP ('+color[i]+' nm)', color = 'gray', cmap = 'jet', clim=[0,1])
        guardar_img(IMG_SAVE_PATH, aolp_im, name + ' AoLP ('+color[i]+' nm)', color = 'gray', cmap = 'jet', clim=[-np.pi/2,np.pi/2])

    #S1 y S2 en grises con colorbar
    for i in range(3):
        for j in range(1,3):

            #Digitaliza S1 o S2
            S_norm = digitalizar(S[:,:,i,j], 'S1')
            
            #Colormap
            im = cv2.cvtColor(cv2.applyColorMap(S_norm, cv2.COLORMAP_BONE),cv2.COLOR_BGR2RGB)
            guardar_img(IMG_SAVE_PATH, im, name + ' S' + str(j) + ' ('+color[i]+' nm)', color = 'red', clim=[-1,1])
 
    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
