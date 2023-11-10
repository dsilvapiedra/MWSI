import sys
from motor_control import controlar_motores

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python main.py <motor> <movimiento>")
        print("Ejemplo: python main.py X F  # Mueve el motor X hacia adelante")
        sys.exit(1)

    motor_input = sys.argv[1].upper()
    movimiento_input = sys.argv[2].upper()

    controlar_motores(motor_input, movimiento_input)a
    

