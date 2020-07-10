from Grafo import Grafo 
from Vertice import Vertice 
from Arista import Arista
import copy
import sys
import random
import math
import numpy as np
from time import time

class Solucion(Grafo):
    def __init__(self, M, Demanda, capacidad):
        super(Solucion, self).__init__(M, Demanda)
        self.__capacidad = capacidad
        self.__capacidadMax = 0

    def __str__(self):
        cad = "\nRecorrido de la solución: " + str(self.getV()) + "\n" + "Aristas de la solución: "+ str(self.getA())
        cad += "\nCosto Asociado: " + str(round(self.getCostoAsociado(),3)) + "        Capacidad: "+ str(self.__capacidad)
        return cad
    def __repr__(self):
        return str(self.getV())
    def __eq__(self, otro):
        return (self._costoAsociado == otro._costoAsociado and self.__class__ == otro.__class__)
    def __ne__(self, otro):
        return (self._costoAsociado != otro._costoAsociado and self.__class__ == otro.__class__)
    def __gt__(self, otro):
        return self._costoAsociado > otro._costoAsociado
    def __lt__(self, otro):
        return self._costoAsociado < otro._costoAsociado
    def __ge__(self, otro):
        return self._costoAsociado >= otro._costoAsociado
    def __le__(self, otro):
        return self._costoAsociado <= otro._costoAsociado
    def __len__(self):
        return len(self._V)
    def setCapacidadMax(self, capMax):
        self.__capacidadMax = capMax
    def setCapacidad(self, capacidad):
        self.__capacidad = capacidad
    def getCapacidad(self):
        return self.__capacidad

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
    def rutasIniciales(self, strSolInicial, nroVehiculos, demandas, capacidad):
        rutas = []
        sol_factible = False
        while(not sol_factible):
            rutas = []
            if(strSolInicial==0):
                R = self.clarkWright(nroVehiculos)
                print("Clark & Wright")
                rutas = self.cargarRutas(R, capacidad)
                print("Clark & Wright")
                sol_factible = True
            elif(strSolInicial==1):
                print("Sol Inicial por Vecino Cercano")
                sol_factible = self.solInicial_VecinoCercano(nroVehiculos, capacidad, demandas, rutas)
                strSolInicial = 3
            elif(strSolInicial == 2):
                secuenciaInd = list(range(1,len(self._matrizDistancias)))
                print("secuencia de indices de los vectores: "+str(secuenciaInd))
                self.cargar_secuencia(secuenciaInd, nroVehiculos, demandas, capacidad, rutas)
            else:
                print("Sol Inicial al azar")
                secuenciaInd = list(range(1,len(self._matrizDistancias)))
                random.shuffle(secuenciaInd)
                self.cargar_secuencia(secuenciaInd, nroVehiculos, demandas, capacidad, rutas)

        return rutas

    #
    def cargar_secuencia(self, secuencia, nroVehiculos, demandas, capacidad, rutas):
        secuenciaInd = secuencia
        sub_secuenciaInd = []
        
        for i in range(0,nroVehiculos):
            #Sin contar la vuelta (x,1)
            #nroVehiculos = 3
            #[1,2,3,4,5,6,7,8,9,10] Lo ideal seria: [1,2,3,4] - [1,5,6,7] - [1,8,9,10]
            sub_secuenciaInd = self.solucion_secuencia(secuenciaInd, capacidad, demandas, nroVehiculos)
            S = Solucion(self._matrizDistancias, self._demanda, 0)
            S.setCapacidadMax(capacidad)
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
    def solucion_secuencia(self, secuenciaInd, capacidad, demandas, nroVehiculos):
        acum_demanda = 0
        sub_secuenciaInd = []
        for x in secuenciaInd:
            value = self.getV()[x].getValue()-1
            if(acum_demanda + demandas[value] <= self.__capacidadMax):
                acum_demanda += demandas[value]
                sub_secuenciaInd.append(x)
                #if (acum_demanda > self.__capacidad/nroVehiculos):
                #    break
        
        return sub_secuenciaInd

    def solInicial_VecinoCercano(self, nroVehiculos, capacidad, demanda, rutas):
        visitados = []
        recorrido = []
        visitados.append(0)    #Agrego el vertice inicial
        
        for j in range(0, nroVehiculos):
            recorrido = []
            masCercano=0
            acum_demanda = 0
            for i in range(0,len(self._matrizDistancias)):
                masCercano = self.vecinoMasCercano(masCercano, visitados, acum_demanda, demanda, capacidad) #obtiene la posicion dela matriz del vecino mas cercano
                if(masCercano != 0):
                    acum_demanda += demanda[masCercano]
                    recorrido.append(masCercano)
                    visitados.append(masCercano)
                if(acum_demanda > self.__capacidad/nroVehiculos):
                    break
                i
            j
            S = Solucion(self._matrizDistancias, self._demanda, 0)
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
        R = []
        #demanda = self._demanda
        
        # for i in range(0,len(rutas)):
        #     print("R #%d: %s" %(i, str(rutas[i])))
        
        for r in rutas:
            S = Solucion(self._matrizDistancias, self._demanda, 0)
            cap = S.cargarDesdeSecuenciaDeVertices(S.cargaVertices(r, False))
            S.setCapacidad(cap)
            S.setCapacidadMax(capacidad)
            R.append(S)
        
        # for i in range(0,len(rutas)):
        #     print("R #%d: %s" %(i, str(R[i].getV())))

        return R

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
        self.__cargaTotal = suma
        return suma

    def removeRuta(self,index,rutas):
        rutas.pop(index) 

    def clarkWright(self, nroVehiculos):
        ahorros = self.obtenerAhorros()
        dem = self._demanda
        rutas = []
        for i in range(2,self.getGrado()+1):
            R = []
            R.append(1)
            R.append(i)
            rutas.append(R)
        
        iteracion = 0
        while(len(ahorros)!=1 and  len(rutas)!=nroVehiculos):
            mejorAhorro = ahorros.pop(0)
            i = self.buscar(mejorAhorro[0],rutas) # i = (r1,c1) índice de la ruta en la que se encuentra 
            j = self.buscar(mejorAhorro[1],rutas) # igual que i
            IesInterno = self.esInterno(mejorAhorro[0],rutas[i[0]])
            JesInterno = self.esInterno(mejorAhorro[1],rutas[j[0]])
            demCliente = dem[mejorAhorro[1]-1]
            if (len(rutas[i[0]]) == 2 and len(rutas[j[0]]) == 2) or (self.estaEnUnRutaNoVacia(i[0],rutas) and not IesInterno and self.estaEnUnRutaNoVacia(j[0],rutas) and not JesInterno and i[0]!=j[0]):
                carga1 = self.cargaTotal(dem,rutas[i[0]])
                carga2 = self.cargaTotal(dem,rutas[j[0]])
                if(carga1 + carga2 <= self.__capacidadMax):
                    self.mezclarRuta(i[0],j[0],rutas)
                    self.removeRuta(j[0],rutas)
            else: 
                if(self.estaEnUnRutaNoVacia(i[0],rutas) and not self.estaEnUnRutaNoVacia(j[0],rutas) and not IesInterno):
                    demCliente = dem[mejorAhorro[1]-1]
                    cargaRuta = self.cargaTotal(dem,rutas[i[0]])
                    if(cargaRuta+demCliente <= self.__capacidadMax):
                        ind = rutas[i[0]].index(mejorAhorro[0])
                        rutas[i[0]].insert(ind+1,mejorAhorro[1])
                        self.removeRuta(j[0],rutas)
                        i = self.buscar(mejorAhorro[0],rutas)
                        IesInterno = self.esInterno(mejorAhorro[0],rutas[i[0]])
                        JesInterno = self.esInterno(mejorAhorro[1],rutas[i[0]])
                elif(self.estaEnUnRutaNoVacia(j[0],rutas) and  not self.estaEnUnRutaNoVacia(i[0],rutas) and not JesInterno):
                    demCliente = dem[mejorAhorro[0]-1]
                    cargaRuta = self.cargaTotal(dem,rutas[j[0]])
                    if(cargaRuta+demCliente <= self.__capacidadMax):
                        if(j[1]==1):
                            rutas[j[0]].insert(1,mejorAhorro[0])
                        else:
                            ind = rutas[j[0]].index(mejorAhorro[1])
                            rutas[j[0]].insert(ind+1,mejorAhorro[0])
                        self.removeRuta(i[0],rutas)
                        j = self.buscar(mejorAhorro[1],rutas)
                        JesInterno = self.esInterno(mejorAhorro[0],rutas[j[0]])
                        IesInterno = self.esInterno(mejorAhorro[1],[j[0]])
            iteracion +=1
        
        return rutas

    def swap(self, k_Opt, aristaIni, rutas_orig, indRutas, indAristas):
        rutas = copy.deepcopy(rutas_orig)
        try:
            print("Opcion: "+str(k_Opt))
            if(k_Opt[0] == 2):
                opcion = k_Opt[1]
                rutas = self.swap_2opt(aristaIni, indRutas, indAristas, rutas, opcion)
            elif(k_Opt[0] == 3):
                opcion = k_Opt[1]
                rutas = self.swap_3opt(aristaIni, indRutas, indAristas, rutas, opcion)
        except IndexError:
            print("Arista Ini: "+str(aristaIni))
            print("indRutas: "+str(indRutas))
            print("indAristas: "+str(indAristas))
            for i in range(0, len(rutas)):
                print("Ruta #%d: %s" %(i, str(rutas[i])))
            print("Opcion: "+str(k_Opt[1]))
            a = 1/0
        #else:
        #    opcion = k_Opt[1]
        #    rutas = self.swap_4opt(aristaIni, indRutas, indAristas, rutas, opcion)
        
        return rutas

    def getPosiciones(self, V_origen, V_destino, rutas):
        ind_verticeOrigen = -1
        ind_verticeDestino = -1
        ind_rutaOrigen = -1
        ind_rutaDestino = -1
        
        #arista_azar = (3,7)    => V_origen = 3 y V_destino = 7
        #Sol:   1-2-3-4-5                  1-6-7-8-9-10   
        #      (1,2)(2,3)(3,4)(4,5)(5,1)   (1,6)(6,7)(7,8)(8,9)(9,10)(10,1)
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

        return [ind_rutaOrigen, ind_rutaDestino],[ind_verticeOrigen, ind_verticeDestino]

    def evaluarOpt(self, lista_permitidos, ind_permitidos, ind_random, rutas):
        kOpt = 0            #2, 3 o 4-opt
        tipo_kOpt = 0       #Las variantes de cada opt's anteriores
        costoSolucion = float("inf")
        nuevoCosto = float("inf")
        indRutas = indAristas = []
        DROP_2opt = DROP_3opt = []
        indDROP_2opt = indDROP_3opt = []
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
            
            indRutas, indAristas = self.getPosiciones(V_origen, V_destino, rutas)
            indR = [indRutas[0], indRutas[1]]
            indA = [indAristas[0], indAristas[1]]
            #tiempo = time()
            nuevoCosto, tipo_2opt, DROP_2opt, indDROP_2opt = self.evaluar_2opt(aristaIni, indR, indA, rutas)
            #print("Tiempo eval2opt: "+str(time()-tiempo))
            if(nuevoCosto < costoSolucion):
                costoSolucion = nuevoCosto
                kOpt = 2
                tipo_kOpt = tipo_2opt
                DROP = DROP_2opt
                indDROP = indDROP_2opt
                
            indR = [indRutas[0], indRutas[1]]
            indA = [indAristas[0], indAristas[1]]
            #tiempo = time()
            nuevoCosto, tipo_3opt, DROP_3opt, indDROP_3opt = self.evaluar_3opt(aristaIni, indR, indA, rutas)
            #print("Tiempo eval3opt: "+str(time()-tiempo))
            if(nuevoCosto < costoSolucion):
                costoSolucion = nuevoCosto
                kOpt = 3
                tipo_kOpt = tipo_3opt
                DROP = DROP_3opt
                indDROP = indDROP_3opt 
            
            # nuevoCosto, tipo_4opt, DROP, indDROP = self.evaluar_4opt(aristaIni, indRutas, indAristas, rutas)
            # if(nuevoCosto < costoSolucion):
            #     costoSolucion = nuevoCosto
            #     kOpt = 4
            #     tipo_kOpt = tipo_4opt
        
        #tiempo = time()
        if(costoSolucion != float("inf")):
            # print("ADD: "+str(ADD))
            # print("DROP: "+str(DROP))
            # print("%d-opt   Opcion: %d" %(kOpt, tipo_kOpt))
            index = [i for i in range(0,len(ind_permitidos)) if ind_permitidos[i] in indDROP or ind_permitidos[i] in indADD]
            ind_permitidos = np.delete(ind_permitidos, index)
        else:
            #print("No se encontro una sol factible")
            ADD = DROP = []
        #print("Tiempo: "+str(time()-tiempo))
        
        return costoSolucion, [kOpt, tipo_kOpt], indRutas, indAristas, ADD, DROP
    
    """
    2-opt:
    
    new_cost = costoSolucion + costo(a,b) + costo(8,4) - costo(a,4) - costo(8,b)
    r1: 1-2-3-a-4-5         r2: 1-6-7-b-8-9-10   -> ruta original
    resultado:
    r1: 1-2-3-a-b-8-9-10    r2: 1-6-7-4-5        -> 1ra opcion
    r1: 1-2-3-8-9-10        r2: 1-6-7-b-a-4-5    -> 2da opcion
    r1: 1-5-4-a-b-8-9-10    r2: 1-2-3-7-6        -> 3ra opcion PENDIENTE 
    r: 1,2,a,3,4,b,5,6     -> ruta original 
    resultado:
    r: 1,2,a,b,4,3,5,6     -> 1ra opcion
    r: 1,6,5,b,a,3,4,2     -> 2da opcion
       1,2,4,3,a,b,5,6
    """
    def swap_2opt(self, arista_ini, ind_rutas, ind_A, rutas, opcion):
        costoSolucion = self.getCostoAsociado()
        ADD = []
        DROP = []
        ADD.append(arista_ini)

        #En distintas rutas(opcion = 0 -> 1ra opcion sino 2da opcion)
        if(opcion==1 or opcion==2):
            if(opcion==1):
                r1 = rutas[ind_rutas[0]]
                r2 = rutas[ind_rutas[1]]
            else:
                r2 = rutas[ind_rutas[0]]
                r1 = rutas[ind_rutas[1]]
                j = ind_A[0]
                ind_A[0] = ind_A[1] +1          #=> La posicion de 'a' es en donde la arista tiene como origen 'a' (+1)
                ind_A[1] = j -1             	#=> La posicion de 'b' es en donde la arista tiene como destino 'b'(-1)
                ADD = []
                arista_ini.invertir()
                ADD.append(arista_ini)
            costoSolucion -= r1.getCostoAsociado() + r2.getCostoAsociado()

            A_r1_left = r1.getA()[:ind_A[0]]
            A_r1_right = r1.getA()[ind_A[0]+1:]
            
            A_r2_left = r2.getA()[:ind_A[1]]
            A_r2_right = r2.getA()[ind_A[1]+1:]
            
            A_r1_drop = r1.getA()[ind_A[0]]
            A_r2_drop = r2.getA()[ind_A[1]]
            
            if(A_r2_left!=[]):
                V_origen = A_r2_left[-1].getDestino()
            #En caso de que la arista al azar se encuentra al principio
            else:
                V_origen = Vertice(1,0)
            
            if(A_r1_right!=[]):
                V_destino = A_r1_right[0].getOrigen()
            #En caso de que la arista al azar se encuentra al final
            else:
                V_destino = Vertice(1,0)
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add = Arista(V_origen,V_destino, peso)   # => (6,4, peso)
            A_r_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

            ADD.append(A_r_add)
            DROP.append(A_r1_drop)
            DROP.append(A_r2_drop)
            
            A_r1_left.append(ADD[0])
            A_r1_left.extend(A_r2_right)
            A_r2_left.append(ADD[1])
            A_r2_left.extend(A_r1_right)
            
            cap_r1 = r1.cargarDesdeAristas(A_r1_left)
            cap_r2 = r2.cargarDesdeAristas(A_r2_left)
            r1.setCapacidad(cap_r1)
            r2.setCapacidad(cap_r2)

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
        
            A_r_drop1 = r.getA()[ind_A[0]]
            A_r_drop2 = r.getA()[ind_A[1]+1]

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
            
            cap = r.cargarDesdeSecuenciaDeVertices(V_r)
            r.setCapacidad(cap)
            costoSolucion += r.getCostoAsociado()
        
        return rutas
    
    #Distintas rutas. opcion = 1 (1ra opcion); opcion(=2)  - Misma ruta: 1ra opcion(-1) = -2 --> Misma ruta(2da opcion)
    def evaluar_2opt(self, aristaIni, ind_rutas, ind_A, rutas):
        opcion = 0
        costo_solucion = float("inf")
        costo_r_add1 = aristaIni.getPeso()
        
        DROP = []
        index_DROP = []

        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            A_r1 = r1.getA()
            A_r2 = r2.getA()
            
            for i in range(1,3):
                if(i==2):
                    #print("2da opcion")
                    r1 = rutas[ind_rutas[1]]
                    r2 = rutas[ind_rutas[0]]
                    a = A_r1
                    A_r1 = A_r2
                    A_r2 = a
                    j = ind_A[0]
                    ind_A[0] = ind_A[1] +1          #=> La posicion de 'a' es en donde la arista tiene como origen 'a' (+1)
                    ind_A[1] = j -1             	#=> La posicion de 'b' es en donde la arista tiene como destino 'b'(-1)
            
                #else:
                    #print("1ra opcion")
                #r1: 1-2-3-a-4-5
                #left: 1-2-3-a      right: 4-5
                #A_r1_left = r1.getA()[:ind_A[0]]
                A_r1_right = A_r1[ind_A[0]+1:]
                #print("A_r1_right: "+str(A_r1_right))
                #r2: 1-6-7-b-8-9-10
                #left: 1-6-7        right: 8-9-10
                A_r2_left = A_r2[:ind_A[1]]
                #print("A_r2_left: "+str(A_r2_left))
                #Caso no factible por ej:
                #r1: 1-2-3-4-5-a    r2: 1-b-6-7-8-9-10  -> Sol: r1: 1-2-3-4-5-a-b-6-7-8-9-10    r2: 1
                if(A_r1_right==[] and A_r2_left==[]):
                    continue
                
                r1DemandaAcumulada = r1.getDemandaAcumulada()
                #print("Demanda acumulada: "+str(r1DemandaAcumulada))
                r2DemandaAcumulada = r2.getDemandaAcumulada()
                #print("Demanda acumulada: "+str(r2DemandaAcumulada))
                
                #print("cap_r1: ",r1.getCapacidad())
                cap_r1_left = r1DemandaAcumulada[ind_A[0]]
                cap_r1_right = r1DemandaAcumulada[-1] - cap_r1_left
                #print("cap_r1_left: ",cap_r1_left)
                #print("cap_r1_right: ",cap_r1_right)
                
                #print("cap_r2: ",r2.getCapacidad())
                cap_r2_left = r2DemandaAcumulada[ind_A[1]]
                cap_r2_right = r2DemandaAcumulada[-1] - cap_r2_left
                # print("cap_r2_left: ",cap_r2_left)
                # print("cap_r2_right: ",cap_r2_right)
                
                cap_r1 = cap_r1_left + cap_r2_right
                cap_r2 = cap_r2_left + cap_r1_right
                #print("New cap_r1: ",cap_r1)
                #print("New cap_r2: ",cap_r2)
                if(cap_r1 > self.__capacidadMax or cap_r2 > self.__capacidadMax):
                    continue
                
                A_r1_drop = A_r1[ind_A[0]]
                #print("A_r1_drop"+str(A_r1_drop))
                #cap_r1_drop = A_r1_drop.getOrigen().getDemanda() + A_r1_drop.getDestino().getDemanda()
                
                A_r2_drop = A_r2[ind_A[1]]
                #print("A_r2_drop"+str(A_r2_drop))
                #cap_r2_drop = A_r2_drop.getOrigen().getDemanda() + A_r2_drop.getDestino().getDemanda()
                
                #vertice 'a' de la arista (a,b) no se encuentra al principio
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
                costo_r2_add = peso

                #print("Costo anterior: ", self.getCostoAsociado())
                nuevo_costo = self.getCostoAsociado() + costo_r_add1 + costo_r2_add - costo_r1_drop - costo_r2_drop
                if(nuevo_costo < costo_solucion):
                    costo_solucion = nuevo_costo
                    opcion = i
                    DROP = []
                    DROP.append(A_r1_drop)
                    DROP.append(A_r2_drop)
                    index_DROP = []
                    index_DROP.append(A_r1_drop.getId())
                    index_DROP.append(A_r2_drop.getId())
            # print("DROP: "+str(DROP))
            # print("indexDROP: "+str(index_DROP))
        else:
            #En la misma ruta hay factibilidad, por lo tanto se calcula unicamente el costo
            r = rutas[ind_rutas[0]]
            V_r = r.getV()
            V_r.append(Vertice(1,0))
            A_r = r.getA()
            #print("V_r: "+str(V_r))
            
            #r: 1,2,a,3,4,b,5,6,1     -> Ruta original
            #Sol:
            #r: 1,2,a,b,4,3,5,6,1     -> 1ra opcion
            #r: 1,6,5,b,4,3,a,2,1     -> Ruta original invertida
            #Sol:
            #r: 1,6,5,b,a,3,4,2,1     -> 2da opcion
            for i in range(1,3):
                if(i==2):
                    # a = 1
                    #r: a,2,3,4,5,b,6,1     -> Ruta original
                    #r: a,b,5,4,3,2,6,1     -> 1ra opcion        
                    #r: 1,6,b,5,4,3,2,a     -> Ruta original invertida
                    #r: 1,6,b,a,2,3,4,5     -> 2da opcion. No se puede xq a = 1        
                    # a o b no pueden ser igual a 1 para la segunda opcion
                    if(0 in ind_A):
                        continue
                    V_r = V_r[::-1]
                    lenV = len(V_r) - 2  #Resto en 2 x la vuelta y xq el indice en la lista empieza en 0
                    ind_a = lenV - ind_A[0]
                    ind_b = lenV - ind_A[1]
                    ind_A = [ind_b, ind_a]
                    
                    V_origen = V_r[ind_A[0]+1]
                    V_destino = V_r[ind_A[0]]
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_drop1 = Arista(V_origen, V_destino, peso)
                    A_r_drop1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    costo_r_drop1 = A_r_drop1.getPeso()
                    
                    V_origen = V_r[ind_A[1]+2]
                    V_destino = V_r[ind_A[1]+1]
                    peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                    A_r_drop2 = Arista(V_origen, V_destino, peso)
                    A_r_drop2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                    costo_r_drop2 = A_r_drop2.getPeso()
                else:
                    A_r_drop1 = A_r[ind_A[0]]
                    costo_r_drop1 = A_r_drop1.getPeso()
                    A_r_drop2 = A_r[ind_A[1]+1]
                    costo_r_drop2 = A_r_drop2.getPeso()

                V_r_middle = V_r[ind_A[0]+1:ind_A[1]+1]
                V_r_right = V_r[ind_A[1]+2:]
            
                V_origen = V_r_middle[0]
                V_destino = V_r_right[0]
                peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                #A_r_add2 = Arista(V_origen, V_destino, peso)
                costo_r_add2 = peso

                nuevo_costo = self.getCostoAsociado() + costo_r_add1 + costo_r_add2 - costo_r_drop1 - costo_r_drop2
                
                if(nuevo_costo < costo_solucion):
                    costo_solucion = nuevo_costo
                    opcion = i*(-1)
                    DROP = []
                    DROP.append(A_r_drop1)
                    DROP.append(A_r_drop2)
                    index_DROP = []
                    index_DROP.append(A_r_drop1.getId())
                    index_DROP.append(A_r_drop2.getId())
            #if(opcion)
            #print("V_r: "+str(r.getV()))
            V_r = r.getV()
            V_r = V_r[:-1]
            r.setV(V_r)
            
            #print("DROP: "+str(DROP))
            #print("indexDROP: "+str(index_DROP))
            #print("ADD: [%s, %s]" %(str(aristaIni), str(A_r_add2)))

            #print("V_r: "+str(r.getV()))
            #print("tiempo empleado: "+str(time()-tiempo))            
        #print("Costo en evaluar 2-opt: ", costo_solucion)

        return costo_solucion, opcion, DROP, index_DROP
    
    """
    new_cost = costoSolucion + costo(a,b) + costo(b,4) + costo(8,9) - costo(a,4) - costo(8,b) - costo(b,9) 
    (a,b)
    3-opt
    r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10,11,12
    costoSolucion = 300
    resultado:
    r1: 1,2,3,a,b,4,5,6          r2: 1,7,8,9,10,11,12       -> 1ra opcion
    r1: 1,2,3,b,a,4,5,6          r2: 1,7,8,9,10,11,12       -> 2da opcion PENDIENTE
    r1: 1,2,3,4,5,6              r2: 1,7,8,a,b,9,10,11,12   -> 3ra opcion PENDIENTE
    r1: 1,2,3,4,5,6              r2: 1,7,8,b,a,9,10,11,12   -> 4ta opcion PENDIENTE
    r1: 1,2,3,a,b,9,4,5,6        r2: 1,7,8,10,11,12         -> 5ta opcion PENDIENTE, si llegamos
    r1: 1,2,3,8,b,a,4,5,6        r2: 1,7,9,10,11,12         -> 6ta opcion PENDIENTE, si llegamos
    ... (y muchos mas!) ...
    r: 1,2,a,3,4,5,b,6,7,8      -> ruta original 
    resultado:
    r: 1,2,a,b,3,4,5,6,7,8      -> 1ra opcion
    r: 1,2,b,a,3,4,5,6,7,8      -> 2da opcion
    r: 1,2,3,4,5,b,a,6,7,8      -> 3ra opcion
    r: 1,2,3,4,5,a,b,6,7,8      -> 4ta opcion
    """
    def swap_3opt(self, arista_ini, ind_rutas, ind_A, rutas, opcion):
        costoSolucion = self.getCostoAsociado()
        
        #print("Swap por 3opt")
        #print("Arista ini: "+str(arista_ini))
        # cad = "\nRutas:"
        # for i in ind_rutas:
        #     cad += "\nruta #%d: %s" %(i, rutas[i])
        # print(cad)
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
            cap_r1 = r1.cargarDesdeAristas(A_r1_left)
            cap_r2 = r2.cargarDesdeAristas(A_r2_left)
            r1.setCapacidad(cap_r1)
            r2.setCapacidad(cap_r2)
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
        #     print("Swap 3-opt")
        #     print("cap r: ",cap_r)
        #     print("r: "+str(r.getV()) + "      -> costo: "+str(r.getCostoAsociado()))  
        
        # print("Costo solucion en SWAP: ", costoSolucion)

        return rutas

    def evaluar_3opt(self, aristaIni, ind_rutas, ind_A, rutas):
        sol_factible_12 = sol_factible_34 = False
        #Opcion: 0 (1ra opcion) | 1 (2da opcion) | 3 (3ra opcion) | 4 (4ta opcion)
        #Misma ruta: -1(1ra opcion) | -2 (2da opcion) | -3 (3ra opcion) | -4 (4ta opcion)
        opcion = 0  
        costo_solucion = float("inf")
        costo_r_add1 = aristaIni.getPeso()

        DROP = []
        index_DROP = []

        #3-opt Distintas rutas
        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]

            #Evaluar la factibilidad en las distintas opciones
            cap_r1 = r1.getCapacidad() + aristaIni.getDestino().getDemanda()
            if(cap_r1 <= self.__capacidadMax):
                sol_factible_12 = True
            #else:
            #    print("Sol no factible. 3-opt 1ra y 2da opcion")
            
            cap_r2 = r2.getCapacidad() + aristaIni.getOrigen().getDemanda()
            if(cap_r2 <= self.__capacidadMax):
                sol_factible_34 = True
            # else:
            #     print("Sol no factible. 3-opt 3ra y 4ta opcion")
            
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
                    #A_r1_add = Arista(V_origen, V_destino, peso)
                    #print("A_r1_add: "+str(A_r1_add))
                    costo_r1_add = peso

                    if(i==3):
                        A_r2_drop = r2.getA()[ind_A[1]]
                        costo_r2_drop = A_r2_drop.getPeso()
                    
                        V_origen = r2.getA()[ind_A[1]].getOrigen()
                        V_destino = r1.getA()[ind_A[0]-1].getDestino()
                        peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                        #A_r2_add = Arista(V_origen, V_destino, peso)
                        #A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                        #print("A_r2_add: "+str(A_r2_add))
                        costo_r2_add = peso
                    else:
                        A_r2_drop = r2.getA()[ind_A[1]+1]
                        costo_r2_drop = A_r2_drop.getPeso()
                    
                        V_origen = r1.getA()[ind_A[0]-1].getDestino()
                        V_destino = r2.getA()[ind_A[1]+1].getDestino()
                        peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                        #A_r2_add = Arista(V_origen, V_destino, peso)
                        #print("A_r2_add: "+str(A_r2_add))
                        costo_r2_add = peso

                    nuevo_costo = self.getCostoAsociado() + costo_r_add1 + costo_r1_add + costo_r2_add - costo_r1_drop1 - costo_r1_drop2 - costo_r2_drop
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
                    #A_r1_add = Arista(V_origen, V_destino, peso)
                    #print("A_r1_add: "+str(A_r1_add))
                    costo_r1_add = peso

                    if(i==1):
                        A_r2_drop = A_r2[ind_A[1]]
                        costo_r2_drop = A_r2_drop.getPeso()
                    
                        V_origen = A_r2[ind_A[1]].getOrigen()
                        V_destino = r1.getA()[ind_A[0]-1].getDestino()
                        peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                        #A_r2_add = Arista(V_origen, V_destino, peso)
                        #print("A_r2_add: "+str(A_r2_add))
                        #A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                        costo_r2_add = peso
                    else:
                        A_r2_drop = A_r2[ind_A[1]+1]
                        costo_r2_drop = A_r2_drop.getPeso()
                    
                        V_origen = r1.getA()[ind_A[0]-1].getDestino()
                        V_destino = A_r2[ind_A[1]+1].getDestino()
                        peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                        #A_r2_add = Arista(V_origen, V_destino, peso)
                        #print("A_r2_add: "+str(A_r2_add))
                        costo_r2_add = peso

                    nuevo_costo = self.getCostoAsociado() + costo_r_add1 + costo_r1_add + costo_r2_add - costo_r1_drop1 - costo_r1_drop2 - costo_r2_drop
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
                    #print("\n3ra y 4ta opcion")
                    if(0 in ind_A):
                        continue
                    ind_A[0] = ind_A[0]-1
                    ind_A[1] = ind_A[1]+1
                    V_r_left = V_r[:ind_A[0]+1]
                #else:
                    #print("\n1ra y 2da opcion")
                
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
                            #print("A_r_add2: "+str(A_r_add2))
                            #print("A_r_add3: "+str(A_r_add3))
                        elif(i==2 and 0 not in ind_A):
                            A_r_drop1 = r.getA()[ind_A[0]-1]
                            costo_r_drop1 = A_r_drop1.getPeso()
                            
                            V_origen = V_r[ind_A[0]-1]
                            V_destino = V_r[ind_A[1]+1]
                            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                            A_r_add3 = Arista(V_origen,V_destino, peso)
                            A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                            costo_r_add3 = peso                    
                            #print("A_r_add2: "+str(A_r_add2))
                            #print("A_r_add3: "+str(A_r_add3))
                        nuevo_costo = self.getCostoAsociado() + costo_r_add1 + costo_r_add2 + costo_r_add3 - costo_r_drop1 - costo_r_drop2 - costo_r_drop3
                        #print("Costo anterior: ", self.getCostoAsociado())
                        #print("Nuevo costo: ", nuevo_costo)
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
                            #print("A_r_add2: "+str(A_r_add2))
                            #print("A_r_add3: "+str(A_r_add3))
                        else:
                            A_r_drop1 = r.getA()[ind_A[1]-1]
                            costo_r_drop1 = A_r_drop1.getPeso()
                            
                            V_destino = V_r[ind_A[0]+1]
                            V_origen = V_r[ind_A[1]-1]
                            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
                            A_r_add3 = Arista(V_origen,V_destino, peso)
                            A_r_add3.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
                            costo_r_add3 = peso                    
                            #print("A_r_add2: "+str(A_r_add2))
                            #print("A_r_add3: "+str(A_r_add3))
                        nuevo_costo = self.getCostoAsociado() + costo_r_add1 + costo_r_add2 + costo_r_add3 - costo_r_drop1 - costo_r_drop2 - costo_r_drop3
                        #print("Costo anterior: ", self.getCostoAsociado())
                        #print("Nuevo costo: ", nuevo_costo)
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
            V_r = r.getV()
            V_r = V_r[:-1]
            r.setV(V_r)
        
        return costo_solucion, opcion, DROP, index_DROP
        
    """
    (a,b)
    4-opt
    r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10
    r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10   
    
    resultado:
    r1: 1,2,3,a,b,5,6          r2: 1,7,8,4,9,10             -> 1ra opcion
    r1: 1,2,b,a,4,5,6          r2: 1,7,8,3,9,10             -> 2da opcion PENDIENTE
    r1: 1,2,3,8,4,5,6          r2: 1,7,a,b,9,10             -> 3ra opcion PENDIENTE
    r1: 1,2,3,9,4,5,6          r2: 1,7,8,b,a,10             -> 4ta opcion PENDIENTE

    r: 1,2,3,a,4,5,b,6,7

    new_costR1 = 123 + costo(a,b) + costo(b,5) - costo(a,4) - costo(4,5)
    new_costR2 = 150 + costo(8,4) + costo(4,9) - costo(8,b) - costo(b,9)
    """
    def evaluar_4opt(self, lista_permitidos, ind_permitidos, ind, rutas_orig):
        """
        (a,b)
        4-opt
        r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10,11,12   -> ruta original
        costoR1 = 123               costoR2 = 150
        resultado:
        r1: 1,2,3,a,b,5,6        r2: 1,7,8,4,9,10,11,12     -> 1ra opcion Si!
        r1: 1,2,b,a,4,5,6        r2: 1,7,8,3,9,10,11,12     -> 2da opcion No
        r1: 1,2,3,8,4,5,6        r2: 1,7,a,b,9,10,11,12     -> 3ra opcion No
        r1: 1,7,8,b,a,10,11,12   r2: 1,2,3,9,4,5,6          -> 4ta opcion PENDIENTE :D

        new_costR1 = 123 + costo(a,b) + costo(b,5) - costo(a,4) - costo(4,5)
        new_costR2 = 150 + costo(8,4) + costo(4,9) - costo(8,b) - costo(b,9)
        
        r: 1,2,3,a,4,5,6,b,7,8  -> Original
        
        resultado:
        r: 1,2,3,a,b,5,6,4,7,8  -> 1ra opcion
        r: 1,2,b,a,4,5,6,3,7,8  -> 2da opcion
        r: 1,2,3,6,4,5,a,b,7,8  -> 3ra opcion
        r: 1,2,3,7,4,5,6,b,a,8  -> 4ta opcion        
        """
        sol_factible = False
        rutas = rutas_orig
        costo_solucion = self.getCostoAsociado()
        ADD = []
        index_ADD = []
        DROP = []
        index_DROP = []
        
        arista_ini = lista_permitidos[ind_permitidos[ind]]

        ADD.append(arista_ini)
        index_ADD.append(arista_ini.getId())

        V_origen = arista_ini.getOrigen()
        V_destino = arista_ini.getDestino()
                
        ind_rutas, ind_A = self.getPosiciones(V_origen, V_destino, rutas_orig)
        #Cada ruta de al menos 4 aristas o 3 clientes. Si a o b estan al final: los intercambio
        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            
            if(len(r1.getV()) <= 3 or len(r2.getV())<=3):
                return [], [], [], 0, [], []
            
            costo_solucion -= r1.getCostoAsociado()+r2.getCostoAsociado()

            V_r1 = r1.getV()
            V_r1.append(Vertice(1,0))
            
            if(V_origen == V_r1[-2]):
                V_r1 = V_r1[::-1]
                ind_A[0] = 1
            
            V_r2 = r2.getV()
            V_r2.append(Vertice(1,0))
            if(V_destino == V_r2[-2]):
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
            pesoDROP1 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]


            #2do DROP
            V_origen = V_destino
            try:
                V_destino = V_r1[ind_A[0]+2]
            except IndexError:
                print("r1: "+str(r1))
                print("r2: "+str(r2))
                print("rutas:"+str(rutas))
                print("V_r1: "+str(V_r1))
                print("ind_A: " +str(ind_A[0]))

            pesoDROP2 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]

            
            #2do ADD
            V_origen = ADD[0].getDestino()
            pesoADD2 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            
            #3er DROP
            V_origen = V_r2[ind_A[1]]
            V_destino = V_r2[ind_A[1]+1]
            pesoDROP3 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]

            #3er ADD
            V_destino = V_r1[ind_A[0]+1]
            pesoADD3 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]

            
            #4to DROP
            V_origen = V_r2[ind_A[1]+1]
            V_destino = V_r2[ind_A[1]+2]
            pesoDROP4 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            
            #4to ADD
            V_origen = A_r2_add1.getDestino()
            pesoADD4 = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r2_add2 = Arista(V_origen, V_destino, peso)

            capacidadR1 = sumaDemandaRuta(demanda,r1.getV())
            capacidadR2 = sumaDemandaRuta(demanda,r2.getV())
            capacidadR1 = V_destino.getDemanda() - V_r1[ind_A[0]+1]
            capacidadR2 -= V_destino.getDemanda() + V_r1[ind_A[0]+1]
 
            if(cap_r1 > self.__capacidadMax or cap_r2 > self.__capacidadMax):
                rutas = []
            else:
                sol_factible = True
                nuevoCostoR1 = r1.getCostoAsociado() + pesoADD2 - pesoDROP1 - pesoDROP2 
                nuevoCostoR1 = r2.getCostoAsociado() + pesoADD3 + pesoADD4 - pesoDROP3- pesoDROP4   

            return nuevoCostoR1 + nuevoCostoR2   
        #4-opt en la misma ruta. Condicion: Deben haber 4 aristas de separacion entre a y b, si no se realiza 2-opt
        else:
            r = rutas[ind_rutas[0]]
            costo_solucion -= r.getCostoAsociado()

            V_r = r.getV()
            V_r.append(Vertice(1,0))
            
            #Descompongo la ruta
            V_r_left = V_r[:ind_A[0]+1]                #1-2-a
            V_r_middle = V_r[ind_A[0]+2:ind_A[1]+1]    #3-4
            V_r_right = V_r[ind_A[1]+2:]               #b-5-6-7
            
            A_r_drop1 = r.getA()[ind_A[0]]
            A_r_drop2 = r.getA()[ind_A[0]+1]
            A_r_drop3 = r.getA()[ind_A[1]]
            A_r_drop4 = r.getA()[ind_A[1]+1]
            
            #Obtengo las otras aristas ADD
            V_origen = V_destino
            V_destino = A_r_drop1.getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add1 = Arista(V_origen,V_destino, peso)
            
            V_origen = A_r_drop3.getOrigen()
            V_destino = A_r_drop1.getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add2 = Arista(V_origen,V_destino, peso)
            
            V_origen = V_destino
            V_destino = V_r_right[0]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add3 = Arista(V_origen,V_destino, peso)
            
            if(len(V_r_middle)>=2):
                nuevoCostoR =  r.getCostoAsociado() + A_r_add1.getPeso() + A_r_add2.getPeso() + A_r_add3.getPeso()
                nuevoCostoR -=   A_r_drop1.getPeso() + A_r_drop2.getPeso() + A_r_drop3.getPeso() + A_r_drop4.getPeso()
                return nuevoCostoR
            else:
                #print("Se aplica 2-opt ya que solo existe una arista intermedia para hacer el swap")
                nuevoCostoR =  r.getCostoAsociado() + A_r_add3.getPeso() + A_r_drop1.getPeso() + A_r_drop4.getPeso()
                return nuevoCostoR 
     
    def swap_4opt(self, lista_permitidos, ind_permitidos, ind_random, rutas_orig):
        sol_factible = False
        rutas = rutas_orig
        costo_solucion = self.getCostoAsociado()
        ADD = []
        index_ADD = []
        DROP = []
        index_DROP = []
        
        ind = ind_random[-1]
        arista_ini = lista_permitidos[ind_permitidos[ind]]
        ind_random = ind_random[:-1]

        ADD.append(arista_ini)
        index_ADD.append(arista_ini.getId())

        V_origen = arista_ini.getOrigen()
        V_destino = arista_ini.getDestino()
        
        rutas = copy.deepcopy(rutas_orig)
        
        ind_rutas, ind_A = self.getPosiciones(V_origen, V_destino, rutas_orig)
        #Cada ruta de al menos 4 aristas o 3 clientes. Si a o b estan al final: los intercambio
        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            
            if(len(r1.getV()) <= 3 or len(r2.getV())<=3):
                return [], [], [], 0, [], []
            
            costo_solucion -= r1.getCostoAsociado()+r2.getCostoAsociado()
            #Sol: 1-2-3-a-4   1-5-6-7-8-b
            #1-2-3-a-b    1-5-6-7-8-4   ADD (a,b)(8,4) DROP (a,4)(8,b)
            #Sol: 1-2-3-4-a   1-5-6-7-8-b
            #1-2-3-4-a-b    1-5-6-7-8   ADD (a,b)(8,1) DROP (a,1)(8,b)
            #Sol: 1-2-3-4-a   1-5-6-7-b-8
            #1-2-3-4-a-b    1-5-6-7-8   ADD (a,b)(7,8) DROP (a,1)(7,b)(b,8)
            #Sol: 1-a-2-3-4   1-5-6-7-8-b
            #(a,b)
            #Sol_nueva:    1-a-b-3-4         1-5-6-7-8-2
            #=>   DROP                ADD
            #     (a,2) que ahora es (a,b)
            #     (2,3) que ahora es (b,3)
            #     (8,b) que ahora es (8,2)
            #     (b,1) que ahora es (2,1)
            #ind_A[0]=1    ind_A[1]=4
            #Descompongo las aristas con respecto al vertice "a"
            #Ruta 1 y 2
            #1 y 3-4         1-5-6-7-8 y 1
            V_r1 = r1.getV()
            V_r1.append(Vertice(1,0))
            
            if(V_origen == V_r1[-2]):
                V_r1 = V_r1[::-1]
                ind_A[0] = 1
            
            V_r2 = r2.getV()
            V_r2.append(Vertice(1,0))
            if(V_destino == V_r2[-2]):
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
            try:
                V_destino = V_r1[ind_A[0]+2]
            except IndexError:
                print("r1: "+str(r1))
                print("r2: "+str(r2))
                print("rutas:"+str(rutas))
                print("V_r1: "+str(V_r1))
                print("ind_A: " +str(ind_A[0]))

            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r1_drop2 = Arista(V_origen, V_destino, peso)
            A_r1_drop2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            #2do ADD
            V_origen = ADD[0].getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r1_add2 = Arista(V_origen, V_destino, peso)
            
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
            
            DROP.append(A_r1_drop1)
            DROP.append(A_r1_drop2)
            DROP.append(A_r2_drop1)
            DROP.append(A_r2_drop2)
            index_DROP.append(A_r1_drop1.getId())
            index_DROP.append(A_r1_drop2.getId())
            index_DROP.append(A_r2_drop1.getId())
            index_DROP.append(A_r2_drop2.getId())

            ADD.append(A_r1_add2)
            ADD.append(A_r2_add1)
            ADD.append(A_r2_add2)

            V_r1_left.append(ADD[0].getDestino())
            V_r1_left.extend(V_r1_right)
            V_r2_left.append(ADD[2].getDestino())
            V_r2_left.extend(V_r2_right)
            
            cap_r1 = r1.cargarDesdeSecuenciaDeVertices(V_r1_left[:-1])
            cap_r2 = r2.cargarDesdeSecuenciaDeVertices(V_r2_left[:-1])
            
            r1.setCapacidad(cap_r1)
            r2.setCapacidad(cap_r2)
            
            if(cap_r1 > self.__capacidadMax or cap_r2 > self.__capacidadMax):
                rutas = []
            else:
                sol_factible = True
                costo_solucion += r1.getCostoAsociado() + r2.getCostoAsociado()
        #4-opt en la misma ruta. Condicion: Deben haber 4 aristas de separacion entre a y b, si no se realiza 2-opt
        else:
            #1-2-a-3-4-5-6-b-7
            #(a,b)  1-2-a-b-4-5-6-3-7
            #=>  ADD     DROP
            #   (a,b)   (a,3)
            #   (b,4)   (3,4)
            #   (6,3)   (6,b)
            #   (3,7)   (b,7)
            r = rutas[ind_rutas[0]]
            costo_solucion -= r.getCostoAsociado()

            V_r = r.getV()
            V_r.append(Vertice(1,0))
            
            #Descompongo la ruta
            V_r_left = V_r[:ind_A[0]+1]                #1-2-a
            V_r_middle = V_r[ind_A[0]+2:ind_A[1]+1]    #3-4
            V_r_right = V_r[ind_A[1]+2:]               #b-5-6-7
            
            A_r_drop1 = r.getA()[ind_A[0]]
            A_r_drop2 = r.getA()[ind_A[0]+1]
            A_r_drop3 = r.getA()[ind_A[1]]
            A_r_drop4 = r.getA()[ind_A[1]+1]
            
            #Obtengo las otras aristas ADD
            V_origen = V_destino
            V_destino = A_r_drop1.getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add1 = Arista(V_origen,V_destino, peso)
            
            V_origen = A_r_drop3.getOrigen()
            V_destino = A_r_drop1.getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add2 = Arista(V_origen,V_destino, peso)
            
            V_origen = V_destino
            V_destino = V_r_right[0]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add3 = Arista(V_origen,V_destino, peso)
            
            if(len(V_r_middle)>=2):
                ADD.append(A_r_add1)
                ADD.append(A_r_add2)
                ADD.append(A_r_add3)
                DROP.append(A_r_drop1)
                DROP.append(A_r_drop2)
                DROP.append(A_r_drop3)
                DROP.append(A_r_drop4)

                index_DROP.append(A_r_drop1.getId())
                index_DROP.append(A_r_drop2.getId())
                index_DROP.append(A_r_drop3.getId())
                index_DROP.append(A_r_drop4.getId())
            else:
                #print("Se aplica 2-opt ya que solo existe una arista intermedia para hacer el swap")
                ADD.append(A_r_add3)
                DROP.append(A_r_drop1)
                DROP.append(A_r_drop4)
                index_DROP.append(A_r_drop1.getId())
                index_DROP.append(A_r_drop4.getId())

            V_r_left.append(A_r_drop4.getOrigen())
            V_r_left.extend(V_r_middle)
            V_r_left.append(A_r_add3.getOrigen())
            V_r_left.extend(V_r_right)
            V_r = V_r_left[:-1]
            
            cap = r.cargarDesdeSecuenciaDeVertices(V_r)
            r.setCapacidad(cap)
            if(cap > self.__capacidadMax):
                rutas = []
            else:
                sol_factible = True
                costo_solucion += r.getCostoAsociado()
        #Fin del while (se encontro una solucion factible)
        if (not sol_factible):
            return [], [], [], 0, [], []

        # for i in range(0,len(ADD)):
        #     print("ADD[%d]: %s      --> ADDid=%d    y indexADD=%s" %(i, str(ADD[i]), ADD[i].getId(), str(lista_permitidos[index_ADD[0]])))
        #     print("DROP[%d]: %s     --> DROPid=%d   y indexDROP=%d" %(i, str(DROP[i]), DROP[i].getId(), index_DROP[i]))

        # for i in ind_permitidos:
        #     print("Arista %d: %s" %(i, str(lista_permitidos[i])))
        
        #index = [i for i in range(0,len(ind_permitidos)) if ind_permitidos[i] in index_DROP or ind_permitidos[i] in index_ADD]
        #ind_permitidos = np.delete(ind_permitidos, index)
        
        # print("\n\nAhora:")
        # for i in ind_permitidos:
        #     print("Arista %d: %s" %(i, str(lista_permitidos[i])))
        
        return rutas, ADD[:1], DROP, costo_solucion, index_ADD, index_DROP

