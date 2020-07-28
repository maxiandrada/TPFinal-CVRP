from Grafo import Grafo 
from Vertice import Vertice 
from Arista import Arista
import copy
import sys
import random
import math
import numpy as np
from time import time
from Ruta import Ruta

class Solucion():
    #
    def __init__(self, M, demanda, capacidad, nroVehiculos):
        self._matrizDistancias = M
        self.costoTotal = 0
        self.capacidadMax = capacidad
        self.nroVehiculos = nroVehiculos
        self.demanda = demanda
        self.rutas = []
        rutaAux = Ruta(M,demanda,capacidad)
        self.dictA = rutaAux.crearDictA()

    def __str__(self):
        rutas = self.rutas
        cad = ""
        for r in range(len(self.rutas)):
            cad += f"\nRecorrido de la Ruta {r+1}: {rutas[r].getV()} \n Aristas de la solución: {rutas[r].getA()}"
            #cad += rutas[r].getCapacidadPorCliente()
            cad += f"\nCosto Asociado: {round(rutas[r].getCostoAsociado(),3)} \tCapacidad: {rutas[r].capacidad}\t"
        cad += f"\nCosto Total: {self.costoTotal} \t CapacidadMax: {self.capacidadMax}\n"
        return cad

    # def __repr__(self):
    #     return str(self.getV())

    def __deepcopy__(self,memo):
        aux = copy.copy(self)
        aux.rutas = []
        for r in range(len(self.getRutas())):
            rutaOriginal = self.getRutas()[r] #Obtiene la ruta
            V_RutaOriginal = rutaOriginal.getV() #Obtiene el V y A de la ruta
            A_RutaOriginal = rutaOriginal.getA() 
            rutaNueva = copy.copy(rutaOriginal) #Realiza una copia superficial de la ruta, ambos objentos tendrán id diferente
            V_rutaNueva = [] #Se crean nuevas listas para que sean tomadas como objetos disintos de la ruta Original
            A_rutaNueva = []
            for x in range(len(V_RutaOriginal)):
                V_rutaNueva.append(copy.copy(V_RutaOriginal[x]))
                A_rutaNueva.append(copy.copy(A_RutaOriginal[x]))
            rutaNueva.setV(copy.deepcopy(V_RutaOriginal))
            rutaNueva.setA(copy.deepcopy(A_RutaOriginal))
            aux.rutas.append(rutaNueva)
            aux.rutas[r].dictAristasRuta = copy.copy(rutaOriginal.dictAristasRuta)
        
        return aux
    
    def contieneArista(self, a):
        for r in self.rutas:
            if(r.estaAristaEnRuta(a)):
                return True 
        return False

    def buscarAristaEnSolucion(self, a):
        for r in self.rutas:
            buscado = r.buscarAristaEnRuta(a)
            if(not buscado is None):
                return buscado 
        return None

    def __eq__(self, otro):
        return (self.costoTotal == otro.costoTotal and self.__class__ == otro.__class__)
    def __ne__(self, otro):
        return (self.costoTotal != otro.costoTotal and self.__class__ == otro.__class__)
    def __gt__(self, otro):
        return self.costoTotal > otro.costoTotal
    def __lt__(self, otro):
        return self.costoTotal < otro.costoTotal
    def __ge__(self, otro):
        return self.costoTotal >= otro.costoTotal
    def __le__(self, otro):
        return self.costoTotal <= otro.costoTotal
    # def __len__(self):
    #     return len(self._V)
    def setCapacidadMax(self, capMax):
        self.capacidadMax = capMax
    def setCapacidad(self, capacidad):
        self.capacidad = capacidad
    def getCapacidad(self):
        return self.capacidad
    def getCapacidadMax(self):
        return self.capacidadMax
    
    def setCostoTotal(self, c=None):
        if c is None:
            suma = 0
            for r in self.rutas:
                suma+=r.getCostoAsociado()
            self.costoTotal = suma
        else:
            self.costoTotal = c
    
    def getCostoTotal(self):
        return self.costoTotal

    def getGrado(self):
        return len(self._matrizDistancias)

    def getRutas(self):
        return self.rutas

    #Longitud que debería tener cada solucion por cada vehiculo
    def longitudSoluciones(self, length, nroVehiculos):
        if(nroVehiculos == 0):
            return length
        length = (length/nroVehiculos)
        decimales = math.modf(length)[0]
        if decimales < 5.0:
            length = int(length)
        else:
            length = int(length)+1
        return length

    #Rutas iniciales o la primera solucion
    def rutasIniciales(self, strSolInicial):
        rutas = []
        sol_factible = False
        while(not sol_factible):
            rutas = []
            if(strSolInicial==0):
                self.clarkWright()
                print("Solucion inicial con Clark & Wright")
                sol_factible = True
            elif(strSolInicial==1):
                print("Sol Inicial por Vecino Cercano")
                sol_factible = self.solInicial_VecinoCercano()
                strSolInicial = 3
            elif(strSolInicial == 2):
                secuenciaInd = list(range(1,len(self._matrizDistancias)))
                print("secuencia de indices de los vectores: "+str(secuenciaInd))
                self.cargar_secuencia(secuenciaInd)
            else:
                print("Sol Inicial al azar")
                secuenciaInd = list(range(1,len(self._matrizDistancias)))
                random.shuffle(secuenciaInd)
                self.cargar_secuencia(secuenciaInd)

        return rutas

    #
    def cargar_secuencia(self, secuencia):
        secuenciaInd = secuencia
        sub_secuenciaInd = []
        
        for i in range(0,self.nroVehiculos):
            rutas = self.rutas
            #Sin contar la vuelta (x,1)
            #nroVehiculos = 3
            #[1,2,3,4,5,6,7,8,9,10] Lo ideal seria: [1,2,3,4] - [1,5,6,7] - [1,8,9,10]
            sub_secuenciaInd = self.solucion_secuencia(secuenciaInd)
            S = Ruta(self._matrizDistancias, self.demanda, self.capacidadMax)
            S.setCapacidadMax(self.capacidad)
            cap = S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+sub_secuenciaInd, True))
            S.setCapacidad(cap)
            rutas.append(S)
            secuenciaInd = [x for x in secuenciaInd if x not in set(sub_secuenciaInd)]
            i
        if len(secuenciaInd) > 0:
            print("La solucion inicial no es factible. Implementar luego....")
            return False
        else:
            return True

    #secuenciaInd: secuencia de Indices
    #capacidad: capacidad maxima de los vehiculos
    #demanda: demanda de cada cliente
    def solucion_secuencia(self, secuenciaInd):
        acum_demanda = 0
        sub_secuenciaInd = []
        demandas = self.demanda
        nroVehiculos = self.nroVehiculos
        for x in secuenciaInd:
            value = self.getV()[x].getValue()-1
            if(acum_demanda + demandas[value] <= self.capacidadMax):
                acum_demanda += demandas[value]
                sub_secuenciaInd.append(x)
                #if (acum_demanda > self.__capacidad/nroVehiculos):
                #    break
        
        return sub_secuenciaInd

    def solInicial_VecinoCercano(self):
        visitados = []
        recorrido = []
        visitados.append(0)    #Agrego el vertice inicial
        
        for j in range(0, self.nroVehiculos):
            recorrido = []
            demanda = self.demanda
            nroVehiculos = self.nroVehiculos
            capacidad = self.capacidad
            rutas = self.rutas
            masCercano=0
            acum_demanda = 0
            for i in range(0,len(self._matrizDistancias)):
                masCercano = self.vecinoMasCercano(masCercano, visitados, acum_demanda, demanda, capacidad) #obtiene la posicion dela matriz del vecino mas cercano
                if(masCercano != 0):
                    acum_demanda += demanda[masCercano]
                    recorrido.append(masCercano)
                    visitados.append(masCercano)
                if(acum_demanda > self.capacidad/nroVehiculos):
                    break
                i
            j
            S = Ruta(self._matrizDistancias, self._demanda, 0)
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+recorrido, True))
            S.setCapacidad(acum_demanda)
            S.setCapacidadMax(capacidad)
            rutas.append(S)
        if(len(visitados)<len(self.getV())):
            #V = np.arange(0, len(self.getV()))
            #noVisitados = [x for x in V if x not in V]
            print("Solucion no factible. Repetimos proceso con otra solucion inicial")
            return False
        else:
            return True

    def vecinoMasCercano(self, pos, visitados, acum_demanda, demanda, capacidad):
        masCercano = self._matrizDistancias[pos][pos]
        indMasCercano = 0
    
        for i in range(0, len(self._matrizDistancias)):
            costo = self._matrizDistancias[pos][i]
            if(costo<masCercano and i not in visitados and demanda[i]+acum_demanda <= capacidad):
                masCercano = costo
                indMasCercano = i
        
        return indMasCercano

    #Cargar rutas de Clark y Wright
    def cargarRutas(self, rutas, capacidad):
        self.rutas = []
        # for i in range(0,len(rutas)):
        #     print("R #%d: %s" %(i, str(rutas[i])))
        for r in rutas:
            S = Ruta(self._matrizDistancias, self.demanda, 0,self.dictA)
            cap = S.cargarDesdeSecuenciaDeVertices(S.cargaVertices(r, False))
            S.setCapacidad(cap)
            S.setCapacidadMax(capacidad)
            self.rutas.append(S)
        
        self.setCostoTotal()
        # for i in range(0,len(rutas)):
        #     print("R #%d: %s" %(i, str(R[i].getV())))


    def mezclarRuta(self,r1,r2,rutas):
        #r1 y r2 son índices de las rutas.
        rutas[r1] = rutas[r1] + rutas[r2][1:]
        
    def obtenerAhorros(self):
        M = self._matrizDistancias
        ahorros = []
        for i in range(1,len(M)-1):
            for j in range(i+1,len(M)):
                s = M[i][0]+ M[0][j]-M[i][j] 
                s = round(s,3)
                t = (i+1,j+1,s)
                ahorros.append(t)
        ahorros = sorted(ahorros, key=lambda x: x[2], reverse=True)
        return ahorros

    #_lambda varía entre [0.1,2] 
    #mu y ni varían entre [0,2]
    def obtenerAhorrosOncan(self,_lambda, mu,ni):
        M = self._matrizDistancias
        D = self.demanda
        avgD = sum(D)/len(D)
        ahorros = []
        for i in range(1,len(M)-1):
            for j in range(i+1,len(M)):
                s = M[i][0]+ M[0][j]- _lambda*M[i][j] + mu * abs(M[i][0]-M[0][j]) + ni * ((D[i]-D[j])/avgD)
                s = round(s,3)
                t = (i+1,j+1,s)
                ahorros.append(t)
        ahorros = sorted(ahorros, key=lambda x: x[2], reverse=True)
        return ahorros
    
    def removerAhorros(self,lista,i,c):
        ret = [x for x in lista if x[i]!=c]
        return ret

    def buscar(self,v1,rutas):
        c = 0 #Indice cliente en ruta r
        r = 0 #Indice ruta
        cond = True
        while(r<len(rutas) and cond):
            if(v1 in rutas[r]):
                cond = False
                c=rutas[r].index(v1)
            else:
                r+=1
        return (r,c)  

    def esInterno(self, c,ruta):
        if c in ruta:  
            posicion = ruta.index(c)
            if(1 < posicion and posicion < len(ruta)-1):
                return True
            else:
                return False
        else:
            return False

    def estaEnUnRutaNoVacia(self,v1,rutas):
        return len(rutas[v1])>2 

    def cargaTotal(self, dem,ruta):
        suma = 0
        for r in ruta:
            suma += dem[r-1]
        self.capacidad = suma
        return suma

    def removeRuta(self,index,rutas):
        rutas.pop(index) 

    def clarkWright(self):
        _lambda = 1
        mu = 0
        ni = 0
        t = time()

        sol_factible = False
        iteracion = 0
        while(not sol_factible):
            ahorros = self.obtenerAhorrosOncan(_lambda,mu,ni)
            # ahorros = self.obtenerAhorros()
            nroVehiculos = self.nroVehiculos 
            dem = self.demanda
            rutas = []
            for i in range(2,self.getGrado()+1):
                R = []
                R.append(1)
                R.append(i)
                rutas.append(R)
            while(len(ahorros)>0):

                mejorAhorro = ahorros.pop(0)
                capacidadMax = self.capacidadMax
                i = self.buscar(mejorAhorro[0],rutas) # i = (r1,c1) índice de la ruta en la que se encuentra 
                j = self.buscar(mejorAhorro[1],rutas) # igual que i
                IesInterno = self.esInterno(mejorAhorro[0],rutas[i[0]])
                JesInterno = self.esInterno(mejorAhorro[1],rutas[j[0]])
                demCliente = dem[mejorAhorro[1]-1]

                if (len(rutas[i[0]]) == 2 and len(rutas[j[0]]) == 2) or (self.estaEnUnRutaNoVacia(i[0],rutas) and not IesInterno and self.estaEnUnRutaNoVacia(j[0],rutas) and not JesInterno and i[0]!=j[0]):
                    carga1 = self.cargaTotal(dem,rutas[i[0]])
                    carga2 = self.cargaTotal(dem,rutas[j[0]])
                    if(carga1 + carga2 <= capacidadMax):
                        self.mezclarRuta(i[0],j[0],rutas)
                        self.removeRuta(j[0],rutas)
                else: 
                    if(self.estaEnUnRutaNoVacia(i[0],rutas) and not self.estaEnUnRutaNoVacia(j[0],rutas) and not IesInterno):
                        demCliente = dem[mejorAhorro[1]-1]
                        cargaRuta = self.cargaTotal(dem,rutas[i[0]])
                        if(cargaRuta+demCliente <= capacidadMax):
                            ind = rutas[i[0]].index(mejorAhorro[0])
                            rutas[i[0]].insert(ind+1,mejorAhorro[1])
                            self.removeRuta(j[0],rutas)
                            i = self.buscar(mejorAhorro[0],rutas)
                            IesInterno = self.esInterno(mejorAhorro[0],rutas[i[0]])
                            JesInterno = self.esInterno(mejorAhorro[1],rutas[i[0]])
                    elif(self.estaEnUnRutaNoVacia(j[0],rutas) and  not self.estaEnUnRutaNoVacia(i[0],rutas) and not JesInterno):
                        demCliente = dem[mejorAhorro[0]-1]
                        cargaRuta = self.cargaTotal(dem,rutas[j[0]])
                        if(cargaRuta+demCliente <= capacidadMax):
                            if(j[1]==1):
                                rutas[j[0]].insert(1,mejorAhorro[0])
                            else:
                                ind = rutas[j[0]].index(mejorAhorro[1])
                                rutas[j[0]].insert(ind+1,mejorAhorro[0])
                            self.removeRuta(i[0],rutas)
                            j = self.buscar(mejorAhorro[1],rutas)
                            JesInterno = self.esInterno(mejorAhorro[0],rutas[j[0]])
                            IesInterno = self.esInterno(mejorAhorro[1],[j[0]])
            if(len(rutas)==self.nroVehiculos):
                sol_factible = True
            else:
                if(iteracion == 0):
                    _lambda = 0.1 
                    mu = 2
                    ni = 2 
                else:
                    _lambda += 0.1
                    mu -= 0.1
                    ni -= 0.1
            iteracion +=1
            print(len(rutas))

        self.cargarRutas(rutas,dem)
        print(time()-t)
        print(self)
        print("Terminó")

    def swap(self, k_Opt, aristaIni, indRutas, indAristas):

        print("ANTES DE SWAP", self)

        if(k_Opt[0] == 2):
            opcion = k_Opt[1]
            self.swap_2opt(aristaIni, indRutas, indAristas, opcion)
        elif(k_Opt[0] == 3):
            opcion = k_Opt[1]
            self.swap_3opt(aristaIni, indRutas, indAristas, opcion)
        else:
            opcion = k_Opt[1]
            self.swap_4optv2(aristaIni, indRutas, indAristas, opcion)

        
        print(aristaIni)
        print(f"Swap  {k_Opt[0]} opcion {k_Opt[1]}")


        print(self)
        print("\n")


    def getPosiciones(self, V_origen, V_destino):
        ind_verticeOrigen = -1
        ind_verticeDestino = -1
        ind_rutaOrigen = -1
        ind_rutaDestino = -1
        
        rutas = self.rutas
        #arista_azar = (3,7)    => V_origen = 3 y V_destino = 7
        #r: 1-2-3-4-5                r2: 1-6-7-8-9-10   
        #  (1,2)(2,3)(3,4)(4,5)(5,1)   (1,6)(6,7)(7,8)(8,9)(9,10)(10,1)
        #ind_VertOrigen = 2     ind_VertDest = 1
        for i in range(0,len(rutas)):
            for j in range(0, len(rutas[i].getV())):
                v = rutas[i].getV()[j]
                if (V_origen == v):
                    ind_verticeOrigen = j
                    ind_rutaOrigen = i
                elif (V_destino == v):
                    ind_verticeDestino = j-1
                    ind_rutaDestino = i
                if (ind_verticeOrigen != -1 and ind_verticeDestino != -1):
                    break
            if (ind_rutaOrigen != -1 and ind_rutaDestino != -1):
                if (ind_rutaOrigen == ind_rutaDestino and ind_verticeOrigen > ind_verticeDestino):
                    ind = ind_verticeOrigen
                    ind_verticeOrigen = ind_verticeDestino + 1
                    ind_verticeDestino = ind - 1
                break
        if(len(rutas)==0):
            print("Error en getPosiciones\n"+str(rutas))

        return [ind_rutaOrigen, ind_rutaDestino],[ind_verticeOrigen, ind_verticeDestino]

    def evaluarOpt(self, lista_permitidos, ind_permitidos, ind_random):
        kOpt = 0            #2, 3 o 4-opt
        tipo_kOpt = 0       #Las variantes de cada opt's anteriores
        costoSolucion = float("inf")
        nuevoCosto = float("inf")
        indRutas = indAristas = []
        DROP_2opt = DROP_3opt = DROP_4opt = []
        indDROP_2opt = indDROP_3opt = indDROP_4opt = []
        ADD = DROP = []
        indDROP = indADD = []
        while(costoSolucion == float("inf") and ind_random!=[]):
            ind = ind_random[-1]
            ind_random = ind_random[:-1]
            aristaIni = lista_permitidos[ind_permitidos[ind]]
            V_origen = aristaIni.getOrigen()
            V_destino = aristaIni.getDestino()
            ADD = []
            ADD.append(aristaIni)
            indADD = []
            indADD.append(aristaIni.getId())
            
            indRutas, indAristas = self.getPosiciones(V_origen, V_destino)
            indR = [indRutas[0], indRutas[1]]
            indA = [indAristas[0], indAristas[1]]
            #tiempo = time()
            # nuevoCosto, tipo_2opt, DROP_2opt, indDROP_2opt = self.evaluar_2opt(aristaIni, indR, indA)
            # #print("Tiempo eval2opt: "+str(time()-tiempo))
            # if(nuevoCosto < costoSolucion):
            #     costoSolucion = nuevoCosto
            #     kOpt = 2
            #     tipo_kOpt = tipo_2opt
            #     DROP = DROP_2opt
            #     indDROP = indDROP_2opt
                
            # indR = [indRutas[0], indRutas[1]]
            # indA = [indAristas[0], indAristas[1]]
            # #tiempo = time()
            # nuevoCosto, tipo_3opt, DROP_3opt, indDROP_3opt = self.evaluar_3opt(aristaIni, indR, indA)
            # #print("Tiempo eval3opt: "+str(time()-tiempo))
            # if(nuevoCosto < costoSolucion):
            #     costoSolucion = nuevoCosto
            #     kOpt = 3
            #     tipo_kOpt = tipo_3opt
            #     DROP = DROP_3opt
            #     indDROP = indDROP_3opt 
            
            
            indR = [indRutas[0], indRutas[1]]
            indA = [indAristas[0], indAristas[1]]
            nuevoCosto, tipo_4opt, DROP_4opt, indDROP_4opt = self.evaluar_4optv2(aristaIni, indR, indA)
            if(nuevoCosto < costoSolucion):
                costoSolucion = nuevoCosto
                kOpt = 4
                tipo_kOpt = tipo_4opt
                DROP = DROP_4opt
                indDROP = indDROP_4opt
      
            
        #tiempo = time()
        if(costoSolucion != float("inf")):
            # print("\n%d-opt   Opcion: %d" %(kOpt, tipo_kOpt))
            # print("ADD: "+str(ADD))
            # print("DROP: "+str(DROP)+"\n")
            index = [i for i in range(0,len(ind_permitidos)) if ind_permitidos[i] in indDROP or ind_permitidos[i] in indADD]
            ind_permitidos = np.delete(ind_permitidos, index)
        else:
            # print("ind_random: "+str(ind_random))
            # print("ind_permitidos: "+str(ind_permitidos))
            # print("No se encontro una sol factible")
            ADD = DROP = []
        #print("Tiempo: "+str(time()-tiempo))
        
        return costoSolucion, [kOpt, tipo_kOpt], indRutas, indAristas, ADD, DROP
    
    """
    2-opt:
    new_cost = costoSolucion + costo(a,b) + costo(8,4) - costo(a,4) - costo(8,b)
    r1: 1-2-3-a-4-5         r2: 1-6-7-b-8-9-10   -> ruta original
    resultado:
    r1: 1-2-3-a-b-8-9-10    r2: 1-6-7-4-5        -> 1ra opcion
    r1: 1-6-7-b-8-9-10      r2: 1-2-3-a-4-5      -> ruta original invertida
    r1: 1-2-3-8-9-10        r2: 1-6-7-b-a-4-5    -> 2da opcion
    r1: 1-5-4-a-b-8-9-10    r2: 1-2-3-7-6        -> 3ra opcion PENDIENTE 

    r: 1,2,a,3,4,b,5,6     -> ruta original 
    resultado:
    r: 1,2,a,b,4,3,5,6     -> 1ra opcion
    r: 1,6,5,b,a,3,4,2     -> 2da opcion
    1,2,4,3,a,b,5,6
    """
    def swap_2opt(self, arista_ini, ind_rutas, ind_A, opcion):
        costoSolucion = self.getCostoTotal()
        ADD = []
        DROP = []
        ADD.append(arista_ini)
        rutas = self.rutas
        #En distintas rutas(opcion = 0 -> 1ra opcion sino 2da opcion)
        if(opcion==1 or opcion==2):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            A_r1 = r1.getA()
            A_r2 = r2.getA()
            if(opcion==1):
                A_r1_left = A_r1[:ind_A[0]]
                A_r1_right = A_r1[ind_A[0]+1:]
                A_r1_drop = A_r1[ind_A[0]]
                        
                A_r2_left = A_r2[:ind_A[1]]
                A_r2_right = A_r2[ind_A[1]+1:]                
                A_r2_drop = A_r2[ind_A[1]]

                if(A_r2_left!=[]):
                    V_origen = A_r2_left[-1].getDestino()
                #vertice 'a' de la arista (a,b) se encuentra al principio
                else:
                    V_origen = Vertice(1,0)    

                #vertice 'b' de la arista (a,b) no se encuentra al final
                if(A_r1_right!=[]):
                    V_destino = A_r1_right[0].getOrigen()
                #vertice 'b' de la arista (a,b) no se encuentra al final
                else:
                    V_destino = Vertice(1,0)
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add = Arista(V_origen,V_destino, peso)   # => (6,4, peso)
                #print("A_r2_add"+str(A_r2_add))
                A_r_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                ADD = []
                ADD.append(arista_ini)                

                if(A_r1_left!=[] and A_r1_left[-1].getDestino()!=arista_ini.getOrigen()):
                    arista_ini.invertir()
                
                A_r1_left.append(arista_ini)
                A_r1_left.extend(A_r2_right)
                A_r2_left.append(A_r_add)
                A_r2_left.extend(A_r1_right)

            else:
                A_r1_left = A_r1[:ind_A[0]-1]
                A_r1_right = A_r1[ind_A[0]:]
                A_r1_drop = A_r1[ind_A[0]-1]
                        
                A_r2_left = A_r2[:ind_A[1]+1]
                A_r2_right = A_r2[ind_A[1]+2:]                
                A_r2_drop = A_r2[ind_A[1]+1]

                if(arista_ini.getDestino() == A_r1_drop.getDestino()):
                    arista_ini.invertir()
                
                if(A_r1_left!=[]):
                    V_origen = A_r1_left[-1].getDestino()
                #En caso de que la arista al azar se encuentra al principio
                else:
                    V_origen = Vertice(1,0)
                
                if(A_r2_right!=[]):
                    V_destino = A_r2_right[0].getOrigen()
                #En caso de que la arista al azar se encuentra al final
                else:
                    V_destino = Vertice(1,0)
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add = Arista(V_origen,V_destino, peso)   # => (6,4, peso)
                A_r_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                if(A_r_add.getDestino() != arista_ini.getOrigen()):
                    arista_ini.invertir()
                
                A_r1_left.append(A_r_add)
                #print("A_r1_left: "+str(A_r1_left))
                A_r1_left.extend(A_r2_right)
                #print("A_r1_left: "+str(A_r1_left))
                A_r2_left.append(arista_ini)
                #print("A_r2_left: "+str(A_r2_left))
                A_r2_left.extend(A_r1_right)
                #print("A_r2_left: "+str(A_r2_left))
        
            costoSolucion -= r1.getCostoAsociado() + r2.getCostoAsociado()

            # ADD = []
            # ADD.append(arista_ini)
            # ADD.append(A_r_add)
            # DROP.append(A_r1_drop)
            # DROP.append(A_r2_drop)

            r1.cargarDesdeAristas(A_r1_left)
            r2.cargarDesdeAristas(A_r2_left)

            costoSolucion += r1.getCostoAsociado() + r2.getCostoAsociado()
        #En la misma ruta
        else:
            r = rutas[ind_rutas[0]]
            costoSolucion -= r.getCostoAsociado()
            V_r = r.getV()
            V_r.append(Vertice(1,0))
            
            if(opcion == -2):
                V_r = V_r[::-1]
                lenV = len(V_r) - 2
                ind_b = lenV - ind_A[1]
                ind_a = lenV - ind_A[0]
                ind_A = [ind_b, ind_a]
                ADD = []
                arista_ini.invertir()
                ADD.append(arista_ini)
            
            V_r_left = V_r[:ind_A[0]+1]
            V_r_middle = V_r[ind_A[0]+1:ind_A[1]+1]
            V_r_middle = V_r_middle[::-1]
            V_r_right = V_r[ind_A[1]+2:]
        
            try:
                A_r_drop1 = r.getA()[ind_A[0]]
                A_r_drop2 = r.getA()[ind_A[1]+1]
            except IndexError:
                print("r: "+str(r.getA()))
                print("aristaIni: "+str(arista_ini))
                print("ind_A: "+str(ind_A))
                a = 1/0
            V_origen = V_r_middle[-1]
            V_destino = V_r_right[0]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add = Arista(V_origen,V_destino, peso)
            A_r_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

            ADD.append(A_r_add)              
            DROP.append(A_r_drop1)
            DROP.append(A_r_drop2)
            
            V_r_left.append(V_r[ind_A[1]+1])
            V_r_left.extend(V_r_middle)
            V_r_left.extend(V_r_right)
            V_r = V_r_left[:-1]
            
            r.cargarDesdeSecuenciaDeVertices(V_r)
            costoSolucion += r.getCostoAsociado()


        if(self.controlarCapacidad(ind_rutas[0])):
            print("---------------------------------------------------EXCEDIÓ CAPACIDAD R1---------------------------------")
        if(self.controlarCapacidad(ind_rutas[1])):
            print("---------------------------------------------------EXCEDIÓ CAPACIDAD R2---------------------------------")



        self.setCostoTotal(costoSolucion)

    
    #Distintas rutas. opcion = 1 (1ra opcion); opcion(=2)  - Misma ruta: 1ra opcion(-1) = -2 --> Misma ruta(2da opcion)
    def evaluar_2opt(self, aristaIni, ind_rutas, ind_A):
        opcion = 0
        costo_solucion = float("inf")
        costo_r_add1 = aristaIni.getPeso()
        
        DROP = []
        index_DROP = []
        rutas = self.rutas
        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            A_r1 = r1.getA()
            A_r2 = r2.getA()
            
            for i in range(1,3):
                if(len(r1.getV())-1 == ind_A[0] or len(r2.getV())-1 == ind_A[1]+1):
                    continue

                if(i==2):
                    #print("2da opcion")            
                    r1 = rutas[ind_rutas[1]]
                    r2 = rutas[ind_rutas[0]]
                    a = copy.copy(A_r1)
                    A_r1 = A_r2
                    A_r2 = a
                    j = ind_A[0]
                    ind_A[0] = ind_A[1] +1          #=> La posicion de 'a' es en donde la arista tiene como origen 'a' (+1)
                    ind_A[1] = j -1             	#=> La posicion de 'b' es en donde la arista tiene como destino 'b'(-1)
                
                    A_r1_right = A_r1[ind_A[0]+1:]
                    A_r2_left = A_r2[:ind_A[1]]
                    
                    #Caso no factible por ej:
                    #r1: 1-2-3-4-5-a    r2: 1-b-6-7-8-9-10  -> Sol: r1: 1-2-3-4-5-a-b-6-7-8-9-10    r2: 1
                    if(A_r1_right==[] and A_r2_left==[] and opcion == 1):
                        continue
                    
                    r1DemandaAcumulada = r1.getDemandaAcumulada()
                    r2DemandaAcumulada = r2.getDemandaAcumulada()
                    
                    cap_r1_left = r1DemandaAcumulada[ind_A[0]]
                    cap_r1_right = r1DemandaAcumulada[-1] - cap_r1_left
                    
                    cap_r2_left = r2DemandaAcumulada[ind_A[1]]
                    cap_r2_right = r2DemandaAcumulada[-1] - cap_r2_left
                    
                    cap_r1 = cap_r1_left + cap_r2_right
                    cap_r2 = cap_r2_left + cap_r1_right
                    
                    if(cap_r1 > self.capacidadMax or cap_r2 > self.capacidadMax):
                        continue
                    
                    A_r1_drop = A_r1[ind_A[0]]
                    A_r2_drop = A_r2[ind_A[1]]
                    
                    if(A_r2_left!=[]):
                        V_origen = A_r2_left[-1].getDestino()
                    #vertice 'a' de la arista (a,b) se encuentra al principio
                    else:
                        V_origen = Vertice(1,0)
                    
                    #vertice 'b' de la arista (a,b) no se encuentra al final
                    if(A_r1_right!=[]):
                        V_destino = A_r1_right[0].getOrigen()
                    #vertice 'b' de la arista (a,b) no se encuentra al final
                    else:
                        V_destino = Vertice(1,0)
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r2_add = Arista(V_origen,V_destino, peso)   # => (6,4, peso)
                    #print("A_r2_add"+str(A_r2_add))
                    costo_r2_add = peso
                    A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                else:
                    A_r1_right = A_r1[ind_A[0]+1:]
                    A_r2_left = A_r2[:ind_A[1]]

                    A_r1_drop = A_r1[ind_A[0]]
                    A_r2_drop = A_r2[ind_A[1]]

                    #Caso no factible por ej:
                    #r1: 1-2-3-4-5-a    r2: 1-b-6-7-8-9-10  -> Sol: r1: 1-2-3-4-5-a-b-6-7-8-9-10    r2: 1
                    if(A_r1_right==[] and A_r2_left==[] and opcion == 1):
                        continue
                    
                    r1DemandaAcumulada = r1.getDemandaAcumulada()
                    r2DemandaAcumulada = r2.getDemandaAcumulada()
                    
                    cap_r1_left = r1DemandaAcumulada[ind_A[0]]
                    cap_r1_right = r1DemandaAcumulada[-1] - cap_r1_left
                    
                    cap_r2_left = r2DemandaAcumulada[ind_A[1]]
                    cap_r2_right = r2DemandaAcumulada[-1] - cap_r2_left
                    
                    cap_r1 = cap_r1_left + cap_r2_right
                    cap_r2 = cap_r2_left + cap_r1_right
                    
                    if(cap_r1 > self.capacidadMax or cap_r2 > self.capacidadMax):
                        continue
                                        
                    if(A_r2_left!=[]):
                        V_origen = A_r2_left[-1].getDestino()
                    #vertice 'a' de la arista (a,b) se encuentra al principio
                    else:
                        V_origen = Vertice(1,0)
                    
                    #vertice 'b' de la arista (a,b) no se encuentra al final
                    if(A_r1_right!=[]):
                        V_destino = A_r1_right[0].getOrigen()
                    #vertice 'b' de la arista (a,b) no se encuentra al final
                    else:
                        V_destino = Vertice(1,0)
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r2_add = Arista(V_origen,V_destino, peso)   # => (6,4, peso)
                    #print("A_r2_add"+str(A_r2_add))
                    costo_r2_add = peso
                    A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    #cap_r_add = V_origen.getDemanda() + V_destino.getDemanda()
                    
                    #r1:  1 - 2 - 3 - a - 4 - 5
                    #     10  20  35  55  60  90    -> cap=90
                    #left:1 - 2 - 3 - a      right: 4 - 5
                    #     10  20  35  55            5   35
                    #r2:  1 - 6 - 7 - b - 8 - 9 - 10
                    #     15  30  45  65  80  90  95 -> cap=95
                    #left:1 - 6 - 7          right: 8 - 9 - 10
                    #     15  30  45                15  25  30  
                    
                costo_r1_drop = A_r1_drop.getPeso()
                costo_r2_drop = A_r2_drop.getPeso()

                nuevo_costo = self.getCostoTotal() + costo_r_add1 + costo_r2_add - costo_r1_drop - costo_r2_drop
                
                if(nuevo_costo < costo_solucion):
                    costo_solucion = nuevo_costo
                    opcion = i
                    DROP = []
                    DROP.append(A_r1_drop)
                    DROP.append(A_r2_drop)
                    index_DROP = []
                    index_DROP.append(A_r1_drop.getId())
                    index_DROP.append(A_r2_drop.getId())
                    ADD = []
                    ADD.append(A_r2_add)
                    index_ADD = []
                    index_ADD.append(A_r2_add.getId())
        else:
            #En la misma ruta hay factibilidad, por lo tanto se calcula unicamente el costo
            r = rutas[ind_rutas[0]]
            V_r = r.getV()
            V_r.append(Vertice(1,0))
            A_r = r.getA()
            #r: 1,2,a,3,4,b,5,6,1     -> Ruta original
            #Sol:
            #r: 1,2,a,b,4,3,5,6,1     -> 1ra opcion
            #r: 1,2,4,3,a,b,5,6,1     -> 2da opcion
            #r: 1,6,5,b,a,3,4,2,1     -> 2da opcion
            for i in range(1,3):
                if(i==2):
                    if(0 in ind_A):
                        # a = 1
                        #r: a,2,3,4,5,b,6,1     -> Ruta original
                        #r: a,b,5,4,3,2,6,1     -> 1ra opcion        
                        #r: 1,6,b,5,4,3,2,a     -> Ruta original invertida
                        #r: 1,6,b,a,2,3,4,5     -> 2da opcion. No se puede xq a = 1        
                        # a o b no pueden ser igual a 1 para la segunda opcion
                        continue
                    
                    A_r_drop1 = A_r[ind_A[0]-1]
                    costo_r_drop1 = A_r_drop1.getPeso()
                    A_r_drop2 = A_r[ind_A[1]]
                    costo_r_drop2 = A_r_drop2.getPeso()
                    
                    V_origen = A_r_drop1.getOrigen()
                    V_destino = A_r_drop2.getOrigen()
                    costo_r_add2 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add2 = Arista(V_origen,V_destino, costo_r_add2)
                else:
                    A_r_drop1 = A_r[ind_A[0]]
                    costo_r_drop1 = A_r_drop1.getPeso()
                    A_r_drop2 = A_r[ind_A[1]+1]
                    costo_r_drop2 = A_r_drop2.getPeso()
                    
                    V_origen = V_r[ind_A[0]+1]
                    V_destino = V_r[ind_A[1]+2]
                    costo_r_add2 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add2 = Arista(V_origen,V_destino, costo_r_add2)
                    
                nuevo_costo = self.getCostoTotal() + costo_r_add1 + costo_r_add2 - costo_r_drop1 - costo_r_drop2
                
                if(nuevo_costo < costo_solucion):
                    costo_solucion = nuevo_costo
                    opcion = i*(-1)
                    DROP = []
                    DROP.append(A_r_drop1)
                    DROP.append(A_r_drop2)
                    index_DROP = []
                    index_DROP.append(A_r_drop1.getId())
                    index_DROP.append(A_r_drop2.getId())
                    ADD = []
                    ADD.append(A_r_add2)
                    index_ADD = []
                    index_ADD.append(A_r_add2.getId())
            
            V_r = V_r[:-1]
            r.setV(V_r)
            

        
        return costo_solucion, opcion, DROP, index_DROP            

    """
    costoSolucion = 300
    new_cost = costoSolucion + costo(a,b) + costo(b,4) + costo(8,9) - costo(a,4) - costo(8,b) - costo(b,9) 
    3-opt
    r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10,11,12
    resultado:
    r1: 1,2,3,a,b,4,5,6          r2: 1,7,8,9,10,11,12       -> 1ra opcion
    r1: 1,2,3,b,a,4,5,6          r2: 1,7,8,9,10,11,12       -> 2da opcion PENDIENTE
    r1: 1,2,3,4,5,6              r2: 1,7,8,a,b,9,10,11,12   -> 3ra opcion PENDIENTE
    r1: 1,2,3,4,5,6              r2: 1,7,8,b,a,9,10,11,12   -> 4ta opcion PENDIENTE
    r: 1,2,a,3,4,5,b,6,7,8      -> ruta original 
    r: 1,2,a,b,3,4,5,6,7,8      -> 1ra opcion
    r: 1,2,b,a,3,4,5,6,7,8      -> 2da opcion
    r: 1,2,3,4,5,b,a,6,7,8      -> 3ra opcion
    r: 1,2,3,4,5,a,b,6,7,8      -> 4ta opcion
    """
    """
    costoSolucion = 300
    new_cost = costoSolucion + costo(a,b) + costo(b,4) + costo(8,9) - costo(a,4) - costo(8,b) - costo(b,9) 
    3-opt
    r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10,11,12
    resultado:
    r1: 1,2,3,a,b,4,5,6          r2: 1,7,8,9,10,11,12       -> 1ra opcion
    r1: 1,2,3,b,a,4,5,6          r2: 1,7,8,9,10,11,12       -> 2da opcion PENDIENTE
    r1: 1,2,3,4,5,6              r2: 1,7,8,a,b,9,10,11,12   -> 3ra opcion PENDIENTE
    r1: 1,2,3,4,5,6              r2: 1,7,8,b,a,9,10,11,12   -> 4ta opcion PENDIENTE
    r: 1,2,a,3,4,5,b,6,7,8      -> ruta original 
    r: 1,2,a,b,3,4,5,6,7,8      -> 1ra opcion
    r: 1,2,b,a,3,4,5,6,7,8      -> 2da opcion
    r: 1,2,3,4,5,b,a,6,7,8      -> 3ra opcion
    r: 1,2,3,4,5,a,b,6,7,8      -> 4ta opcion
    """
    def swap_3opt(self, arista_ini, ind_rutas, ind_A, opcion):
        costoSolucion = self.getCostoTotal()
        rutas = self.rutas
        if(opcion > 0):
            # r1: 1,2,3,a,4,5,6            r2: 1,7,8,b,9,10,11,12
            if(opcion == 3 or opcion == 4):
                # r1: 1,2,3,4,5,6              r2: 1,7,8,b,a,9,10,11,12   -> 3ra opcion
                # r1: 1,2,3,4,5,6              r2: 1,7,8,a,b,9,10,11,12   -> 4ta opcion
                r1 = rutas[ind_rutas[0]]
                r2 = rutas[ind_rutas[1]]
                #print("\nsol factible por 3-opt 3ra y 4ta opcion")
                A_r1_left = r1.getA()[:ind_A[0]-1]
                A_r1_right = r1.getA()[ind_A[0]+1:]
            else:
                #r1: 1,2,3,b,a,4,5,6          r2: 1,7,8,9,10,11,12       -> 1ra opcion
                #r1: 1,2,3,a,b,4,5,6          r2: 1,7,8,9,10,11,12       -> 2da opcion
                #print("\nsol factible por 3-opt 1ra y 2da opcion")
                r1 = rutas[ind_rutas[1]]
                r2 = rutas[ind_rutas[0]]
                i = ind_A[0]
                ind_A[0] = ind_A[1] + 1
                ind_A[1] = i - 1
                A_r1_left = r1.getA()[:ind_A[0]-1]
                A_r1_right = r1.getA()[ind_A[0]+1:]
            costoSolucion -= r1.getCostoAsociado() + r2.getCostoAsociado()

            #print("A_r1_left: "+str(A_r1_left))
            #print("A_r1_right: "+str(A_r1_right))
            
            #ADD
            V_origen = r1.getA()[ind_A[0]-1].getOrigen()
            V_destino = r1.getA()[ind_A[0]].getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r1_add = Arista(V_origen, V_destino, peso)
            #print("A_r1_add: "+str(A_r1_add))
            #costo_r1_add = peso

            if(opcion == 3 or opcion == 1):
                #print("Opcion 1 o 3")
                A_r2_left = r2.getA()[:ind_A[1]]
                A_r2_right = r2.getA()[ind_A[1]+1:]
                #print("A_r2_left: "+str(A_r2_left))
                #print("A_r2_right: "+str(A_r2_right))
                V_origen = r2.getA()[ind_A[1]].getOrigen()
                V_destino = r1.getA()[ind_A[0]-1].getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r2_add = Arista(V_origen, V_destino, peso)
                A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                #print("A_r2_add: "+str(A_r2_add))
                #costo_r2_add = peso
                A_r2_left.append(A_r2_add)
                if(opcion==1):
                    arista_ini.invertir()
                A_r2_left.append(arista_ini)
            else:
                #print("Opcion 2 o 4")
                A_r2_left = r2.getA()[:ind_A[1]+1]
                A_r2_right = r2.getA()[ind_A[1]+2:]
                #print("A_r2_left: "+str(A_r2_left))
                #print("A_r2_right: "+str(A_r2_right))
                V_origen = r1.getA()[ind_A[0]-1].getDestino()
                V_destino = r2.getA()[ind_A[1]+1].getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r2_add = Arista(V_origen, V_destino, peso)
                A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                #print("A_r2_add: "+str(A_r2_add))
                #costo_r2_add = peso
                if(opcion==4):
                    arista_ini.invertir()
                A_r2_left.append(arista_ini)
                A_r2_left.append(A_r2_add)
            A_r2_left.extend(A_r2_right)
            #print("A_r2: "+str(A_r2_left))            
            
            A_r1_left.append(A_r1_add)
            A_r1_left.extend(A_r1_right)
            #print("A_r1: "+str(A_r1_left))            
            #print("A_r2: "+str(A_r2_left))
            r1.cargarDesdeAristas(A_r1_left)
            r2.cargarDesdeAristas(A_r2_left)
            costoSolucion += r1.getCostoAsociado() + r2.getCostoAsociado()
            # print("Swap 3-opt")
            # print("cap r1: ",cap_r1)
            # print("r1: "+ str(r1.getV()) + "      -> costo: "+str(r1.getCostoAsociado()))
            # print("cap r2: ",cap_r2)
            # print("r2: "+ str(r2.getV()) + "      -> costo: "+str(r2.getCostoAsociado()))
        #3-opt en la misma ruta
        # r: 1,2,a,3,4,5,b,6,7,8      -> ruta original 
        # resultado:
        # r: 1,2,a,b,3,4,5,6,7,8      -> 1ra opcion
        # r: 1,2,b,a,3,4,5,6,7,8      -> 2da opcion
        # r: 1,2,3,4,5,b,a,6,7,8      -> 3ra opcion
        # r: 1,2,3,4,5,a,b,6,7,8      -> 4ta opcion
        else:
            #print("Misma ruta")
            r = rutas[ind_rutas[0]]
            costoSolucion -= r.getCostoAsociado()
            V_r = r.getV()
            V_r.append(Vertice(1,0))
            V_r_left = V_r[:ind_A[0]]
            V_r_middle = V_r[ind_A[0]+1:ind_A[1]+1]
            V_r_right = V_r[ind_A[1]+2:]
            #print("V_r_r: "+str(V_r_right))
            #print("V_r_m: "+str(V_r_middle))
            #print("V_r_l: "+str(V_r_left))
            
            # if(opcion == -1 or opcion == -2):
            #     #print("1ra opcion")
            #     #print("2da opcion")
            #     V_origen = V_r[ind_A[1]]
            #     V_destino = V_r[ind_A[1]+2]
            # elif(opcion == -3 or opcion == -4):
            #     #print("3ra y 4ta opcion")
            #     V_origen = V_r_left[-1]
            #     V_destino = V_r_middle[0]
            # peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            # A_r_add2 = Arista(V_origen,V_destino, peso)
            #A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            if(opcion == -1 or opcion == -4):
                V_origen = V_r[ind_A[0]]
                V_destino = V_r[ind_A[1]+1]
            elif(opcion == -2 or opcion == -3):
                V_origen = V_r[ind_A[1]+1]
                V_destino = V_r[ind_A[0]]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add1 = Arista(V_origen,V_destino, peso)
            A_r_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))               
            #print("A_r_add1: "+str(A_r_add1))
            #print("A_r_add2: "+str(A_r_add2))
            
            if(opcion == -1 or opcion == -2):
                V_r_left.append(A_r_add1.getOrigen())
                V_r_left.append(A_r_add1.getDestino())
                V_r_left.extend(V_r_middle)
                V_r_left.extend(V_r_right)
            else:
                V_r_left.extend(V_r_middle)
                V_r_left.append(A_r_add1.getOrigen())
                V_r_left.append(A_r_add1.getDestino())
                V_r_left.extend(V_r_right)
            
            V_r_left = V_r_left[:-1]
            #V_r = r.getV()
            #V_r = V_r[:-1]
            #r.setV(V_r)
            r.cargarDesdeSecuenciaDeVertices(V_r_left)
            costoSolucion += r.getCostoAsociado()

        if(self.controlarCapacidad(ind_rutas[0])):
            print("---------------------------------------------------EXCEDIÓ CAPACIDAD R1---------------------------------")
        if(self.controlarCapacidad(ind_rutas[1])):
            print("---------------------------------------------------EXCEDIÓ CAPACIDAD R2---------------------------------")

    
        self.setCostoTotal(costoSolucion)

    def evaluar_3opt(self, aristaIni, ind_rutas, ind_A):
        sol_factible_12 = sol_factible_34 = False
        #Opcion: 0 (1ra opcion) | 1 (2da opcion) | 3 (3ra opcion) | 4 (4ta opcion)
        #Misma ruta: -1(1ra opcion) | -2 (2da opcion) | -3 (3ra opcion) | -4 (4ta opcion)
        opcion = 0  
        costo_solucion = float("inf")
        costo_r_add1 = aristaIni.getPeso()

        DROP = []
        index_DROP = []

        rutas = self.rutas
        #3-opt Distintas rutas
        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]

            #Evaluar la factibilidad en las distintas opciones
            cap_r1 = r1.getCapacidad() + aristaIni.getDestino().getDemanda()
            if(cap_r1 <= self.capacidadMax):
                sol_factible_12 = True
            
            cap_r2 = r2.getCapacidad() + aristaIni.getOrigen().getDemanda()
            if(cap_r2 <= self.capacidadMax):
                sol_factible_34 = True
            
            # r1: 1,2,3,a,4,5,6            r2: 1,7,8,b,9,10,11,12
            # r1: 1,2,3,4,5,6              r2: 1,7,8,a,b,9,10,11,12   -> 3ra opcion
            # r1: 1,2,3,4,5,6              r2: 1,7,8,b,a,9,10,11,12   -> 4ta opcion    
            if(sol_factible_34):
                #print("\nsol factible por 3-opt 3ra y 4ta opcion")
                #A_r1_left = r1.getA()[:ind_A[0]-1]
                A_r1_right = r1.getA()[ind_A[0]+1:]
                #print("A_r1_left: "+str(A_r1_left))
                #print("A_r1_r: "+str(A_r1_right))
                
                #A_r2_left = r2.getA()[:ind_A[1]]
                A_r2_right = r2.getA()[ind_A[1]+1:]
                #print("A_r2_left: "+str(A_r2_left))
                #print("A_r2_right: "+str(A_r2_right)+"\n")
                for i in range(3,5):
                    if(i==4 and A_r2_right == []):
                        #print("4ta opcion no es posible")
                        continue
                    #Obtengo las aristas que se eliminan y las que se añaden
                    #DROP
                    A_r1_drop1 = r1.getA()[ind_A[0]-1]
                    costo_r1_drop1 = A_r1_drop1.getPeso()
                    
                    A_r1_drop2 = r1.getA()[ind_A[0]]
                    costo_r1_drop2 = A_r1_drop2.getPeso()
                    
                    #ADD
                    V_origen = r1.getA()[ind_A[0]-1].getOrigen()
                    V_destino = r1.getA()[ind_A[0]].getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r1_add = Arista(V_origen, V_destino, peso)
                    #print("A_r1_add: "+str(A_r1_add))
                    costo_r1_add = peso
                    A_r1_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    if(i==3):
                        A_r2_drop = r2.getA()[ind_A[1]]
                        costo_r2_drop = A_r2_drop.getPeso()
                    
                        V_origen = r2.getA()[ind_A[1]].getOrigen()
                        V_destino = r1.getA()[ind_A[0]-1].getDestino()
                        peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                        A_r2_add = Arista(V_origen, V_destino, peso)
                        A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                        costo_r2_add = peso
                    else:
                        A_r2_drop = r2.getA()[ind_A[1]+1]
                        costo_r2_drop = A_r2_drop.getPeso()
                    
                        V_origen = r1.getA()[ind_A[0]-1].getDestino()
                        V_destino = r2.getA()[ind_A[1]+1].getDestino()
                        peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                        A_r2_add = Arista(V_origen, V_destino, peso)
                        A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                        costo_r2_add = peso

                    nuevo_costo = self.getCostoTotal() + costo_r_add1 + costo_r1_add + costo_r2_add - costo_r1_drop1 - costo_r1_drop2 - costo_r2_drop
                    
                    if(nuevo_costo < costo_solucion):
                        costo_solucion = nuevo_costo
                        opcion = i
                        DROP = []
                        index_DROP = []
                        DROP.append(A_r1_drop1)
                        DROP.append(A_r1_drop2)
                        DROP.append(A_r2_drop)
                        index_DROP.append(A_r1_drop1.getId())
                        index_DROP.append(A_r1_drop2.getId())
                        index_DROP.append(A_r2_drop.getId())

            #r1: 1,2,3,a,4,5,6            r2: 1,7,8,b,9,10,11,12
            #r1: 1,2,3,b,a,4,5,6          r2: 1,7,8,9,10,11,12   -> 1ra opcion    
            #r1: 1,2,3,a,b,4,5,6          r2: 1,7,8,9,10,11,12   -> 2da opcion
            if(sol_factible_12):
                r1 = rutas[ind_rutas[1]]
                r2 = rutas[ind_rutas[0]]
                A_r1 = r1.getA()
                if(len(A_r1)<3):
                    #print("Sol no factible. No se cuenta con suficiente aristas para realizar el swap")
                    return costo_solucion, opcion, DROP, index_DROP        
                #print("Sol factible. 3-opt 1ra y 2da opcion")
                A_r2 = r2.getA()

                i = ind_A[0]
                ind_A[0] = ind_A[1] + 1
                ind_A[1] = i - 1
                #A_r1_left = A_r1[:ind_A[0]-1]
                A_r1_right = A_r1[ind_A[0]+1:]
                #print("A_r1_left: "+str(A_r1_left))
                #print("A_r1_r: "+str(A_r1_right))
                
                #A_r2_left = A_r2[:ind_A[1]]
                A_r2_right = A_r2[ind_A[1]+1:]
                #print("A_r2_left: "+str(A_r2_left))
                #print("A_r2_right: "+str(A_r2_right)+"\n")
                
                for i in range(1,3):
                    if(i==2 and A_r1_right == []):
                        #print("2da opcion no es posible")
                        continue
                    
                    #Obtengo las aristas que se eliminan y las que se añaden
                    #DROP
                    A_r1_drop1 = r1.getA()[ind_A[0]-1]
                    costo_r1_drop1 = A_r1_drop1.getPeso()
                    
                    A_r1_drop2 = r1.getA()[ind_A[0]]
                    costo_r1_drop2 = A_r1_drop2.getPeso()
                    
                    #ADD
                    V_origen = r1.getA()[ind_A[0]-1].getOrigen()
                    V_destino = r1.getA()[ind_A[0]].getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r1_add = Arista(V_origen, V_destino, peso)
                    #print("A_r1_add: "+str(A_r1_add))
                    costo_r1_add = peso
                    A_r1_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    if(i==1):
                        A_r2_drop = A_r2[ind_A[1]]
                        costo_r2_drop = A_r2_drop.getPeso()
                    
                        V_origen = A_r2[ind_A[1]].getOrigen()
                        V_destino = r1.getA()[ind_A[0]-1].getDestino()
                        peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                        A_r2_add = Arista(V_origen, V_destino, peso)
                        #print("A_r2_add: "+str(A_r2_add))
                        A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                        costo_r2_add = peso
                    else:
                        A_r2_drop = A_r2[ind_A[1]+1]
                        costo_r2_drop = A_r2_drop.getPeso()
                    
                        V_origen = r1.getA()[ind_A[0]-1].getDestino()
                        V_destino = A_r2[ind_A[1]+1].getDestino()
                        peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                        A_r2_add = Arista(V_origen, V_destino, peso)
                        A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                        #print("A_r2_add: "+str(A_r2_add))
                        costo_r2_add = peso

                    nuevo_costo = self.getCostoTotal() + costo_r_add1 + costo_r1_add + costo_r2_add - costo_r1_drop1 - costo_r1_drop2 - costo_r2_drop
                    #print("Nuevo costo: ", nuevo_costo)
                    if(nuevo_costo < costo_solucion):
                        costo_solucion = nuevo_costo
                        opcion = i
                        DROP = []
                        index_DROP = []
                        DROP.append(A_r1_drop1)
                        DROP.append(A_r1_drop2)
                        DROP.append(A_r2_drop)
                        index_DROP.append(A_r1_drop1.getId())
                        index_DROP.append(A_r1_drop2.getId())
                        index_DROP.append(A_r2_drop.getId())
                        #print("DROP: "+str(DROP))

        #3-opt en la misma ruta
        else:
            # r: 1,2,a,3,4,5,b,6,7,8      -> ruta original 
            # resultado:
            # r: 1,2,a,b,3,4,5,6,7,8      -> 1ra opcion
            # r: 1,2,b,a,3,4,5,6,7,8      -> 2da opcion
            # r: 1,2,3,4,5,a,b,6,7,8      -> 3ra opcion
            # r: 1,2,3,4,5,b,a,6,7,8      -> 4ta opcion
            #print("\nPor la misma ruta")
            r = rutas[ind_rutas[0]]
            V_r = r.getV()
            V_r_middle = V_r[ind_A[0]+1:ind_A[1]+1]
            if(len(V_r_middle)<=1):                    #r: 1,2,a,3,b,4   Solo se aplica 2-opt y ya la aplicamos anteriormente
                return float("inf"), opcion, DROP, index_DROP        
            else:
                V_r.append(Vertice(1,0))
            
            V_r_left = V_r[:ind_A[0]+1]
            V_r_right = V_r[ind_A[1]+2:]
            # print("ind_A: "+str(ind_A))
            # print("V_r_r: "+str(V_r_right))
            # print("V_r_m: "+str(V_r_middle))
            # print("V_r_l: "+str(V_r_left))
            
            for ind in range(2):
                if(ind==1):
                    if(0 in ind_A):
                        continue
                    ind_A[0] = ind_A[0]-1
                    ind_A[1] = ind_A[1]+1
                    V_r_left = V_r[:ind_A[0]+1]
                
                if(ind == 0):
                    A_r_drop2 = r.getA()[ind_A[1]+1]
                    A_r_drop3 = r.getA()[ind_A[1]]
                    V_origen = V_r_middle[-1]
                    V_destino = V_r_right[0]
                else:
                    A_r_drop2 = r.getA()[ind_A[0]+1]
                    A_r_drop3 = r.getA()[ind_A[0]]
                    V_destino = V_r_middle[0]
                    V_origen = V_r_left[-1]
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add2 = Arista(V_origen,V_destino, peso)
                A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                
                costo_r_add2 = peso
                costo_r_drop2 = A_r_drop2.getPeso()
                costo_r_drop3 = A_r_drop3.getPeso()
                
                if(ind == 0):
                    for i in range(1,3):
                        if(i==1):
                            A_r_drop1 = r.getA()[ind_A[0]]
                            costo_r_drop1 = A_r_drop1.getPeso()
                            
                            V_origen = V_r[ind_A[1]+1]
                            V_destino = V_r_middle[0]
                            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                            A_r_add3 = Arista(V_origen,V_destino, peso)
                            A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                            costo_r_add3 = peso
                        elif(i==2 and 0 not in ind_A):
                            A_r_drop1 = r.getA()[ind_A[0]-1]
                            costo_r_drop1 = A_r_drop1.getPeso()
                            
                            V_origen = V_r[ind_A[0]-1]
                            V_destino = V_r[ind_A[1]+1]
                            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                            A_r_add3 = Arista(V_origen,V_destino, peso)
                            A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                            costo_r_add3 = peso                    
                        
                        nuevo_costo = self.getCostoTotal() + costo_r_add1 + costo_r_add2 + costo_r_add3 - costo_r_drop1 - costo_r_drop2 - costo_r_drop3
                        
                        if(nuevo_costo < costo_solucion):
                            costo_solucion = nuevo_costo
                            opcion = (-1)*i - 2*ind
                            DROP = []
                            index_DROP = []
                            DROP.append(A_r_drop1)
                            DROP.append(A_r_drop2)
                            DROP.append(A_r_drop3)
                            index_DROP.append(A_r_drop1.getId())
                            index_DROP.append(A_r_drop2.getId())
                            index_DROP.append(A_r_drop3.getId())
                            #print("DROP: "+str(DROP))
                elif(ind == 1):
                    for i in range(1,3):
                        if(i==1):
                            A_r_drop1 = r.getA()[ind_A[1]]
                            costo_r_drop1 = A_r_drop1.getPeso()
                            
                            V_origen = V_r[ind_A[0]+1]
                            V_destino = V_r[ind_A[1]+1]
                            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                            A_r_add3 = Arista(V_origen,V_destino, peso)
                            A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                            costo_r_add3 = peso
                        else:
                            A_r_drop1 = r.getA()[ind_A[1]-1]
                            costo_r_drop1 = A_r_drop1.getPeso()
                            
                            V_destino = V_r[ind_A[0]+1]
                            V_origen = V_r[ind_A[1]-1]
                            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                            A_r_add3 = Arista(V_origen,V_destino, peso)
                            A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                            costo_r_add3 = peso                    
                        
                        nuevo_costo = self.getCostoTotal() + costo_r_add1 + costo_r_add2 + costo_r_add3 - costo_r_drop1 - costo_r_drop2 - costo_r_drop3
                        
                        if(nuevo_costo < costo_solucion):
                            costo_solucion = nuevo_costo
                            opcion = (-1)*i - 2*ind
                            DROP = []
                            index_DROP = []
                            DROP.append(A_r_drop1)
                            DROP.append(A_r_drop2)
                            DROP.append(A_r_drop3)
                            index_DROP.append(A_r_drop1.getId())
                            index_DROP.append(A_r_drop2.getId())
                            index_DROP.append(A_r_drop3.getId())

            V_r = r.getV()
            V_r = V_r[:-1]
            r.setV(V_r)
        
        return costo_solucion, opcion, DROP, index_DROP  

    # def controlVariantes4OPT(self,ind_A,rutas):
    def getAristaInvertidas(self,A):
        for a in A:
            a.invertirArista

    def sumarCostos(self,A):
        #Suma los costos de una lista de Aristas
        suma = 0 
        for a in A:
            suma+= a.getPeso()
        return suma

    def sumarDemandas(self,A):
        suma = 0 
        for a in A:
            suma+= a.getOrigen().getDemanda()
        return suma

    """
    r1: 1,2,3,a,4,5,6        r2: 1,7,8,b,9,10,11,12
    resultado:
    r1: 1,2,3,a,b,5,6        r2: 1,7,8,4,9,10,11,12       -> 1ra opcion        
    r1: 1,2,b,a,4,5,6        r2: 1,7,8,3,9,10,11,12       -> 2da opcion
    r1: 1,2,3,9,4,5,6        r2: 1,7,8,b,a,10,11,12       -> 3ra opcion
    r1: 1,2,3,8,4,5,6        r2: 1,7,a,b,9,10,11,12       -> 4ta opcion 
    
    r: 1,2,3,a,4,5,6,b,7,8  -> Original
    resultado:
    r: 1,2,3,a,b,5,6,4,7,8  -> 1ra opcion
    r: 1,2,b,a,4,5,3,6,7,8  -> 2da opcion        
    r: 1,2,3,7,4,5,6,b,a,8  -> 3ra opcion
    r: 1,2,3,6,4,5,a,b,7,8  -> 4ta opcion
    """
    def evaluar_4optv2(self, arista_ini, ind_rutas, ind_A):
        opcion = 0
        costo_solucion = float("inf")
        
        DROP = []
        index_DROP = []
        rutas = self.rutas

        if(ind_A[1]-ind_A[0] == 1):
            return costo_solucion, opcion, DROP, index_DROP

        if(ind_rutas[0] != ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            
            A_r1 = r1.getA()
            A_r2 = r2.getA()

            """
            r1: 1,2,a,3      r2: 1,5,b,6
            resultado:
            r1: 1,2,a,b      r2: 1,5,3,6       -> 1ra opcion        
            r1: 1,b,a,3      r2: 1,5,2,6       -> 2da opcion
            r1: 1,2,6,3      r2: 1,5,b,a       -> 3ra opcion
            r1: 1,2,5,3      r2: 1,a,b,6       -> 4ta opcion 
            """
            if(len(A_r1) <= 2 or len(A_r2) <= 2):
                return costo_solucion, opcion, [], []
            
            for i in range(1,5):
                if((i==2 or i==4) and (0 in ind_A or 1 in ind_A)):
                    continue
                if((i == 1 or i==3) and (len(r1.getV())-1 == ind_A[0] or len(r2.getV())-1 == ind_A[1]+1)):
                    #r1: 1,2,a        r2: 1,b,3
                    #r1: 1,2,a,b      r2: 1,1,4       -> No se puede 1ra opcion    
                    #r1: 1,2,3        r2: 1,b,a       -> 3ra opcion (No se puede aplicar 4-opt, se aplica 2-opt)
                    continue
                
                if(i == 1):
                    #r1: 1,2,3,a,4,5,6        r2: 1,7,8,b,9,10,11,12
                    #r1: 1,2,3,a,b,5,6        r2: 1,7,8,4,9,10,11,12       -> 1ra opcion
                    #print("Opcion ", i)
                    try:
                        A_r1_drop1 = A_r1[ind_A[0]]
                        A_r1_drop2 = A_r1[ind_A[0]+1]
                        A_r2_drop1 = A_r2[ind_A[1]]
                        A_r2_drop2 = A_r2[ind_A[1]+1]
                    except IndexError:
                        print("Arista ini: "+str(arista_ini))
                        print("A_r1: "+str(A_r1))
                        print("A_r2: "+str(A_r2))
                        print("ind_A: "+str(ind_A))
                        a = 1/0
                    A_r1_add1 = arista_ini

                    V_origen = A_r2_drop1.getDestino()
                    V_destino = A_r1_drop2.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r1_add2 = Arista(V_origen, V_destino, peso)
                    A_r1_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    
                    V_origen = A_r2_drop1.getOrigen()
                    V_destino = A_r1_drop1.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r2_add1 = Arista(V_origen, V_destino, peso)
                    A_r2_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    
                    V_origen = V_destino
                    V_destino = A_r2_drop2.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r2_add2 = Arista(V_origen, V_destino, peso)
                    A_r2_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                
                    if(A_r1_add1.getDestino() != A_r1_add2.getOrigen()):
                        arista_ini.invertir()
                    # print("\nA_r1_drop1: "+str(A_r1_drop1))
                    # print("A_r1_drop2: "+str(A_r1_drop2))
                    # print("A_r2_drop1: "+str(A_r2_drop1))
                    # print("A_r2_drop2: "+str(A_r2_drop2))
                    # print("\nA_r1_add1: "+str(A_r1_add1))
                    # print("A_r1_add2: "+str(A_r1_add2))
                    # print("A_r2_add1: "+str(A_r2_add1))
                    # print("A_r2_add2: "+str(A_r2_add2))
                    # print("costo r1: ", r1.getCostoAsociado())
                    # print("costo r2: ", r2.getCostoAsociado())
                elif(i == 2):
                    #print("Opcion ", i)
                    #r1: 1,2,3,a,4,5,6        r2: 1,7,8,b,9,10,11,12
                    #r1: 1,2,b,a,4,5,6        r2: 1,7,8,3,9,10,11,12       -> 2da opcion
                    A_r1_drop1 = A_r1[ind_A[0]-2]
                    A_r1_drop2 = A_r1[ind_A[0]-1]
                    A_r2_drop1 = A_r2[ind_A[1]]
                    A_r2_drop2 = A_r2[ind_A[1]+1]

                    A_r1_add2 = arista_ini

                    V_origen = A_r1_drop1.getOrigen()
                    V_destino = A_r2_drop1.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r1_add1 = Arista(V_origen, V_destino, peso)
                    A_r1_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    
                    V_origen = A_r2_drop1.getOrigen()
                    V_destino = A_r1_drop1.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r2_add1 = Arista(V_origen, V_destino, peso)
                    A_r2_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    
                    V_origen = V_destino
                    V_destino = A_r2_drop2.getDestino()
                    costo_r2_add2 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r2_add2 = Arista(V_origen, V_destino, costo_r2_add2)
                    A_r2_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                elif(i == 3):
                    #r1: 1,2,3,a,4,5,6        r2: 1,7,8,b,9,10,11,12
                    #r1: 1,2,3,9,4,5,6        r2: 1,7,8,b,a,10,11,12       -> 3ra opcion
                    #print("Opcion ", i)
                    
                    A_r1_drop1 = A_r1[ind_A[0]-1]
                    A_r1_drop2 = A_r1[ind_A[0]]
                    A_r2_drop1 = A_r2[ind_A[1]+1]
                    A_r2_drop2 = A_r2[ind_A[1]+2]

                    A_r2_add1 = arista_ini

                    V_origen = A_r1_drop1.getOrigen()
                    V_destino = A_r2_drop1.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r1_add1 = Arista(V_origen, V_destino, peso)
                    A_r1_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = V_destino
                    V_destino = A_r1_drop2.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r1_add2 = Arista(V_origen, V_destino, peso)
                    A_r1_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = A_r1_drop1.getDestino()
                    V_destino = A_r2_drop2.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r2_add2 = Arista(V_origen, V_destino, peso)
                    A_r2_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    #if(A_r_add1.getDestino() != A_r_add2.getOrigen()):
                    #    arista_ini.invertir()            

                    # print("\nA_r1_drop1: "+str(A_r1_drop1))
                    # print("A_r1_drop2: "+str(A_r1_drop2))
                    # print("A_r2_drop1: "+str(A_r2_drop1))
                    # print("A_r2_drop2: "+str(A_r2_drop2))
                    # print("\nA_r1_add1: "+str(A_r1_add1))
                    # print("A_r1_add2: "+str(A_r1_add2))
                    # print("A_r2_add1: "+str(A_r2_add1))
                    # print("A_r2_add2: "+str(A_r2_add2))
                    # print("costo r1: ", r1.getCostoAsociado())
                    # print("costo r2: ", r2.getCostoAsociado())
                else:
                    #r1: 1,2,3,a,4,5,6        r2: 1,7,8,b,9,10,11,12
                    #r1: 1,2,3,8,4,5,6        r2: 1,7,a,b,9,10,11,12       -> 4ta opcion 
                    #print("Opcion ", i)
                    A_r1_drop1 = A_r1[ind_A[0]-1]
                    A_r1_drop2 = A_r1[ind_A[0]]
                    A_r2_drop1 = A_r2[ind_A[1]-1]
                    A_r2_drop2 = A_r2[ind_A[1]]

                    A_r2_add2 = arista_ini

                    V_origen = A_r1_drop1.getOrigen()
                    V_destino = A_r2_drop1.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r1_add1 = Arista(V_origen, V_destino, peso)
                    A_r1_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = V_destino
                    V_destino = A_r1_drop2.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r1_add2 = Arista(V_origen, V_destino, peso)
                    A_r1_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = A_r2_drop1.getOrigen()
                    V_destino = A_r1_drop1.getDestino()
                    costo_r2_add1 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r2_add1 = Arista(V_origen, V_destino, costo_r2_add1)
                    A_r2_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                cap_r1 = r1.getCapacidad() - A_r1_drop1.getDestino().getDemanda() + A_r1_add1.getDestino().getDemanda()
                cap_r2 = r2.getCapacidad() - A_r2_drop1.getDestino().getDemanda() + A_r2_add1.getDestino().getDemanda()
                
                nuevo_costo = self.getCostoTotal() + A_r1_add1.getPeso() + A_r1_add2.getPeso() + A_r2_add1.getPeso() + A_r2_add2.getPeso()
                nuevo_costo = nuevo_costo - A_r1_drop1.getPeso() - A_r1_drop2.getPeso() - A_r2_drop1.getPeso() - A_r2_drop2.getPeso()
                
                print(f"A_r1_drop1: {A_r1_drop1}\t A_r1_add1: {A_r1_add1} ")
                print(f"A_r1_drop1: {A_r2_drop1}\t A_r2_add1: {A_r2_add1} ")
                print(f"capacidad antes r1: {r1.getCapacidad()}\t r2: {r2.getCapacidad()}")
                print(f"cap_r1 {cap_r1}\t cap_r2 {cap_r2} \t costo: {nuevo_costo}")
                if(cap_r1 > self.capacidadMax or cap_r2 > self.capacidadMax):
                    continue


                if(nuevo_costo < costo_solucion):
                    costo_solucion = nuevo_costo
                    opcion = i
                    DROP = []
                    index_DROP = []
                    DROP.append(A_r1_drop1)
                    DROP.append(A_r1_drop2)
                    DROP.append(A_r2_drop1)
                    DROP.append(A_r2_drop2)
                    index_DROP.append(A_r1_drop1.getId())
                    index_DROP.append(A_r1_drop2.getId())
                    index_DROP.append(A_r2_drop1.getId())
                    index_DROP.append(A_r2_drop2.getId())
                
                #print("-> Nuevo costo: "+str(nuevo_costo)+"\n\n")
        else:
            # r: 1,2,3,a,4,5,6,b,7,8  -> Original
            # r: 1,2,3,a,b,5,6,4,7,8  -> 1ra opcion
            # r: 1,2,b,a,4,5,3,6,7,8  -> 2da opcion        
            # r: 1,2,3,7,4,5,6,b,a,8  -> 3ra opcion
            # r: 1,2,3,6,4,5,a,b,7,8  -> 4ta opcion    
            r = rutas[ind_rutas[0]]
            A_r = r.getA()
            if(len(A_r) <= 2):
                return costo_solucion, opcion, [], []
            
            for i in range(1,5):
                if(i==2 and (0 in ind_A or 1 in ind_A)):
                    continue
                if((i==3 or i==4) and 0 == ind_A[0]):
                    continue
                if(i==3 and len(r.getV())-1 == ind_A[1]+1):
                    continue
                if((i==1 or i==4) and (ind_A[1]-ind_A[0] <= 2)):
                    continue
                
                if(i == 1):
                    # r: 1,2,3,a,4,5,6,b,7,8  -> Original
                    # r: 1,2,3,a,b,5,6,4,7,8  -> 1ra opcion
                    #print("Opcion ",i)      
                    A_r_drop1 = A_r[ind_A[0]]
                    A_r_drop2 = A_r[ind_A[0]+1]
                    A_r_drop3 = A_r[ind_A[1]]
                    A_r_drop4 = A_r[ind_A[1]+1]

                    A_r_add1 = arista_ini
                    V_origen = A_r_drop4.getOrigen()
                    V_destino = A_r_drop2.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add2 = Arista(V_origen, V_destino, peso)
                    A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = A_r_drop3.getOrigen()
                    V_destino = A_r_drop1.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add3 = Arista(V_origen, V_destino, peso)
                    A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = V_destino
                    V_destino = A_r_drop4.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add4 = Arista(V_origen, V_destino, peso)
                    A_r_add4.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    if(A_r_add1.getDestino() != A_r_add2.getOrigen()):
                        arista_ini.invertir()
                elif(i == 2):
                    # r: 1,2,3,a,4,5,6,b,7,8  -> Original
                    # r: 1,2,b,a,4,5,3,6,7,8  -> 2da opcion
                    A_r_drop1 = A_r[ind_A[0]-2]
                    A_r_drop2 = A_r[ind_A[0]-1]
                    A_r_drop3 = A_r[ind_A[1]]
                    A_r_drop4 = A_r[ind_A[1]+1]
                    
                    A_r_add2 = arista_ini

                    V_origen = A_r_drop1.getOrigen()
                    V_destino = A_r_drop4.getOrigen()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add1 = Arista(V_origen, V_destino, peso)
                    A_r_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                        
                    V_origen = A_r_drop3.getOrigen()
                    V_destino = A_r_drop1.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add3 = Arista(V_origen, V_destino, peso)
                    A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    
                    V_origen = V_destino
                    V_destino = A_r_drop4.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add4 = Arista(V_origen, V_destino, peso)
                    A_r_add4.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    if(A_r_add1.getDestino() != A_r_add2.getOrigen()):
                        arista_ini.invertir()
                elif(i == 3):
                    # r: 1,2,3,a,4,5,6,b,7,8  -> Original
                    # r: 1,2,3,7,4,5,6,b,a,8  -> 3ra opcion
                    #print("Opcion ", i)
                    A_r_drop1 = A_r[ind_A[0]-1]
                    A_r_drop2 = A_r[ind_A[0]]
                    A_r_drop3 = A_r[ind_A[1]+1]
                    A_r_drop4 = A_r[ind_A[1]+2]

                    A_r_add3 = arista_ini

                    V_origen = A_r_drop1.getOrigen()
                    V_destino = A_r_drop3.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add1 = Arista(V_origen, V_destino, peso)
                    A_r_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = V_destino
                    V_destino = A_r_drop2.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add2 = Arista(V_origen, V_destino, peso)
                    A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = A_r_drop2.getOrigen()
                    V_destino = A_r_drop4.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add4 = Arista(V_origen, V_destino, peso)
                    A_r_add4.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    
                    if(A_r_add3.getDestino() != A_r_add4.getOrigen()):
                        arista_ini.invertir()
                else:
                    # r: 1,2,3,a,4,5,6,b,7,8  -> Original
                    # r: 1,2,3,6,4,5,a,b,7,8  -> 4ta opcion
                    #print("Opcion ", i)
                    A_r_drop1 = A_r[ind_A[0]-1]
                    A_r_drop2 = A_r[ind_A[0]]
                    A_r_drop3 = A_r[ind_A[1]-1]
                    A_r_drop4 = A_r[ind_A[1]]

                    A_r_add4 = arista_ini

                    V_origen = A_r_drop1.getOrigen()
                    V_destino = A_r_drop3.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add1 = Arista(V_origen, V_destino, peso)
                    A_r_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = V_destino
                    V_destino = A_r_drop2.getDestino()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add2 = Arista(V_origen, V_destino, peso)
                    A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    V_origen = A_r_drop3.getOrigen()
                    V_destino = A_r_drop2.getOrigen()
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_add3 = Arista(V_origen, V_destino, peso)
                    A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                    if(A_r_add3.getDestino() != A_r_add4.getOrigen()):
                        arista_ini.invertir()

                nuevo_costo = self.getCostoTotal() + A_r_add1.getPeso() + A_r_add2.getPeso() + A_r_add3.getPeso() + A_r_add4.getPeso()
                nuevo_costo = nuevo_costo - A_r_drop1.getPeso() - A_r_drop2.getPeso() - A_r_drop3.getPeso() - A_r_drop4.getPeso()



                print(f"cap_r {r.getCapacidad()}\t costo: {nuevo_costo}")
                if(nuevo_costo < costo_solucion):
                    costo_solucion = nuevo_costo
                    opcion = i*(-1)
                    DROP = []
                    index_DROP = []
                    DROP.append(A_r_drop1)
                    DROP.append(A_r_drop2)
                    DROP.append(A_r_drop3)
                    DROP.append(A_r_drop4)
                    index_DROP.append(A_r_drop1.getId())
                    index_DROP.append(A_r_drop2.getId())
                    index_DROP.append(A_r_drop3.getId())
                    index_DROP.append(A_r_drop4.getId())
                
                #print("-> Nuevo costo: "+str(nuevo_costo)+"\n\n")

        return costo_solucion, opcion, DROP, index_DROP


    def swap_4optv2(self, arista_ini, ind_rutas, ind_A, opcion):
        costo_solucion = self.getCostoTotal()
        ADD = []
        DROP = []
        
        ADD.append(arista_ini)
        rutas = self.rutas
        V_origen = arista_ini.getOrigen()
        V_destino = arista_ini.getDestino()
        rutas = self.rutas
        #Cada ruta de al menos 4 aristas o 3 clientes. Si a o b estan al final: los intercambio
        ind_A_inicial = copy.copy(ind_A)
        
        
        if(opcion > 0):
            if(opcion==1 or opcion == 2):
                r1 = rutas[ind_rutas[0]]
                r2 = rutas[ind_rutas[1]]       
                if(opcion==2):     
                    ind_A[0] = ind_A_inicial[0]-2           
                    ind_A[1] = ind_A_inicial[1]      
                    V_origen = r1.getA()[ind_A[0]].getOrigen()
                    V_destino = arista_ini.getDestino()
                    peso = self._matrizDistancias[r1.getA()[ind_A[0]].getOrigen().getValue()-1][arista_ini.getDestino().getValue()-1]    
                    arista_nueva = Arista(V_origen, V_destino,peso)       
                    arista_nueva.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    ADD = [arista_nueva]
                else:
                    ADD = [arista_ini]
                DROP = []
            elif(opcion==3 or opcion == 4):
                ind_A = copy.copy(ind_A_inicial)
                r2 = rutas[ind_rutas[0]]
                r1 = rutas[ind_rutas[1]]
                ind_A.reverse()

                if(opcion ==4):
                    ind_A[0] = ind_A[0]-1
                    ind_A[1] = ind_A[1]-1         
                    V_origen = r1.getA()[ind_A[0]].getOrigen()
                    V_destino = arista_ini.getOrigen()
                    peso = self._matrizDistancias[r1.getA()[ind_A[0]].getOrigen().getValue()-1][arista_ini.getOrigen().getValue()-1]    
                    arista_nueva = Arista(V_origen, V_destino,peso)       
                    arista_nueva.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    ADD = [arista_nueva]                    
                else:
                    ADD = [arista_ini.getAristaInvertida()]
                    ind_A[0] += 1          
                    ind_A[1] -= 1
                DROP = []

            costo_solucion -= r1.getCostoAsociado()+r2.getCostoAsociado()
            
            V_r1 = r1.getV()
            if(V_r1[-1] != 1):
                V_r1.append(Vertice(1,0))
            
            if(V_origen == V_r1[-2] and opcion!=2):
                V_r1 = V_r1[::-1]
                ind_A[0] = 1
            
            V_r2 = r2.getV()
            if(V_r2[-1] != 1 ):
                V_r2.append(Vertice(1,0))

            if(V_destino == V_r2[-2] and opcion!=2):
                V_r2 = V_r2[::-1]
                ind_A[1] = 0
            
            V_r1_left = V_r1[:ind_A[0]+1]
            V_r1_right = V_r1[ind_A[0]+2:]
            V_r2_left = V_r2[:ind_A[1]+1]
            V_r2_right = V_r2[ind_A[1]+2:]    
            
            #Obtengo las aristas que se eliminan y las que se añaden
            #3 ADD's y 4 DROP's
            #1er DROP
            V_origen = V_r1[ind_A[0]]
            V_destino = V_r1[ind_A[0]+1]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r1_drop1 = Arista(V_origen, V_destino, peso)
            A_r1_drop1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

            #2do DROP
            V_origen = V_destino
            V_destino = V_r1[ind_A[0]+2]
            
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r1_drop2 = Arista(V_origen, V_destino, peso)
            A_r1_drop2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            #2do ADD
            V_origen = ADD[0].getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r1_add2 = Arista(V_origen, V_destino, peso)
            A_r1_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            #3er DROP
            V_origen = V_r2[ind_A[1]]
            V_destino = V_r2[ind_A[1]+1]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r2_drop1 = Arista(V_origen, V_destino, peso)
            A_r2_drop1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            #3er ADD
            V_destino = V_r1[ind_A[0]+1]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r2_add1 = Arista(V_origen, V_destino, peso)
            A_r2_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            #4to DROP
            V_origen = V_r2[ind_A[1]+1]
            V_destino = V_r2[ind_A[1]+2]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r2_drop2 = Arista(V_origen, V_destino, peso)
            A_r2_drop2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            #4to ADD
            V_origen = A_r2_add1.getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r2_add2 = Arista(V_origen, V_destino, peso)
            A_r2_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            DROP.append(A_r1_drop1)
            DROP.append(A_r1_drop2)
            DROP.append(A_r2_drop1)
            DROP.append(A_r2_drop2)
            
            ADD.append(A_r1_add2)
            ADD.append(A_r2_add1)
            ADD.append(A_r2_add2)

            V_r1_left.append(ADD[0].getDestino())
            V_r1_left.extend(V_r1_right)
            V_r2_left.append(ADD[2].getDestino())
            V_r2_left.extend(V_r2_right)
            
            if V_r1[-1] == 1:
                r1.setV(r1.getV()[:-1])
            if V_r2[-1] == 1:                
                r2.setV(r2.getV()[:-1])

            r1.cargarDesdeSecuenciaDeVertices(V_r1_left[:-1])
            r2.cargarDesdeSecuenciaDeVertices(V_r2_left[:-1])
            
        #4-opt en la misma ruta. Condicion: Deben haber 4 aristas de separacion entre a y b, si no se realiza 2-opt
        else:
            # r: 1,2,3,a,4,5,6,b,7,8  -> Original
            # r: 1,2,3,a,b,5,6,4,7,8  -> 1ra opcion
            # r: 1,2,b,a,4,5,3,6,7,8  -> 2da opcion        
            # r: 1,2,3,7,4,5,6,b,a,8  -> 3ra opcion
            # r: 1,2,3,6,4,5,a,b,7,8  -> 4ta opcion
            r = rutas[ind_rutas[0]]
            costo_solucion -= r.getCostoAsociado()
            A_r = r.getA()
            A_r_left = []
            A_r_middle = []
            A_r_right = []
            if(opcion == -1):
                # r: 1,2,3,a,4,5,6,b,7,8  -> Original
                # r: 1,2,3,a,b,5,6,4,7,8  -> 1ra opcion
                A_r_left = A_r[:ind_A[0]]
                A_r_middle = A_r[ind_A[0]+2:ind_A[1]]
                A_r_right = A_r[ind_A[1]+2:]

                A_r_drop1 = A_r[ind_A[0]]
                A_r_drop2 = A_r[ind_A[0]+1]
                A_r_drop3 = A_r[ind_A[1]]
                A_r_drop4 = A_r[ind_A[1]+1]

                A_r_add1 = arista_ini
                V_origen = A_r_drop4.getOrigen()
                V_destino = A_r_drop2.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add2 = Arista(V_origen, V_destino, peso)
                A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))


                V_origen = A_r_drop3.getOrigen()
                V_destino = A_r_drop1.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add3 = Arista(V_origen, V_destino, peso)
                A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                V_origen = V_destino
                V_destino = A_r_drop4.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add4 = Arista(V_origen, V_destino, peso)
                A_r_add4.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                if(A_r_add1.getDestino() != A_r_add2.getOrigen()):
                    arista_ini.invertir()

                # print("A_r_add1: "+str(A_r_add1))
                # print("A_r_add2: "+str(A_r_add2))
                # print("A_r_add3: "+str(A_r_add3))
                # print("A_r_add4: "+str(A_r_add4))
                # print("A_r_drop1: "+str(A_r_drop1))
                # print("A_r_drop3: "+str(A_r_drop2))
                # print("A_r_drop2: "+str(A_r_drop3))
                # print("A_r_drop4: "+str(A_r_drop4))

            elif(opcion == -2):
                # r: 1,2,3,a,4,5,6,b,7,8  -> Original
                # r: 1,2,b,a,4,5,3,6,7,8  -> 2da opcion
                #print("Opcion ",opcion)
                A_r_left = A_r[:ind_A[0]-2]
                A_r_middle = A_r[ind_A[0]:ind_A[1]]
                A_r_right = A_r[ind_A[1]+2:]
      
                A_r_drop1 = A_r[ind_A[0]-2]
                A_r_drop2 = A_r[ind_A[0]-1]
                A_r_drop3 = A_r[ind_A[1]]
                A_r_drop4 = A_r[ind_A[1]+1]

                A_r_add2 = arista_ini

                V_origen = A_r_drop1.getOrigen()
                V_destino = A_r_drop4.getOrigen()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add1 = Arista(V_origen, V_destino, peso)
                A_r_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    
                V_origen = A_r_drop3.getOrigen()
                V_destino = A_r_drop1.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add3 = Arista(V_origen, V_destino, peso)
                A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                
                V_origen = V_destino
                V_destino = A_r_drop4.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add4 = Arista(V_origen, V_destino, peso)
                A_r_add4.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                if(A_r_add1.getDestino() != A_r_add2.getOrigen()):
                    arista_ini.invertir()
            elif(opcion == -3):
                # r: 1,2,3,a,4,5,6,b,7,8  -> Original
                # r: 1,2,3,7,4,5,6,b,a,8  -> 3ra opcion
                A_r_left = A_r[:ind_A[0]-1]
                A_r_middle = A_r[ind_A[0]+1:ind_A[1]+1]
                A_r_right = A_r[ind_A[1]+3:]

                A_r_drop1 = A_r[ind_A[0]-1]
                A_r_drop2 = A_r[ind_A[0]]
                A_r_drop3 = A_r[ind_A[1]+1]
                A_r_drop4 = A_r[ind_A[1]+2]

                A_r_add3 = arista_ini

                V_origen = A_r_drop1.getOrigen()
                V_destino = A_r_drop3.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add1 = Arista(V_origen, V_destino, peso)
                A_r_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                V_origen = V_destino
                V_destino = A_r_drop2.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add2 = Arista(V_origen, V_destino, peso)
                A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                V_origen = A_r_drop2.getOrigen()
                V_destino = A_r_drop4.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add4 = Arista(V_origen, V_destino, peso)
                A_r_add4.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                
                if(A_r_add3.getDestino() != A_r_add4.getOrigen()):
                    arista_ini.invertir()
            else:
                # r: 1,2,3,a,4,5,6,b,7,8  -> Original
                # r: 1,2,3,6,4,5,a,b,7,8  -> 4ta opcion
                #print("Opcion ", opcion)
                A_r_left = A_r[:ind_A[0]-1]
                A_r_middle = A_r[ind_A[0]+1:ind_A[1]-1]
                A_r_right = A_r[ind_A[1]+1:]

                A_r_drop1 = A_r[ind_A[0]-1]
                A_r_drop2 = A_r[ind_A[0]]
                A_r_drop3 = A_r[ind_A[1]-1]
                A_r_drop4 = A_r[ind_A[1]]

                A_r_add4 = arista_ini

                V_origen = A_r_drop1.getOrigen()
                V_destino = A_r_drop3.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add1 = Arista(V_origen, V_destino, peso)
                A_r_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                V_origen = V_destino
                V_destino = A_r_drop2.getDestino()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add2 = Arista(V_origen, V_destino, peso)
                A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                V_origen = A_r_drop3.getOrigen()
                V_destino = A_r_drop2.getOrigen()
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                A_r_add3 = Arista(V_origen, V_destino, peso)
                A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

                if(A_r_add3.getDestino() != A_r_add4.getOrigen()):
                    arista_ini.invertir()

            A_r_left.append(A_r_add1)
            A_r_left.append(A_r_add2)
            A_r_left.extend(A_r_middle)
            A_r_left.append(A_r_add3)
            A_r_left.append(A_r_add4)
            A_r_left.extend(A_r_right)
            
            r.cargarDesdeAristas(A_r_left)

        if(self.controlarCapacidad(ind_rutas[0])):
            print("---------------------------------------------------EXCEDIÓ CAPACIDAD R1---------------------------------")
        if(self.controlarCapacidad(ind_rutas[1])):
            print("---------------------------------------------------EXCEDIÓ CAPACIDAD R2---------------------------------")

    
        self.setCostoTotal()

    def controlarCapacidad(self,r):
        """ True si excedió la capacidad
            False si no.
        """
        suma = 0
        for ruta in self.rutas[r].getV():
            suma += ruta.getDemanda()
        
        if(suma>self.capacidadMax):
            return True
        else:
            return False






    def setDemandaAcumulada(self,r):
        ruta = self.rutas[r]
        ruta._demandaAcumulada = []
        suma = 0
        for v in ruta.getV():
            dem = v.getDemanda()
            ruta._demandaAcumulada.append(dem)
            suma += dem
        ruta.setCapacidad(suma)

    def controlarIntegridad(self,r):
        ruta = self.rutas[r]
        values = list(ruta.dictAristasRuta.values())
        for A in ruta.getA():
            flag = False

            for j in values:
                if hash(A) == hash(j):
                    flag = True
                    
            if(flag==False):
                print("Diccionario inconscitente")
                return False
        if flag:
            return True 
        



