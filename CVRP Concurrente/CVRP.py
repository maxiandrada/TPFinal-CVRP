from Vertice import Vertice
from Arista import Arista
from Grafo import Grafo
from Solucion import Solucion
from Tabu import Tabu
import random 
import sys
import re
import math 
import copy
import numpy as np
from clsTxt import clsTxt
from time import time

class CVRP:
    def __init__(self, M, D, nroV, capac, archivo, solI, tADD, tDROP, tiempo, optimo):
        self._G = Grafo(M, D)                #Grafo original
        self.__S = Solucion(M, D, sum(D))    #Solucion general del CVRP
        self.__Distancias = M                #Mareiz de distancias
        self.__Demandas = D                  #Demandas de los clientes
        self.__capacidadMax = capac          #Capacidad max por vehiculo
        self.__rutas = []                    #Soluciones por vehiculo (lista de soluciones)
        self.__nroVehiculos = nroV           #Nro de vehiculos disponibles
        self.__tipoSolucionIni = solI        #Tipo de solucion inicial (Clark & Wright, Vecino cercano, Secuencial o al Azar)
        self.__beta = 1                      #Parametro de dispersion
        self.__umbralMin = 0                 #Umbral de granularidad minimo
        self.__optimosLocales = []           #Lista de optimos locales 
        self.__porcentajeParada = 5.0        #Porcentaje de desvio minimo como condicion de parada
        self.__optimo = optimo               #Mejor valor de la instancia
        self.__tenureADD =  tADD             
        self.__tenureMaxADD = int(tADD*1.7)
        self.__tenureDROP =  tDROP
        self.__tenureMaxDROP = int(tDROP*1.7)
        self.__txt = clsTxt(str(archivo))
        self.__tiempoMaxEjec = float(tiempo)
        self.escribirDatos()
        self.__S.setCapacidadMax(self.__capacidadMax)
        self.__rutas = self.__S.rutasIniciales(self.__tipoSolucionIni, self.__nroVehiculos, self.__Demandas, self.__capacidadMax)
        self.__S = self.cargaSolucion(self.__rutas)

        self.tabuSearch()

    #Escribe los datos iniciales: el grafo inicial y la demanda
    def escribirDatos(self):
        self.__txt.escribir("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ GRAFO CARGADO +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
        self.__txt.escribir(str(self._G))
        cad = "\nDemandas:"
        for v in self._G.getV():
            cad_aux = str(v)+": "+str(v.getDemanda())
            cad+="\n"+ cad_aux
        self.__txt.escribir(cad)
        print("\nSuma Demanda: ",sum(self.__Demandas))
        print("Nro vehiculos: ",self.__nroVehiculos)
        self.__txt.escribir("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ SOLUCION INICIAL +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")

    #Carga la solucion general a partir de las rutas
    def cargaSolucion(self, rutas):
        A = []
        V = []
        S = Solucion(self.__Distancias, self.__Demandas, sum(self.__Demandas))
        cap = 0
        costoTotal = 0
        sol_ini = ""
        
        for i in range(0, len(rutas)):
            s = rutas[i]
            costoTotal += s.getCostoAsociado()
            cap += s.getCapacidad()
            A.extend(s.getA())
            V.extend(s.getV())
            sol_ini+="\nRuta #"+str(i+1)+": "+str(s.getV())
            sol_ini+="\nCosto asociado: "+str(s.getCostoAsociado())+"      Capacidad: "+str(s.getCapacidad())+"\n"
        sol_ini+="\n--> Costo total: "+str(costoTotal)+"          Capacidad total: "+str(cap)
        self.__txt.escribir(sol_ini)
        S.setA(A)
        S.setV(V)
        costoTotal = round(costoTotal, 3)
        S.setCostoAsociado(costoTotal)
        S.setCapacidad(cap)
        S.setCapacidadMax(self.__capacidadMax)
        
        return S
    #Umbral de granularidad: phi = Beta*(c/(n+k))
    #Beta = 1  parametro de dispersion. Sirve para modificar el grafo disperso para incluir la diversificación y la intensificación
    #          durante la búsqueda.
    #c = valor de una sol. inicial
    #k = nro de vehiculos
    #n = nro de clientes
    def calculaUmbral(self, costo):
        c = costo
        k = self.__nroVehiculos
        n = len(self.__Distancias)-1
        phi = c/(n+k)
        phi = phi*self.__beta
        return round(phi,3)

    #+-+-+-+-+-+-+- Empezamos con Tabu Search +-+-+-+-+-+-+-+-+#
    #lista_tabu: tiene objetos de la clase Tabu (una arista con su tenure)
    #Lista_permitidos: o grafo disperso tiene elementos del tipo Arista que no estan en la lista tabu y su distancia es menor al umbral
    #nuevas_rutas: nuevas rutas obtenidas a partir de los intercambios
    #nueva_solucion: nueva solucion obtenida a partir de los intercambios
    #rutas_refer: rutas de referencia que sirve principalmente para evitar estancamiento, admitiendo una solucion peor y hacer los intercambios
    #             a partir de esas
    #solucion_refer: idem al anterior
    #tiempoIni: tiempo inicial de ejecucion - tiempoMax: tiempo maximo de ejecucion - tiempoEjecuc: tiempo de ejecución actual
    #iteracEstancamiento: iteraciones de estancamiento para admitir una solución peor, modificar Beta y escapar del estancamiento
    #iterac: cantidad de iteraciones actualmente
    def tabuSearch(self):
        lista_tabu = []
        ind_permitidos = np.array([], dtype = int)
        tiempo=time()
        rutas_refer = copy.deepcopy(self.__rutas)
        nuevas_rutas = rutas_refer
        solucion_refer = copy.deepcopy(self.__S)
        nueva_solucion = solucion_refer
        nuevo_costo = self.__S.getCostoAsociado()
        print("tiempo deepcopy: "+str(time()-tiempo))
        
        #Atributos de tiempo e iteraciones
        tiempoIni = time()
        tiempoMax = float(self.__tiempoMaxEjec*60)
        tiempoEstancamiento = tiempoIni
        tiempoEjecuc = 0
        iteracEstancamiento = 1
        iteracEstancamiento_Opt = 1
        iteracEstancMax = 200
        iterac = 1
        indOptimosLocales = -2
        umbral = self.calculaUmbral(self.__S.getCostoAsociado())
        porc_Estancamiento = 1.05
        porc_EstancamientoMax = 1.15
        cond_Optimiz = True
        #cond_Estancamiento = False

        Aristas_Opt = np.array([], dtype = object)
        for EP in self._G.getA():
            if(EP.getOrigen().getValue() < EP.getDestino().getValue() and EP.getPeso() <= umbral):
                Aristas_Opt = np.append(Aristas_Opt, EP)
                ind_permitidos = np.append(ind_permitidos, EP.getId())
        #ind_permitidos = np.unique(ind_permitidos)
        Aristas = Aristas_Opt
        
        self.__optimosLocales.append(nuevas_rutas)
        porcentaje = round(self.__S.getCostoAsociado()/self.__optimo -1.0, 3)
        print("Costo sol Inicial: "+str(self.__S.getCostoAsociado())+"      ==> Optimo: "+str(self.__optimo)+"  Desvio: "+str(round(porcentaje*100,3))+"%")
        
        while(tiempoEjecuc < tiempoMax and porcentaje*100 > self.__porcentajeParada):
            
            if(cond_Optimiz):
                #tiempo = time()
                ind_permitidos, Aristas = self.getPermitidos(Aristas, lista_tabu, umbral, solucion_refer)    #Lista de elementos que no son tabu
                ind_AristasOpt = copy.deepcopy(ind_permitidos)
                self.__umbralMin = 0
                #print("Tiempo getPermitidos: ", (time()-tiempo))
            cond_Optimiz = False
            ADD = []
            DROP = []
            
            ind_random = np.arange(0,len(ind_permitidos))
            random.shuffle(ind_random)
            
            indRutas = indAristas = []
            nuevo_costo, k_Opt, indRutas, indAristas, aristasADD, aristasDROP = nueva_solucion.evaluarOpt(self._G.getA(), ind_permitidos, ind_random, rutas_refer)
            nuevo_costo = round(nuevo_costo, 3)

            tenureADD = self.__tenureADD
            tenureDROP = self.__tenureDROP
            
            costoSolucion = self.__S.getCostoAsociado()
            #tiempo = time()
            #Si encontramos una mejor solucion que la tomada como referencia
            if(nuevo_costo < solucion_refer.getCostoAsociado()):
                cad = "\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- Iteracion %d  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\n" %(iterac)
                print(cad)
                self.__txt.escribir(cad)
                nuevas_rutas = nueva_solucion.swap(k_Opt, aristasADD[0], rutas_refer, indRutas, indAristas)
                nueva_solucion = self.cargaSolucion(nuevas_rutas)
                solucion_refer = nueva_solucion
                rutas_refer = nuevas_rutas
                #print("Tiempo swap: "+str(time()-tiempo))
                
                #Si la nueva solucion es mejor que la obtenida hasta el momento
                if(nuevo_costo < costoSolucion):
                    porcentaje = round(nuevo_costo/self.__optimo -1.0, 3)
                    tiempoTotal = time()-tiempoEstancamiento
                    cad = "\nLa solución anterior duró " + str(int(tiempoTotal/60))+"min "+ str(int(tiempoTotal%60))
                    cad += "seg    -------> Nuevo optimo local. Costo: "+str(nuevo_costo)
                    cad += "       ==> Optimo: "+str(self.__optimo)+"  Desvio: "+str(porcentaje*100)+"%"
                    self.__S = nueva_solucion
                    self.__rutas = nuevas_rutas
                    self.__beta = 1
                    tiempoEstancamiento = time()
                    if(len(self.__optimosLocales) >= 15):
                        self.__optimosLocales.pop(0)
                    self.__optimosLocales.append(nuevas_rutas)
                    indOptimosLocales = -2
                else:
                    cad = "\nNuevo optimo como referencia. Costo: "+str(nueva_solucion.getCostoAsociado())
                print(cad)
                cad += "\nLista tabu: "+str(lista_tabu)
                self.__txt.escribir(cad)
                umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())
                tenureADD = self.__tenureMaxADD
                tenureDROP = self.__tenureMaxDROP
                cond_Optimiz = True
                Aristas = Aristas_Opt
                iteracEstancamiento = 1
                iteracEstancamiento_Opt = 1
                iteracEstancMax = 200
            #Si se estancó, tomamos a beta igual a 2
            elif(iteracEstancamiento > iteracEstancMax and self.__beta < 2):
                tiempoTotal = time()-tiempoEstancamiento
                print("Se estancó durante %d min %d seg. Incrementanos Beta para diversificar" %(int(tiempoTotal/60), int(tiempoTotal%60)))
                self.__beta = 2
                self.__umbralMin = umbral
                umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())
                cond_Optimiz = True
                iteracEstancamiento = 1
                iteracEstancMax = 150
                Aristas = Aristas_Opt
            #Si se estancó nuevamente, tomamos la proxima sol peor que difiera un 5% del optimo o la penultima de los optimos locales
            elif(iteracEstancamiento > iteracEstancMax and len(self.__optimosLocales) >= indOptimosLocales*(-1)):
                nuevas_rutas = self.__optimosLocales[indOptimosLocales]
                nueva_solucion = self.cargaSolucion(nuevas_rutas)
                costo = nueva_solucion.getCostoAsociado()
                tiempoTotal = time()-tiempoEstancamiento
                cad = "Se estancó durante %d min %d seg. Admitimos el penultimo optimo local " %(int(tiempoTotal/60), int(tiempoTotal%60))
                print(cad + "-->    Costo: "+str(costo))
                
                lista_tabu = []
                ind_permitidos = ind_AristasOpt
                umbral = self.calculaUmbral(costo)
                solucion_refer = nueva_solucion
                rutas_refer = nuevas_rutas
                cond_Optimiz = True
                Aristas = Aristas_Opt
                iteracEstancamiento = 1
                indOptimosLocales -= 1
                iteracEstancMax = 100
            elif(iteracEstancamiento > iteracEstancMax and costoSolucion*porc_Estancamiento > nuevo_costo and nuevo_costo < costoSolucion*porc_EstancamientoMax):
                nuevas_rutas = nueva_solucion.swap(k_Opt, aristasADD[0], rutas_refer, indRutas, indAristas)
                nueva_solucion = self.cargaSolucion(nuevas_rutas)
                tiempoTotal = time()-tiempoEstancamiento
                costo = nueva_solucion.getCostoAsociado()
                cad = "Se estancó durante %d min %d seg. Admitimos una solucion peor para diversificar" %(int(tiempoTotal/60), int(tiempoTotal%60))
                print(cad + "-->    Costo: "+str(costo))
                
                lista_tabu = []
                ind_permitidos = ind_AristasOpt
                umbral = self.calculaUmbral(costo)
                solucion_refer = nueva_solucion
                rutas_refer = nuevas_rutas
                cond_Optimiz = True
                iteracEstancamiento = 1
                Aristas = Aristas_Opt
                iteracEstancMax = 200
            elif(iteracEstancamiento > iteracEstancMax):
                nuevas_rutas = nueva_solucion.swap(k_Opt, aristasADD[0], rutas_refer, indRutas, indAristas)
                nueva_solucion = self.cargaSolucion(nuevas_rutas)            
                umbral = self.calculaUmbral(nueva_solucion.getCostoAsociado())
                cond_Optimiz = True
            else:
                nuevas_rutas = rutas_refer
                nueva_solucion = solucion_refer

            #Añado y elimino de la lista tabu
            if (aristasADD != []):
                ADD.append(Tabu(aristasADD[0], tenureADD))
                for i in range(0, len(aristasDROP)):
                    DROP.append(Tabu(aristasDROP[i], tenureDROP))
                self.decrementaTenure(lista_tabu, ind_permitidos)
                lista_tabu.extend(DROP)
                lista_tabu.extend(ADD)
            else:
                lista_tabu = []
                ind_permitidos = ind_AristasOpt
            
            tiempoEjecuc = time()-tiempoIni
            iterac += 1
            iteracEstancamiento += 1
            iteracEstancamiento_Opt += 1
        #Fin del while. Imprimo los valores obtenidos

        print("\nMejor solucion obtenida: "+str(self.__rutas))
        tiempoTotal = time() - tiempoIni
        print("\nTermino!! :)")
        print("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg\n")
        self.__txt.escribir("\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- Solucion Optima +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
        sol_ini = ""
        for i in range(0, len(self.__rutas)):
            sol_ini+="\nRuta #"+str(i+1)+": "+str(self.__rutas[i].getV())
            sol_ini+="\nCosto asociado: "+str(self.__rutas[i].getCostoAsociado())+"      Capacidad: "+str(self.__rutas[i].getCapacidad())+"\n"
        self.__txt.escribir(sol_ini)
        porcentaje = round(self.__S.getCostoAsociado()/self.__optimo -1.0, 3)
        self.__txt.escribir("\nCosto total:  " + str(self.__S.getCostoAsociado()) + "        Optimo real:  " + str(self.__optimo)+
                            "      Desviación: "+str(porcentaje*100)+"%")
        self.__txt.escribir("\nCantidad de iteraciones: "+str(iterac))
        self.__txt.escribir("Nro de vehiculos: "+str(self.__nroVehiculos))
        self.__txt.escribir("Capacidad Maxima/Vehiculo: "+str(self.__capacidadMax))
        self.__txt.escribir("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg")
        tiempoTotal = time()-tiempoEstancamiento
        self.__txt.escribir("Tiempo de estancamiento: "+str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg")
        self.__txt.imprimir()

    def getPermitidos(self, Aristas, lista_tabu, umbral, solucion):
        AristasNuevas = []
        ind_permitidos = np.array([], dtype = int)

        #No tengo en consideracion a las aristas que exceden el umbral y las que pertencen a S
        A_solucion = copy.copy(solucion.getA())
        for EP in Aristas:
            pertS = False
            i=0
            while(i < len(A_solucion)):
                A_S = A_solucion[i]
                if A_S == EP:
                    A_solucion.pop(i)
                    pertS = True
                    break
                i+=1
            if(not pertS and self.__umbralMin <= EP.getPeso() and EP.getPeso() <= umbral):
                AristasNuevas.append(EP)
                ind_permitidos = np.append(ind_permitidos, EP.getId())
        ind_permitidos = np.unique(ind_permitidos)

        return ind_permitidos, AristasNuevas

    #Decrementa el Tenure en caso de que no sea igual a -1. Si luego de decrementar es 0, lo elimino de la lista tabu
    def decrementaTenure(self, lista_tabu, ind_permitidos):
        i=0
        while (i < len(lista_tabu)):
            elemTabu=lista_tabu[i]
            elemTabu.decrementaT()
            if(elemTabu.getTenure()==0):
                ind_permitidos = np.append(ind_permitidos, elemTabu.getElemento().getId())
                lista_tabu.pop(i)
                i-=1
            i+=1
    