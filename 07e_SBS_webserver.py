#!/usr/bin/python
'''
	Author: Igor Maculan - n3wtron@gmail.com
	A Simple mjpg stream http server
'''
import cv2
import numpy as np
from PIL import Image
import threading
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import StringIO
import time
#from imutils.video import WebcamVideoStream
#from imutils.video import FPS
import imutils
from threading import Thread


from Adafruit_AMG88xx import Adafruit_AMG88xx

# Bildgröße auf dem Bildschirm
global l_xres
global l_yres
global r_xres
global r_yres

l_xres = 240
l_yres = 240

r_xres = 240
r_yres = 240

global videoanzeige
videoanzeige = 0


# Größe von der Kamera selbst
global l_img_res_x
global l_img_res_y
global r_img_res_x
global r_img_res_y

l_img_res_x = 640
l_img_res_y = 480

r_img_res_x = 640
r_img_res_y = 480

global mix_bild
global sensor

mix_bild = np.zeros((240,240,3), np.uint8)
sensor = Adafruit_AMG88xx()
time.sleep(0.1)

global waerme
global w2
global w3
global resized_thermo

waerme = sensor.readPixels()
w2 = np.asfarray (waerme)
w3 = np.reshape(w2, (8,-1))

global width
global height

width = 8
height = 8
resized_thermo = cv2.resize(w3, (30*width, 30*height), interpolation= cv2.INTER_CUBIC)

cv2.startWindowThread()
#cv2.namedWindow('image')

