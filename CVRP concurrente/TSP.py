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
from clsTxt import clsTxt
from time import time

class TSP:
    def __init__(self, M: list, nombreArchivo, solInicial, nroIntercambios, opt, tenureADD, tenureDROP, tiempoEjec, optimo):
        self._G = Grafo(M,0)  #Grafo original
        print("Se cargo el archivo")
        self.__soluciones = []   #Lista de Grafos que corresponden a las soluciones
        self.__nroIntercambios=nroIntercambios*2    #corresponde al nro de vertices los intercambios. 1intercambio => 2 vertices
        self.__opt=opt
        self.__optimo = optimo
        self.__tenureADD =  tenureADD
        self.__tenureMaxADD = int(tenureADD*1.7)
        self.__tenureDROP =  tenureDROP
        self.__tenureMaxDROP = int(tenureDROP*1.7)
        self.__txt = clsTxt(str(nombreArchivo))
        self.__tiempoMaxEjec = float(tiempoEjec)
        self.__frecMatriz = []
        for i in range(0, len(self._G.getMatriz())):
            fila = []
            for j in range(0, len(self._G.getMatriz())):
                fila.append(0)
                j
            self.__frecMatriz.append(fila)
            i
        self.tabuSearch(solInicial)

    def vecinoMasCercano(self, matrizDist: list, pos: int, visitados: list):
        masCercano = matrizDist[pos][pos]
        indMasCercano = 0
    
        for i in range(0, len(matrizDist)):
            costo = matrizDist[pos][i]
            if(costo<masCercano and i not in visitados):
                masCercano = costo
                indMasCercano = i
        
        return indMasCercano 
    
    def solucionVecinosCercanos(self):
        inicio = self._G.getV()[0]
        matrizDist = self._G.getMatriz()

        recorrido = []
        visitados = []
        
        recorrido.append(inicio)    #Agrego el vertice inicial
        visitados.append(0)     #Agrego el vertice inicial
        masCercano=0
        for i in range(0,len(matrizDist)-1):
            masCercano = self.vecinoMasCercano(matrizDist,masCercano, visitados) #obtiene la posicion dela matriz del vecino mas cercano
            recorrido.append(Vertice(masCercano+1,0))
            visitados.append(masCercano)
            i

        return recorrido

    def solucionAlAzar(self):
        inicio = self._G.getVerticeInicio()
        indices_azar = random.sample( range(2,len(self._G.getV())+1), len(self._G.getV())-1)
        
        alAzar = []
        alAzar.append(inicio)
        for i in indices_azar:
            alAzar.append(Vertice(i,0))

        return alAzar
 
    # Para el Tabu Search Granular
    def vecinosMasCercanosTSG(self, indicesRandom: list, lista_permitidos: list, recorrido: list):
        indices = []                #Indices de la lista de permitidos para hacer el swapp
        valores_permitidos = []     #Lista de permitidos como enteros y no como vertices
        valores_recorrido = []              #La solucion como una lista de enteros
        matrizDist = self._G.getMatriz()
        
        for x in lista_permitidos:
            valores_permitidos.append(x.getValue()) #Se carga con los indices que ocupan en el grafo. Lo mismo que en lista_permit solo que
                                                    #ahora son enteros y no vertices
        
        for x in recorrido:
            valores_recorrido.append(x.getValue())
        
        permitRandom = []
        for x in indicesRandom:
            permitRandom.append(valores_permitidos[x])
        
        permitidos = list(set(valores_permitidos)-set(permitRandom))

        for i in indicesRandom:
            indices.append(i)
            ind = self.vecinoMasCercanoV2(matrizDist,valores_permitidos[i], permitidos, valores_permitidos, valores_recorrido)
            indices.append(ind)
            if(permitidos!=[]):
                permitidos.remove(valores_permitidos[ind])

        return indices

    def vecinoMasCercanoV2(self, matrizDist: list, pos: int, permitidos: list, list_permit, recorrido):
        masCercano = 999999999999
        indMasCercano = 0
        posAnterior = recorrido.index(pos) -1
        posAnterior=int(recorrido[posAnterior])
    
        for ind in permitidos:
            costo = matrizDist[posAnterior-1][ind-1]
            if(costo<masCercano or len(permitidos)==1):
                masCercano = costo
                indMasCercano = list_permit.index(ind)

        return indMasCercano

    #Incrementa la frecuencia en cada arista, en caso de que se obtenga un optimo local
    def incrementaFrecuencia(self, sol):
        for x in sol.getA():
            origen = int(x.getOrigen().getValue()-1)
            destino = int(x.getDestino().getValue()-1)
            self.__frecMatriz[origen][destino] = self.__frecMatriz[origen][destino] + 1
            self.__frecMatriz[destino][origen] = self.__frecMatriz[destino][origen] + 1
        
    #Analizamos las aristas mas frecuentadas para mantenerlas estaticas
    def TS_Frecuencia(self, Sol_Optima, lista_tabu, nroIntercambios):      
        aristasSol = Sol_Optima.getA()
        lista_Frecuentados = lista_tabu
        vertADD = None
        vertDROP = None

        #Me fijo si "esta llena" la lista tabu, tal que permita realizar los intercambios que se indicaron
        longitud =  len(Sol_Optima.getV()) - len(lista_tabu)    #Longitud de los permitidos
        longitud -= (4 +1)     #Verifico si hay suficiente permitidos para agregar a la lista tabu, sin contar el V(1)
        
        #print("Lista tabu antes: "+str(lista_tabu))
        #Verifico que se cumpla las condiciones con respecto a longitudes
        if(longitud>=0):
            mayFrecuencia = -1
            
            #Recorro las aristas de la ultima solucion optima obtenida
            for a in aristasSol:
                vert_Origen = a.getOrigen()
                vert_Destino = a.getDestino()
                frec_Actual = self.__frecMatriz[vert_Origen.getValue()-1][vert_Destino.getValue()-1]
                pertenece = self.pertenListaTabu_TSF(vert_Origen, vert_Destino, lista_tabu)
                
                if(frec_Actual > mayFrecuencia and not pertenece):
                    mayFrecuencia = frec_Actual
                    vertADD = vert_Origen
                    vertDROP = vert_Destino 
            #Cargamos los mas frecuentados con un Tenure igual a -1, para que no se eliminen
            if(vertADD != None and vertDROP != None):
                lista_Frecuentados = self.frecuentados(vertADD, vertDROP, lista_tabu)
                #print("vertADD: "+str(vertADD)+"    vertDROP: "+str(vertDROP)+ "       Max Frecuencia: "+str(mayFrecuencia))
                #print("Lista tabu ahora: "+str(lista_Frecuentados))
                return lista_Frecuentados
        
        #Si no se cumple, tengo la lista tabu "llena"
        #Elimino una cantidad suficiente de la lista Tabu para que permita realizar los intercambios
        lista_Frecuentados = self.borraFrecuentados(lista_tabu)
        
        #print("Lista tabu ahora: "+str(lista_Frecuentados))
        
        return lista_Frecuentados

    #Devuelve los frecuentados
    def frecuentados(self, vert_ADD, vert_DROP, lista_tabu):
        lista_Frecuentados = []
        for x in lista_tabu:
            valor = x.getElemento().getValue()
            if(valor != vert_ADD.getValue() and valor != vert_DROP.getValue()):
                lista_Frecuentados.append(x)

        if(vert_ADD.getValue()!= 1):
            Tabu_ADD = Tabu(vert_ADD, -1)
            lista_Frecuentados.append(Tabu_ADD)
    
        if(vert_DROP.getValue()!= 1):
            Tabu_DROP = Tabu(vert_DROP, -1)
            lista_Frecuentados.append(Tabu_DROP)

        return lista_Frecuentados

    #Pertenece o no a la lista tabu
    def pertenListaTabu_TSF(self, v1, v2, lista_tabu):
        lista_ElementosTabu = []
        e1 = v1.getValue()
        e2 = v2.getValue()
        
        for x in lista_tabu:
            elem = int(x.getElemento().getValue())
            lista_ElementosTabu.append(elem)
        
        return (e1 in lista_ElementosTabu) or (e2 in lista_ElementosTabu)

    #Borro una cantidad necesaria para realizar los Swapp proximos
    def borraFrecuentados(self, lista_tabu):
        #Borramos al azar
        indices_azar = random.sample(range(0,len(lista_tabu)), 4)
        
        ADD = None
        DROP = None
        print("Lista de frecuentados llena. Borramos algunos")
        for ind in indices_azar:
            lista_tabu[ind].setTenure(1)
            if(ADD == None):
                ADD = lista_tabu[ind].getElemento().getValue() -1
            elif(DROP == None):
                DROP = lista_tabu[ind].getElemento().getValue() -1
            else:
                self.__frecMatriz[int(ADD)][int(DROP)] = 0
                ADD = None
                DROP = None
        self.decrementaTenure(lista_tabu)

        return lista_tabu

    ####### Empezamos con Tabu Search #########
    def tabuSearch(self, strSolInicial):
        lista_tabu = []     #Tiene objetos de la clase Tabu
        lista_permit = []   #Tiene objetos del tipo vertice      
        g1 = self._G.copyVacio()  #La primera solucion corresponde a g1
        
        if(strSolInicial=="Vecino mas cercano"):
            ########Partimos del vecino mas cercano###########
            print("Soluncion inicial por Vecino mas cercano")
            vecinosCercanos = self.solucionVecinosCercanos() #Obtiene un vector de vértices
            g1.cargarDesdeSecuenciaDeVertices(vecinosCercanos) #Carga el recorrido a la solución
        else:
            ########Partimos de una solucion al Azar#############
            print("Solucion inicial al azar")
            solucionAzar = self.solucionAlAzar()
            g1.cargarDesdeSecuenciaDeVertices(solucionAzar)

        self.__soluciones.append(g1) #Agregar solución inicial
        self.incrementaFrecuencia(g1)
        
        print("Comenzando Tabu Search")
        self.__txt.escribir("############### GRAFO CARGADO #################")
        self.__txt.escribir(str(self._G))
        self.__txt.escribir("################ SOLUCION INICIAL #################")
        self.__txt.escribir("Vertices:        " + str(g1.getV()))
        self.__txt.escribir("Aristas:         " + str(g1.getA()))
        self.__txt.escribir("Costo asociado:  " + str(g1.getCostoAsociado()))
        
        ##############     Atributos       ################
        #Soluciones a utilizar
        Sol_Actual = self._G.copyVacio()
        Sol_Actual = self.__soluciones[len(self.__soluciones)-1]        #La actual es la Primera solución
        Sol_Optima = copy.deepcopy(Sol_Actual)      #Ultima solucion optima obtenida, corresponde a la primera Solucion
        
        #Atributos banderas utilizados
        condOptim = False   #En caso de que encontre uno mejor que el optimo lo guardo en el archivo txt
        condTS_Frecuencia = False #Empezamos a utilizar las aristas mas frecuentadas
        cond_3opt = False
        cond_4opt = False

        if(self.__opt == "3-opt"):
            cond_3opt = True
            print("Movimiento: 3-opt")

        #Atributos de tiempo y otros
        tiempoIni = time()
        tiempoIniEstancamiento = tiempoIni       
        tiempoIniNoMejora = tiempoIni
        tiempoMax = float(self.__tiempoMaxEjec*60)
        tiempoEjecuc = 0
        iterac = 1
        
        #Duarnte 1min de no mejora o si es demasiado, la 1/5 parte del tiempo
        tiempoMaxNoMejora = 2*60
        if(tiempoMaxNoMejora > tiempoMax/4):
            tiempoMaxNoMejora = float(tiempoMax/4)  #La 1/5 parte del tiempo, en caso de que los 1min sea demasiado

        print("Tiempo maximo: "+str(int(tiempoMax/60))+"min "+str(int(tiempoMax%60))+"seg")
        print("Tiempo maximo estancamiento: "+str(int(tiempoMaxNoMejora/60))+"min "+str(int(tiempoMaxNoMejora%60))+"seg")
        print("Optimo real: "+str(self.__optimo))
        print("Solucion inicial: "+str(Sol_Optima.getCostoAsociado()))

        nroIntercambios = 2 #Empezamos con 2 al inicio
        while(tiempoEjecuc <= tiempoMax):
            lista_permit = self.pertenListaTabu(lista_tabu)    #Lista de elementos que no son tabu
            ADD = []
            DROP = []
            
            #Verifico si hay vertices disponibles suficientes para el intercambio
            if(len(lista_permit)>=4):
                #Controla que el nro de intercambios no supere la longitud de permitidos
                if(len(lista_permit)<nroIntercambios):
                    nroIntercambios=len(lista_permit)
                    if(nroIntercambios%2!=0):
                        nroIntercambios-=1                    
                
                tiempoRestante = tiempoMax - tiempoEjecuc       #Lo que queda de tiempo
                
                #+-+-+-+-+-+-+- En caso de estancamientos +-+-+-+-+-+-+-+-+-+-+-
                if(time()-tiempoIniEstancamiento > tiempoMaxNoMejora):    
                    tiempoTotal = time()-tiempoIniEstancamiento
                    print("\nDurante " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg no hubo mejora")
                    print("Tiempo restante: "+str(int(tiempoRestante/60))+"min "+str(int(tiempoRestante%60))+ "seg")
                    
                    print("\nAplicamos frecuencia de aristas mas visitadas")
                    lista_tabu = self.TS_Frecuencia(Sol_Optima, lista_tabu, nroIntercambios)                    
                    lista_permit = self.pertenListaTabu(lista_tabu)
                    condTS_Frecuencia = not condTS_Frecuencia
                    
                    #Se intercambia movimientos entre 2-opt, 3-opt y 4-opt
                    if(not cond_3opt and not cond_4opt):
                        print("Aplicamos movimientos 3-opt")
                        cond_3opt = True
                    else:
                        cond_3opt = False
                        if(not cond_4opt):
                            print("Aplicamos movimientos 4-opt v2")
                            cond_4opt = True
                        elif(nroIntercambios < self.__nroIntercambios):
                            nroIntercambios += 2
                            cond_4opt = False
                            print("Aplicamos movimientos 4-opt v1")
                        else:
                            cond_4opt = False
                            nroIntercambios = 2
                            print("Aplicamos movimientos 2-opt")

                    #Obtengo 2/3 de lo que resta de tiempo, para que la proxima vez ingrese en menor tiempo cuando no hay mejoria
                    #solo en caso de que el tiempo restante sea menor al tiempo MaxNoMejora, ya que si no, no habra una proxima
                    #vez en que se estanque
                    if(tiempoRestante < tiempoMaxNoMejora and not cond_3opt):
                        tiempoMaxNoMejora = tiempoRestante*2/3
                    elif(tiempoMaxNoMejora > 20 and not cond_3opt):   #Mayor que 20seg
                        tiempoMaxNoMejora = tiempoMaxNoMejora*0.75

                    tiempoIniEstancamiento=time()    #Reiniciamos el tiempo de No mejora
                    
                ######### Tabu Search Granular ##########                
                if(cond_3opt):
                    #3-opt
                    ind_random = random.sample(range(0,len(lista_permit)),1)
                    ind_random = self.vecinosMasCercanosTSG(ind_random, lista_permit, Sol_Optima.getV())
                    ind_aux = self.vecinosMasCercanosTSG(ind_random, lista_permit, Sol_Optima.getV())
                    ind_random.append(ind_aux[-1])
                elif(cond_4opt):
                    #4-opt
                    ind_random = random.sample(range(0,len(lista_permit)),2)
                    ind_random = self.vecinosMasCercanosTSG(ind_random, lista_permit, Sol_Optima.getV())
                else:
                    #2-opt    
                    ind_random = random.sample(range(0,len(lista_permit)),int(nroIntercambios/2))
                    ind_random = self.vecinosMasCercanosTSG(ind_random, lista_permit, Sol_Optima.getV())
                
                #Crea los elementos ADD y DROP
                for i in range(0,len(ind_random)):
                    if(i%2==0): #Los pares para ADD y los impares para DROP
                        ADD.append(Tabu(lista_permit[ind_random[i]], self.__tenureADD))
                    else:
                        DROP.append(Tabu(lista_permit[ind_random[i]], self.__tenureDROP))

                #Realiza el intercambio de los vertices seleccionados
                if(cond_3opt):
                    #3-opt
                    Sol_Actual = Sol_Actual.swap_3opt(ADD[0].getElemento(), DROP[0].getElemento(), ADD[1].getElemento())
                elif(cond_4opt):
                    #4-opt v2
                    Sol_Actual = Sol_Actual.swap_4opt(ADD[0].getElemento(), DROP[0].getElemento(), ADD[1].getElemento(), DROP[1].getElemento())
                else:
                    #2-opt y 4-opt v1
                    for i in range(0,len(ADD)):
                        Sol_Actual = Sol_Actual.swapp(ADD[i].getElemento(), DROP[i].getElemento())
                    
                #Si obtengo una nueva solucion optima
                if(Sol_Actual < Sol_Optima):
                    Sol_Optima = Sol_Actual                  #Actualizo la solucion optima
                    self.incrementaFrecuencia(Sol_Optima)    #Incrementa Frecuencia de Aristas visitadas
                    
                    condOptim = True
                    
                    tiempoTotal = time() - tiempoIniNoMejora
                    print("La solución anterior duró " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg    -------> Nuevo optimo encontrado. Costo: "+str(Sol_Optima.getCostoAsociado()))
                    
                    self.__soluciones.append(Sol_Actual) #Cargo las soluciones optimas
                    tiempoIniEstancamiento=time()
                    tiempoIniNoMejora = time()

                    #Actualizo el tenure con el tenureMax de ADD y DROP
                    for i in range(0,len(ADD)):
                        if(i<len(ADD)):
                            ADD[i].setTenure(self.__tenureMaxADD)
                        elif(i<len(DROP)):
                            DROP[i].setTenure(self.__tenureMaxDROP)
                else:
                    #Si no hubo un estancamiento, utilizo la ultima solucion optima obtenida, y sigo aplicando Tabu Search
                    Sol_Actual = Sol_Optima
                
                #Si hemos encontramos un optima local, lo guardamos en el txt
                if(condOptim):
                    self.__txt.escribir("################################ " + str(iterac) + " ####################################")
                    self.__txt.escribir("Vertices:        " + str(Sol_Actual.getV()))
                    self.__txt.escribir("Aristas:         " + str(Sol_Actual.getA()))
                    self.__txt.escribir("Costo asociado:  " + str(Sol_Actual.getCostoAsociado()))
                    self.__txt.escribir("Tiempo actual:   "+ str())
                    self.__txt.escribir("-+-+-+-+-+-+-+-+-+-+-+-+ Lista TABÚ +-+-+-+-+-+-+-+-+-+-+-+-+")
                    self.__txt.escribir("Lista Tabu: "+ str(lista_tabu))
                    condOptim = False
                    
                    self.decrementaTenure(lista_tabu)   #Decremento el tenure y elimino algunos elementos con tenure igual a 0
                    
                    #Agrego los nuevos vertices a la lista tabu o decremento el tiempo de iteracion de TS_Frecuencia
                    if(not condTS_Frecuencia):
                        lista_tabu.extend(ADD)
                        lista_tabu.extend(DROP)
            
                    condTS_Frecuencia = False
            else:
                print("No hay vertices disponibles para el intercambio. Elimina vertices de la lista Tabu")
                self.borraFrecuentados(lista_tabu)
            
            lista_permit = []
            iterac += 1
            tiempoEjecuc = time()-tiempoIni
        
        #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        #Fin del while. Imprimo la solucion optima y algunos atributos
        tiempoFin = time()
        tiempoTotal = tiempoFin - tiempoIni
        self.__txt.escribir("\n################################ Solucion Optima ####################################")
        self.__txt.escribir("Vertices:        " + str(Sol_Optima.getV()))
        self.__txt.escribir("Aristas:         " + str(Sol_Optima.getA()))
        porcentaje = round(Sol_Optima.getCostoAsociado()/self.__optimo -1.0, 3)
        self.__txt.escribir("Costo asociado:  " + str(Sol_Optima.getCostoAsociado()) + "        Optimo real:  " + str(self.__optimo)+"      Desviación: "+str(porcentaje*100)+"%")
        self.__txt.escribir("\nNro Intercambios: " + str(int(self.__nroIntercambios/2)))
        self.__txt.escribir("Cantidad de iteraciones: "+str(iterac))
        self.__txt.escribir("Movimiento Opt inicial: "+self.__opt)
        self.__txt.escribir("Tenure ADD: " + str(self.__tenureADD) + "           Tenure DROP: "+str(self.__tenureDROP))
        self.__txt.escribir("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg")
        self.__txt.imprimir()
        
        print("\nTermino!! :)")
        print("Tiempo total: " + str(int(tiempoTotal/60))+"min "+str(int(tiempoTotal%60))+"seg\n")

    #Devuelve una lista con los vertices que no pertenecen a la lista tabu
    def pertenListaTabu(self, lista_tabu: list):
        ListaPermit = []
        CopyVert = copy.deepcopy(self._G.getV())
        cantVert = len(copy.deepcopy(self._G.getV()))
        if(len(lista_tabu) == 0):
            ListaPermit = CopyVert
        else:
            for i in range(0, cantVert):
                EP = CopyVert[i]      #EP: Elemento Permitido
                j = 0
                cond = True
                while(j < len(lista_tabu) and cond):
                    ET = lista_tabu[j].getElemento()    #ET: Elemento Tabu
                    if(EP == ET):
                        cond = False
                    j+=1
                if(cond):
                    ListaPermit.append(EP)
        
        ListaPermit.pop(0) #Eliminamos el vertice inicial, el 1
        
        return ListaPermit

    #Decrementa el Tenure en caso de que no sea igual a -1. Si luego de decrementar es 0, lo elimino de la lista tabu
    def decrementaTenure(self, lista_tabu: list):
        i=0
        while (i <len(lista_tabu)):
            elemTabu=lista_tabu[i]
            if(elemTabu.getTenure()!=-1):
                elemTabu.decrementaT()
            if(elemTabu.getTenure()==0):
                lista_tabu.pop(i)
                i-=1
            i+=1
