import numpy as np
import cv2
from numpy.lib.type_check import imag

class Imaging():

    @staticmethod
    def normalize_to_1(imageBefore):
        '''normalize a image's value to between 0 and 1
        
        '''
        image64 = imageBefore.astype(np.float64)
        if np.min(image64) < 0:
            image64 -= np.min(image64)
        out_image = image64 / np.max(image64)
        return out_image

    @staticmethod
    def normalized_to_255(imageBefore):
        '''normalize a image's value to between 0 and 255
        
        '''
        image64 = imageBefore.astype(np.float64)
        if np.min(image64) < 0:
            image64 -= np.min(image64)
        out_image = 255 * image64 / np.max(image64)
        out_image = out_image.astype(np.uint8)
        return out_image

    @staticmethod
    def psnr(output, reference):
        '''calcualte PSNR of superresolved image against its input
        
        '''
        output = Imaging.normalized_to_255(output)
        reference = Imaging.normalized_to_255(reference)

        return '{:.2f}'.format(round(cv2.PSNR(output, reference), 2))
