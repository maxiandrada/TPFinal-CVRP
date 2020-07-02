from Vertice import Vertice
from Arista import Arista
from Grafo import Grafo
from Solucion import Solucion
from Tabu import Tabu, ListaTabu
import random 
import sys
import re
import math 
import copy
from clsTxt import clsTxt
from time import time
from Ingreso import Ingreso

class CVRP:
    def __init__(self, M, D, nroV, capac, archivo, solI, intercamb, opt, tADD, tDROP, tiempo, optimo,beta):
        self._G = Grafo(M)      #Grafo original
        print(len(M))
        self._S = Solucion(self._G,D,nroV,capac,solI)
        self._S2 = Solucion(self._S)
        self.__Distancias = M
        self.__Demanda = D      #Demanda de los clientes
        self.__capacidad = capac
        self.__soluciones = []
        self.__rutas = []   #Solucion general del CVRP
        self.__costoTotal = 0
        self.__nroIntercambios=intercamb*2    #corresponde al nro de vertices los intercambios. 1intercambio => 2 vertices
        self.__opt=opt
        self.__optimo = optimo
        self.__tenureADD =  tADD
        self.__tenureMaxADD = int(tADD*1.7)
        self.__tenureDROP =  tDROP
        self.__tenureMaxDROP = int(tDROP*1.7)
        self.beta = beta
        self.__txt = clsTxt(str(archivo))
        self.__tiempoMaxEjec = float(tiempo)
        self.__frecMatriz = []
        self.__nroVehiculos = nroV
        self.__tipoSolucionIni = solI

