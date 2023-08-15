import paramiko
import sys

RPI_USER = 'mwsi'
RPI_PASS = 'mwsi'
RPI_IP = '169.254.110.82'  #10.42.0.112
RPI_PORT = 22

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