if __name__ == "__main__":
    # inf = float("inf")
    # matriz = [[inf,25,43,57,43,61,29,41,48,71],
    #           [25,inf,29,34,43,68,49,66,72,91],
    #           [43,29,inf,52,72,96,72,81,89,114],
    #           [57,34,52,inf,45,71,71,95,99,108],
    #           [43,43,72,45,inf,27,36,65,65,65],
    #           [61,68,96,71,27,inf,40,66,62,46],
    #           [29,49,72,71,36,40,inf,31,31,43],
    #           [41,66,81,95,65,66,31,inf,11,46],
    #           [48,72,89,99,65,62,31,11,inf,36],
    #           [71,91,114,108,65,46,43,46,36,inf]]
    # dem = [0,4,6,5,4,7,3,5,4,4]
    from Ingreso import Ingreso
    arg = Ingreso(sys.argv)
    matriz = arg.M
    dem = arg.D
    nv = arg.NV 
    cap = arg.C
    S = Solucion(matriz,dem,cap,nv)
    S.rutasIniciales(0)
    print(S)

    #arista_ini = S.rutas[0].buscarArista((10,5)) #Opcion 4 misma ruta

    #arista_ini = S.rutas[0].buscarArista((24,10)) #Opcion 4 distinta ruta
    #arista_ini = S.rutas[0].buscarArista((2,5))   #Opcion 3 distinta ruta
    # arista_ini = S.rutas[0].buscarArista((16,31)) #Opcion 1 distinta ruta
    #arista_ini = S.rutas[0].buscarArista((4,14)) #Opcion 2 distinta ruta

    #arista_ini = S.rutas[0].buscarArista((5,10)) #Opcion 4 misma ruta
    #arista_ini = S.rutas[0].buscarArista((2,5))   #Opcion 3 misma ruta
    #arista_ini = S.rutas[0].buscarArista((14,25)) #Opcion 1 misma ruta
    #arista_ini = S.rutas[0].buscarArista((4,14)) #Opcion 2 misma ruta
    # print(arista_ini)
    # indR, indA = S.getPosiciones(arista_ini.getOrigen(),arista_ini.getDestino())
    # nuevoCosto, tipo_4opt, ADD_4opt, DROP_4opt, indDROP_4opt = S.evaluar_4optv2(arista_ini,indR,indA)
    # print(f"ruta {indR[0]}\n V:{S.rutas[indR[0]].getV()} \n A:{S.rutas[indR[0]].getA()} ")
    # S.rutas[indR[0]].mostrarDictAristasRuta()
    # print(f"ruta {indR[1]}\n V:{S.rutas[indR[1]].getV()} \n A:{S.rutas[indR[1]].getA()} ")
    # S.rutas[indR[1]].mostrarDictAristasRuta()
    # indR, indA = S.getPosiciones(arista_ini.getOrigen(),arista_ini.getDestino())
    # print("costoEvaluado: ", nuevoCosto)
    # print("ADD: ", ADD_4opt)
    # print("DROP: ", DROP_4opt)
    # print("Opcion: ", tipo_4opt)

    # S.swap_4optv3(ADD_4opt,DROP_4opt,indR,indA,tipo_4opt)
    
    # print(f"ruta {indR[0]} después de swap \nV:{S.rutas[indR[0]].getV()} \n A:{S.rutas[indR[0]].getA()} ")
    # S.rutas[indR[0]].mostrarDictAristasRuta()
    # print(f"ruta {indR[1]} después de swap \nV:{S.rutas[indR[1]].getV()} \n A:{S.rutas[indR[1]].getA()} ")
    # S.rutas[indR[1]].mostrarDictAristasRuta()


    #3-opt
    arista_ini = S.rutas[0].buscarArista((8,25)) #Opcion 1 distinta ruta
    #arista_ini = S.rutas[0].buscarArista((26,15)) #Opcion 2 distinta ruta
    # arista_ini = S.rutas[0].buscarArista((24,29)) #Opcion 3 distinta ruta
    # arista_ini = S.rutas[0].buscarArista((15,26)) #Opcion 4 distinta ruta
    # arista_ini = S.rutas[0].buscarArista((7,10)) #Opcion 1 misma ruta
    # arista_ini = S.rutas[0].buscarArista((10,15)) #Opcion 2 misma ruta
    #arista_ini = S.rutas[0].buscarArista((12,15)) #Opcion 3 misma ruta
    # arista_ini = S.rutas[0].buscarArista((32,24)) #Opcion 4 misma ruta
    # print(arista_ini)
    indR, indA = S.getPosiciones(arista_ini.getOrigen(),arista_ini.getDestino())
    nuevoCosto, tipo_3opt, DROP_3opt, indDROP_3opt = S.evaluar_3opt(arista_ini,indR,indA)
    print(f"ruta {indR[0]}\n V:{S.rutas[indR[0]].getV()} \n A:{S.rutas[indR[0]].getA()} ")
    print(f"ruta {indR[1]}\n V:{S.rutas[indR[1]].getV()} \n A:{S.rutas[indR[1]].getA()} ")
    print(S.controlarCapacidad(indR[0]))
    print(S.controlarCapacidad(indR[1]))
    indR, indA = S.getPosiciones(arista_ini.getOrigen(),arista_ini.getDestino())
    print("costoEvaluado: ", nuevoCosto)
    print("indR: ", indR)
    print("indA: ", indA)
    print("DROP: ", DROP_3opt)
    print("Opcion: ", tipo_3opt)

    S.swap_3opt(arista_ini,indR,indA,tipo_3opt)
    
    print(f"ruta {indR[0]} después de swap \nV:{S.rutas[indR[0]].getV()} \n A:{S.rutas[indR[0]].getA()} ")
    print(f"ruta {indR[1]} después de swap \nV:{S.rutas[indR[1]].getV()} \n A:{S.rutas[indR[1]].getA()} ")
    print(S.controlarCapacidad(indR[0]))
    print(S.controlarCapacidad(indR[1]))
