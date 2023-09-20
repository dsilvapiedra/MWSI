from simple_pyspin import Camera
import cv2
import sys
import paramiko
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from tools.stokeslib import polarization_full_dec_array, calcular_stokes, calcular_mueller_inv, acoplar_mueller

#Esta librería cuenta con algoritmos para controlar la cámara y los motores.

#Definiciones
RPI_USER = 'mwsi'
RPI_PASS = 'mwsi'
RPI_IP = '169.254.110.82'
RPI_PORT = 22

#Control de motores

def ejecutar_comando_ssh(comando):
    print('Conectando a raspberry...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(RPI_IP,RPI_PORT, username=RPI_USER, password=RPI_PASS)
    print('Ejecutando comando... ')
    # Realizar la copia segura utilizando SCP
    sftp = ssh.open_sftp()
    sftp.put('motor_control.py', '/home/mwsi/Desktop/main/' + 'motor_control.py')
    sftp.close()
    stdin, stdout, stderr = ssh.exec_command(comando)
    print(stdout.read().decode())
    print(stderr.read().decode())
    ssh.close()
    
    return stdout.readlines()


#Captura una imagen de intensidad  simplepyspin

def take_photo(exposure_time, N):
		
    with Camera() as cam: # Acquire and initialize Camera
    	#Exposicion
        cam.ExposureAuto = 'Off'
        cam.ExposureTime = exposure_time # microseconds
    	
        #Formato
        cam.PixelFormat = "BayerRG8"

    	#Toma las fotos
        cam.start() # Start recording
        imgs = [cam.get_array() for n in range(N)] # Get 10 frames
        cam.stop() # Stop recording

    	#Promedia las fotos 
        img_mean = 1/N*(sum(imgs)).astype(float)
    
    return imgs[0]

#Captura un tensor que representa el vector de Stokes observado.

def take_stokes(exposure_time, N):
    # Dimension sensor
    dim = (2048,2448)      

    # Vector de Stokes
    S = np.zeros((dim[0]//2,dim[1]//2,3,3), dtype=float)
   
    #Toma la foto
    image_data = take_photo(exposure_time, N)
    
    # Decodifica
    I90, I45, I135, I0 = polarization_full_dec_array(image_data)
    
    # Calcula Stokes
    S[:,:,:,0], S[:,:,:,1], S[:,:,:,2] = calcular_stokes(I90, I45, I135, I0)

    return S

#Captura el vector de Stokes variando el ángulo de entrada
def take_mueller_stokes(exposure_time, N, thetas_list):

    # Dimension sensor
    dim = (2048,2448)  

    #Decimador 
    decimador = 1

    #Numero de angulos    
    N_datos = len(thetas_list)

    #Matrices de estadísticas
    S_stat = np.zeros((dim[0]//2,dim[1]//2,3,3,N_datos), dtype=float)[::decimador,::decimador]
    
    for i, theta in enumerate(thetas_list):
        # Toma una captura de Stokes
        print("Tomando Stokes...") 
        S = take_stokes(exposure_time, N)
    
        #Almacena Stokes        
        for j in range(3):
            S_stat[:,:,:,j,i] = S[:,:,:,j] 

        # Mientras no sea el ultimo
        if theta != thetas_list[-1]:
            #Mueve el motor
            print("Moviendo T en direccion F...")
            comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T F"
            ejecutar_comando_ssh(comando)

    # Volver a posicion original
    for _ in range(len(thetas_list)-1):
        print("Moviendo T en direccion B...")
        comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T B"
        ejecutar_comando_ssh(comando)

    return S_stat

#Calcula la matriz de Mueller. Sincroniza con los motores, toma las fotos, 
# carga la Sin invertida y entrega la matriz de mueller observada.

def take_mueller(S_in_stat_inv, exposure_time, N, path, thetas_list):
    #Dimension del sensor
    dim = (2048,2448) 

    #Número de ángulos
    N_datos = len(thetas_list)

    #Captura Stokes en los tres ángulos
    S_out_stat = take_mueller_stokes(exposure_time, N, thetas_list)

    #Calcula Mueller
    print("Calculando Matriz de Mueller...")
    M = calcular_mueller_inv(S_in_stat_inv,S_out_stat)

    return M

#Digitalizadora de medidas físicas

def digitalizar(A, medida,  inversa = False):
    #Constantes
    MAX8 = 2**8-1
    MAX16 = 2**16-1

    if not inversa:
        #Intensidad
        if medida == 'S0':
            A_digital = (A // 2).astype(np.uint8)

        #Polarización
        elif (medida == 'S1') or (medida == 'S2'):
            A_digital = ((A + MAX8) // 2).astype(np.uint8)

        #DoLP entre 0 y 1
        elif medida == 'dolp':
            A_digital = A*MAX8
            A_digital[A_digital > MAX8] = MAX8
            A_digital[A_digital < 0] = 0
            A_digital = A_digital.astype(np.uint8)

        #AoLP entre -pi y pi
        elif medida == 'aolp':
            A_digital = (A+np.pi/2)/np.pi*MAX8
            A_digital[A_digital > MAX8] = MAX8
            A_digital[A_digital < 0] = 0
            A_digital = A_digital.astype(np.uint8)

        #Mueller en 8 bits
        elif medida == 'M8':
            A_digital = ((A + 1)/2 * MAX8)
            A_digital[A_digital > MAX8] = MAX8
            A_digital[A_digital < 0] = 0
            A_digital = A_digital.astype(np.uint8)
        
        #Mueller en 16 bits
        elif medida == 'M16':
            A_digital = ((A + 1)/2 * MAX16)
            A_digital[A_digital > MAX16] = MAX16
            A_digital[A_digital < 0] = 0
            A_digital = A_digital.astype(np.uint16)

    return A_digital


# Guarda imagen con la barra

def guardar_img(path, img, name, cmap = 'gray', color = 'white', clim = None):
    # Magnificacion
    Mag = 22

    #Crea Figure
    fig = plt.figure()

    #Crea ejes
    ax = fig.add_subplot()

    #Muestra la imagen
    im = ax.imshow(img, cmap=cmap)

    #Titulo
    ax.set_title(name,fontsize = 20)

    #Barra
    scalebar = AnchoredSizeBar(ax.transData, 0.5*Mag*100/3.45 , '100 μm', 'lower right', pad=0.2, 
                                color=color, frameon=False, size_vertical=6,
                                fontproperties=fm.FontProperties(size=14))
    ax.add_artist(scalebar)
    #Limites de la barra
    if clim != None:
        cbar = plt.colorbar(im)
        im.set_clim(vmin=clim[0],vmax=clim[1])

    #Guarda Figura
    plt.savefig(path + name + ".png")

    #Cierra Figura
    plt.close()

    return None

def guardar_stokes(S, path, name):
    #Colores R G B
    color = ['650', '550', '450']

    #Digitaliza S0
    S0_norm = digitalizar(S[:,:,:,0], 'S0')

    #Color S0
    S0_RGB = cv2.cvtColor(S0_norm,cv2.COLOR_BGR2RGB)

    #Guarda imagen en color
    guardar_img(path, S0_RGB, name + ' S0')

    #S0 en grises con colorbar
    for i in range(3):

        #Colormap canal
        im = cv2.cvtColor(cv2.applyColorMap(S0_RGB[:,:,i], cv2.COLORMAP_BONE),cv2.COLOR_BGR2RGB)

        #Guarda imagen
        guardar_img(path, im, name + ' S0 ('+color[i]+' nm)', color = 'red', clim=[0,2])

    #S1 y S2 en grises con colorbar
    for i in range(3):
        for j in range(1,3):
            
            #Digitaliza S1 o S2
            S_norm = digitalizar(S[:,:,i,j], 'S1')

            #Colormap
            im = cv2.cvtColor(cv2.applyColorMap(S_norm, cv2.COLORMAP_BONE),cv2.COLOR_BGR2RGB)
            guardar_img(path, im, name + ' S' + str(j) + ' ('+color[i]+' nm)', color = 'red', clim=[-1,1])

    return True    

def guardar_mueller(M, path, name):
    #Codigo de color
    codigo=['R','G','B']

    #Mueller RGB
    M_RGB16 = np.zeros((M.shape[0]*3,M.shape[1]*3,3),dtype=np.uint16)

    for i in range(3):
        #Acoplar en una imagen la Matriz de Mueller en el canal
        M_acoplada = acoplar_mueller(M[:,:,i,:,:])
        
        #Normalizar Mueller en 8 y 16 bits
        M_norm8 = digitalizar(M_acoplada, "M8")
        M_RGB16[:,:,i] = digitalizar(M_acoplada, "M16")

        #Colormap
        im = cv2.cvtColor(cv2.applyColorMap(M_norm8, cv2.COLORMAP_JET), cv2.COLOR_BGR2RGB)
            
        #Guardar
        guardar_img(path, im, name + " Mueller_" + codigo[i], cmap = 'jet', clim = [-1,1])
    
    #Guardar Mueller color
    cv2.imwrite(path + name + 'Mueller_RGB' + '.png', M_RGB16)

    return True

def main():
  return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