cv2.namedWindow('image', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


global bild1
		
# Schieberegler erzeugen


# wird aufgerufen, wenn Schieberegler genutzt werden; hier nur Leerfunktion
def nothing(x):
    pass
					
cv2.createTrackbar('Transp','image',1,100,nothing)
cv2.createTrackbar('MIN','image',0,80,nothing)
cv2.createTrackbar('MAX','image',0,80,nothing)
cv2.createTrackbar('Augenabstand','image',1,70,nothing)
#cv2.createTrackbar('Thermo_Shift','image',1,70,nothing)
cv2.setTrackbarPos('Transp','image',90)
cv2.setTrackbarPos('MIN','image',10)
cv2.setTrackbarPos('MAX','image',40)
cv2.setTrackbarPos('Augenabstand','image',1)
#cv2.setTrackbarPos('Thermo_Shift','image',10)
					





capture=None

class WebcamVideoStream:
	def __init__(self, src=0):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(src)
		self.stream.set(3,640)
		self.stream.set(4,480)
		
                #capture_r.set(4,r_img_res_y)
		(self.grabbed, self.frame) = self.stream.read()
 
		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False
		
	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self
 
	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
 
			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()
 
	def read(self):
		# return the frame most recently read
		return self.frame
 
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

class CamHandler(BaseHTTPRequestHandler):
	
	def do_GET(self):
		global bild1
		global waerme
		global w2
		global w3
		global resized_thermo
		global mix_bild
		global sensor
		global l_img_res_x
		global l_img_res_y
		global r_img_res_x
		global r_img_res_y
		global l_xres
		global l_yres
		global r_xres
		global r_yres
		l_img_res_x = 640
		l_img_res_y = 480

		r_img_res_x = 640
		r_img_res_y = 480
		l_xres = 240
		l_yres = 240

		r_xres = 240
		r_yres = 240




		
		
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			while True:
				try:
					#rc,img_right = capture_r.read()
					#if not rc:
					#	continue

					#rc,img_left = capture_l.read()
					#if not rc:
					#	continue

					#if (videoanzeige == 0):
					img_right = capture_r.read()
					#img_right = imutils.resize(img_right, width=480)
					img_left = capture_l.read()
					#img_left = imutils.resize(img_left, width=480)
					img_r=cv2.cvtColor(img_right,cv2.COLOR_BGR2RGB)
					img_l=cv2.cvtColor(img_left,cv2.COLOR_BGR2RGB)
					
					


					#videoanzeige = 1


					# Werte der Schieberegler einlesen
					abstand = cv2.getTrackbarPos('Augenabstand','image')
					transp = cv2.getTrackbarPos('Transp','image')
					min_temp = cv2.getTrackbarPos('MIN','image')
					max_temp = cv2.getTrackbarPos('MAX','image')
					thermoshift = cv2.getTrackbarPos('Thermo_Shift','image')


					#high = cv2.getTrackbarPos('high','image')

					l_x_roi = (l_img_res_x-l_xres)/2
					l_y_roi = (l_img_res_y-l_yres)/2-abstand
					l_img = img_l[l_y_roi:(l_y_roi+l_yres), l_x_roi:(l_x_roi+l_xres)]
					r_x_roi = (r_img_res_x-r_xres)/2
					r_y_roi = (r_img_res_y-r_yres)/2-abstand
					r_img = img_r[r_y_roi:(r_y_roi+r_yres), r_x_roi:(r_x_roi+r_xres)]
        
        
					# Bild rotieren (Kameras sind Hochkant und spiegelsymmetrisch)    
        
					l_img = np.rot90(l_img,1)
					r_img = np.rot90(r_img,3)
        
					# Wärmesensor auslesen
					waerme = sensor.readPixels()
					#ergebnis ist eine Liste; muss in ein Numpy-Array umgewandelt werden, dann rotiert,bis Bild aufrecht
					w2 = np.asfarray (waerme)
					w3 = np.reshape(w2, (8,-1))
					w4 = np.rot90(w3,3)

					#8x8 Bildpunkte vom Sensor hochrechnen...
					resized_thermo = cv2.resize(w4, (30*width, 30*height), interpolation= cv2.INTER_CUBIC)

					# Min-Max Bereich auf den vollen Wertebereich strecken
					clamp = np.uint8(np.interp(resized_thermo, [min_temp, max_temp],[0,255]))

					# ... und einfärben
					col = cv2.applyColorMap(clamp, cv2.COLORMAP_JET)


					# Webcambilder mit Farbverlauf Thermo überlagern:
					l_mix_bild = cv2.addWeighted(l_img, transp/100.0 , col , 1-transp/100.0 ,0)
					r_mix_bild = cv2.addWeighted(r_img, transp/100.0 , col , 1-transp/100.0 ,0)
        
					# Bilder zusammenfassen:
					bild1 = np.concatenate((l_mix_bild, r_mix_bild), axis =1)
        
					# zusammengefügtes Bild zeigen
					
					cv2.imshow('image',cv2.cvtColor(bild1,cv2.COLOR_BGR2RGB))
					#print("test")


					
					#imgRGB_r=cv2.cvtColor(img_r,cv2.COLOR_BGR2RGB)
					#imgRGB_l=cv2.cvtColor(img_l,cv2.COLOR_BGR2RGB)
					#doppelt = np.concatenate((imgRGB_l, imgRGB_r), axis =1)

					jpg = Image.fromarray(bild1)
					tmpFile = StringIO.StringIO()
					jpg.save(tmpFile,'JPEG')
					self.wfile.write("--jpgboundary")
					self.send_header('Content-type','image/jpeg')
					self.send_header('Content-length',str(tmpFile.len))
					self.end_headers()
					jpg.save(self.wfile,'JPEG')
					time.sleep(0.05)
				except KeyboardInterrupt:
					break
			return
		if self.path.endswith('.html'):
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write('<html><head></head><body>')
			self.wfile.write('<img src="http://127.0.0.1:8080/cam.mjpg"/>')
			self.wfile.write('</body></html>')
			return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():

	#fullscreen-Modus
	#cv2.namedWindow('image', cv2.WND_PROP_FULLSCREEN)
	#cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

	#für tests ohne fullscreen
    


        



        global capture_l
        capture_l = WebcamVideoStream(src=1).start()

        #capture_l = cv2.VideoCapture(1)
        #capture_l.set(3,l_img_res_x)
        #capture_l.set(4,l_img_res_y)
        #capture_l.set(cv2.CAP_PROP_FPS, 10)

        global capture_r
        capture_r = WebcamVideoStream(src=0).start()
        
        #capture_r = cv2.VideoCapture(0)
        #capture_r.set(3,r_img_res_x)
        #capture_r.set(4,r_img_res_y)
        #capture_r.set(cv2.CAP_PROP_FPS, 10)


	# kurz abwarten bis kamera gestartet ist
        time.sleep(0.1)

	# Bilder einlesen von der Kamera

        global img_r
        global img_l



	
        try:
                server = ThreadedHTTPServer(('0.0.0.0', 8080), CamHandler)
                print "server started"
                server.serve_forever()
        except KeyboardInterrupt:
                capture_r.stop()
                capture_l.stop()
                server.socket.close()

if __name__ == '__main__':
	main()
