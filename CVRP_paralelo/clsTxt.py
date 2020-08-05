import sys
import os
import csv
import re
import ntpath
class clsTxt:
    def __init__(self, nombreTxt, Carpeta):
        nombreTxt = nombreArchivo(nombreTxt)
        Carpeta = Carpeta + " solucion"
        nombreCarpeta = re.findall(r"[0-9A-Za-z-]+.",nombreTxt)[0]
        
        if(os.path.exists(Carpeta)):
            self.__carpeta = Carpeta
        else:
            os.mkdir(Carpeta)
            self.__carpeta = Carpeta
        
        nombreCarpeta = self.__carpeta +"/"+nombreCarpeta
        if(os.path.exists(nombreCarpeta)):
            self.__nombre = "%s/%s" %(nombreCarpeta,nombreTxt)
        else:
            os.mkdir(nombreCarpeta)
            self.__nombre = "%s/%s" %(nombreCarpeta,nombreTxt)    
            
        i = 0
        while os.path.exists("%s (%i).txt" %(self.__nombre ,i)):
            i += 1

        self.__nombre = "%s (%i)" %(self.__nombre,i)
        self.__txt = open(str(self.__nombre)+".txt", "w")
        #self.__ArchivoCSV = open(str(self.__nombre)+".csv", "w",newline="")
        self.__st = ""
        #self.__fieldnames = ['iteración','Vertices','Aristas','costo',"intercambios","tenureADD","tenureDROP","tiempo"]
        #self.__CSV = csv.DictWriter(self.__ArchivoCSV, fieldnames=self.__fieldnames)

    def escribir(self, st):
        self.__st = self.__st + st+"\n"
    
    def CSV(self,iteracion,Vertices,Aristas,costo,intercambios,tenureADD,tenureDROP,tiempo):
        #self.__CSV.writerow({'iteración':str(iteracion),
        #'Vertices':str(Vertices),
        #'Aristas':str(Aristas),
        #'costo':str(costo),
        #"intercambios":str(intercambios),
        #"tenureADD":str(tenureADD),
        #"tenureDROP":str(tenureDROP),
        #"tiempo":str(tiempo)}) 
        pass

    def imprimir(self):
        try:
            self.__txt = open(self.__nombre+".txt", "w")
            self.__txt.write(self.__st)
            self.__txt.close()
        except IOError:
            print ("No se pudo abrir el txt para imprimir")
    
def nombreArchivo(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)