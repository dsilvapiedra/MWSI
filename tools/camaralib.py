from simple_pyspin import Camera

#Esta librería cuenta con algoritmos para manipular la cámara

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
    
