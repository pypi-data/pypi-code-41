# -*- coding: utf-8 -*-

"""
PyElectrica   |1.1.4|

Modulo Python con funciones útiles para resolver problemas específicos
en Ingeniería Eléctrica relativos a los Circuitos y Máquinas Eléctricas.

Funciones integradas en el módulo PyElectrica:
----------------------------------------------
       ANÁLISIS DE CIRCUITOS ELÉCTRICOS
----------------------------------------------
* leyOhm
* vNodos
* vNodosV
* iLazos
* iLazosV
* bode
* bodeNB
* escalon
* c_1orden

----------------------------------------------
       ANÁLISIS DE MÁQUINAS ELÉCTRICAS
----------------------------------------------
* mLineal_CC
* compCA_GenSinc
* par_vel
* cepTransformador

----------------------------------------------
       CALCULOS EN INSTALACIONES ELÉCTRICAS
----------------------------------------------
* imonoF
* cTensionMono

----------------------------------------------
      CONSTANTES Y FUNCIONES MATEMÁTICAS
----------------------------------------------
* pi   - Constante pi = 3.141592653589793
* exp  - Constante e : Número de Euler
* cos  - Función coseno
* sin  - Función seno
* sqrt - Raíz cuadrada
"""

__author__ = "Isai Aragón Parada"
__copyright__ = "Copyright 2018, Isai Aragón"
__credits__ = "Isai Aragón Parada"
__license__ = "MIT"
__version__ = "1.1.3"
__maintainer__ = "Isai Aragón Parada"
__email__ = "isaix25@gmail.com"
__status__ = "En constante desarrollo"

# -----------------------------------------------------------------------------

# Se importan los modulos necesarios.
#import pylab
#import numpy as np
#from scipy import signal
#from numpy.linalg import solve
#import matplotlib.pyplot as plt
#from numpy import linspace, arange, pi, cos, sin, exp, array, sqrt


# -----------------------------------------------------------------------------
# ---------------------   CIRCUITOS ELÉCTRICOS  -------------------------------
# -----------------------------------------------------------------------------


# Función para calcular la Ley de Ohm, en base al parámetro con incognita '?'.


def leyOhm(**param):
    """
    Función para calcular la Ley de Ohm, en base al parámetro
    con incognita '?'.

    Ejemplo:
    leyOhm(V='?', I=3, R=4)

    V = Valor de tensión
    I = Valor corriente
    R = Valor de resistencia

    IMPORTANTE: Se debe indicar dos valores numericos y el valor
                que se quiere calcular indicando su valor con la
                cadena de texto: '?'

                Ejemplo:
                # Para calcular el voltaje:
                leyOhm(V='?', I=3, R=4)

                # Para calcular la resistencia:
                leyOhm(V=24, I=3.5, R='?')

                # Para calcular la corriente:
                leyOhm(V=12, I='?', R=5)

                ** La función acepta números complejos **
    """

    # Se importan los módulos necesarios.
    import numpy as np

    # Se resuelve la ecuacion de la Ley de Ohm.
    if param['V'] == '?':
        print('V =',
              np.ma.round((param['I'] * param['R']), 3), 'V')

    elif param['I'] == '?':
        print('I =',
              np.ma.round((param['V'] / param['R']), 3), 'A')

    elif param['R'] == '?':
        print('R =',
              np.ma.round((param['V'] / param['I']), 3), 'Ω')

    else:
        print('¡No hay nada que calcular!')
        print('''         (#_#)''')
        print('Si quieres que calcule algo,')
        print('tienes que indicar la incognita \'?\' en algun parametro.')

# -----------------------------------------------------------------------------

# Función para calcular los diagramas de bode. Versión Consola.


