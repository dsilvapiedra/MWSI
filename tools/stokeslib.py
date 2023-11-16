import numpy as np
import sys

# Esta librería cuenta con todas las herramientas para hacer cálculo de parámetros de Stokes 
# (calibrado y sin calibrar), cálculo de medidas polarimétricas (dolp, aolp, diatenuación, 
# birrefringencia, depolarizancia, etc), cálculo de Mueller (un canal o tres canales) y 
# Descomposición de Lu-Chipman (M = Mdelta MR MD).

#########################################################################################################
#########################################################################################################
############################## Decodificadores del sensor polarizado ####################################
#########################################################################################################
#########################################################################################################

# Interpolación por vecinos cercanos
#
# La codificación de colores se hace en BGR, tal como está especificado en OpenCV
#
# I[:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#               Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#

def bayer_interpolacion_vecinos(M):
  I = np.zeros((M.shape[0],M.shape[1],3), dtype=np.uint8)
  #Rojos R
  I[0::2,0::2,2] = M[0::2,0::2]
  I[0::2,1::2,2] = M[0::2,0::2]
  I[1::2,0::2,2] = M[0::2,0::2]
  I[1::2,1::2,2] = M[0::2,0::2]
  #Verdes G
  I[0::2,0::2,1] = M[1::2,0::2]
  I[1::2,1::2,1] = M[1::2,0::2]
  I[1::2,0::2,1] = M[1::2,0::2]
  I[0::2,1::2,1] = M[0::2,1::2]
  #Azules B
  I[0::2,0::2,0] = M[1::2,1::2]
  I[1::2,0::2,0] = M[1::2,1::2]
  I[0::2,1::2,0] = M[1::2,1::2]
  I[1::2,1::2,0] = M[1::2,1::2]
  return I
  
# Interpolación por vecinos cercanos
#
# La codificación de colores se hace en BGR, tal como está especificado en OpenCV
#
# I[:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#               Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#

def bayer_interpolacion_bilineal(M):
  I = np.zeros((M.shape[0],M.shape[1],3), dtype=np.uint8)
  #Rojos
  I[0::2,0::2,2] = M[0::2,0::2]
  I[0::2,1::2,2][:,:-1] = 0.5*(M[0::2,0::2][:,:-1]+M[0::2,2::2])
  I[1::2,0::2,2][:-1,:] = 0.5*(M[0::2,0::2][:-1,:]+M[2::2,0::2])
  I[1::2,1::2,2][:-1,:-1] = 0.25*(M[0::2,0::2][:-1,:-1]+M[2::2,0::2][:,:-1]+M[0::2,2::2][:-1,:]+M[2::2,2::2])
  #Verdes 
  I[2::2,2::2,1] = 0.25*(M[1::2,2::2][:-1,:]+M[2::2,1::2][:,:-1]+M[3::2,2::2]+M[2::2,3::2])
  I[1::2,1::2,1][:-1,:-1] = 0.25*(M[0::2,1::2][:-1,:-1]+M[1::2,0::2][:-1,:-1]+M[1::2,2::2][:-1,:]+M[2::2,1::2][:,:-1])
  I[1::2,0::2,1] = M[1::2,0::2]
  I[0::2,1::2,1] = M[0::2,1::2]
  #Azules
  I[2::2,2::2,0] = 0.25*(M[1::2,1::2][:-1,:-1]+M[1::2,3::2][:-1,:]+M[3::2,1::2][:,:-1]+M[3::2,3::2])
  I[2::2,1::2,0] = 0.5*(M[1::2,1::2][:-1,:]+M[3::2,1::2])
  I[1::2,2::2,0] = 0.5*(M[1::2,1::2][:,:-1]+M[1::2,3::2])
  I[1::2,1::2,0] = M[1::2,1::2]
  return I

# Devuelve un observable lo mas rápido posible
#
# I[:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#               Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#

def fast_polarization_full_dec_array(A):
  I90 = bayer_interpolacion_vecinos(A[0::2,0::2])
  return I90

