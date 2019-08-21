"""ALGORITMO QUE DETECTA COLORES
    EN IMAGENES Y MEDIANTE LA CAMARA"""



import cv2
import numpy as np

"""
    Importar Modulo
"""

if __name__=="__main__":

    """INICIO DE PROGRAMA"""


    print("PROYECTO DE PROGRAMACION 3")
    print("Detector de Colores")
    print("MENU")
    print("1.Detectar colores")
    print("2.Detectar colores en imagenes predeterminadas")
    print("3.Detectar colores por barra de SVH")
    print("4.Salir")
    """MENU DE PRESENTACION"""

    opc = int(input("Introduzca la opcion que desea: "))
    """VARIABLE PARA SELECCIONAR OPCION"""

    if opc == 1:
        print("Detectar Colores")
        print("1.Detectar Color Verde")
        print("2.Detectar Color Rojo")
        print("3.Detectar Color Amarillo")
        print("4.Detectar Color Azul")
        print("5.Detectar Color Rosado")
        """MENU DE SELECCION DE COLORES"""
        opc = int(input("Introduzca la opcion que desea: "))
        """VARIABLE PARA SELECCIONAR OPCION"""

        if opc == 1:
            print("1.Detectar Color Verde")
            captura = cv2.VideoCapture(0)
            """Iniciamos la camara"""
            while (1):
                _, imagen = captura.read()
                """Capturamos una imagen y la convertimos de RGB -> HSV"""
                hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

                verde_bajos = np.array([49, 50, 50], dtype=np.uint8)
                verde_altos = np.array([80, 255, 255], dtype=np.uint8)
                """Establecemos el rango de colores que vamos a detectar"""
                """En este caso de verde oscuro a verde-azulado claro"""

                mask = cv2.inRange(hsv, verde_bajos, verde_altos)
                """Crear una mascara con solo los pixeles dentro del rango de verdes"""

                moments = cv2.moments(mask)
                """Encontrar el area de los objetos que detecta la camara"""
                area = moments['m00']


                if (area > 2000000):
                    """Descomentar para ver el area por pantalla"""
                    """print area"""
                    x = int(moments['m10'] / moments['m00'])
                    y = int(moments['m01'] / moments['m00'])
                    """Buscamos el centro x, y del objeto"""
                    cv2.rectangle(imagen, (x, y), (x + 2, y + 2), (0, 0, 255), 2)
                    """Dibujamos una marca en el centro del objeto"""


                cv2.imshow('mask', mask)
                cv2.imshow('Camara', imagen)
                """Mostramos la imagen original con la marca del centro y
                                   la mascara"""
                tecla = cv2.waitKey(5) & 0xFF
                if tecla == 27:
                    break

            cv2.destroyAllWindows()

        elif opc == 2:
            print("2.Detectar Color Rojo")
            captura = cv2.VideoCapture(0)
            """Iniciamos la camara"""
            while (1):


                _, imagen = captura.read()
                """Capturamos una imagen y la convertimos de RGB -> HSV"""
                hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

                rojo_bajos = np.array([0, 65, 75], dtype=np.uint8)
                rojo_altos = np.array([12, 255, 255], dtype=np.uint8)
                """Se establece el rango del color que vamos a detectar"""
                """En este caso de rojo oscuro a rojo claro"""

                mask = cv2.inRange(hsv, rojo_bajos, rojo_altos)
                """Crear una mascara con solo los pixeles dentro del rango de rojo"""

                moments = cv2.moments(mask)
                """Encontrar el area de los objetos que detecta la camara"""
                area = moments['m00']
                if (area > 2000000):
                    """Descomentar para ver el area por pantalla"""
                    """print area"""
                    x = int(moments['m10'] / moments['m00'])
                    y = int(moments['m01'] / moments['m00'])
                    """Buscamos el centro x, y del objeto"""

                    cv2.rectangle(imagen, (x, y), (x + 2, y + 2), (0, 0, 255), 2)
                    """Dibujamos una marca en el centro del objeto"""
                cv2.imshow('mask', mask)
                cv2.imshow('Camara', imagen)
                """Mostramos la imagen original con la marca del centro y
                   la mascara"""
                k = cv2.waitKey(5)
                if k == ord("e"):
                    break

            cv2.destroyAllWindows()
        elif opc == 3:
            print("3.Detectar Color Amarillo")
            captura = cv2.VideoCapture(0)
            """Iniciamos la camara"""
            while (1):
                _, imagen = captura.read()
                """Capturamos una imagen y la convertimos de RGB a HSV"""
                hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
                ama_bajos = np.array([20, 100, 100], dtype=np.uint8)
                ama_altos = np.array([30, 255, 255], dtype=np.uint8)
                """Se establece el rango del color que vamos a detectar"""
                """En este caso de amarillo oscuro a amarillo claro"""

                mask = cv2.inRange(hsv, ama_bajos, ama_altos)
                """Crear una mascara con solo los pixeles dentro del rango de amarillo"""
                moments = cv2.moments(mask)
                """Encontrar el area de los objetos que detecta la camara"""
                area = moments['m00']
                if (area > 2000000):
                    """Descomentar para ver el area por pantalla"""
                    """print area"""
                    x = int(moments['m10'] / moments['m00'])
                    y = int(moments['m01'] / moments['m00'])
                    """Buscamos el centro x, y del objeto"""
                    cv2.rectangle(imagen, (x, y), (x + 2, y + 2), (0, 0, 255), 2)
                    """Dibujamos una marca en el centro del objeto"""
                cv2.imshow('mask', mask)
                cv2.imshow('Camara', imagen)
                """Mostramos la imagen original con la marca del centro y
                   la mascara"""
                k = cv2.waitKey(5)
                if k == ord("e"):
                    break

            cv2.destroyAllWindows()
        elif opc == 4:
            print("4.Detectar Color Azul")
            captura = cv2.VideoCapture(0)
            """Iniciamos la camara"""
            while (1):
                _, imagen = captura.read()
                """Capturamos una imagen y la convertimos de RGB -> HSV"""
                hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
                azul_bajos = np.array([100, 65, 75], dtype=np.uint8)
                azul_altos = np.array([130, 255, 255], dtype=np.uint8)
                """Establecemos el rango de colores que vamos a detectar"""
                """En este caso de azul oscuro a azul claro"""

                """Crear una mascara con solo los pixeles dentro del rango de azul"""
                mask = cv2.inRange(hsv, azul_bajos, azul_altos)

                """Encontrar el area de los objetos que detecta la camara"""
                moments = cv2.moments(mask)
                area = moments['m00']

                """Descomentar para ver el area por pantalla"""
                """print area"""
                if (area > 2000000):
                    """Buscamos el centro x, y del objeto"""
                    x = int(moments['m10'] / moments['m00'])
                    y = int(moments['m01'] / moments['m00'])

                    """Dibujamos una marca en el centro del objeto"""
                    cv2.rectangle(imagen, (x, y), (x + 2, y + 2), (0, 0, 255), 2)

                """Mostramos la imagen original con la marca del centro y
                   la mascara"""
                cv2.imshow('mask', mask)
                cv2.imshow('Camara', imagen)
                k = cv2.waitKey(5)
                if k == ord("e"):
                    break

            cv2.destroyAllWindows()
        elif opc == 5:
            print("2.Detectar Color Rosado")
            """Iniciamos la camara"""
            captura = cv2.VideoCapture(0)
            while (1):

                """Capturamos una imagen y la convertimos de RGB -> HSV"""
                _, imagen = captura.read()
                hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

                """Establecemos el rango de colores que vamos a detectar"""
                """En este caso de rosado fuerte a rosado claro"""
                rosado_bajos = np.array([125, 50, 50], dtype=np.uint8)
                rosado_altos = np.array([167, 255, 255], dtype=np.uint8)

                """Crear una mascara con solo los pixeles dentro del rango de rosado"""
                mask = cv2.inRange(hsv, rosado_bajos, rosado_altos)

                """Encontrar el area de los objetos que detecta la camara"""
                moments = cv2.moments(mask)
                area = moments['m00']

                """Descomentar para ver el area por pantalla"""
                """print area"""
                if (area > 2000000):
                    """Buscamos el centro x, y del objeto"""
                    x = int(moments['m10'] / moments['m00'])
                    y = int(moments['m01'] / moments['m00'])

                    """Dibujamos una marca en el centro del objeto"""
                    cv2.rectangle(imagen, (x, y), (x + 2, y + 2), (0, 0, 255), 2)

                """Mostramos la imagen original con la marca del centro y
                   la mascara"""
                cv2.imshow('mask', mask)
                cv2.imshow('Camara', imagen)
                k = cv2.waitKey(5)
                if k == ord("e"):
                    break

            cv2.destroyAllWindows()

    elif opc == 2:
        print("1.Imagen de Winnie Pooh")
        print("2.Arcoiris")
        print("3.Logo de Python")
        """VARIABLE PARA SELECCIONAR OPCION"""
        opc = int(input("Introduzca cual desea examinar: "))

        if opc==1:
            image = cv2.imread('winnie.jpg')

            while (1):
                """toma cada cuadro"""
                """Convierte de BGR a HSV"""
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                """define el rango de los colores en HSV"""
                ama_bajos = np.array([20, 100, 100], dtype=np.uint8)
                ama_altos = np.array([30, 255, 255], dtype=np.uint8)
                rojo_bajos = np.array([0, 65, 75], dtype=np.uint8)
                rojo_altos = np.array([12, 255, 255], dtype=np.uint8)
                """Umbral de la imagen HSV para obtener solo colores azules"""
                mask = cv2.inRange(hsv, ama_bajos, ama_altos)
                mask1 = cv2.inRange(hsv, rojo_bajos, rojo_altos)
                """Comparar mask con la imagen original"""
                camisa = cv2.bitwise_and(image, image, mask=mask)
                winnie = cv2.bitwise_and(image, image, mask=mask1)
                cv2.imshow('frame', image)
                cv2.imshow('winnie', camisa)
                cv2.imshow('camisa', winnie)
                k = cv2.waitKey(5) & 0xFF
                """si pulsa q se rompe el ciclo"""
                if k == ord("q"):
                    break
            cv2.destroyAllWindows()
        elif opc == 2:
                image = cv2.imread('Arcoiris.jpg')

                while (1):
                    """toma cada cuadro"""
                    """Convierte de BGR a HSV"""
                    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                    """define el rango de los colores en HSV"""
                    ama_bajos = np.array([20, 100, 100], dtype=np.uint8)
                    ama_altos = np.array([30, 255, 255], dtype=np.uint8)
                    rojo_bajos = np.array([0, 65, 75], dtype=np.uint8)
                    rojo_altos = np.array([12, 255, 255], dtype=np.uint8)
                    azul_bajos = np.array([100, 65, 75], dtype=np.uint8)
                    azul_altos = np.array([130, 255, 255], dtype=np.uint8)
                    """Umbral de la imagen HSV para obtener solo colores rojo, azul y amarillo"""
                    mask = cv2.inRange(hsv, ama_bajos, ama_altos)
                    mask1 = cv2.inRange(hsv, rojo_bajos, rojo_altos)
                    mask2 = cv2.inRange(hsv, azul_bajos, azul_altos)
                    """Comparar mask con la imagen original"""
                    amarillo = cv2.bitwise_and(image, image, mask=mask)
                    rojo = cv2.bitwise_and(image, image, mask=mask1)
                    azul = cv2.bitwise_and(image, image, mask=mask2)
                    cv2.imshow('frame', image)
                    cv2.imshow('Amarillo', amarillo)
                    cv2.imshow('Rojo', rojo)
                    cv2.imshow('Azul', azul)
                    k = cv2.waitKey(5) & 0xFF
                    """si pulsa q se rompe el ciclo"""
                    if k == ord("q"):
                        break
                cv2.destroyAllWindows()
        elif opc == 3:

                image = cv2.imread('Python.png')

                while (1):
                    """toma cada cuadro"""
                    """Convierte de BGR a HSV"""
                    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                    """define el rango de los colores en HSV"""
                    ama_bajos = np.array([20, 100, 100], dtype=np.uint8)
                    ama_altos = np.array([30, 255, 255], dtype=np.uint8)
                    azul_bajos = np.array([100, 65, 75], dtype=np.uint8)
                    azul_altos = np.array([130, 255, 255], dtype=np.uint8)
                    """Umbral de la imagen HSV para obtener solo colores verdes y azules"""
                    mask = cv2.inRange(hsv, ama_bajos, ama_altos)
                    mask1 = cv2.inRange(hsv, azul_bajos, azul_altos)
                    """Comparar mask con la imagen original"""
                    amarillo = cv2.bitwise_and(image, image, mask=mask)
                    azul = cv2.bitwise_and(image, image, mask=mask1)
                    cv2.imshow('frame', image)
                    cv2.imshow('amarillo', amarillo)
                    cv2.imshow('azul', azul)
                    k = cv2.waitKey(5) & 0xFF
                    """si pulsa q se rompe el ciclo"""
                    if k == ord("q"):
                        break
                cv2.destroyAllWindows()

    elif opc == 3:
        cap = cv2.VideoCapture(0)


        def nothing(x):
            pass


        """Creamos una ventana llamada 'image' en la que habra todos los sliders"""
        cv2.namedWindow('image')
        cv2.createTrackbar('Hue Minimo', 'image', 0, 255, nothing)
        cv2.createTrackbar('Hue Maximo', 'image', 0, 255, nothing)
        cv2.createTrackbar('Saturation Minimo', 'image', 0, 255, nothing)
        cv2.createTrackbar('Saturation Maximo', 'image', 0, 255, nothing)
        cv2.createTrackbar('Value Minimo', 'image', 0, 255, nothing)
        cv2.createTrackbar('Value Maximo', 'image', 0, 255, nothing)

        while (1):
            """Leer un frame"""
            _, frame = cap.read()
            """Convertirlo a espacio de color HSV"""
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            """Los valores maximo y minimo de H,S y V se guardan en funcion de la posicion de los sliders"""
            hMin = cv2.getTrackbarPos('Hue Minimo', 'image')
            hMax = cv2.getTrackbarPos('Hue Maximo', 'image')
            sMin = cv2.getTrackbarPos('Saturation Minimo', 'image')
            sMax = cv2.getTrackbarPos('Saturation Maximo', 'image')
            vMin = cv2.getTrackbarPos('Value Minimo', 'image')
            vMax = cv2.getTrackbarPos('Value Maximo', 'image')

            """Se crea un array con las posiciones minimas y maximas"""
            lower = np.array([hMin, sMin, vMin])
            upper = np.array([hMax, sMax, vMax])

            """Deteccion de colores"""
            mask = cv2.inRange(hsv, lower, upper)

            """Mostrar los resultados y salir"""
            cv2.imshow('camara', frame)
            cv2.imshow('mask', mask)
            k = cv2.waitKey(5) & 0xFF
            if k == 27:
                break
        cv2.destroyAllWindows()
    elif opc == 4:
        exit()
    else:
        print("Opcion Invalida")







