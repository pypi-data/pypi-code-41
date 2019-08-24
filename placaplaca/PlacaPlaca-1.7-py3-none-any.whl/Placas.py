import re
import platform
import os
OpSys=platform.system()
if (OpSys=="Windows"):
    os.system("cls")
else:
    os.system("clear")

def ShowPlaca(type):
    if (type!=""):
        print("\nLa placa pertenece a", type)
    else:
        print("\nPlaca irreconocida")

class Placa:

    def TypePlaca(self):
        placa=input("\nIngrese una placa: ")
        if re.match("^(([A-Z]){2}|[0-9]){6}$", placa):
            print("\nIngresaste una placa")
        
            if re.match("^MA([A-Z]|[0-9])+$", placa):
                type="una motocicleta"
            
            elif re.match("^MB[0-9]+", placa):
                type=("un MetroBus")
            
            elif re.match("^T([A-Z]|[0-9])+", placa):
                type=("un taxi")
            
            elif re.match("^E[A-Z][0-9]+", placa):
                type=("un vehiculo fiscal o judicial")
                
            elif re.match("^CP[0-9]+", placa):
                type=("un vehiculo del canal")
            
            elif re.match("^B[0-9]+$", placa):
                type=("un Bus")
            
            elif re.match("^HP[0-9]+", placa):
                type=("un radioaficionado")
            
            elif re.match("^A[A-G][0-9]+$", placa):
                type=("un auto regular")
            
            elif re.match("^CC[0-9]+$", placa):
                type=("un cuerpo consular")
            
            elif re.match("[0-9]+$", placa):
                type=("una serie antigua...")
            
            elif re.match("^PR[0-9])+", placa):
                type=("un auto de prensa")
                
            else:
                type=("")
            ShowPlaca(type)
        else:
            print("Eso no es una placa")

placa=Placa()

if __name__=="__main__":
    print("\nAiuda :v \n El formato para las placas a ingresar son los siguientes")
    print("\n\nMoto:            MA####\nAuto Regular:    (A-G)(A-G)####")
    print("Autos de prensa: PR####\nCuerpo Consular: CC####")
    print("Radioaficionado: HP####\nBus:             B(A-Z)####")
    print("Fiscal :         E(A-Z)####\nTaxi:            T(A-Z)####\nMetroBus:        MB####")
    print("Las series de placas antiguas se conforman de 6 numeros.")
    print("\n\n")
    placa.TypePlaca()