def bode(num, den):
    """
    Función que genera los diagramas de Bode para una función  de
    transferencia, indicada por su numerador (num) y denominador(den).

    Ejemplo:
    bode(num, den)

    num = valores en formato de lista, que contiene lo valores del
          númerador de la fución de transferencia.

    den = valores en formato de lista, que contiene los valores del
          denominador de la función de transferencia.
    """

    # Se importan los módulos necesarios.
    import pylab
    from scipy import signal
    import matplotlib.pyplot as plt

    # Se determina el tamaño de la gráfica
    #import pylab
    pylab.rcParams['figure.figsize'] = (9, 6.5)

    # Se declara la función de transferencia, frecuencia (w), magnitud (mag)
    # y la fase.
    sistema = signal.TransferFunction(num, den)
    w, mag, fase = signal.bode(sistema)

    # Se generan las gráficas de la lo diagramas de Bode.
    # Diagrama de Amplitud
    plt.subplot(2, 1, 1)
    plt.semilogx(w, mag)
    plt.title('Diagramas de Bode')
    plt.ylabel('Amplitud $(dB)$')
    plt.grid(True, which='both', axis='both')

    # Diagrama de Fase
    plt.subplot(2, 1, 2)
    plt.semilogx(w, fase)
    plt.ylabel('Fase $(°)$')
    plt.xlabel('$ \omega \ (rad/seg) $')
    plt.grid(which='both', axis='both')

    # Se muestran los diagrmas en pantalla
    plt.show()

# -----------------------------------------------------------------------------

# Función para calcular los diagramas de Bode. Versión Jupyter Notebook.


def bodeNb(num, den):
    """
    Función que genera los diagramas de Bode para una función  de
    transferencia, indicada por su numerador (num) y denominador(den).

    Ejemplo:
    bodeNb(num, den)

    num = valores en formato de lista, que contiene lo valores del
          númerador de la fución de transferencia.

    den = valores en formato de lista, que contiene los valores del
          denominador de la función de transferencia.
    """

    # Se importan los modulos necesarios.
    import pylab
    from scipy import signal
    import matplotlib.pyplot as plt

    # Se determina el tamaño de la gráfica
    #import pylab
    pylab.rcParams['figure.figsize'] = (9, 6.5)

    # Se declara la función de transferencia, frecuencia (w), magnitud (mag)
    # y la fase.
    sistema = signal.TransferFunction(num, den)
    w, mag, fase = signal.bode(sistema)

    # Se generan las gráficas de la lo diagramas de Bode.
    # Diagrama de Amplitud
    plt.figure()
    plt.semilogx(w, mag)
    plt.title('Diagramas de Bode')
    plt.ylabel('Amplitud $(dB)$')
    plt.grid(True, which='both', axis='both')

    # Diagrama de Fase
    plt.figure()
    plt.semilogx(w, fase)
    plt.ylabel('Fase $(°)$')
    plt.xlabel('$ \omega \ (rad/seg) $')
    plt.grid(which='both', axis='both')

    # Se muestran los diagrmas en pantalla
    plt.show()

# -----------------------------------------------------------------------------

# Función para generar la respuesta escalón de una función de transferencia.


def escalon(num, den):
    """
    Función escalón, para generar la respuesta escalón en base a una
    función de transferencia.

    Ejemplo:
    escalon(num, den)

    num = valores en formato de lista, que contiene lo valores del
          númerador de la fución de transferencia.

    den = valores en formato de lista, que contiene los valores del
          denominador de la función de transferencia.
    """

    # Se importan los modulos necesarios.
    import pylab
    from scipy import signal
    import matplotlib.pyplot as plt

    # Se determina el tamaño de la gráfica
    pylab.rcParams['figure.figsize'] = (9, 6.5)

    # Se declara la función de transferencia, se genera el tiempo (t),  y
    # la respuesta escalon y(t).
    sistema = signal.TransferFunction(num, den)
    t, y = signal.step(sistema)

    # Se declara la gráfica la respuesta escalón .
    plt.plot(t, y, 'r')
    plt.title('Respuesta escalón')
    plt.xlabel('Tiempo $(s)$')
    plt.ylabel('Amplitud')
    plt.grid()

    # Se imprime en pantalla la gráfica de la respuesta escalón.
    plt.show()