#        print(str(self._G))

        #self.mostrarDemanda()
        
        print(self.__nroVehiculos)
        #print(self._S)
        self.setUmbral()
        self.tabuSearch()

    def setUmbral(self):
        self.umbralGranularidad = self.beta*(self._S.getCostoTotal()/(self._G.getGrado()+self.__nroVehiculos))

    

    def mostrarDemanda(self):
        for i in range(0, len(self.__Demanda)):
            print('%i : %s' %(i+1,str(self.__Demanda[i]))) 
        print(sum(self.__Demanda))
    # Para el Tabu Search Granular


    def crearGrafoDispercion(self):
        self.GD = Grafo()
        self.GD.setMatriz(self._G.getMatriz())

        A = self._G.getA()
        self.GD.setV(self._G.getV())
        umbral = self.umbralGranularidad
        #print("Umbral de Granularidad: "+str(self.umbralGranularidad))
        for a in A:
            if(a.getPeso()<umbral or (a.getOrigen()==Vertice(1)and a.getDestino()!=Vertice(1))):
                self.GD.getA().append(a)
        self.GD.setCosto() #Actualiza el costo


    ####### Empezamos con Tabu Search #########
    def tabuSearch(self):
        lista_tabu = ListaTabu()         #Tiene objetos de la clase Tabu
        lista_permitidos = []   #Tiene objetos de la clase arista
        #Sol_Actual = copy.deepcopy(self._S)
        
        #Atributos banderas utilizados
        condNoMejora = False
        alfaMin = 1
        alfaMax = 6400
        alfa = 100
        tenureMin = 5
        tenureMax = 10
        
        nd = 15 * self._G.getGrado()
        nh = self._G.getGrado()
        betaD = 2.5#Controla la diversificación
        betaOriginal = 0.75
        self.beta = betaOriginal
        self.crearGrafoDispercion() 

        tiempoMax = float(1*60)
        noFactibles = 0
        solucionActual = Solucion(self._S)
        solucionOptima = Solucion(self._S)
        solucionOptima.penalizarSolucion(alfa)
        cantidadMaximaIteraciones = 10000
        subIteracion = 0
        iteracionDispercion = 0
        iteracion = 0
        maxNoFactibles = 4
        iteracionNoMejora = 0
        maxNoMejora = int(self._S.getGrado()/2)
        q = 0.1 #Controla la intensificación

        soluciones = []
        tiempoIni = time()
        #while(iteracion < cantidadMaximaIteraciones):
        while(time()-tiempoIni < tiempoMax): 
            #print("Iteración: ",iteracion)
            #print("subIteración: ",subIteracion)
            lista_permitidos = lista_tabu.getListaPermitidos(self.GD.getA())
            #print("umbral ",self.umbralGranularidad)
            solucionActual.penalizarSolucion(alfa)
            if condNoMejora:
                iteracionDispercion +=1
                if(iteracionDispercion == nh):
                #    print("Vuelve al grafo con beta ",betaOriginal)
                    condNoMejora = False
                    subIteracion = 0
                    self.beta = betaOriginal
                    self.setUmbral()
                    self.crearGrafoDispercion()
                    q=q/2
                #    print("Se baja el q a: ",q)
            else:
                if(subIteracion == nd): 
                #    print("No mejoró, se crea un nuevo grafo de disperción con beta",betaD," por ",nh,"iteraciones")
                    condNoMejora = True
                    self.beta = betaD
                    iteracionDispercion = 0
                    iteracionNoMejora += 1
                    if(iteracionNoMejora == maxNoMejora):
                        iteracionNoMejora = 0
                        if(soluciones!=[]):
                            solucionAleatoria = random.sample(soluciones,1)[0]
                            solucionActual = Solucion(solucionAleatoria)
                            solucionActual.penalizarSolucion(alfa)
                            lista_tabu = ListaTabu()
                        print(solucionActual)
                    q=q*2
                    #print("Se sube el q a: ",q)
                    self.setUmbral()
                    self.crearGrafoDispercion()
                else:
                    if(iteracion % 2*self._G.getGrado()==0):
                        self.setUmbral()
                        self.crearGrafoDispercion() 

            #mejorMovimiento = solucionActual.buscarMejorMovimiento(lista_permitidos,q,alfa,solucionActual.getCostoTotal(),lista_tabu)
            mejorMovimiento = solucionActual.buscarMejorMovimiento(self.GD.getA(),q,alfa,solucionActual.getCostoTotal(),lista_tabu)
            if(isinstance(mejorMovimiento, bool)):
                noFactibles +=1
                if(noFactibles==maxNoFactibles):
                    noFactibles = 0
                    if(soluciones!=[]):
                        solucionAleatoria = random.sample(soluciones,1)[0]
                        solucionActual = Solucion(solucionAleatoria)
                        solucionActual.penalizarSolucion(alfa)
                        lista_tabu = ListaTabu()

                    #print(solucionActual)
                #print("No Factibles: ",noFactibles)
            else:
                #aristasTabu = solucionActual.aristasTabu(mejorMovimiento.getOrigen(),mejorMovimiento.getDestino())
                solucionActual.customerSwap(mejorMovimiento.getOrigen(),mejorMovimiento.getDestino())
                solucionActual.penalizarSolucion(alfa)
                tenure = random.sample(range(tenureMin,tenureMax+1),1)[0]
                lista_tabu.addTabu(mejorMovimiento,tenure)
                #lista_tabu.addTabu(aristasTabu,tenure)
            #print(solucionActual)


            if(solucionActual.getCostoPenalizado()<solucionOptima.getCostoPenalizado()):
                solucionOptima = Solucion(solucionActual)
                solucionOptima.penalizarSolucion(alfa)
                print("Costo Nueva Solución optima encontrada: ",solucionActual.getCostoTotal())
                print("Carga Solución optima encontrada: ",solucionActual.getCostoPenalizado())
                subIteracion = 0
                soluciones.append(solucionOptima)
                self.__txt.escribir("################################ " + str(iteracion) + " ####################################")
                self.__txt.escribir(str(solucionOptima))
            
            #print(len(lista_tabu))
            lista_tabu.decrementaTenure()
            subIteracion +=1
            #print(iteracion)
            iteracion+=1
        self.__txt.escribir("################################ MEJOR SOLUCIÓN ####################################")
        self.__txt.escribir(str(solucionOptima))            
        self.__txt.escribir(str(solucionOptima.getCapacidadDisponible()))    
        self.__txt.escribir("OPTIMO REAL: "+str(self.__optimo))    
        porcentaje = (self.__optimo-solucionOptima.getCostoTotal())/self.__optimo*100                   
        self.__txt.escribir("Error: "+str(porcentaje)) 
        self.__txt.imprimir()
        print(len(soluciones))
        for s in soluciones:
            print("SOLUCIONES")
            print("Costo: ",s.getCostoTotal())
            print("Optimo real: ",self.__optimo)
            print("Error: ",porcentaje)
            print("CostoPenalizado: ",str(s.getCostoPenalizado()))
            print("Capacidad: ",str(s.getCapacidad()))
            print("Carga: ",str(s.getCapacidadDisponible()))

if __name__ == "__main__":
    arg = Ingreso(sys.argv)
    
    cvrp = CVRP(arg.M,arg.D,arg.NV,arg.C,arg.nombreArchivo,arg.I,arg.intercambios,2,0,0,4,arg.O,1.0)

