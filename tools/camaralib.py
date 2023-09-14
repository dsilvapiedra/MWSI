from simple_pyspin import Camera
import cv2
import sys
import paramiko
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from tools.stokeslib import polarization_full_dec_array, calcular_stokes, calcular_mueller_inv

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


#Captura una imagen de intensidad 

def take_photo(exposure_time, N):
		
    with Camera() as cam: # Acquire and initialize Camera
    	#Exposicion
        cam.ExposureAuto = 'Off'
        cam.ExposureTime = exposure_time # microseconds
    	
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
def take_mueller_stokes(exposure_time, N, path, name, thetas_list):

    # Dimension sensor
    dim = (2048,2448)  

    #Decimador 
    decimador = 1

    #Numero de angulos    
    N_datos = len(thetas_list)

    #Matrices de estadísticas
    S_in_stat = np.zeros((dim[0]//2,dim[1]//2,3,3,N_datos), dtype=float)[::decimador,::decimador]
    
    for i, theta in enumerate(thetas_list):
        # Toma una captura de Stokes
        print("Tomando Stokes...") 
        S = take_stokes(exposure_time, N)
    
        #Almacena Stokes        
        for j in range(3):
            S_in_stat[:,:,:,j,i] = S[:,:,:,j] 

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

    return S_in_stat


#Calcula la matriz de Mueller. Sincroniza con los motores, toma las fotos, 
# carga la Sin invertida y entrega la matriz de mueller observada.

def take_mueller(exposure_time, N, path, thetas_list):
    #Dimension del sensor
    dim = (2048,2448) 

    #Decimador 
    decimador = 1

    #Número de ángulos
    N_datos = len(thetas_list)

    #Matrices de estadísticas	
    with open(path + 'Sin.npy', 'rb') as f:
        print("Cargando Stokes de entrada...")
        S_in_stat_inv = np.load(f)[::decimador,::decimador]           
    
    S_out_stat = np.zeros((dim[0]//2,dim[1]//2,3,3,N_datos))[::decimador,::decimador]
    
    #Captura vectores de Stokes
    for i, theta in enumerate(thetas_list):
        # Stokes        
        S_out_stat[:,:,:,:,i]  = take_stokes(exposure_time, N)

        #Mueve el motor
        if theta != thetas_list[-1]:
            print("Moviendo T en direccion F...")
            comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T F"
            ejecutar_comando_ssh(comando)

    # Volver a posicion original
    for _ in range(len(thetas_list)-1):
        print("Moviendo T en direccion B...")
        comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T B"
        ejecutar_comando_ssh(comando)

    #Calcula Mueller
    print("Calculando Matriz de Mueller...")
    M = calcular_mueller_inv(S_in_stat_inv,S_out_stat)

    return M

# Guarda imagen con la barra

def guardar_img(path, img, name, cmap = 'gray', color = 'white', clim = None):
    # Magnificacion
    Mag = 22

    # Guarda figura
    fig = plt.figure()
    ax = fig.add_subplot()
    im = ax.imshow(img, cmap=cmap)
    ax.set_title(name,fontsize = 20)
    scalebar = AnchoredSizeBar(ax.transData, 0.5*Mag*50/3.45 , '50 μm', 'lower right', pad=0.2, 
                                color=color, frameon=False, size_vertical=6,
                                fontproperties=fm.FontProperties(size=14))
    ax.add_artist(scalebar)
    if clim != None:
        cbar = plt.colorbar(im)
        im.set_clim(vmin=clim[0],vmax=clim[1])
    plt.savefig(path + name + ".png")
    plt.close()

    return None

def guardar_stokes(S, path, name):
    #Colores
    color = [450, 550, 650]

    #S0 normalizada
    S0 = cv2.cvtColor((S[:,:,:,0]//2).astype(np.uint8),cv2.COLOR_BGR2RGB)

    #Guarda imagen en color
    guardar_img(path, S0, name + ' S0')

    #S0 en grises con colorbar
    for i in range(3):
        im = cv2.cvtColor(cv2.applyColorMap(S0[:,:,i], cv2.COLORMAP_BONE),cv2.COLOR_BGR2RGB)
        guardar_img(path, im, name + ' S0 ('+color[i]+' nm)', color = 'red', clim=[0,2])

    #S1 y S2 en grises con colorbar
    for i in range(3):
        for j in range(1,3):
            S_norm = ((S[:,:,i,j]+255)//2).astype(np.uint8)
            im = cv2.cvtColor(cv2.applyColorMap(S_norm, cv2.COLORMAP_BONE),cv2.COLOR_BGR2RGB)
            guardar_img(path, im, name + ' S' + str(j) + ' ('+color[i]+' nm)', color = 'red', clim=[-1,1])

    return True    


def main():
  return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