# -----------------------------------------------------------------------------

# Función para resolver un sistema de ecuaciones en forma matricial.
# Generadas por el analisis nodal de un circuito eléctrico.


def vNodos(A, B):
    """
    Función vNodos, que resuelve un sistema de ecuaciones en forma
    matricial y entrega los correspondientes voltajes de nodo en base
    al sistema de ecuaciones del circuito.

    Ejemplo:
    vNodos(A, B)

    A = lista que define la matriz de coeficiente.
    B = lista que define la matriz del vector solución.
    """

    # Se importan los modulos necesarios.
    import numpy as np
    from numpy.linalg import solve

    # Se resuelve el sistema de ecuaciones.
    V = solve(A, B)

    print('Los voltajes de nodo del circuito son:\n')

    # Se genera una iteración sobre cada uno de los valores de la matriz V.
    # Para imprimir la designación de cada voltaje con su respectivo valor.

    num = 0
    for v in V:
        num += 1
        print('v' + str(num), '=', np.ma.round(v[0], 3), 'Volts')


# Se genera función que imprime las corrientes de lazo en forma de lista
# para que puedan ser manipulados.


def vNodosV(A, B):
    """
    Función vNodos, que resuelve un sistema de ecuaciones en forma
    matricial y entrega los correspondientes voltajes de nodo en base
    al sistema de ecuaciones del circuito.

    Ejemplo:
    vNodosV(A, B)

    A = lista que define la matriz de coeficiente.
    B = lista que define la matriz del vector solución.
    """

    # Se importan los modulos necesarios.
    from numpy.linalg import solve

    # Se resuelve el sistema de ecuaciones.
    return solve(A, B)

# -----------------------------------------------------------------------------


# Función para resolver un sistema de ecuaciones en forma matricial.
# Generadas por el analisis nodal de un circuito eléctrico.


def iLazos(A, B):
    """
    Función iLazos, que resuelve un sistema de ecuaciones en forma
    matricial y entrega las correspondientes corrientes de lazo en base
    al sistema de ecuaciones del circuito.

    Ejemplo:
    iLazos(A, B)

    A = lista que define la matriz de coeficiente.
    B = lista que define la matriz del vector solución.
    """

    # Se importan los modulos necesarios.
    import numpy as np
    from numpy.linalg import solve

    # Se resuelve el sistema de ecuaciones.
    I = solve(A, B)

    print('Las corrientes de lazo del circuito son:\n')

    # Se genera una iteración sobre cada uno de los valores de la matriz I.
    # Para imprimir la designación de cada corriente con su respectivo valor.

    num = 0
    for i in I:
        num += 1
        print('i' + str(num), '=', np.ma.round(i[0], 3), 'Amperes')


# Se genera función que imprime las corrientes de lazo en forma de lista
# para que puedan ser manipulados.


def iLazosV(A, B):
    """
    Función iLazosF (Entrega lista de valores), que resuelve un sistema
    de ecuaciones en forma matricial y entrega las correspondientes
    corrientes de lazo en base al sistema de ecuaciones del circuito.

    Ejemplo:
    iLazosV(A, B)

    A = lista que define la matriz de coeficiente.
    B = lista que define la matriz del vector solución.
    """

    # Se importan los modulos necesarios.
    from numpy.linalg import solve

    # Se resuelve el sistema de ecuaciones.
    return solve(A, B)

# -----------------------------------------------------------------------------


# Función "cpo_RC" para generar la gráfica de en función del voltaje para
# un circuito eléctrico RC de primer orden sin fuente.

