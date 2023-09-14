import sys
from tools.camaralib import ejecutar_comando_ssh

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python controlar_motores_ssh.py <motor> <movimiento>")
        print("Ejemplo: python controlar_motores_ssh.py X F  # Mueve el motor X hacia adelante")
        sys.exit(1)

    motor_input = sys.argv[1].upper()
    movimiento_input = sys.argv[2].upper()
    
    comando = f"cd /home/mwsi/Desktop/main && python motor_control.py {motor_input} {movimiento_input}"
    
    respuesta = ejecutar_comando_ssh(comando)
    print("Respuesta del servidor:")
    print("".join(respuesta))
