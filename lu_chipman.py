import sys
import numpy as np
from tools.stokeslib import lu_chipman, calcular_dolp_mueller, calcular_aolp_mueller, calcular_diatenuacion, power_of_depolarization, optical_activity, linear_retardance
from tools.camaralib import guardar_img, guardar_mueller, png2mueller, digitalizar
import cv2

IMG_LOAD_PATH = 'mueller/'
IMG_SAVE_PATH = 'lu_chipman/'

def main(name = None):

    #Nombre archivo
    if name is None:
        name = sys.argv[1]

    # Abrir imagen de Mueller en el formato que sea
    M_show = cv2.imread(IMG_LOAD_PATH + name + ' Mueller_RGB.png',-1)

    # Convertir imagen en Matriz
    M = png2mueller(M_show, 'M16')

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
        guardar_mueller(mueller, IMG_SAVE_PATH, name + name_list[i])

    #Propiedades Físicas
    color = ['R','G','B']
    prop_name = ['P','AoP','D','PoD','OA','LR']
    clim_prop = [[0,1],[-np.pi,np.pi],[0,1],[0,1],[-np.pi,np.pi],[-np.pi,np.pi]]
    medida_list = ['dolp','aolp','dolp','dolp','aolp','aolp']

    #Por cada canal de color
    for i in range(3):

        #Calcula medida
        dolp = calcular_dolp_mueller(M[:,:,i,:,:])
        aolp = calcular_aolp_mueller(M)
        D = calcular_diatenuacion(M[:,:,i,:,:])
        delta = power_of_depolarization(MDelta[:,:,i,:,:])
        cr = optical_activity(MR[:,:,i,:,:])
        lr = linear_retardance(MR[:,:,i,:,:])
        prop_list = [dolp, aolp, D, delta, cr, lr]
        
        #Por cada propiedad polarimétrica
        for j, prop in enumerate(prop_list):

            #Digitaliza
            img = digitalizar(prop, medida_list[j])

            #Guardar imagen
            guardar_img(IMG_SAVE_PATH, img, name + ' ' + prop_name[j] + '_' + color[i], cmap = 'jet', color = 'white', clim = clim_prop[j])

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
