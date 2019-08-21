'''
Module to transfer the style from one image to another. Executes the code from the model
'''
import logging
import requests
import io
from PIL import Image

from styletransfer.exceptions import ImageLoadException
from styletransfer.model import Model

logger = logging.getLogger(__name__)

DEFAULT_STYLE_LAYER_WEIGHTS = {'conv1_1':1.,'conv2_1':0.75,'conv3_1':0.2,'conv4_1':0.2,'conv5_1':0.2}
DEFAULT_CONTENT_WEIGHT = 1
DEFAULT_STYLE_WEIGHT = 1e6


def loadImageFromUrl(url):
    '''
    Load an image from a URL into a PIL image

    Args:
        url: URL to the picture

    Returns:
        PIL image

    Raises:
        ImageLoadException: If the image cannot be loaded or is empty
    '''
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 7_0_6 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Mobile/11B651'})
        picture  = r.content
    except requests.adapters.SSLError as e:
        logger.error('SSL Error on URL {}'.format(url))
        raise ImageLoadException('SSL Error on URL {}'.format(url))
    except requests.exceptions.RequestException as e:
        logger.error('Requests error {} on URL {}'.format(e,url))
        raise ImageLoadException('Requests error {} on URL {}'.format(e,url))
    except (ConnectionResetError, http.client.HTTPException) as e:
        logger.error('ConnectionResetError or BadStatusLine Error on URL {}'.format(url))
        raise ImageLoadException('ConnectionResetError or BadStatusLine Error on URL {}'.format(url))
    #Process the image
    bytesPicture = io.BytesIO(picture)
    if len(bytesPicture.getvalue()) == 0:
        logger.error('Received empty image from URL {}'.format(url))
        raise ImageLoadException('Received empty image from URL {}'.format(url))
    return Image.open(bytesPicture)


class StyleTransfer():
    '''
    Class that encapsulates all components needed to run deep drems on a picture
    '''

    def setContentFromPath(self, path):
        '''
        Set the content image from a path if the content image is stored on the local drive.

        Args:
            path: Path to the image file
        '''
        #Load image and convert to RGB. Standard is RBG
        self.contentImage = Image.open(path).convert('RGB')

    def setContentFromUrl(self, url):
        '''
        Set the content image from a URL if the image should be downloaded.

        Args:
            url: URL to the image
        '''
        self.contentImage = loadImageFromUrl(url)

    def setStyleFromPath(self, path):
        '''
        Set the style image from a path if the style image is stored on the local drive.

        Args:
            path: Path to the image file
        '''
        #Load image and convert to RGB. Standard is RBG
        self.styleImage = Image.open(path).convert('RGB')

    def setStyleFromUrl(self, url):
        '''
        Set the style image from a URL if the image should be downloaded.

        Args:
            url: URL to the image
        '''
        self.styleImage = loadImageFromUrl(url)

    def setParams(self,weightL1, weightL2, weightL3, weightL4, weightL5,contentWeight, styleWeight):
        '''
        Set the weights for training the model

        Args:
            weightL1: Weight with which to consider 1st style layer
            weightL2: Weight with which to consider 2nd style layer
            weightL3: Weight with which to consider 3rd style layer
            weightL4: Weight with which to consider 4th style layer
            weightL5: Weight with which to consider 5th style layer
            contentWeight: Weight for considering the content
            styleWeight: Weight for considering the style image
        '''
        self.styleLayerWeights = {'conv1_1': weightL1, 'conv2_1': weightL2,'conv3_1': weightL3,
                 'conv4_1': weightL4,'conv5_1': weightL5}
        self.contentWeight = contentWeight
        self.styleWeight = styleWeight

    def apply(self, epochs = 600):
        '''
        Train the model. Content image, style image and parameters must have been set before.

        Args:
            epochs: Number of iterations to train the model

        Returns:
            PIL Image of the stylized image

        Raises:
            MissingConfigException: If images are not set an exception will be raised
        '''
        if self.contentImage is None:
            logger.error('No content image set. Please set one via setContentFromPath/setContentFromUrl first')
            raise MissingConfigException('No content image set')

        if self.styleImage is None:
            logger.error('No syle image set. Please set one via setStyleFromPath/setStyleFromUrl first')
            raise MissingConfigException('No style image set')

        styleLayerWeights = self.styleLayerWeights
        if styleLayerWeights is None:
            styleLayerWeights = DEFAULT_STYLE_LAYER_WEIGHTS
            logger.info('styleLayerWeights not set. Using default values: {}'.format(styleLayerWeights))

        contentWeight = self.contentWeight
        if contentWeight is None:
            contentWeight = DEFAULT_CONTENT_WEIGHT
            logger.info('contentWeight not set. Using default value: {}'.format(contentWeight))

        styleWeight = self.styleWeight
        if styleWeight is None:
            styleWeight = DEFAULT_STYLE_WEIGHT
            logger.info('styleWeight not set. Using default value: {}'.format(styleWeight))

        model = Model()
        model.setImages(self.contentImage, self.styleImage)
        self.styledImage = model.train(styleLayerWeights,contentWeight,styleWeight, epochs)
        return self.styledImage

    def writeFinalImage(self,path):
        '''
        Write the final image to the file system

        Args:
            path: Full path containing the file name to use as output. File ending should be jpg
        '''
        #Using standard PIL functionality
        self.styledImage.save(path)
