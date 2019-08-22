def velocidadeMedia(vInicial, vFinal, tInicial, tFinal):
    return (vInicial - vFinal)/(tInicial - tFinal)

def imc (sexo, peso, altura):
    return peso / altura ** 2

def bhaskara (a, b, c):
    x =(b**2)-(4*a*c)

    if x <0 :
        return 0

    else :

        x1=(-b+x)/(2*a)
        x2=(-b-x)/(2*a)
        return x1, x2

