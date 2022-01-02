import os, uuid, io
import torch
import matplotlib.pyplot as plt
import numpy as np 
import cv2
from PIL import Image
from imaging import Imaging

from model import SRCNN

class Worker():
    def __init__(
        self, 
        dirArtefact='artefact', 
        model='srcnn_state_dict.tar', 
        dirGallary='gallary', 
        dirInput = 'input', 
        dirOutput='output'
    ):
        self.dirArtefact = dirArtefact
        self.model = model
        self.dirGallary = dirGallary
        self.dirInput = dirInput
        self.dirOutput = dirOutput
        self.device = torch.device('cuda' if (torch.cuda.is_available()) else 'cpu')
        self.generatedOutput = []

    def get_generated_files(self):
        '''return a list of generated file by this worker
        
        '''
        return self.generatedOutput

    def list_gallary(self):
        '''get a list of available images from gallary

        Returns
        -------
        list[str]
            a list of image names
        
        '''
        dataset = os.listdir(self.dirGallary)
        return dataset

    def save_uploaded_image(self, imageByteArr):
        '''save uploaded image from user,
        return saved image path and image byte array
        
        '''
        image = Image.open(io.BytesIO(imageByteArr))
        imageName = '{}.png'.format(uuid.uuid4())
        imagePath = os.path.join(self.dirInput, imageName)
        image.save(imagePath)
        self.generatedOutput.append(imagePath)

        with open(imagePath, 'rb') as f:
            out = f.read()
        return imagePath, out

    def get_image(self, dir, imgFileName):
        '''convert a stored image file into string
        to be sent back to front end
        
        '''
        imageDir = ''
        if dir == 'gallary':
            imageDir = self.dirGallary
        elif dir == 'output':
            imageDir = self.dirOutput
        elif dir == 'input':
            imageDir = self.dirInput

        imagePath = os.path.join(imageDir, imgFileName)
        with open(imagePath, 'rb') as f:
            out = f.read()
        return imagePath, out

    def superresolve_color(self, imagePath, debug=False):
        '''make a superresolved prediction using a given image

        Parameters
        ----------
        imgName : str
            file name of the low resolution image
        
        '''
        srcnn = SRCNN()
        srcnn.load_state_dict(torch.load(os.path.join(self.dirArtefact, self.model), map_location=torch.device(self.device)))

        image = plt.imread(os.path.join(imagePath))
        image_ori_shape = image.shape
        image = cv2.resize(image, (image_ori_shape[1]//2, image_ori_shape[0]//2))
        image = cv2.resize(image, (image_ori_shape[1], image_ori_shape[0]))

        image_lowRes = image

        out_image = np.zeros_like(image)
        srcnn.eval()
        for i in range(image.shape[2]):
            sub_image = image[:,:,i]
            sub_image = sub_image[np.newaxis, ...]

            with torch.no_grad():
                sub_image = sub_image.astype(np.float32)
                sub_image = torch.tensor(sub_image, dtype=torch.float).to(self.device)
                sub_image = sub_image.unsqueeze(0)
                outputs = srcnn(sub_image)

            outputs = outputs.cpu()
            outputs = outputs.detach().numpy()
            outputs = outputs.reshape(outputs.shape[2], outputs.shape[3], outputs.shape[1])

            out_image[:,:,i] = outputs[:,:,0]

        out_image = out_image.astype(np.float64)
        if np.min(out_image) < 0:
            out_image -= np.min(out_image)
        out_image /= np.max(out_image)
        
        outImageName = '{}.png'.format(uuid.uuid4())
        outImagePath = os.path.join(self.dirOutput, outImageName)
        plt.imsave(outImagePath, out_image, cmap='gray')
        _, serializedOutImage = self.get_image(self.dirOutput, outImageName)
        self.generatedOutput.append(outImagePath)

        psnr = Imaging.psnr(out_image, image_lowRes)

        if debug == True:
            plt.subplot(1,2,1)
            plt.imshow(image_lowRes, cmap='gray')
            plt.subplot(1,2,2)
            plt.imshow(out_image, cmap='gray')
            plt.show()

        return serializedOutImage, psnr