def c_1orden(**kwarg):
    """
    Función para calcular y dibujar la gráfica de la curva de respuesta
    en un circuito RC o RL sin fuente, tomando como base a los parámetros
    indicados en la función.

    Ejemplo1:
    c_1orden(Vi=18, R=4.5 C=0.1) * Para circuitos RC

    Ejemplo1:
    c_1orden(Ii=18, R=1.4, L=0.5) * Para circuitos RL

    Donde:
    R = Resistencia del circuito
    t = el tiempo máximo a tomar en cuenta para la grafica
        *(Para mejores efectos visuales: 1 > t < 10)
    Vi = Voltaje inicial en el capacitor
    Ii = Corriente inicial en el inductor
    C = Valor del capacitor
    L = Valor del inductor
    """
    # Se importan los módulos necesarios.
    import pylab
    import matplotlib.pyplot as plt
    from numpy import exp, linspace

    # Se determina el tamaño de la gráfica
    pylab.rcParams['figure.figsize'] = (9, 6.5)

    # Se declara el código para generar la curva de respuesta de un
    # circuito de primer orden.

    try:
        # Código para la curva del circuito RC.
        if ('Vi' in kwarg) & ('C' in kwarg):
            tau = kwarg['R'] * kwarg['C']
            # El rango de tiempo se determina segun la teoria, que indica
            # que en un circuito de primer orden se llega a su estado
            # estable cuando el tiempo es igual a 5 veces el valor de tau.
            t = linspace(0, 5 * tau, num=200)

            # Se declara la ecuación v(t).
            v_t = kwarg['Vi'] * exp(-t / tau)

            # Se declara la ecuación de v(t) a 1/2 de la constante de
            # tiempo.
            v_t_med = kwarg['Vi'] * exp(-t / (tau * 0.5))

            # Se declara la ecuación de i(x) con el doble de constante de
            # tiempo.
            v_t_dob = kwarg['Vi'] * exp(-t / (tau * 2))

            # Se genera la curva de respuesta del circuito RC.
            plt.plot(t,
                     v_t_med,
                     color='green',
                     label=r'$v/V_i(t) \ \ \ \tau = 0.5$')

            plt.plot(
                t, v_t, color='blue', label=r'$v/V_i(t) \ \ \ \tau = 1$')

            plt.plot(
                t, v_t_dob, color='red', label=r'$v/V_i(t) \ \ \ \tau = 2$')

            plt.legend()
            plt.title('Curva de respuesta del circuito RC')
            plt.ylabel('Tensión $(V)$')
            plt.xlabel('Tiempo $(s)$')
            plt.grid()
            plt.show()

        # Código para la curva del circuito RL.
        elif ('Ii' in kwarg) & ('L' in kwarg):
            tau = kwarg['R'] / kwarg['L']
            t = linspace(0, 5 * tau, num=200)

            # Se declara la ecuación v(t).
            v_t = kwarg['Ii'] * exp(-t / tau)

            # Se declara la ecuación de v(t) a 1/2 de la constante de
            # tiempo.
            v_t_med = kwarg['Ii'] * exp(-t / (tau * 0.5))

            # Se declara la ecuación de i(x) con el doble de constante de
            # tiempo.
            v_t_dob = kwarg['Ii'] * exp(-t / (tau * 2))

            # Se genera la curva de respuesta del circuito RC.
            plt.plot(
                t, v_t_med, color='green', label=r'$i/I_i(t) \ \ \ \tau = 0.5$')

            plt.plot(
                t, v_t, color='blue', label=r'$i/I_i(t) \ \ \ \tau = 1$')

            plt.plot(
                t, v_t_dob, color='red', label=r'$i/I_i(t) \ \ \ \tau = 2$')

            plt.legend()
            plt.title('Curva de respuesta del circuito RL')
            plt.ylabel('Corriente $(I)$')
            plt.xlabel('Tiempo $(s)$')
            plt.grid()
            plt.show()

        else:
            print('¡Error de definición!')
            print('No ingresaste los parametros correctos.')
            print('Revisa los parametros ingresados.')

    except KeyError:
        print('¡ERROR de parametros!')
        print('Falta declarar algun parametro del circuito.')
        print('Revisa los parametros ingresados.')