# Decodificación completa de la cámara polarizada
#
# Por defecto se utiliza la interpolación por vecinos cercanos
# Devuelve el vector de observables I = (I90, I45, I135, I0) en codificación de color BGR
#
# I90[:,:,:], I45[:,:,:], I135[:,:,:], I0[:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#               Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#
#
def polarization_full_dec_array(A, interpolacion = 'vecinos'):
  if interpolacion == 'vecinos':
    # Interpolación vecinos y descomposición de Bayer
    I0 = bayer_interpolacion_vecinos(A[1::2,1::2])
    I45 = bayer_interpolacion_vecinos(A[0::2,1::2])
    I90 = bayer_interpolacion_vecinos(A[0::2,0::2])
    I135 = bayer_interpolacion_vecinos(A[1::2,0::2])
  elif interpolacion == 'bilineal':
    # Interpolación vecinos y descomposición de Bayer
    I0 = bayer_interpolacion_bilineal(A[1::2,1::2])
    I45 = bayer_interpolacion_bilineal(A[0::2,1::2])
    I90 = bayer_interpolacion_bilineal(A[0::2,0::2])
    I135 = bayer_interpolacion_bilineal(A[1::2,0::2])
  return I90, I45, I135, I0


#########################################################################################################
#########################################################################################################
######################################## Calibración del sistema ########################################
#########################################################################################################
#########################################################################################################

# Calcula la matriz de instrumentación A (S = AI) del sistema 
#
# Toma como entrada una estadística de parámetros de Stokes (S_stat) y observables (I_stat)
# Devuelve la matriz de instrumentaición A
#
# S[:,:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#               Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#                Cuarta componente: Dimensión vertical del vector (S0, S1, S2)
#                Quinta componente: Dimensión horizontal de estadísticas (dato1, dato2, ... datoN)
#
# I[:,:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#               Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#                Cuarta componente: Dimensión vertical del vector (I90, I45, I135, I0)
#                Quinta componente: Dimensión horizontal de estadísticas (dato1, dato2, ... datoN)
#
# A[:,:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#               Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)

def calcular_instrumentacion(I_stat,S_stat):
  A = np.einsum('ijklm,ijkmn->ijkln',S_stat,np.linalg.pinv(I_stat))
  return A     

#Devuelve matriz promediada y matriz de desviación de la matriz de instrumentación
#
# A[:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2,3)
#
# A_mean[:,:,:]: 
#                Primera componente: Dimensión vertical de la matriz (0,1,2)
#                Segunda componente: Dimensión horizontal de la matriz (0,1,2,3)
#
def instrumentacion_media_std(A):
  A_mean = np.zeros((3,4,3))
  A_std = np.zeros((3,4,3))
  for k in range(3):
    for i in range(3):
      for j in range(4):
        A_mean[i,j,k] = np.mean(A[:,:,k,i,j])
        A_std[i,j,k] = np.std(A[:,:,k,i,j])
  return A_mean, A_std

#########################################################################################################
#########################################################################################################
########################################### Stokes y Mueller ############################################
#########################################################################################################
#########################################################################################################

# Calcula los parámetros de Stokes
#
# Toma como entrada en vector de observables I = (I90, I45, I135, I0),
# la matriz de instrumentación A (S = AI) y la bandera calibrar (si o no)
# Devuelve el vector de Stokes S = (S0, S1, S2) calibrado o no
#
# A[:,:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#               Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)
#
# S0[:,:,:],S1[:,:,:],S2[:,:,:]: 
#                                 Primera componente: Dimensión vertical pixeles [0, dimy]
#                                 Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                                 Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#
def calcular_stokes (I90, I45, I135, I0, A = None, decimador = 1):

  #Decimador
  I0 = I0[::decimador,::decimador]
  I45 = I45[::decimador,::decimador]
  I90 = I90[::decimador,::decimador]
  I135 = I135[::decimador,::decimador]
  
  #Modo sin calibración
  if A == None:

    #Calculo
    S0 = I0.astype(np.int16)+I90.astype(np.int16)
    S1 = I0.astype(np.int16)-I90.astype(np.int16)
    S2 = I45.astype(np.int16)-I135.astype(np.int16)

  #Modo calibrado  
  else:

    #Decimador
    A = A[::decimador,::decimador]
    A = A[::decimador,::decimador]
    A = A[::decimador,::decimador]
    A = A[::decimador,::decimador]
    
    #Calculo
    S0 = A[:,:,:,0,0]*I0.astype(float)+A[:,:,:,0,1]*I45.astype(float)+A[:,:,:,0,2]*I90.astype(float)+A[:,:,:,0,3]*I135.astype(float)
    S1 = A[:,:,:,1,0]*I0.astype(float)+A[:,:,:,1,1]*I45.astype(float)+A[:,:,:,1,2]*I90.astype(float)+A[:,:,:,1,3]*I135.astype(float)
    S2 = A[:,:,:,2,0]*I0.astype(float)+A[:,:,:,2,1]*I45.astype(float)+A[:,:,:,2,2]*I90.astype(float)+A[:,:,:,2,3]*I135.astype(float)
  
  return S0, S1, S2


