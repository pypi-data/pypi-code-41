import os, sys
import numpy as np
import cv2
    
class TFLiteModel:
    
    def __init__(self, tf, model_path):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_shape = self.input_details[0]['shape']
        self.target_img_size = tuple(self.input_shape[1:3])

    def predict(self, image, color_mode='bgr'):
        assert color_mode in ['bgr', 'rgb']

        image = cv2.resize(image, self.target_img_size)

        if color_mode == 'bgr':
            image = image[:,:,::-1]
        
        image = image[np.newaxis,:,:,:].astype(np.float32) / 127.5 - 1

        self.interpreter.set_tensor(self.input_details[0]['index'], image)
        self.interpreter.invoke()

        output_scores = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        return output_scores