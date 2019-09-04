import cv2
import matplotlib.pyplot as plt
import numpy as np
from skimage.exposure import rescale_intensity

# Objetivo: Aplicar técnica da equalização adaptativa em uma imagem.
# Parâmetros: Imagem a ser processada, limite do contraste e dimensões dos tiles. ** Para mais informações, ver referências no notebook de tecnicas_propostas.
# Saída: Imagem processada.
def equalizacao_adaptativa(image,clip_limit=1,tile_grid_size=(2,2)):
    clahe = cv2.createCLAHE(clip_limit, tile_grid_size)
    resulting_image = clahe.apply(image)
    return resulting_image

# Objetivo: Aplicar técnica da normalização/contrast streching em uma imagem.
# Parâmetros: Imagem a ser processada, primeiro limite de pixels e segundo limite de pixels. ** Para mais informações, ver referências no notebook de tecnicas_propostas.
# Saída: Imagem processada.
def normalizacao(image,first_range=2,second_range=98):
    valor_inicial, valor_final = np.percentile(image, (first_range, second_range))     
    resulting_image = rescale_intensity(image,in_range=(valor_inicial, valor_final))
    return resulting_image

# Objetivo: Aplicar técnicas a uma lista de imagens e visualizar imagens antes e depois da aplicação.
# Parâmetros: Path das imagens, lista de imagens a serem processadas, inicial da técnica e número de colunas da visualização.
# Saída: Imagens apresentadas em grade pelo pyplot.
def visualizar_imagens(train_image_path,images,tecnica,col=2):
    fig = plt.figure()
    counter = 0
    for image in images:
        current_image = cv2.imread(train_image_path + image,0)
        if(tecnica == 'e'):
            corrected_image = equalizacao_adaptativa(current_image)
        elif(tecnica == 'n'):
            corrected_image = normalizacao(current_image)
        fig.add_subplot(len(images),col,1 + counter)
        counter += 1
        plt.set_cmap('gray')
        plt.title('Antes')
        plt.imshow(current_image)
        fig.add_subplot(len(images),col,1 + counter)
        counter += 1
        plt.title('Depois')
        plt.imshow(corrected_image)

# Objetivo: Aplicar técnicas a uma lista de imagens e visualizar histogramas antes e depois da aplicação.
# Parâmetros: Path das imagens, lista de imagens a serem processadas, inicial da técnica e número de colunas da visualização.
# Saída: Histogramas apresentados em grade pelo pyplot.
def visualizar_histogramas(train_image_path,images,tecnica,col=2):
    fig = plt.figure()
    counter = 0
    for image in images:
        current_image = cv2.imread(train_image_path + image,0)
        if(tecnica == 'e'):
            corrected_image = equalizacao_adaptativa(current_image)
        elif(tecnica == 'n'):
            corrected_image = normalizacao(current_image)
        fig.add_subplot(len(images),col,1 + counter)
        counter += 1
        plt.set_cmap('gray')
        plt.title('Antes')
        histr = cv2.calcHist([current_image],[0],None,[256],[0,256])
        plt.plot(histr)
        fig.add_subplot(len(images),col,1 + counter)
        counter += 1
        plt.title('Depois')
        histr = cv2.calcHist([corrected_image],[0],None,[256],[0,256])
        plt.plot(histr)