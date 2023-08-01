from simple_photo import main
from motor_control_ssh import ejecutar_comando_ssh
import time


# Definir la cantidad de pasos en cada dirección
X_STEPS = 6
Y_STEPS = 6

# Calcular la posición del centro en términos de pasos
centro_x = X_STEPS // 2
centro_y = Y_STEPS // 2

# Definir el rango de índices para las fotos en la grilla
# Puedes ajustar estos valores según tus necesidades
INDICE_INICIAL = 1
INDICE_FINAL = X_STEPS * Y_STEPS

# Definir el tiempo de espera entre movimientos (en segundos)
TIEMPO_ESPERA = 0.5

def capturar_muestra(X, Y):
    x = y = 0
    dx = 0
    dy = -1
    for i in range(max(X, Y)**2):
        if (-X/2 < x <= X/2) and (-Y/2 < y <= Y/2):

            print (x, y)
            
            # Tomar una foto en la posición actual de la grilla
            main(str(i).zfill(2))

            

        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
            dx, dy = -dy, dx
        x, y = x+dx, y+dy
        
        if dx != 0:
            direccion_x = "F" if dx > 0 else "B"
            print("Mover X en direccion ", direccion_x)

            comando = f"cd /home/mwsi/Desktop/main && python motor_control.py X {direccion_x}"
            ejecutar_comando_ssh(comando)
            
        if dy != 0:
            direccion_y = "F" if dy > 0 else "B"
            print("Mover Y en direccion ", direccion_y)
            comando = f"cd /home/mwsi/Desktop/main && python motor_control.py Y {direccion_y}"
            ejecutar_comando_ssh(comando)

capturar_muestra(X_STEPS, Y_STEPS)        