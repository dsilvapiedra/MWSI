import sys
from tools.camaralib import take_stokes
from motor_control_ssh import ejecutar_comando_ssh
import time
import numpy as np
import cv2

IMG_SAVE_PATH = 'img/'   

#Exposicion
exposure_time = 5000

# Numero de promedios
N = 1

# Definir la cantidad de pasos en cada dirección
X_STEPS = 10
Y_STEPS = 10

# Calcular la posición del centro en términos de pasos
centro_x = X_STEPS // 2
centro_y = Y_STEPS // 2

# Definir el rango de índices para las fotos en la grilla
# Puedes ajustar estos valores según tus necesidades
INDICE_INICIAL = 1
INDICE_FINAL = X_STEPS * Y_STEPS

# Definir el tiempo de espera entre movimientos (en segundos)
TIEMPO_ESPERA = 0.5

# Definir angulos para polarizacion
POL_ANGS = [0, 60, 120]

def captura_polarizacion(nombre_img):
    for angulo in POL_ANGS:
        #main(nombre_img + '_' + str(angulo))
        if angulo != POL_ANGS[-1]:
            print("Mover T en direccion F")
            comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T F"
            ejecutar_comando_ssh(comando)
    # volver a posicion original
    for _ in range(len(POL_ANGS)-1):
        print("Mover T en direccion B")
        comando = f"cd /home/mwsi/Desktop/main && python motor_control.py T B"
        ejecutar_comando_ssh(comando)

def mover_motor(motor, direccion, pasos=1):
    for _ in range(pasos):
        print(f"Mover {motor} en direccion ", direccion)
        comando = f"cd /home/mwsi/Desktop/main && python motor_control.py {motor} {direccion}"
        ejecutar_comando_ssh(comando)

def capturar_espiral(X, Y):
    x = y = 0
    dx = 0
    dy = -1
    for i in range(max(X, Y)**2):
        if (-X/2 < x <= X/2) and (-Y/2 < y <= Y/2):

            print (x, y)
            
            # Tomar una foto en la posición actual de la grilla
            captura_polarizacion(str(i).zfill(2))

        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
            dx, dy = -dy, dx
        x, y = x+dx, y+dy
        
        if dx != 0:
            direccion_x = "F" if dx > 0 else "B"
            mover_motor('X',"F" if dx > 0 else "B")
            
        if dy != 0:
            direccion_y = "F" if dy > 0 else "B"
            mover_motor('Y',direccion_y)

def capturar_muestra(X, Y, tipo):
    # comienza en centro x, extremo y
    x = 0
    y = -centro_y + 1
    dx = -1
    dy = 0
    for i in range(max(X, Y)**2):
        
        # Si estamos dentro de los límites, capturamos
        if (-X/2 <= x <= X/2) and (-Y/2 <= y <= Y/2):    
            
            #Imprime posición actual
            print (x, y)

            # Tomar segun el tipo una foto en la posición actual de la grilla
            if tipo == 'mueller':

                captura_polarizacion(str(i).zfill(2)) #Captura matriz de mueller

            elif tipo == 'intensidad':

                # Captura Stokes
                S = take_stokes(exposure_time, N)

                # Guarda imagen de intensidad
                cv2.imwrite(IMG_SAVE_PATH + str(i).zfill(2) + '.png', S[:,:,:,0].astype(np.uint8))

        #if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
        if x in [-X/2, X/2]:
            if dy == 0:
                dx, dy = 0, 1
            else:
                dx, dy = -np.sign(x), 0
    
        x, y = x+dx, y+dy
        
        if dx != 0:
            direccion_x = "F" if dx > 0 else "B"
            mover_motor('X',"F" if dx > 0 else "B")
            
        if dy != 0:
            direccion_y = "F" if dy > 0 else "B"
            mover_motor('Y',direccion_y)
            
    # volver a posicion inicial
    print('Volviendo a posición inicial...')
    mover_motor('Y', 'B', Y_STEPS)
    mover_motor('X', 'B', X_STEPS//2)

def main(tipo = None):

    #Nombre archivo
    if tipo is None:
        tipo = sys.argv[1]

    #Captura muestra, calcula tiempo
    tic = time.time()
    capturar_muestra(X_STEPS, Y_STEPS, tipo)        
    toc = time.time()

    print("Muestra completa capturada en "+str(int((toc-tic)//60))+" minutos y "+str(int((toc-tic) % 60))+' segundos.')

    return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