# -----------------------------------------------------------------------------
# -----------------------   MÁQUINAS ELÉCTRICAS  ------------------------------
# -----------------------------------------------------------------------------


# Función para encontrar la magnitud de la fuerza inducida en un alambre, te-
# niendo como datos la corriente(i), la longitud (l) y la densidad de flujo de
# campo.


def mLineal_CD(Vb=120, R=0.5, l=1, B=0.5):
    """
    Función \"mLineal_CD\", util para calcular el comportamiento de una
    máquina lineal CD en base a los parámetros declarados.

    Ejemplo:
    mLineal_CD(Vb, R, l, B)

    Vb = Voltaje de la batería
    R = Resistencia del diagrama de la máquina lineal CD
    l = longitud del conductor en el campo magnético
    B =  Vector de densidad de flujo magnético
    """

    # Se importan los modulos necesarios.
    import pylab
    import matplotlib.pyplot as plt
    from numpy import linspace

    # Se determina el tamaño de la gráfica
    #import pylab
    pylab.rcParams['figure.figsize'] = (9, 6.5)

    # Se declara el rango de fuerzas a aplicar
    F = linspace(0, 50, num=50)

    # Se Calcula la corriente en el motor
    i = F / (l * B)

    # Se calcula el voltaje inducido
    eind = Vb - (i * R)

    # Se calcula la velocidad de la barra
    Vel = eind / (l * B)

    # Se grafica la velocidad en función de la fuerza aplicada
    plt.plot(F, Vel, 'b', label='Velocidad')
    plt.plot(F, i, 'r', label='Corriente')
    plt.plot(F, eind, 'g', label='Voltaje inducido')

    plt.title('Comportamiento de la maquina lineal CD')
    plt.xlabel('Fuerza (N)')
    plt.ylabel('Velocidad barra (m/s) / Corriente (A) / $e_{ind}$ (V)')
    plt.legend(loc='best')
    plt.grid()

    plt.show()


# -----------------------------------------------------------------------------


# Función "compCA_GenSinc" que genera una la gráfica de la componente AC
# de la corriente de falla de un generador síncrono.


def compCA_GenSinc(Sbase=(100 * 10**6), Vbase=(13.8 * 10**3), Xs=1.0,
                   X1p=0.25, X2p=0.12, T1p=1.10, T2p=0.04):
    """
    Función \"compCA_GenSinc\" para calcular la componente CA de la
    corriente de falla de un generador síncrono en base a los
    parámetros ingresados.

    Ejemplo:
    compCA_GenSinc(Sbase, Vbase, Xs, X1p, X2p, T1p, T2p)

    Donde:
    Sbase = Potencia aparente del generador síncrono
    Vbase = Voltaje base del generador síncrono
    Xs = Reactancia síncrona del generador síncrono
    X1p = Reactancia transitoria
    X2p = Reactancia subtrancitoria
    T1p = Constante de tiempo de la corriente transitoria
    T2p = Constante de tiempo de la corriente subtrancitoria
    """

    # Se importan los modulos necesarios.
    import pylab
    import matplotlib.pyplot as plt
    from numpy import linspace, pi, sin, exp, sqrt

    # Se determina el tamaño de la gráfica
    #import pylab
    pylab.rcParams['figure.figsize'] = (9, 6.5)

    # Se calcula la componente ac de la corriente
    t = linspace(0.0, 5.0, num=155)

    Ibase = Sbase / (sqrt(3) * Vbase)

    I2p = (1.0 / X2p) * Ibase
    I1p = (1.0 / X1p) * Ibase
    Iss = (1.0 / Xs) * Ibase

    It = (I2p - I1p) * exp(-t / T2p) + (I1p - Iss) * exp(-t / T1p) + Iss

    Isen = It * sin(2 * pi * 60 * t)

    # Se grafica la componente ac de la corriente
    plt.plot(t, It, 'r')
    plt.plot(t, Isen, 'b')
    plt.plot(t, -It, 'r')

    plt.title('Componente CA de corriente de falla en generador síncrono')
    plt.xlabel('tiempo (s)')
    plt.ylabel('Corriente de corto circuito (A)')

    plt.grid()

    plt.show()

