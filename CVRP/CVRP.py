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
from Grafico import Grafico
class CVRP:
    def __init__(self, M, D, nroV, capac, archivo, carpeta, solI, tADD, tDROP, tiempo, porcentaje, optimo):       
        self._G = Grafo(M, D,True)                #Grafo original
        self.__S = Solucion(M,D,capac, nroV)    #Solucion general del CVRP
        self.__Distancias = M                #Mareiz de distancias
        self.__Demandas = D                  #Demandas de los clientes
        self.__capacidadMax = capac          #Capacidad max por vehiculo
        self.__rutas = []                    #Soluciones por vehiculo (lista de soluciones)
        self.__nroVehiculos = nroV           #Nro de vehiculos disponibles
        self.__tipoSolucionIni = solI        #Tipo de solucion inicial (Clark & Wright, Vecino cercano, Secuencial o al Azar)
        self.__beta = 1                      #Parametro de dispersion
        self.__umbralMin = 0                 #Umbral de granularidad minimo
        self.__optimosLocales = []           #Lista de optimos locales 
        self.__porcentajeParada = float(porcentaje) #Porcentaje de desvio minimo como condicion de parada
        self.__optimo = optimo               #Mejor valor de la instancia
        self.__tenureADD =  tADD             
        self.__tenureMaxADD = int(tADD*1.7)
        self.__tenureDROP =  tDROP
        self.__tenureMaxDROP = int(tDROP*1.7)
        self.__txt = clsTxt(str(archivo))
        self.__tiempoMaxEjec = float(tiempo)
        self.escribirDatos()
        t = time()
        self.__S.rutasIniciales(self.__tipoSolucionIni)
        print("Rutas iniciales: ",time()-t)
        print(self.__S)
        self.tabuSearch()
        #self.Grafico = Grafico(coord,rutas)

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

    def mostrarError(self):
        porcentaje =  round(self.__S.getCostoTotal()/self.__optimo -1.0, 3)
        print(str(round(porcentaje*100,3))+"%")

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
        # tiempo=time()
        solucion_refer = copy.deepcopy(self.__S)
        nueva_solucion = solucion_refer
        nuevo_costo = self.__S.getCostoTotal()
        # print("tiempo deepcopy: "+str(time()-tiempo))
        
        #Atributos de tiempo e iteraciones
        tiempoIni = time()
        tiempoMax = float(self.__tiempoMaxEjec*60)
        tiempoEstancamiento = tiempoIni
        tiempoEjecuc = 0
        iteracEstancamiento = 1
        iteracEstancamiento_Opt = 1
        iteracEstancMax = 300
        iterac = 1
        indOptimosLocales = -2
        umbral = self.calculaUmbral(self.__S.getCostoTotal())
        porc_Estancamiento = 1.05
        porc_EstancamientoMax = 1.15
        cond_Optimiz = True
        cond_Estancamiento = False


        N = self._G.getGrado()
        Aristas_Opt = []
        ind_permitidos = []

        for i in range(1,N):
            j = i+1
            while(j<N):
                A = self._G.buscarArista((i,j))
                if(A.getPeso() <= umbral):
                    Aristas_Opt.append(A)
                    ind_permitidos.append(A.getId())
                j+=1
        Aristas = Aristas_Opt
        ind_AristasOpt = copy.deepcopy(ind_permitidos)
        print(self.__S)
        self.__optimosLocales.append(nueva_solucion)
        #print(Aristas_Opt)

        porcentaje = round(self.__S.getCostoTotal()/self.__optimo -1.0, 3)
        print("Costo sol Inicial: "+str(self.__S.getCostoTotal())+"      ==> Optimo: "+str(self.__optimo)+"  Desvio: "+str(round(porcentaje*100,3))+"%")

        while(tiempoEjecuc < tiempoMax and porcentaje*100 > self.__porcentajeParada):
            if(cond_Optimiz):
                #tiempo = time()
                ind_permitidos, Aristas = self.getPermitidos(Aristas, lista_tabu, umbral, solucion_refer)    #Lista de elementos que no son tabu
                self.__umbralMin = 0
                #print("Tiempo getPermitidos: ", (time()-tiempo))
            #print("ind_AristasOpt: "+str(ind_AristasOpt))
            cond_Optimiz = False
            ADD = []
            DROP = []
            
            ind_random = np.arange(0,len(ind_permitidos))
            random.shuffle(ind_random)
            
            indRutas = indAristas = []
            nuevo_costo, k_Opt, indRutas, indAristas, aristasADD, aristasDROP = nueva_solucion.evaluarOpt(self._G.getA(), ind_permitidos, ind_random)
            nuevo_costo = round(nuevo_costo, 3)

            tenureADD = self.__tenureADD
            tenureDROP = self.__tenureDROP
            
            costoSolucion = self.__S.getCostoTotal()
            tiempo = time()
            #Si encontramos una mejor solucion que la tomada como referencia
            if(nuevo_costo < solucion_refer.getCostoTotal() and nuevo_costo!= float("inf")):
                cad = "\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- Iteracion %d  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\n" %(iterac)
                self.__txt.escribir(cad)
                # cad = "Rutas antes:"
                # for i in indRutas:
                #     cad+="\nruta #%d: %s"%(i,str(nuevas_rutas[i].getA()))
                # print(cad)
                # print("Opcion: Swap %d-opt opcion: %d " %(k_Opt[0], k_Opt[1]))
                # print("ADD: %s          DROP: %s" %(str(aristasADD), str(aristasDROP)))
                # print("indADD: "+str(indAristas))
                nueva_solucion.swap(k_Opt, aristasADD[0], indRutas, indAristas)

                # cad = "\nRUtas ahora:"
                # for i in indRutas:
                #     cad+="\nruta #%d: %s"%(i,str(nuevas_rutas[i].getA()))
                #print(cad)
                # print("nuevo costo: ", nuevo_costo)
                # print("nueva solucion (cargaSolucion): ", nueva_solucion.getCostoAsociado())
                # print("costo solucion: ", costoSolucion)
                # print("costo solucion: ", self.__S.getCostoAsociado())
                # print("Opcion: Swap %d-opt opcion: %d " %(k_Opt[0], k_Opt[1]))
                # print("ADD: %s          DROP: %s" %(str(aristasADD), str(aristasDROP)))
                # print("indADD: "+str(indAristas))
                
                solucion_refer = nueva_solucion
                # print("Tiempo swap: "+str(time()-tiempo))
                #Si la nueva solucion es mejor que la obtenida hasta el momento
                if(nuevo_costo < costoSolucion):    
                    porcentaje = round(nuevo_costo/self.__optimo -1.0, 3)
                    tiempoTotal = time()-tiempoEstancamiento
                    print(cad)
                    cad = "\nLa solución anterior duró " + str(int(tiempoTotal/60))+"min "+ str(int(tiempoTotal%60))
                    cad += "seg    -------> Nuevo optimo local. Costo: "+str(nuevo_costo)
                    cad += "       ==> Optimo: "+str(self.__optimo)+"  Desvio: "+str(porcentaje*100)+"%"
                    self.__S = nueva_solucion
                    self.__beta = 1
                    tiempoEstancamiento = time()
                    if(len(self.__optimosLocales) >= 15):
                        self.__optimosLocales.pop(0)
                    self.__optimosLocales.append(nueva_solucion)
                    indOptimosLocales = -2
                    print(cad)
                else:
                    cad += "\nSolucion peor. Costo: "+str(nueva_solucion.getCostoTotal())
                cad += "\nLista tabu: "+str(lista_tabu)
                self.__txt.escribir(cad)
                umbral = self.calculaUmbral(nueva_solucion.getCostoTotal())
                tenureADD = self.__tenureMaxADD
                tenureDROP = self.__tenureMaxDROP
                cond_Optimiz = True
                Aristas = Aristas_Opt
                iteracEstancamiento = 1
                iteracEstancamiento_Opt = 1
                iteracEstancMax = 300
            #Si se estancó, tomamos a beta igual a 2
            elif(iteracEstancamiento > iteracEstancMax and self.__beta < 2):
                tiempoTotal = time()-tiempoEstancamiento
                print("Se estancó durante %d min %d seg. Incrementanos Beta para diversificar" %(int(tiempoTotal/60), int(tiempoTotal%60)))
                self.__beta = 2
                self.__umbralMin = umbral
                umbral = self.calculaUmbral(nueva_solucion.getCostoTotal())
                cond_Optimiz = True
                iteracEstancamiento = 1
                iteracEstancMax = 200
                Aristas = Aristas_Opt
            #Si se estancó nuevamente, tomamos la proxima sol peor que difiera un 5% del optimo o la penultima de los optimos locales
            elif(iteracEstancamiento > iteracEstancMax and len(self.__optimosLocales) >= indOptimosLocales*(-1)):
                solucion_peor = self.__optimosLocales[indOptimosLocales]
                nueva_solucion = copy.deepcopy(solucion_peor)
                costo = nueva_solucion.getCostoTotal()
                tiempoTotal = time()-tiempoEstancamiento
                cad = "Se estancó durante %d min %d seg. Admitimos el penultimo optimo local " %(int(tiempoTotal/60), int(tiempoTotal%60))
                print(cad + "-->    Costo: "+str(costo))
                lista_tabu = []
                ind_permitidos = ind_AristasOpt
                umbral = self.calculaUmbral(costo)
                solucion_refer = copy.deepcopy(nueva_solucion)
                cond_Optimiz = True
                Aristas = Aristas_Opt
                iteracEstancamiento = 1
                indOptimosLocales -= 1
                iteracEstancMax = 100
                self.__beta = 3
            elif(iteracEstancamiento > iteracEstancMax and costoSolucion*porc_Estancamiento > nuevo_costo):
                nueva_solucion.swap(k_Opt, aristasADD[0], indRutas, indAristas)
                tiempoTotal = time()-tiempoEstancamiento
                costo = nueva_solucion.getCostoTotal()
                cad = "Se estancó durante %d min %d seg. Admitimos una solucion peor para diversificar" %(int(tiempoTotal/60), int(tiempoTotal%60))
                print(cad + "-->    Costo: "+str(costo))
                lista_tabu = []
                ind_permitidos = ind_AristasOpt
                umbral = self.calculaUmbral(costo)
                solucion_refer = copy.deepcopy(nueva_solucion)
                cond_Optimiz = True
                iteracEstancamiento = 1
                Aristas = Aristas_Opt
                iteracEstancMax = 300
            elif(iteracEstancamiento > iteracEstancMax):
                nueva_solucion.swap(k_Opt, aristasADD[0], indRutas, indAristas)        
                solucion_refer = copy.deepcopy(nueva_solucion)
                cond_Optimiz = True
                self.__beta = 3
                lista_tabu = []
                ind_permitidos = ind_AristasOpt
                umbral = self.calculaUmbral(costo)
            else:
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
                #print("Lista tabu: "+str(lista_tabu))
                lista_tabu = []
                #print("ind permitidos antes: "+str(ind_permitidos))
                ind_permitidos = copy.copy(ind_AristasOpt)
                #print("ind permitidos despues: "+str(ind_permitidos))

            
            tiempoEjecuc = time()-tiempoIni
            iterac += 1
            iteracEstancamiento += 1
            iteracEstancamiento_Opt += 1
        #Fin del while. Imprimo los valores obtenidos

        print("\nMejor solucion obtenida: "+str(self.__S))
        tiempoTotal = time() - tiempoIni
        print("\nTermino!! :)")
        print("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg\n")
        self.__txt.escribir("\n+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+- Solucion Optima +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-")
        sol_ini = ""
        for i in range(0, len(self.__rutas)):
            sol_ini+="\nRuta #"+str(i+1)+": "+str(self.__rutas[i].getV())
            sol_ini+="\nCosto asociado: "+str(self.__rutas[i].getCostoAsociado())+"      Capacidad: "+str(self.__rutas[i].getCapacidad())+"\n"
        self.__txt.escribir(sol_ini)
        porcentaje = round(self.__S.getCostoTotal()/self.__optimo -1.0, 3)
        self.__txt.escribir("\nCosto total:  " + str(self.__S.getCostoTotal()) + "        Optimo real:  " + str(self.__optimo)+
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
        #ind_permitidos = np.array([], dtype = int)
        ind_permitidos = []
        #No tengo en consideracion a las aristas que exceden el umbral y las que pertencen a S
        #print(solucion.rutas)
        for EP in Aristas:
            cond1 = solucion.contieneArista(EP) #Este es para la arista EP normal 
            cond2 = solucion.contieneArista(EP.getAristaInvertida()) #Para la arista EP invertida
            if(self.__umbralMin <= EP.getPeso() and EP.getPeso() <= umbral and not cond1 and not cond2):
                AristasNuevas.append(EP)
                ind_permitidos.append(EP.getId())
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