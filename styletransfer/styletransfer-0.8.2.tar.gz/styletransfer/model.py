'''
Deep learning model to transfer the style from one image to another
'''
import numpy as np
import torch
import torch.optim as optim
import logging
from torchvision import models, transforms
from PIL import Image

logger = logging.getLogger(__name__)

def prepImage(image, maxSize=400, shape=None):
    '''
    Helper function to prepare an image by scaling and transforming

    Args:
        image: PIL image object to scale
        maxSize: Max size of the picture. Reduce for faster training
        shape: Shape (height/widht) of the image

    Returns:
        Normalized image as tensor
    '''
    #Determine if image should be resized
    size = maxSize if max(image.size) > maxSize else max(image.size)
    #Reshape the image if needed
    if shape is not None: size = shape

    #Apply the transformation to scale and normalize the image
    transform = transforms.Compose([
                        transforms.Resize(size),
                        transforms.ToTensor(),
                        transforms.Normalize((0.485, 0.456, 0.406),
                                             (0.229, 0.224, 0.225))])
    image = transform(image)
    #Remove the alpha dimension
    image = image[:3,:,:]
    #Add the batch dimension since the model expects batches of images
    image = image.unsqueeze(0)
    return image

def getFeatures(image, model):
    '''
    Execute one forward pass through a model and get the features per layer

    Args:
        image: Image to get the features from
        model: PyTorch VGG19 model

    Returns:
        Fetaures for selected layers after one forward pass
    '''
    #Get a list of layers holding the content from VGG 19
    layers = {'0': 'conv1_1',
            '5': 'conv2_1',
            '10': 'conv3_1',
            '19': 'conv4_1',
            '21': 'conv4_2',
            '28': 'conv5_1'}

    features = {}
    x = image
    #Loop through all modules in the model
    for name, layer in model._modules.items():
        x = layer(x) #Forward pass
        #For selected layers store the features as this stage
        if name in layers: features[layers[name]] = x
    return features

def gramMatrix(tensor):
    '''
    Calculate a Gram Matrix (https://en.wikipedia.org/wiki/Gramian_matrix) from a given tensor

    Args:
        tensor: Image in tensor form

    Returns:
        Gram Matrix for a tensor
    '''
    #Get all dimensions from the tensor
    batchSize, depth, height, width = tensor.size()
    #Reshape the tensor so the features for each channel are multiplied
    tensor = tensor.view(depth,height*width)
    #Calculate the Gram Matrix
    gram = torch.mm(tensor,tensor.t())
    return gram

def convertToImage(tensor):
    '''
    Helper function to take a stylized image in tensor form and return a PIL image

    Args:
        tensor: PyTorch tensor based on an image

    Retruns:
        PIL Image
    '''
    image = tensor.to("cpu").clone().detach()
    image = image.numpy().squeeze()
    image = image.transpose(1,2,0)
    image = image * np.array((0.229, 0.224, 0.225)) + np.array((0.485, 0.456, 0.406))
    image = image.clip(0, 1)
    image = Image.fromarray(np.uint8(image*255))
    return image

class Model():
    '''Wrapper for VGG19 for style transfer'''

    def __init__(self):
        '''Constructor to prepare the model'''
        logger.debug('Creating model')
        #Set the device
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info('Running on GPU')
        else:
            self.device = torch.device("cpu")
            logger.warning('Running on CPU. Training might be slow and take easily 60+ minutes with 600 epochs')
        #Get the features from VGG19
        vgg = models.vgg19(pretrained=True).features
        #Freeze all parameters. Optimization is only done on the target image
        for param in vgg.parameters():
            param.requires_grad_(False)
        #Move to GPU if available
        vgg.to(self.device)
        self.model = vgg
        logger.debug('Completed model creation')

    def train(self, styleLayerWeights, contentWeight, styleWeight, epochs, contTrain = False, logEvery = 200):
        '''
        Run the content image through

        Args:
            styleLayerWeights: Dictionary with weights per layer in format: styleWeights = {'conv1_1': <value>,
                'conv2_1': <value>,'conv3_1': <value>,'conv4_1': <value>,'conv5_1': <value>}
            contentWeight: Weight for considering the content
            styleWeight: Weight for considering the style image
            epochs: Number of epochs to train
            contTrain: Set to true to continue training with previous image, otherwise takes new copy
            logEvery: Number of epochs after which a log message should be displayed
        '''
        logger.debug('Starting training')
        #Create a target image from the content image
        if contTrain == False:#If contTrain is set just coninue training with the previous one
            #Target image will then be changed during training
            self.target = self.content.clone().requires_grad_(True).to(self.device)

        optimizer = optim.Adam([self.target], lr=0.003)

        for i in range(1,epochs+1):
            #Get the current features of the target image and run a forward pass
            targetFeatures = getFeatures(self.target,self.model)

            #Calculate loss against the content image
            contentLoss = torch.mean((targetFeatures['conv4_2'] - self.contentFeatures['conv4_2'])**2)

            #Calculate the loss for each style layer
            styleLoss = 0 #Starting with a loss of 0 before going through all style layers
            for layer in styleLayerWeights:
                #Get the current target represenation of this layer
                targetFeature = targetFeatures[layer]
                #Calculate Gram Matrix of target layer
                targetGram = gramMatrix(targetFeature)

                #Get the Gram Matrix of the style layer
                styleGram = self.styleGrams[layer]

                #Calculate the loss for this layer
                layerStyleLoss = torch.mean((targetGram - styleGram)**2)
                #Apply the weighting for the loss
                layerStyleLoss = layerStyleLoss * styleLayerWeights[layer] #TODO directly in loop?

                #Get the dimensions
                _, depth, height, width = targetFeature.shape
                #Add the loss to the total style loss
                styleLoss += layerStyleLoss / (depth * height * width)

            #Calculate the total loss weighted by content and style loss factor
            loss = contentLoss * contentWeight + styleLoss * styleWeight

            #Run a backward pass based on the calculated loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if logEvery > 0 and (i % logEvery) == 0:
                logger.debug('Epoch {}/{}'.format(i,epochs))
        logger.debug('Completed training')
        #Conver the image from tensor to PIL
        return convertToImage(self.target)

    def getStylizedImage(self):
        '''Returns the same image as the training loop'''
        return convertToImage(self.target)

    def setImages(self, contentImage, styleImage):
        '''
        Run training loops to apply to style to content image

        Args:
            contentImage: Image to take the content layers from
            styleImage: Image to take the style layers from
        '''
        logger.debug('Preparing images')
        self.content = prepImage(contentImage).to(self.device)
        #Resize the style image to match the shape of the content image
        style = prepImage(styleImage,shape=self.content.shape[-2:]).to(self.device)

        #Get the features for each image by running a forward pass through the model
        self.contentFeatures = getFeatures(self.content,self.model)
        styleFeatures = getFeatures(style,self.model)

        #Calculate the Gram Matrix for every layer in the style features
        self.styleGrams = {}
        for layer in styleFeatures:
            self.styleGrams[layer] = gramMatrix(styleFeatures[layer])
        logger.debug('Models ready')
