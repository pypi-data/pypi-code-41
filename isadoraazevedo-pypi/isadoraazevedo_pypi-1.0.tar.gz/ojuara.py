def calcularVelocidadeMedia(distancia, tempo):
    return distancia/tempo

def calcularAceleracaoMedia(velocidade, tempo):
    return velocidade/tempo

def calcularEquacaoTorricelli(velocidadeInicial, aceleracao, distancia):
    velocidadeQuadrado = (velocidadeInicial*velocidadeInicial) + 2*aceleracao*distancia
    return velocidadeQuadrado

def calcularVelocidadeMUV(velocidadeInicial, aceleracao, tempo):
    return velocidadeInicial + (aceleracao*tempo)

def calcularPosicaoMRU(posicaoInicial, velocidade, tempo):
    return posicaoInicial + (velocidade * tempo)