# Calcula matriz de Mueller en tres canales
# Recibe como entrada los vectores de stokes de entrada (Sin) y los vectores de Stokes de salida (Sout)
# en codificación de colores BGR 
# Devuelve la matriz de Mueller M del sistema 
#
# S_out_stat[:,:,:,:,:]:
#                       Primera componente: Dimensión vertical pixeles [0, dimy]
#                       Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                       Tercer componente:  Canales de colores Blue (B), Green (G) y Red (R) 
#                       Cuarta componente:  Componente del vector (S0,S1,S2) 
#                       Cuarta componente:  Datos (1,...,N) (entradas)
#
# S_in_stat[:,:,:,:,:]:
#                       Primera componente: Dimensión vertical pixeles [0, dimy]
#                       Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                       Tercer componente:  Canales de colores Blue (B), Green (G) y Red (R) 
#                       Cuarta componente:  Componente del vector (S0,S1,S2) 
#                       Cuarta componente:  Datos (1,...,N) (entradas)
#
# M[:,:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#               Tercera componente: Canales de colores Blue (B), Green (G) y Red (R) 
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)

def calcular_mueller(S_in_stat,S_out_stat):
  M = np.einsum('ijklm,ijkmn->ijkln',S_out_stat,np.linalg.pinv(S_in_stat))
  return M

def normalizar_mueller(M):
  # Normaliza una matriz de mueller M
  # En cada i,j y en cada color k, divide la componente i,j,k por m00

  M_norm = M.copy()
  for i in range(3):
    for j in range(3):
      for k in range(3):
        #print(i,j,k)
        #print(np.mean(M[:, :, k, i, j]))
        M_norm[:, :, k, i, j] = M_norm[:, :, k, i, j] / M[:, :, k, 0, 0]
        print(np.mean(M_norm[:, :, k, i, j]))
  return M_norm

# Version con Sin ya invertida

def calcular_mueller_inv(S_in_stat_inv,S_out_stat):
  M = np.einsum('ijklm,ijkmn->ijkln',S_out_stat,S_in_stat_inv)
  return M

# Calcula matriz de Mueller en un canal (tiempo real)
# Recibe como entrada los vectores de stokes de entrada (Sin) y los vectores de Stokes de salida (Sout)
# Devuelve la matriz de Mueller M del sistema en un único canal
#
# S_out_stat[:,:,:,:]:
#                       Primera componente: Dimensión vertical pixeles [0, dimy]
#                       Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                       Tercer componente:  Dimensión horizonal pixeles (0,1,2)
#                       Cuarta componente:  Dimensión horizonal pixeles (B,G,R) (entradas)
#
# S_in_stat[:,:,:,:]:
#                       Primera componente: Dimensión vertical pixeles [0, dimy]
#                       Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                       Tercer componente:  Dimensión horizonal pixeles (0,1,2)
#                       Cuarta componente:  Dimensión horizonal pixeles (B,G,R) (entradas)
#
# M[:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)

def calcular_mueller_canal(S_in_stat,S_out_stat):
  Mueller_img = np.einsum('ijlm,ijmn->ijln',S_out_stat,np.linalg.pinv(S_in_stat))
  return Mueller_img
  
# Acopla componentes de la matriz de Mueller en una sola imagen monocromática
#
# M[:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)
#
# M_show:       Figura con imagen la matriz de Mueller.
#
def acoplar_mueller(M):
  M_show = M.copy()
  M1_show = np.append(M_show[:,:,0,0], M_show[:,:,0,1], axis=1)
  M1_show = np.append(M1_show, M_show[:,:,0,2], axis=1)
  M2_show = np.append(M_show[:,:,1,0], M_show[:,:,1,1], axis=1)
  M2_show = np.append(M2_show, M_show[:,:,1,2], axis=1)
  M3_show = np.append(M_show[:,:,2,0], M_show[:,:,2,1], axis=1)
  M3_show = np.append(M3_show, M_show[:,:,2,2], axis=1)
  M_show = np.append(M1_show, M2_show, axis = 0)
  M_show = np.append(M_show, M3_show, axis = 0)
  return M_show

#Desacoplar imagen y recuperar array en RGB