# -----------------------------------------------------------------------------


# Función "par_vel" que genera una la gráfica de la curva Par-Velocidad
# de un motor de inducción.


def par_vel(Vn=460, Polos=4, R1=0.641, X1=1.106,
            R2=0.332, X2=0.464, Xm=26.3):
    """
    Función \"par_vel\" para calcular y generar la gráfica de la curva
    Par-Velocidad de un motor de inducción con rotor devanado y/o
    rotor jaula de ardilla.

    Ejemplo:
    par_vel(Vn, Polos, R1, X1, R2, X2, Xm)

    Donde:
    Vn = Voltaje nominal del motor
    Polos = Número de polos del motor
    f = Frecuencia de operación del motor
    R1 = Resistencia del estator
    X1 = Reactancia del estator
    R2 = Resistencia del rotor
    X2 = Reactancia del rotor
    Xm = Reactancia de magnetización
    """

    # Se importan los modulos necesarios.
    import pylab
    import matplotlib.pyplot as plt
    from numpy import arange, pi, sqrt

    # Se determina el tamaño de la gráfica
    #import pylab
    pylab.rcParams['figure.figsize'] = (9, 6.5)

    # Se preparan las variables para el cálculo
    Vfase = Vn / sqrt(3)
    f = 60

    ns = 120 * f / Polos
    ws = ns * (2 * pi / 1) * (1 / 60)

    s = arange(0.001, 1.0, 0.001)

    # Se calcula el voltaje y la impedancia de Thevenin
    Vth = Vfase * (Xm / sqrt(R1**2 + (X1 + Xm)**2))
    Zth = ((1j * Xm) * (R1 + 1j * X1)) / (R1 + 1j * (X1 + Xm))
    Rth = Zth.real
    Xth = Zth.imag

    # Se calcula la característica par-velocidad
    nm = (1 - s) * ns

    # Se calcula el Par para la resistencia original del rotor
    t_ind = (3 * Vth**2 * R2 / s) / (
        ws * ((Rth + R2 / s)**2 + (Xth + X2)**2))

    # Se calcula el Par para el doble de la resistencia del rotor
    t_ind2 = (3 * Vth**2 * (2 * R2) / s) / (
        ws * ((Rth + (2 * R2) / s)**2 + (Xth + X2)**2))

    # Se generan las curvas Par-Velocidad
    plt.plot(nm, t_ind, 'b', label='$R_2 \ $ Original')
    plt.plot(nm, t_ind2, 'r-.', label='$R_2 \ $ Duplicada')

    plt.title('Curva Par-Velocidad del motor de inducción')
    plt.xlabel('$n_m$, $r/min$')
    plt.ylabel('$\\tau_{ind} $, $N*M$')
    plt.legend()
    plt.grid()

    plt.show()

# -----------------------------------------------------------------------------


# Función "cepTransformador" que analiza y entrega el circuito equivalente en
# el lado primario de un tranformador en base a sus parametros de las pruebas
# de corto circuito y circuito abierto.


