def imc(h,p):
    imc = p / h**2
    if imc < 16:
    	return "Magreza grave"
    elif imc < 17:
        return "Magreza moderada"
    elif imc < 18.5:
        return "Magreza leve"
    elif imc < 25:
        return "Saudável"
    elif imc < 30:
        return "Sobrepeso"
    elif imc < 35:
        return "Obesidade Grau I"
    elif imc < 40:
        return "Obesidade Grau II (severa)"
    else:
        return "Obesidade Grau III (mórbida)"
