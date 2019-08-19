import re
import time
class Persona:
    class Persona:
        def __init__(self, nombre, placa):
            self.nombre = nombre
            self.placa = placa
def Comparar_Placas():

    print("REGISTRO Y RECONOCIMIENTO ")
    print("DE PLACAS DE VEHICULOS EN PANAMA")
    print("-------------------")
    Placas_Registradas = open("/tmp/ Placas.txt", "w")
    Placas_Registradas.close()


    veces = int(input("Cuantas placas deseas evaluar: "))


    for i in range(veces):
        nombre = Persona()
        nombre = input("Introduzca Nombre: ")
        placa = Persona()
        placa = input("\nIntroduzca su placa para evaluar: ")

        if re.match("^T([0-9])([0-9])([0-9])([0-9])([0-9]$)", placa):
            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Taxi")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()

        elif re.match("(^M)([0-9])([0-9])([0-9])([0-9])([0-9]$)", placa):
            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Moto")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()

        elif re.match("(^M)(B)([0-9])([0-9])([0-9])([0-9]$)", placa):
            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Metro Bus")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()


        elif re.match("(^B)([0-9])([0-9])([0-9])([0-9])([0-9]$)", placa):
            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Bus")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()


        elif re.match("(^C)(D)([0-9])([0-9])([0-9])([0-9]$)", placa):
            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Cuerpo Diplomatico")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()

        elif re.match("(^M)([0-9])([0-9])([0-9])([0-9]$)", placa):

            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Moto")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()

        elif re.match("(^D)([0-9])([0-9])([0-9])([0-9])([0-9]$)", placa):

            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Automovil de Prueba")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()

        elif re.match("(^P)(R)([0-9])([0-9])([0-9])([0-9]$)", placa):
            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Periodista")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()

        elif re.match("(^C)(C)([0-9])([0-9])([0-9])([0-9]$)", placa):
            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Cuerpo Consular")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()

        elif re.match("(^E)([0-9])([0-9])([0-9])([0-9])([0-9]$)", placa):

            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Juez o Fiscal")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()

        elif re.match("(^[A-Z_0-9])([A-Z-0-9])([0-9])([0-9])([0-9])([0-9]$)", placa):

            Placas_Registradas = open("/tmp/ Placas.txt", "a")
            print("{} Su placa {} es: ".format(nombre, placa))
            print("\nPlaca de Carro Particular")
            Placas_Registradas.write("\n" + time.strftime("%d/%m/%y"))
            Placas_Registradas.write("\n" + time.strftime("%I:%M:%S"))
            Placas_Registradas.write("\n{} Su placa {} es: ".format(nombre, placa))
            Placas_Registradas.write("\n")
            Placas_Registradas.close()

        else:
            print("{} Su placa {}: ".format(nombre, placa))
            print("No coincide con la Base de Datos")