def cepTransformador(Voc, Ioc, Poc, Vsc, Isc, Psc):
    """
    Función \"cepTransformador\" para calcular el circuito equivalente de
    un transformador en el lado primário, en función de sus parametros
    de las pruebas de circuito abierto y corto circuito.

    Ejemplo:
    cepTransformador(Voc, Ioc, Poc, Vsc, Isc, Psc)

    Donde:
    Voc = Voltaje en prueba de circuito abierto en el lado primario.
    Ioc = Corriente en prueba de circuito abierto en el lado primario.
    Poc = Potencia en prueba de circuito abierto en el lado primario.
    Vsc = Voltaje en prueba de corto circuito en el lado primario.
    Isc = Corriente en prueba de corto circuito en el lado primario.
    Psc = Potencia en prueba de corto circuito en el lado primario.
    """

    # Se importan los módulos necesarios.
    from cmath import rect
    from numpy import arccos, sqrt
    import SchemDraw as schem
    import SchemDraw.elements as e
    from numpy.ma import round as roundC

    # Análisis de circuito abierto.
    FP_oc = Poc / (Voc * Ioc)    # FP de circuito abierto
    Ye = rect(Ioc / Voc, - arccos(FP_oc))
    Rc = roundC(sqrt((1 / Ye.real * (1/1000))**2), 2)
    Xm = roundC(sqrt((1 / Ye.imag * (1/1000))**2), 2)

    # Análisis de cortocircuito.
    FP_sc = Psc / (Vsc * Isc)   # FP de cortocircuito
    Zse = rect(Vsc / Isc, - arccos(FP_sc))
    Req = roundC(sqrt(Zse.real**2), 2)
    Xeq = roundC(sqrt(Zse.imag**2), 2)

    # Se imprimen los valores en pantalla.
    print('Rc', '\t', '=', '\t', Rc, 'kOhms')
    print('Xm', '\t', '=', '\t', Xm, 'kOhms')
    print('Req', '\t', '=', '\t', Req, 'Ohms')
    print('Xeq', '\t', '=', '\t', Xeq, 'Ohms')

    # Se genera el diagrama del circuito equivalente.
    d = schem.Drawing()

    # Terminal voltaje primario positivo.
    Vp_mas = d.add(e.DOT_OPEN, label='+')
    d.add(e.LINE, d='right', l=6)

    # Nodo 1
    D1 = d.add(e.DOT)

    # Resistencia y Reactancia equivalente en serie.
    d.add(e.LINE, d='right', l=2, xy=D1.start)
    eReq = d.add(e.RES, botlabel='{} $\Omega$'.format(Req))
    eReq.add_label('$R_{eq}$', loc='top')
    d.add(e.LINE, d='right', l=1, xy=eReq.end)
    eXeq = d.add(e.INDUCTOR, botlabel='j{} $\Omega$'.format(Xeq))
    eXeq.add_label('$jX_{eq}$', loc='top')
    d.add(e.LINE, d='right', l=2, xy=eXeq.end)

    # Terminal voltaje secundario positivo.
    Vs_mas = d.add(e.DOT_OPEN, label='+')

    # Nodo 2
    d.add(e.LINE, d='down', l=3, xy=D1.start)
    D2 = d.add(e.DOT)
    d.add(e.LINE, d='right', l=3, xy=D2.start)
    d.add(e.LINE, d='down', l=1)

    # Reactancia Xm en paralelo.
    eXm = d.add(e.INDUCTOR, botlabel='$j{} \ k\Omega$'.format(Xm))
    eXm.add_label('$jX_m$', loc='top')
    d.add(e.LINE, d='down', l=1)
    d.add(e.LINE, d='left', l=3)

    # Nodo 3
    D3 = d.add(e.DOT)
    d.add(e.LINE, d='left', l=3)
    d.add(e.LINE, d='up', l=1)

    # Resistencia Rc en paralelo
    eRc = d.add(e.RES, botlabel='{} k$\Omega$'.format(Rc))
    eRc.add_label('$R_c$', loc='top')
    d.add(e.LINE, d='up', l=1)
    d.add(e.LINE, d='right', l=3)

    # Nodo 4
    d.add(e.LINE, d='down', l=3, xy=D3.start)
    D4 = d.add(e.DOT)

    # Terminal Voltaje secundario negativo.
    d.add(e.LINE, d='right', l=11, xy=D4.start)
    Vs_menos = d.add(e.DOT_OPEN, label='-')

    # Terminal Voltaje primario negativo.
    d.add(e.LINE, d='left', l=6, xy=D4.start)
    Vp_menos = d.add(e.DOT_OPEN, label='-')

    # Etiqueta invisible de terminal de voltaje primario.
    d.add(e.GAP_LABEL, label='$V_p$', endpts=[Vp_mas.start, Vp_menos.start])

    # Etiqueta invisible de terminal de voltaje secundario.
    d.add(e.GAP_LABEL, label='$V_s$', endpts=[Vs_mas.start, Vs_menos.start])

    # Se dibuja el diagrama.
    d.draw()

