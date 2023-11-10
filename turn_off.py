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
    stdin, stdout, stderr = ssh.exec_command(comando)
    print(stdout.read().decode())
    print(stderr.read().decode())
    ssh.close()
    return stdout.readlines()

if __name__ == "__main__":

    comando = f"sudo shutdown -h now"
    
    respuesta = ejecutar_comando_ssh(comando)
    print("Respuesta del servidor:")
    print("".join(respuesta))
