from Grafo import Grafo 
from Vertice import Vertice 
from Arista import Arista
import copy
import sys
import random
import math
import numpy as np

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

    def getCopyVacio(self):
        ret = Solucion([], [], 0)
        ret.setMatriz(self.getMatriz())
        return ret

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
                print("Clark & Wright")
                R = self.clarkWright(nroVehiculos)
                rutas = self.cargarRutas(R)
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
            cap = S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+sub_secuenciaInd))
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
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+recorrido))
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

    #Clark y Wright
    def cargarRutas(self, rutas):
        R = []
        demanda = self._demanda
        for r in rutas:
            S = Solucion(self._matrizDistancias, self._demanda, 0)
            S.setCapacidadMax(self.__capacidadMax)
            V = []
            for i in r:
                V.append(Vertice(i,demanda[i-1]))
            cap = S.cargarDesdeSecuenciaDeVertices(V)
            S.setCapacidad(cap)
            R.append(S)

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

    def mezclarAristas(self, indDROP2opt, aristasDROP2opt, indDROP3opt, aristasDROP3opt, indDROP4opt, aristasDROP4opt):
        cond = False
        aristasDROP = []
        indDROP = []
        
        if(aristasDROP2opt != []):
            indDROP.extend(indDROP2opt)
            aristasDROP.extend(aristasDROP2opt)
        if(aristasDROP3opt != []):
            indDROP.extend(indDROP3opt)
            if(aristasDROP != []):
                for a_Drop3 in aristasDROP3opt:
                    repetido = False
                    for a in aristasDROP:
                        if(a_Drop3 == a):
                            repetido = True
                            break
                    if(not repetido):
                        aristasDROP.append(a_Drop3)
        if(aristasDROP4opt != []):
            indDROP.extend(indDROP4opt)
            if(aristasDROP != []):
                for a_Drop4 in aristasDROP4opt:
                    repetido = False
                    for a in aristasDROP:
                        if(a_Drop3 == a):
                            repetido = True
                            break
                    if(not repetido):
                        aristasDROP.append(a_Drop3)
        
        return indDROP, aristasDROP

    def swap(self, lista_permitidos, ind_permitidos, ind_random, rutas_orig, condOptim):
        rutas2opt = rutas3opt = rutas4opt = []
        aristasADD = []
        aristasDROP = []
        indDROP = []
        aristasDROP2opt = aristasDROP3opt = aristasDROP4opt = []
        costo2opt = costo3opt = costo4opt = 0

        while(rutas2opt==[] and rutas3opt==[] and rutas4opt==[] and ind_random!=[]):
            ind = ind_random[-1:]
            ind_random = ind_random[:-1]
            rutas2opt, aristasADD, aristasDROP2opt, costo2opt, indADD, indDROP2opt = self.swap_2opt(lista_permitidos, ind_permitidos, ind, rutas_orig)
            rutas3opt, aristasADD, aristasDROP3opt, costo3opt, indADD, indDROP3opt = self.swap_3opt(lista_permitidos, ind_permitidos, ind, rutas_orig)
            rutas4opt, aristasADD, aristasDROP4opt, costo4opt, indADD, indDROP4opt = self.swap_4opt(lista_permitidos, ind_permitidos, ind, rutas_orig)
        
        indDROP, aristasDROP = self.mezclarAristas(indDROP2opt, aristasDROP2opt, indDROP3opt, aristasDROP3opt, indDROP4opt, aristasDROP4opt)
        
        costo = [costo2opt, costo3opt, costo4opt]
        costo = [x for x in costo if x!=0]
        if(costo!=[]):
            costo = sorted(costo)
            if(condOptim):
                random.shuffle(costo)
            costo = costo[0]
        #print("costo: "+str(costo))
        #Encontramos una sol factible
        if(ind_random!=[]):
            if(costo == costo2opt):
                rutas = rutas2opt
                aristasDROP = aristasDROP2opt
                indDROP = indDROP2opt
            elif(costo == costo3opt):
                rutas = rutas3opt
                aristasDROP = aristasDROP3opt
                indDROP = indDROP3opt
            else:
                rutas = rutas4opt
                aristasDROP = aristasDROP4opt
                indDROP = indDROP4opt
            
            index = [i for i in range(0,len(ind_permitidos)) if ind_permitidos[i] in indDROP or ind_permitidos[i] in indADD]
            ind_permitidos = np.delete(ind_permitidos, index)
        else:
            print("No se encontro una sol factible")
            return rutas_orig, [], [], self.getCostoAsociado()

        return rutas, aristasADD, aristasDROP, costo


    def getPosiciones(self, V_origen, V_destino, rutas):
        ind_verticeOrigen = -1
        ind_verticeDestino = -1
        ind_rutaOrigen = -1
        ind_rutaDestino = -1
        
        #arista_azar = (3,7)    => V_origen = 3 y V_destino = 7
        #Sol:   1-2-3-4-5                  1-6-7-8-9-10   
        #      (1,2)(2,3)(3,4)(4,5)(5,1)   (1,6)(6,7)(7,8)(8,9)(9,10)(10,1)
        #ind_VertOrigen = 2     ind_VertDest = 6
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

    def swap_2opt(self, lista_permitidos, ind_permitidos, ind_random, rutas_orig):
        sol_factible = False
        costo_solucion = self.getCostoAsociado()
        rutas = rutas_orig
        ADD = []
        index_ADD = []
        DROP = []
        index_DROP = []
        
        #while(not sol_factible and len(ind_random)>=1):
        # ADD = []
        # index_ADD = []
        # DROP = []
        # index_DROP = []
        # costo_solucion = self.getCostoAsociado()
        ind = ind_random[-1]
        arista_ini = lista_permitidos[ind_permitidos[ind]]
        ind_random = ind_random[:-1]
        
        V_origen = arista_ini.getOrigen()
        V_destino = arista_ini.getDestino()
        
        ADD.append(arista_ini)
        index_ADD.append(arista_ini.getId())

        rutas = copy.deepcopy(rutas_orig)

        ind_rutas, ind_A = self.getPosiciones(V_origen, V_destino, rutas_orig)
        #En distintas rutas
        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            costo_solucion -= r1.getCostoAsociado() + r2.getCostoAsociado()
            
            A_r1_left = r1.getA()[:ind_A[0]]
            A_r1_right = r1.getA()[ind_A[0]+1:]
            
            A_r2_left = r2.getA()[:ind_A[1]]
            A_r2_right = r2.getA()[ind_A[1]+1:]
            
            if(A_r1_right==[] and A_r2_left==[]):
                return [], [], [], 0, [], []

            A_r1_drop = r1.getA()[ind_A[0]]
            A_r2_drop = r2.getA()[ind_A[1]]
            
            if(A_r2_left!=[]):
                V_origen = A_r2_left[-1].getDestino()    # => (6, )
            #En caso de que la arista al azar se encuentra al principio
            else:
                V_origen = Vertice(1,0)
            if(A_r1_right!=[]):
                V_destino = A_r1_right[0].getOrigen()   # => ( ,4)
            #En caso de que la arista al azar se encuentra al final
            else:
                V_destino = Vertice(1,0)
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add = Arista(V_origen,V_destino, peso)   # => (6,4, peso)
            A_r_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

            ADD.append(A_r_add)
            DROP.append(A_r1_drop)
            index_DROP.append(A_r1_drop.getId())
            DROP.append(A_r2_drop)
            index_DROP.append(A_r2_drop.getId())
            
            A_r1_left.append(ADD[0])
            A_r1_left.extend(A_r2_right)
            A_r2_left.append(ADD[1])
            A_r2_left.extend(A_r1_right)
            
            cap_r1 = r1.cargaDesdeAristas(A_r1_left)
            cap_r2 = r2.cargaDesdeAristas(A_r2_left)
            r1.setCapacidad(cap_r1)
            r2.setCapacidad(cap_r2)

            if(cap_r1 > self.__capacidadMax or cap_r2 > self.__capacidadMax):
                rutas = []
            else:
                sol_factible = True
                costo_solucion += r1.getCostoAsociado() + r2.getCostoAsociado()
        #En la misma ruta
        else:
            r = rutas[ind_rutas[0]]
            costo_solucion -= r.getCostoAsociado()
            V_r = r.getV()
            V_r.append(Vertice(1,0))
            V_r_left = V_r[:ind_A[0]+1]
            V_r_middle = V_r[ind_A[0]+1:ind_A[1]+1]
            V_r_middle = V_r_middle[::-1]               #invierto el medio
            V_r_right = V_r[ind_A[1]+2:]
            
            A_r_drop1 = r.getA()[ind_A[0]]
            A_r_drop2 = r.getA()[ind_A[1]+1]

            try:
                V_origen = V_r_middle[-1]    # => (6, )
            except ValueError:
                print("error")    
                print("arista_ini: "+str(arista_ini))    
                print("lista de perm: "+str(lista_permitidos))
                    
            V_destino = V_r_right[0]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add = Arista(V_origen,V_destino, peso)   # => (6,4, peso)
            A_r_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

            ADD.append(A_r_add)
                            
            DROP.append(A_r_drop1)
            DROP.append(A_r_drop2)
            index_DROP.append(A_r_drop1.getId())
            index_DROP.append(A_r_drop2.getId())
            
            V_r_left.append(r.getV()[ind_A[1]+1])
            V_r_left.extend(V_r_middle)
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

    #2-opt:
    #arista_azar = (a,b)
    #r1: 1-2-3-a-4-5         r2: 1-6-7-b-8-9-10   -> ruta original
    #resultado:
    #r1: 1-2-3-a-b-8-9-10    r2: 1-6-7-4-5        -> 1ra opcion
    #r1: 1-2-3-8-9-10        r2: 1-6-7-b-a-4-5    -> 2da opcion
    def evaluar_2opt(self, lista_permitidos, ind_permitidos, ind, rutas):
        sol_factible = False
        #costo_solucion = self.getCostoAsociado()
        costo_solucion = float("inf")

        A_r1_add = lista_permitidos[ind_permitidos[ind]]
        costo_r1_add = A_r1_add.getPeso()

        V_origen = A_r1_add.getOrigen()
        V_destino = A_r1_add.getDestino()
        ind_rutas, ind_A = self.getPosiciones(V_origen, V_destino, rutas)
        
        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            
            #r1: 1-2-3-a-4-5
            #left: 1-2-3-a      right: 4-5
            A_r1_left = r1.getA()[:ind_A[0]]
            cap_r1_left = r1.getDemandaAcumulada[ind_A[0]]
            A_r1_right = r1.getA()[ind_A[0]+1:]
            cap_r1_right = r2.getDemandaAcumulada[-1] - cap_r1_left
            
            #r2: 1-6-7-b-8-9-10
            #left: 1-6-7        right: 8-9-10
            A_r2_left = r2.getA()[:ind_A[1]]
            cap_r2_left = r1.getDemandaAcumulada[ind_A[1]]
            A_r2_right = r2.getA()[ind_A[1]+1:]
            cap_r2_right = r2.getDemandaAcumulada[-1] - cap_r1_left
            
            #Caso no factible por ej:
            #r1: 1-2-3-4-5-a    r2: 1-b-6-7-8-9-10
            if(A_r1_right==[] and A_r2_left==[]):
                #No es factible
                return float("inf"), float("inf")

            A_r1_drop = r1.getA()[ind_A[0]]
            cap_r1_drop = A_r1_drop.getOrigen().getDemanda() + A_r1_drop.getDestino().getDemanda()
            costo_r1_drop = A_r1_drop.getPeso()

            A_r2_drop = r2.getA()[ind_A[1]]
            cap_r2_drop = A_r2_drop.getOrigen().getDemanda() + A_r2_drop.getDestino().getDemanda()
            costo_r2_drop = A_r2_drop.getPeso()

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
            A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            cap_r_add = V_origen.getDemanda() + V_destino.getDemanda()
            costo_r2_add = peso

            #1ra opcion
            cap_r1 = cap_r1_left + cap_r_add - cap_r1_drop + cap_r2_right
            cap_r2 = cap_r2_left - cap_r2_drop + cap_r1_right
            if(cap_r1 > self.__capacidadMax or cap_r2 > self.__capacidadMax):
                rutas = []
            if(costo_)
            costo_solucion = costo_solucion + costo_r1_add + costo_r2_add - costo_r1_drop - costo_r2_drop
            

    """
    (a,b)
    4-opt
    r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10,11,12
    costoR1 = 123               costoR2 = 150
    resultado:
    r1: 1,2,3,a,b,5,6          r2: 1,7,8,4,9,10,11,12

    new_costR1 = 123 + costo(a,b) + costo(b,5) - costo(a,4) - costo(4,5)
    new_costR2 = 150 + costo(8,4) + costo(4,9) - costo(8,b) - costo(b,9)

    3-opt
    r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10,11,12
    costoR1 = 123               costoR2 = 150
    resultado:
    r1: 1,2,3,a,b,4,5,6          r2: 1,7,8,9,10,11,12       -> 1ra opcion
    r1: 1,2,3,4,5,6              r2: 1,7,8,a,b,9,10,11,12   -> 2da opcion
    r1: 1,2,3,a,b,4,5,6              r2: 1,7,8,9,10,11,12   -> 2da opcion

    2-opt
    r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10,11,12
    costoR1 = 123               costoR2 = 150
    resultado:
    r1: 1,2,3,a,b,9,10,11,12    r2: 1,7,8,4,5,6
    x:  new_costR1 = costoR1 + costo(a,b) + costo(r2[ind(b):]) - costo(a,4) - costo(r1[ind(4):])
    x:  new_costR2 = costoR2 + costo(8,4) + costo(r1[ind(4):]) - costo(8,b) - costo(r2[ind(b):])
    ok: new_cost = costoSolucion + costo(a,b) + costo(8,4) - costo(a,4) - costo(8,b)
    """

    def evaluar_3opt(self, lista_permitidos, ind_permitidos, ind, rutas_orig):
        sol_factible = False
        costo_solucion = self.getCostoAsociado()
        rutas = rutas_orig
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
        
        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            costo_solucion -= r1.getCostoAsociado() + r2.getCostoAsociado()
            #Descompongo las aristas con respecto al vertice "a"
            # 1-2 y 3-4         1-5 y 6-7-8
            A_r1_left = r1.getA()[:ind_A[0]-1]
            A_r1_right = r1.getA()[ind_A[0]+1:]
            
            #Obtengo las aristas que se eliminan y las que se añaden
            #DROP 1 y 2
            A_r1_drop1 = r1.getA()[ind_A[0]-1]
            A_r1_drop2 = r1.getA()[ind_A[0]]
            
            #ADD 1
            V_origen = r1.getA()[ind_A[0]-1].getOrigen()
            V_destino = r1.getA()[ind_A[0]].getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r1_add = Arista(V_origen, V_destino, peso)
            
            

            #Ruta 2
            A_r2_left = r2.getA()[:ind_A[1]]
            A_r2_drop = r2.getA()[ind_A[1]]
            A_r2_right = r2.getA()[ind_A[1]+1:]
            
            V_origen = r2.getA()[ind_A[1]].getOrigen()
            V_destino = r1.getA()[ind_A[0]-1].getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r2_add = Arista(V_origen, V_destino, peso)
            A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            DROP.append(A_r1_drop1)
            DROP.append(A_r1_drop2)
            DROP.append(A_r2_drop)

            NuevcostoR1 = 

            ADD.append(A_r1_add)
            ADD.append(A_r2_add)

            A_r1_left.append(ADD[1])
            A_r1_left.extend(A_r1_right)
            A_r2_left.append(ADD[2])
            A_r2_left.append(ADD[0])
            A_r2_left.extend(A_r2_right)
            
            cap_r1 = r1.cargaDesdeAristas(A_r1_left)
            cap_r2 = r2.cargaDesdeAristas(A_r2_left)
            r1.setCapacidad(cap_r1)
            r2.setCapacidad(cap_r2)
            
            if(cap_r1 > self.__capacidadMax or cap_r2 > self.__capacidadMax):
                rutas = []
            else:
                sol_factible = True
                costo_solucion += r1.getCostoAsociado() + r2.getCostoAsociado()
        #3-opt en la misma ruta
        else:
            #1-2-a-3-4-b-5-6-7
            #(a,b)  1-2-a-b-3-4-5-6-7
            #=>  ADD     DROP
            #   (a,b)   (4,b)
            #   (4,5)   (5,b)
            #   (b,3)   (a,3)
            r = rutas[ind_rutas[0]]
            costo_solucion -= r.getCostoAsociado()
            
            #Descompongo la ruta
            V_r_left = r.getV()[:ind_A[0]+1]                #1-2-a
            V_r_middle = r.getV()[ind_A[0]+1:ind_A[1]+1]    #3-4
            V_r_right = r.getV()[ind_A[1]+1:]               #b-5-6-7
            V_r_right = V_r_right[1:]                       #5-6-7   *No puedo hacer r.getV()[ind_A[1]+2:] xq el indice podria exceder el tam 
            V_r_right.append(Vertice(1,0))                  #5-6-7-1

            A_r_drop1 = r.getA()[ind_A[0]]
            A_r_drop2 = r.getA()[ind_A[1]+1]
            A_r_drop3 = r.getA()[ind_A[1]]

            #Obtengo las otra arista ADD
            try:
                V_origen = V_r_middle[-1]
            except ValueError:
                print("error: "+str(arista_ini))
                print(str(r))
                print(str(V_r_middle))
            V_destino = V_r_right[0]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add1 = Arista(V_origen,V_destino, peso)
            A_r_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

            V_origen = r.getV()[ind_A[1]+1]
            V_destino = V_r_middle[0]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add2 = Arista(V_origen,V_destino, peso)
            A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            ADD.append(A_r_add1)           
            DROP.append(A_r_drop1)
            DROP.append(A_r_drop2)
            index_DROP.append(A_r_drop1.getId())
            index_DROP.append(A_r_drop2.getId())

            if(len(V_r_middle)>1):
                ADD.append(A_r_add2)
                DROP.append(A_r_drop3)
                index_DROP.append(A_r_drop3.getId())
            #else:
            #    print("Se aplica 2-opt ya que solo existe una arista intermedia para hacer el swap")

            #print("DROP: "+str(DROP))
            #print("ADD: "+str(ADD))

            V_r_left.append(r.getV()[ind_A[1]+1])
            V_r_left.extend(V_r_middle)
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

        return rutas, ADD[:1], DROP, costo_solucion, index_ADD, index_DROP




    def evaluar_4opt(self, lista_permitidos, ind_permitidos, ind, rutas_orig):
        """
        (a,b)
        4-opt
        r1: 1,2,3,a,4,5,6          r2: 1,7,8,b,9,10,11,12   -> ruta original
        costoR1 = 123               costoR2 = 150
        resultado:
        -> r1: 1,2,3,a,b,5,6        r2: 1,7,8,4,9,10,11,12       -> 1ra opcion
        x  r1: 1,2,b,a,4,5,6          r2: 1,7,8,3,9,10,11,12     -> 2da opcion
        x  r1: 1,2,3,8,4,5,6          r2: 1,7,a,b,9,10,11,12     -> 3ra opcion
        -> r1: 1,7,8,b,a,10,11,12   r2: 1,2,3,9,4,5,6            -> 4ta opcion PENDIENTE :D

        new_costR1 = 123 + costo(a,b) + costo(b,5) - costo(a,4) - costo(4,5)
        new_costR2 = 150 + costo(8,4) + costo(4,9) - costo(8,b) - costo(b,9)
        
        r: 1,2,3,a,4,5,6,b,7,8  -> Original
        
        resultado:
        r: 1,2,3,a,b,5,6,4,7,8  -> 1ra opcion

        r: 1,2,3,a,4,5,b,6,7,8
        
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
 



    #Swap 3-opt
    #Sol: 1-2-a-3-4   1-5-b-6-7-8
    #(a,b)
    #Sol_nueva:    1-2-3-4         1-5-a-b-6-7-8
    #     DROP   ADD
    #     (2,a) (2,3)
    #     (a,3) (a,b)
    #     (5,b) (5,a)
    def swap_3opt(self, lista_permitidos, ind_permitidos, ind_random, rutas_orig):
        sol_factible = False
        costo_solucion = self.getCostoAsociado()
        rutas = rutas_orig
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
        
        if(ind_rutas[0]!=ind_rutas[1]):
            r1 = rutas[ind_rutas[0]]
            r2 = rutas[ind_rutas[1]]
            costo_solucion -= r1.getCostoAsociado() + r2.getCostoAsociado()
            #Descompongo las aristas con respecto al vertice "a"
            # 1-2 y 3-4         1-5 y 6-7-8
            A_r1_left = r1.getA()[:ind_A[0]-1]
            A_r1_right = r1.getA()[ind_A[0]+1:]
            
            #Obtengo las aristas que se eliminan y las que se añaden
            #DROP 1 y 2
            A_r1_drop1 = r1.getA()[ind_A[0]-1]
            A_r1_drop2 = r1.getA()[ind_A[0]]
            
            #ADD 1
            V_origen = r1.getA()[ind_A[0]-1].getOrigen()
            V_destino = r1.getA()[ind_A[0]].getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r1_add = Arista(V_origen, V_destino, peso)
            
            A_r1_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            #Ruta 2
            A_r2_left = r2.getA()[:ind_A[1]]
            A_r2_drop = r2.getA()[ind_A[1]]
            A_r2_right = r2.getA()[ind_A[1]+1:]
            
            V_origen = r2.getA()[ind_A[1]].getOrigen()
            V_destino = r1.getA()[ind_A[0]-1].getDestino()
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r2_add = Arista(V_origen, V_destino, peso)
            A_r2_add.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            DROP.append(A_r1_drop1)
            DROP.append(A_r1_drop2)
            DROP.append(A_r2_drop)
            index_DROP.append(A_r1_drop1.getId())
            index_DROP.append(A_r1_drop2.getId())
            index_DROP.append(A_r2_drop.getId())

            ADD.append(A_r1_add)
            ADD.append(A_r2_add)

            A_r1_left.append(ADD[1])
            A_r1_left.extend(A_r1_right)
            A_r2_left.append(ADD[2])
            A_r2_left.append(ADD[0])
            A_r2_left.extend(A_r2_right)
            
            cap_r1 = r1.cargaDesdeAristas(A_r1_left)
            cap_r2 = r2.cargaDesdeAristas(A_r2_left)
            r1.setCapacidad(cap_r1)
            r2.setCapacidad(cap_r2)
            
            if(cap_r1 > self.__capacidadMax or cap_r2 > self.__capacidadMax):
                rutas = []
            else:
                sol_factible = True
                costo_solucion += r1.getCostoAsociado() + r2.getCostoAsociado()
        #3-opt en la misma ruta
        else:
            #1-2-a-3-4-b-5-6-7
            #(a,b)  1-2-a-b-3-4-5-6-7
            #=>  ADD     DROP
            #   (a,b)   (4,b)
            #   (4,5)   (5,b)
            #   (b,3)   (a,3)
            r = rutas[ind_rutas[0]]
            costo_solucion -= r.getCostoAsociado()
            
            #Descompongo la ruta
            V_r_left = r.getV()[:ind_A[0]+1]                #1-2-a
            V_r_middle = r.getV()[ind_A[0]+1:ind_A[1]+1]    #3-4
            V_r_right = r.getV()[ind_A[1]+1:]               #b-5-6-7
            V_r_right = V_r_right[1:]                       #5-6-7   *No puedo hacer r.getV()[ind_A[1]+2:] xq el indice podria exceder el tam 
            V_r_right.append(Vertice(1,0))                  #5-6-7-1

            A_r_drop1 = r.getA()[ind_A[0]]
            A_r_drop2 = r.getA()[ind_A[1]+1]
            A_r_drop3 = r.getA()[ind_A[1]]

            #Obtengo las otra arista ADD
            try:
                V_origen = V_r_middle[-1]
            except ValueError:
                print("error: "+str(arista_ini))
                print(str(r))
                print(str(V_r_middle))
            V_destino = V_r_right[0]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add1 = Arista(V_origen,V_destino, peso)
            A_r_add1.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))

            V_origen = r.getV()[ind_A[1]+1]
            V_destino = V_r_middle[0]
            peso = self._matrizDistancias[V_origen.getValue()-1][V_destino.getValue()-1]
            A_r_add2 = Arista(V_origen,V_destino, peso)
            A_r_add2.setId(V_origen.getValue()-1, V_destino.getValue()-1, len(self._matrizDistancias))
            
            ADD.append(A_r_add1)           
            DROP.append(A_r_drop1)
            DROP.append(A_r_drop2)
            index_DROP.append(A_r_drop1.getId())
            index_DROP.append(A_r_drop2.getId())

            if(len(V_r_middle)>1):
                ADD.append(A_r_add2)
                DROP.append(A_r_drop3)
                index_DROP.append(A_r_drop3.getId())
            #else:
            #    print("Se aplica 2-opt ya que solo existe una arista intermedia para hacer el swap")

            #print("DROP: "+str(DROP))
            #print("ADD: "+str(ADD))

            V_r_left.append(r.getV()[ind_A[1]+1])
            V_r_left.extend(V_r_middle)
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

        return rutas, ADD[:1], DROP, costo_solucion, index_ADD, index_DROP
    
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


if __name__ == "__main__":
    inf = float("inf")
    matriz = [[inf,25,43,57,43,61,29,41,48,71],
              [25,inf,29,34,43,68,49,66,72,91],
              [43,29,inf,52,72,96,72,81,89,114],
              [57,34,52,inf,45,71,71,95,99,108],
              [43,43,72,45,inf,27,36,65,65,65],
              [61,68,96,71,27,inf,40,66,62,46],
              [29,49,72,71,36,40,inf,31,31,43],
              [41,66,81,95,65,66,31,inf,11,46],
              [48,72,89,99,65,62,31,11,inf,36],
              [71,91,114,108,65,46,43,46,36,inf]]
    dem = [0,4,6,5,4,7,3,5,4,4]

    S = Solucion(matriz,dem,34)
    ruta1 = [1,2,3,4,5,6,7,8,9,10]
    ruta2 = [1,11,12,13,14,15,16,17,18,19,20]
    rutas = [ruta1,ruta2]
    S = S.cargarRutas(rutas)

    print(S)