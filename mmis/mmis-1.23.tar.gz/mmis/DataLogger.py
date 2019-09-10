 # -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 16:17:01 2017

@author: rrbheemireddy
"""
            
class Create_ExcelFile:
    
    def __init__(self, Modules_List, workbook, Logging_Sheet):
        
        Module_Names = ['Not Found','Sample Heater', 'Dual Heater', 'Beta Tilt']
        self.bold = workbook.add_format({'bold':True})
        self.Cell_List = []
        self.Cell = 65
        Logging_Sheet.write(chr(self.Cell)+str(1), "Time", self.bold)
        self.Cell_List.append(chr(self.Cell)+str(1))
        
        for i in range(len(Modules_List)):

            if (Modules_List[i] == Module_Names[0]):
                self.Module_Not_Found(Logging_Sheet)
            elif (Modules_List[i] == Module_Names[1]):
                self.Sample_Heater(Logging_Sheet)
            elif (Modules_List[i] == Module_Names[2]):
                self.Dual_Heater(Logging_Sheet)
    
    def Sample_Heater(self, Log_Sheet):
        self.Cell += 1
        Log_Sheet.merge_range(chr(self.Cell)+str(1)+str(':')+chr(self.Cell+4)+str(1), "Sample Heater", self.bold)
        Temperature = chr(self.Cell)+str(2)
        self.Cell_List.append(Temperature)
        Log_Sheet.write(Temperature, "Temperature", self.bold)
        self.Cell += 1
        Voltage = chr(self.Cell)+str(2)
        self.Cell_List.append(Voltage)
        Log_Sheet.write(Voltage, "Voltage", self.bold)
        self.Cell += 1
        Current = chr(self.Cell)+str(2)
        self.Cell_List.append(Current)
        Log_Sheet.write(Current, "Current", self.bold)
        self.Cell += 1
        Resistance = chr(self.Cell)+str(2)
        self.Cell_List.append(Resistance)
        Log_Sheet.write(Resistance, "Resistance", self.bold)

    def Dual_Heater(self, Log_Sheet):
        self.Cell += 1
        Log_Sheet.merge_range(chr(self.Cell)+str(1)+str(':')+chr(self.Cell+6)+str(1), "Dual Heater", self.bold)
        Amb_Temp = chr(self.Cell)+str(2)
        self.Cell_List.append(Amb_Temp)
        Log_Sheet.write(Amb_Temp, "Ambient Temperature", self.bold)
        self.Cell += 1
        Volt_Amb_Ctrl = chr(self.Cell)+str(2)
        self.Cell_List.append(Volt_Amb_Ctrl)
        Log_Sheet.write(Volt_Amb_Ctrl, "Voltage - Amb - Control", self.bold)
        self.Cell += 1
        Current_Amb_Ctrl = chr(self.Cell)+str(2)
        self.Cell_List.append(Current_Amb_Ctrl)
        Log_Sheet.write(Current_Amb_Ctrl, "Current - Amb - Control", self.bold)
        self.Cell += 1
        N2_Temp = chr(self.Cell)+str(2)
        self.Cell_List.append(N2_Temp)
        Log_Sheet.write(N2_Temp, "Nitrogen Temperature", self.bold)
        self.Cell += 1
        Volt_N2_Ctrl = chr(self.Cell)+str(2)
        self.Cell_List.append(Volt_N2_Ctrl)
        Log_Sheet.write(Volt_N2_Ctrl, "Voltage - N2 - Control", self.bold)
        self.Cell += 1
        Current_N2_Ctrl = chr(self.Cell)+str(2)
        self.Cell_List.append(Current_N2_Ctrl)
        Log_Sheet.write(Current_N2_Ctrl, "Current - N2 - Control", self.bold)

    def Module_Not_Found(self, Log_Sheet):
        self.Cell += 1
        Log_Sheet.merge_range(chr(self.Cell)+str(1)+str(':')+chr(self.Cell+1)+str(1), "No Module", self.bold)
        Empty_Cell = chr(self.Cell)+str(2)
        self.Cell_List.append(Empty_Cell)             
 