# -----------------------------------------------------------------------------
# ---------------------   INSTALACIONES ELÉCTRICAS  ---------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# Función para calcular la corriente de la carga de un circuito eléctrico en
# en diseño de instalaciones eléctricas.

def imonoF(VA, Vn):
    """
    Función para calcular la corriente de un circuito eléctrico en el diseño
    de instalaciones eléctricas residenciales. La función también recomienda
    el calibre de cable adecuado para la corriente del circuito.

    Sintaxis:
    imonoF(VA, Vn)

    Donde:
    VA = Volt-Ampere de la carga o del circuito a calcular.
    Vn = Voltaje nominal de fase a neutro.
    """

    i = VA / Vn

    def resultado():
        # Imprimir los resultados en pantalla.
        print('\nPara una carga de {0} VA conectada a {1} V.'.format(VA, Vn))
        print('La corriente calculada es de: {} A.'.format(round(i, 2)))
        print('El calibre de cable recomendado es del {}, tipo THW o similar.'
              .format(cable))

    # Determinar el calibre de conductor.
    # Basado en capacidad de cables tipo THW y similares.
    if i <= 20:
        cable = '#14 AWG'
        resultado()
    elif i <= 25:
        cable = '#12 AWG'
        resultado()
    elif i <= 35:
        cable = '#10 AWG'
        resultado()
    elif i <= 50:
        cable = '#8 AWG'
        resultado()
    elif i > 50:
        cable = ''
        print('\nLa corriente calculada es de {} A.'.format(round(i, 2)))
        print('El calibre del conductor será demasiado grande.')
        print('Considera dividir la carga del circuito.')
        print('O considera cambiar la tensión del circuito.')


# -----------------------------------------------------------------------------

# Función para calcular la caída de tensión en un conductor usando la formula
# de caída de tensión.


def cTensionMono(l, I, Vn, c):
    """
    Función cTension para calcular la caída de tensión en un conductor,
    utilizando la formula de caída de tensión de instalaciones eléctricas.

    Sintaxis:
    cTensionMono(l, I, Vn, c)

    Donde:
    l = Longitud hasta la última carga del circuito.
    I = Corriente que pasara en el conductor.
    Vn = Tensión nominal a neutro.
    c =  Calibre del conductor.
    """

    if c ==  14:
        s = 2.08 #mm2
    elif c == 12:
        s = 3.31 #mm2
    elif c == 10:
        s = 5.26 #mm2
    elif c == 8:
        s = 8.37 #mm2
    elif c == 6:
        s = 13.3 #mm2
    else:
        s = 0

    if s != 0:
        ex100 = 4 * l * I / (Vn * s)
        print('\nLos datos ingresados son los siguientes:')
        print('La longitud del circuito es de {} Mts.'.format(l))
        print('La corriente en el circuito es de {} A.'.format(I))
        print('El voltaje de operación del circuito es de {} V.'.format(Vn))
        print('El calibre del conductor seleccionado es del #{} AWG.'
              .format(c))
        print('La caída de tensión del circuito es de {} %.'
              .format(round(ex100,2)))
    else:
        print('\nEl calibre del conductor no esta incluido o normalizado.')


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print('Este es el modulo \"PyElectrica\" para Python.')
    print('Útil en la solución de problemas de Ingeniería Eléctrica.')
    input('Presiona <Enter> para salir.')
