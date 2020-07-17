import sys
import argparse
import re
import math
import os
class Ingreso():
    def __init__(self, argv): #recibe como parámetro la lista de argumentos recibidos por consola
        self.arg= argv 
        if(len(argv)==0):
            print("No se cargaron argumentos")
            self.mostrarAyuda()
            sys.exit()
        self.M = []
        self.tenureADD = 0
        self.tenureDROP = 0
        self.nombreArchivo = ""
        self.tiempo = 0
        self.iteraciones = 0

        self.subiteraciones = 0
        self.controlArgumentos()
        

    
    def controlArgumentos(self):
        arg = self.arg 
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", nargs='+', metavar= "FILE", help='Nombre del Archivo',type=str, required=True)
        parser.add_argument("--v", nargs='?', default= 900 , help='Cantidad de vehículos',type=int)
        parser.add_argument("--tenureadd", nargs='?', default = 0 , help='--tenureadd tenure add (si no se especifica se toma por defecto el 10% de la cantidad de vertices)',type=int)
        #parser.add_argument("--tenureaddmax", nargs='?', default = 0 , help='--tenureaddmax  tenure máximo (si no se especifica se toma por defecto el 15% de la cantidad de vertices)',type=int)
        parser.add_argument("--tenuredrop", nargs='?', default = 0 , help='--tenuredrop tenure drop (si no se especifica se toma por defecto el 10% de la cantidad de vertices)',type=int)
        #parser.add_argument("--tenuredropmax", nargs='?', default = 0 , help='--tenuredropmax tenure drop máximo (si no se especifica se toma por defecto el 15% de la cantidad de vertices)',type=int)
        parser.add_argument("--intercambios", nargs='?', default = 0 , help='--intercambios número de intercambios',type=int)
        parser.add_argument("-I", nargs='?',default = 0 ,  help='--solucioninicial tipo de solución inicial, 0 para vecino cercano, 1 para solución inicial al azar',type=int)
        parser.add_argument('--capacidad', nargs='?', default = 1000 , help='--iteration cantidad máxima de iteraciones, por defecto se toma 1000',type=int)   
        parser.add_argument('--time', nargs='?', default = 0 , help='--time tiempo total de la busqueda se expresa en minutos',type=int)
        parser.add_argument('--opt',nargs='?', default = 2 , help='2-opt o 3-opt',type=int)
        arg = parser.parse_args()
        self.cargarDesdeEUC_2D(str(arg.file[0]))
        self.M = self.getMatriz()
        self.D = self.getDemanda()
        self.NV = self.__nroVehiculos
        self.C = self.__capacidad
        self.F = str(arg.file[0])
        self.I = int(arg.I)
        self.intercambios = arg.intercambios,
        self.solucionInicial = arg.opt
        self.tenureADD = arg.tenureadd
        self.tenureDROP = arg.tenuredrop
        self.T = arg.time
        self.O = self.getOptimo()

    def mostrarAyuda(self):
        mensaje = """
                Se debe cargar una instancia en formato EUC 2D
                -f o --file [Nombre del Archivo]
                -t o --time tiempo total de la busqueda se expresa en minutos
                -I o --iteration cantidad máxima de iteraciones, por defecto se toma 1000
                -i o --subiteration cantidad máxima de subiteraciones, si no se ingresa, se toma el 90% de las iteraciones
                -tA o --tenureadd tenure add (si no se especifica se toma por defecto el 10% de la cantidad de vertices)
                -tAM o --tenureaddmax  tenure máximo (si no se especifica se toma por defecto el 15% de la cantidad de vertices)
                -tD o --tenuredrop tenure drop (si no se especifica se toma por defecto el 10% de la cantidad de vertices)
                -tDM o --tenuredropmax tenure drop máximo (si no se especifica se toma por defecto el 15% de la cantidad de vertices)
                -int o --intercambios número de intercambios
                -sI o --solucioninicial tipo de solución inicial, 0 para vecino cercano, 1 para solución inicial al azar
                """
        print(mensaje)



    def getArchivo(self):
        return self.nombreArchivo

    #Convierto mi archivo EUC_2D en una matriz en la cual pueda trabajar
    def cargarDesdeEUC_2D(self,pathArchivo):
        #+-+-+-+-+-Para cargar la distancias+-+-+-+-+-+-+-+-
        archivo = open(pathArchivo,"r")
        lineas = archivo.readlines()
        self.nombreArchivo = os.path.splitext(os.path.basename(str(archivo)))[0]

        #Busco la posiciones de...
        try:
            indSeccionCoord = lineas.index("NODE_COORD_SECTION \n")
            lineaEOF = lineas.index("DEMAND_SECTION \n")
        except ValueError:
            indSeccionCoord = lineas.index("NODE_COORD_SECTION\n")
            lineaEOF = lineas.index("DEMAND_SECTION\n")
        #Linea optimo y nro de vehiculos
        lineaOptimo = [x for x in lineas[0:indSeccionCoord] if re.findall(r"Optimal value:[\S 0-9]+",x) or  re.findall(r"Best Value:[\S 0-9]+",x)][0]
        parametros = re.findall(r"[0-9]+",lineaOptimo)
        
        self.__nroVehiculos = int(float(parametros[0]))
        print(self.__nroVehiculos)
        
        self.__optimo = float(parametros[1])
        print(self.__optimo)
        
        lineaCapacidad = [x for x in lineas[0:indSeccionCoord] if re.findall(r"CAPACITY[\s]*:[\s]*[0-9]+",x)][0]
        self.__capacidad = float(re.findall(r"[0-9]+",lineaCapacidad)[0])
        #Lista donde irán las coordenadas (vertice, x, y)
        coordenadas = []
        #Separa las coordenadas en una matriz, es una lista de listas (vertice, coordA, coordB)
        for i in range(indSeccionCoord+1, lineaEOF):
            textoLinea = lineas[i]
            textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de línea
            splitLinea = textoLinea.split(" ") #Divide la línea por " " 
            if(splitLinea[0]==""):
                coordenadas.append([splitLinea[1],splitLinea[2],splitLinea[3]]) #[[v1,x1,y1], [v2,x2,y2], ...]
            else:
                coordenadas.append([splitLinea[0],splitLinea[1],splitLinea[2]]) #[[v1,x1,y1], [v2,x2,y2], ...]
        self.cargaMatrizDistancias(coordenadas)
        #print("Matriz: "+str(self.__matrizDistancias))
        #+-+-+-+-+-+-+-Para cargar la demanda+-+-+-+-+-+-+-
        seccionDemanda = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEMAND_SECTION+",x)][0]
        indSeccionDemanda = lineas.index(seccionDemanda)
        
        seccionEOF = [x for x in lineas[indSeccionCoord:] if re.findall(r"DEPOT_SECTION+",x)][0]
        indLineaEOF = lineas.index(seccionEOF)

        demanda = []
        for i in range(indSeccionDemanda+1, indLineaEOF):
            textoLinea = lineas[i]
            textoLinea = re.sub("\n", "", textoLinea) #Elimina los saltos de línea
            splitLinea = textoLinea.split(" ") #Divide la línea por " " 
            demanda.append(float(splitLinea[1]))
        self.__demanda = demanda
        #print("\nDemanda: "+str(self.__demanda))
    
    def cargaMatrizDistancias(self, coordenadas):
        matriz = []
        #Arma la matriz de distancias. Calculo la distancia euclidea
        coordNuevo = []
        for coordRow in coordenadas:
            fila = []           
            coord = []
            coord.append(int(coordRow[0]))
            coord.append(float(coordRow[1]))
            coord.append(float(coordRow[2]))
            coordNuevo.append(coord)

            for coordCol in coordenadas:
                x1 = float(coordRow[1])
                y1 = float(coordRow[2])
                x2 = float(coordCol[1])
                y2 = float(coordCol[2])
                dist = self.distancia(x1,y1,x2,y2)
                
                #Para el primer caso. Calculando la distancia euclidea entre si mismo da 0
                fila.append(dist)

            #print("Fila: "+str(fila))    
            matriz.append(fila)
        self.coordenadas=coordNuevo
        self.__matrizDistancias = matriz
        for i in range(len(self.__matrizDistancias)):
            self.__matrizDistancias[i][i]=float("inf")

    def distancia(self, x1,y1,x2,y2):
        return round(math.sqrt((x1-x2)**2+(y1-y2)**2),3)

    def getMatriz(self):
        return self.__matrizDistancias

    def getDemanda(self):
        return self.__demanda

    def getOptimo(self):
        return self.__optimo