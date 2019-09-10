#!/usr/bin/env/python3

import time
import multiprocessing
import picamera
import tifffile
import numpy as np
import cv2
import datetime as dt
import logging

# Class of raspberrypi video recorder based on Picamera and multiprocessing.
# Outputs into a big tiff appropriate for downstream use in Deep Lab Cut or other software.
# Supports the stereopi.  

class ProcessedPiRecorder:
    #initialize the mf
    def __init__(self, x_resolution, y_resolution, framerate, rec_length, tif_path,
                 stereo=False, scale_factor=1, timestamp=True):      
                     
        #Stereo or mono
        self.stereo = stereo
        
        #Camera sensor and downscaling
        self.cam_width  = int((x_resolution+31)/32)*32
        self.cam_height = int((y_resolution+15)/16)*16
        
        self.img_width  = int(self.cam_width * scale_factor)
        self.img_height = int(self.cam_height * scale_factor)
        
        #Camera recording
        self.framerate  = framerate
        self.rec_length = rec_length
        self.video_path = tif_path
        self.timestamp  = timestamp
        
        #init the numpy array
        self.capture = np.zeros((self.img_height, self.img_width, 4), dtype=np.uint8)

        
    #Write the buffer to file
    def file_writer(self, queue, vid_path):
        #define our writer
        with tifffile.TiffWriter(vid_path, bigtiff=True) as tif:
            #infinite loop
            while True:
                #Grab the next entry in the queue
                if not queue.empty():
                    end, frame = queue.get()

                    #Catch the break condition
                    if end is True:
                        break
                    
                    #write to file
                    else:
                        #reorder frame to be rgba
                        frame = cv2.cvtColor(frame,  cv2.COLOR_BGRA2RGB)
                        tif.save(frame, compress=6, photometric='rgb')
    
    #Reads in the video stream, timestamps, monitors framerate and passes frames
    def camera_reader(self, queue):        
        #set up the camera
        if self.stereo:
            camera = picamera.PiCamera(stereo_mode='side-by-side',stereo_decimate=False)
            camera.hflip = True
        else:
            camera = picamera.PiCamera()

        camera.resolution = (self.cam_width, self.cam_height)
        camera.framerate  = self.framerate
        
        #Get the start time for latency and prep the counter variable
        counter=0
        t0 = dt.datetime.now()
        #Read frames
        for frame in camera.capture_continuous(self.capture, format='bgra', use_video_port=True,
                                                    resize=(self.img_width, self.img_height)):
            #Track performance
            counter = counter+1
            Hz = counter/(dt.datetime.now() - t0).total_seconds()

            #Annotate the frame
            if self.timestamp: camera.annotate_text = dt.datetime.now().strftime('%H:%M:%S:%f')

            #write the frame to the queue
            queue.put((False, frame))     
            
            #Break if time runs out
            if (dt.datetime.now()-t0).total_seconds() > self.rec_length :
                queue.put((True, frame))
                logging.info('Measured Framerate: %d Hz' % Hz)
                if abs(Hz/self.framerate-1) >0.05: logging.warning('WARNING: Camera ran @ %d Hz' % Hz)
                break
                
    #Starts the recorder            
    def recordVid(self):
        #define the queue
        self.q = multiprocessing.Queue()

        #Run it
        try:
            p1 = multiprocessing.Process(target=self.camera_reader, args=(self.q,))
            p2 = multiprocessing.Process(target=self.file_writer,   args=(self.q, self.video_path,))
            p1.start()
            p2.start()
            p1.join()
            p2.join()
        except Exception as e:
            logging.exception(e)