def desacoplar_mueller(M_show):
  M = np.zeros((M_show.shape[0]//3,M_show.shape[1]//3,3,3,3),dtype=float)
  for i in range(3):
    for j in range(3):
      for k in range(3):
        M[:,:,k,i,j] = M_show[i*1024:(i+1)*1024,j*1224:(j+1)*1224,k]
  return M

# Promedia matriz de Mueller
#
# M[:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)
#
# M_mean[:,:]: 
#                Primera componente: Dimensión vertical de la matriz (0,1,2)
#                Segunda componente: Dimensión horizontal de la matriz (0,1,2)
#
def mueller_mean(M):
    M_mean = np.zeros((3,3))
    for i in range(3):
      for j in range(3):
        M_mean[i,j] = np.round(np.mean(M[:,:,i,j]),1)
    return M_mean
  
###################################################################
################ Descomposición de Lu-Chipman #####################
###################################################################

# Calcula la descomposición de Lu-Chipman de una matriz de Mueller
# Recibe como entrada una matriz de Mueller M no singular (det(M) != 0 para todo pixel (x,y))
# y devuelve tres matrices de mueller (MDelta, MR, MD) y la componente m00
# MDelta: Matriz de depolarizancia 
# MR: Matriz de retardancia
# MD: Matriz de diatenuación
#
# M[:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)
#
# MR[:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)
#
# MD[:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)
#
# MDelta[:,:,:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#                Cuarta componente: Dimensión vertical de la matriz (0,1,2)
#                Quinta componente: Dimensión horizontal de la matriz (0,1,2)
#
# m00[:,:]: 
#               Primera componente: Dimensión vertical pixeles [0, dimy]
#               Segunda componente: Dimensión horizonal pixeles [0, dimx]
#
def lu_chipman(M):
  #Identidades
  I2 = np.stack([np.stack([np.identity(2)]*M.shape[1])]*M.shape[0])
  I3 = np.stack([np.stack([np.identity(3)]*M.shape[1])]*M.shape[0])

  #Normalización
  M_norm = M.copy()
  for i in range(3):
    for j in range(3):
      M_norm[:,:,i,j] = M[:,:,i,j]/M[:,:,0,0]
  
  #M Diatenuación
  MD = np.ones_like(M)
  MD_inv = np.ones_like(M)
  D = M_norm[:,:,0,1:]
  D2 = np.einsum('ijk,ijk->ij',D, D)
  a = np.sqrt(1-D2,out=np.zeros_like(D2),where=D2<=1)
  b = np.divide(1-a,D2,out=np.zeros_like(D2),where=D2!=0)
  MD[:,:,0,1:] = D
  MD[:,:,1:,0] = D
  for i in range(2):
    for j in range(2):
      MD[:,:,1+i,1+j] = a*I2[:,:,i,j] + b*np.einsum('ijk,ijl->ijkl',D,D)[:,:,i,j]

  #M Diatenuación inversa
  #MD_inv[:,:,0,0] = np.ones_like(D2)/(1-D2)
  #for i in range(2):
  #  MD_inv[:,:,0,1+i] = -D[:,:,i]/(1-D2)
  #  MD_inv[:,:,1+i,0] = -D[:,:,i]/(1-D2)
  #  for j in range(2):
  #    MD_inv[:,:,1+i,1+j] = I2[:,:,i,j]/a+np.einsum('ijk,ijl->ijkl',D,D)[:,:,i,j]/(a**2*(1+a))

  #M Prima
  Mprima = np.einsum('ijkl,ijlm->ijkm',M_norm[:,:,:,:],np.linalg.pinv(MD))
  mprima = Mprima[:,:,1:,1:]

  #M Delta
  mdr = np.einsum('ijkl,ijlm->ijkm',mprima,mprima.transpose(0,1,3,2))
  L , V = np.linalg.eig(mdr)

  #Depolarizancia
  delta = np.sqrt(np.abs(L[:,:,0])) * (L[:,:,0] >= L[:,:,1]) + np.sqrt(np.abs(L[:,:,1])) * (L[:,:,0] < L[:,:,1])
  MDelta = np.zeros_like(M)
  MDelta[:,:,0,0] = np.ones(M[:,:,0,0].shape)
  MDelta[:,:,1,1] = delta
  MDelta[:,:,2,2] = delta

  #Polarizancia:
  PDelta = np.zeros((M.shape[0],M.shape[1],2))
  for i in range(2):
    PDelta[:,:,i] = (M_norm[:,:,1+i,0] - np.einsum('ijkl,ijl->ijk',M_norm[:,:,1:,1:],D)[:,:,i])/(1-D2)
  MDelta[:,:,1:,0] = PDelta
  
  #M Retardancia
  MR = np.einsum('ijkl,ijlm->ijkm', np.linalg.pinv(MDelta), Mprima)

  return MDelta, MR, MD, M[:,:,0,0]

# Devuelve la matriz de Mueller 4x4 del polarizador lineal con transmitancia T, tasa de extinción e y 
# ángulo de polarización theta_d (en grados)
def mueller_polarizador(T,D,theta_d):
  theta_d = theta_d*np.pi/180 #Radianes
  MR = np.array([[1,0,0,0],[0,np.cos(2*theta_d),np.sin(2*theta_d),0],[0,-np.sin(2*theta_d),np.cos(2*theta_d),0],[0,0,0,1]])
  M = MR.T @ np.array([[1,D,0,0],[D,1,0,0],[0,0,np.sqrt(1-D**2),0],[0,0,0,np.sqrt(1-D**2)]]) @ MR
  return M

# Devuelve la matriz de Mueller 4x4 del retardador lineal con birrefringencia phi (en grados) y 
# ángulo de rotación theta (en grados)
def mueller_retardador(phi,theta):
  theta = theta*np.pi/180   #Radianes
  phi = phi*np.pi/180       #Radianes
  MR = np.array([[1,0,0,0],[0,np.cos(2*theta),np.sin(2*theta),0],[0,-np.sin(2*theta),np.cos(2*theta),0],[0,0,0,1]])
  M =  MR.T @ np.array([[1,0,0,0],[0,1,0,0],[0,0,np.cos(phi),np.sin(phi)],[0,0,-np.sin(phi),np.cos(phi)]]) @ MR
  return M

# Devuelve la matriz de Mueller 4x4 del rotador con ángulo de rotación theta (en grados)
def mueller_rotador(theta):
  theta = theta*np.pi/180 #Radianes
  M = np.array([[1,0,0,0],[0,np.cos(2*theta),-np.sin(2*theta),0],[0,np.sin(2*theta),np.cos(2*theta),0],[0,0,0,1]])
  return M

# Medidas fisicas

# Nuevo arcotangente entre 0 y 2pi
def arctan3(y,x):
  return np.mod(np.arctan2(y,x),2*np.pi)

#Grado de polarización
def calcular_dolp(S0,S1,S2):
  dolp = np.divide(np.sqrt(np.power(S1.astype(float),2) + np.power(S2.astype(float),2)),S0, out = np.zeros_like(S0.astype(float)), where = S0!= 0) 
  return dolp

#Ángulo de polarización
def calcular_aolp(S1,S2):
  aolp = 0.5*arctan3(S2.astype(float),S1.astype(float))
  return aolp

# Grado de polarización
def calcular_dolp_mueller(M):
  S0 = M[:,:,0,0];   S1 = M[:,:,1,0];   S2 = M[:,:,2,0]
  return calcular_dolp(S0,S1,S2)

# Ángulo de polarización
def calcular_aolp_mueller(M):
  S1 = M[:,:,1,0];   S2 = M[:,:,2,0]
  return calcular_aolp(S1,S2)

# Diatenuación
def calcular_diatenuacion(M):
  D = np.sqrt(M[:,:,0,1]**2+M[:,:,0,2]**2)/M[:,:,0,0]
  return D

# Angulo de diatenuación  
def calcular_aod(M):
  S1 = M[:,:,0,1];   S2 = M[:,:,0,2]
  return calcular_aolp(S1,S2)

# Poder de polarizancia
def power_of_depolarization(M_delta):
  delta = np.ones((1024,1224))-M_delta[:,:,1,1]
  return delta

# Actividad optica
def optical_activity(M_R):
  psi = np.arctan2(M_R[:,:,2,1]-M_R[:,:,1,2],M_R[:,:,1,1]+M_R[:,:,2,2])
  return psi

# Retardancia lineal
def linear_retardance(M_R):
  delta = np.arccos(np.sqrt((M_R[:,:,1,1]+M_R[:,:,2,2])**2+(M_R[:,:,2,1]-M_R[:,:,1,2])**2)-1)
  return delta

def main():
  return True

if __name__ == '__main__':

    if main():
        sys.exit(0)
    else:
        sys.exit(1)
