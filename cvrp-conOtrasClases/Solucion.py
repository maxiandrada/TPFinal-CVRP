from Grafo import Grafo 
from Vertice import Vertice 
from Arista import Arista
import copy
import sys
import random
import math
from Ingreso import Ingreso
import os
from Grafico import Grafico
import numpy as np


class Ruta(Grafo):
    def __init__(self, M,seq=None):
        super(Ruta, self).__init__(M)
        if(not seq is None):
            self.cargarDesdeSecuenciaDeVertices(seq)
            self.setCosto()
        else:
            self.setV([Vertice(1)])
    
    
    def __str__(self):
        A=self.getA()
        return "Recorrido de la ruta: " + str(self.getV()) + "\n" + "Aristas de la ruta: "+ str(A) + " \nCosto Asociado: " + str(round(self.getCostoAsociado(),3))
   
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

    def getCosto(self):
        return self._costoAsociado

   
    def getCopyVacio(self):
        ret = Ruta(Grafo([]))
        ret.setMatriz(self.getMatriz())
        return ret

    def addCliente(self,C,index = None, V = None):
        """
        C: Cliente a insertar, puede ser un entero un objeto Vértice
        index: Posición en la que se va a insertar C
        V: Es para el caso que se quiera insertar después de un vértice en específico
        ¡OJO! el V no es un índice
        """
        if(isinstance(C,int)):
            C = Vertice(C)
        if(index is None and V is None):
            self.getV().append(C)
        elif(not index is None and V is None):
            self.getV().insert(index,C)
        else:
            self.getV().insert(self.getV().index(V)+1,C)

        self.cargarDesdeSecuenciaDeVertices(self.getV())

    def cargaTotal(self, dem):
        suma = 0
        for r in self.getV():
            suma += dem[r.getValue()-1]
        self.__cargaTotal = suma
        return suma

        
    def buscarCliente(self,C):
        if isinstance(C,int):
            C = Vertice(C)
        if not C in self.getV():
            return self.getV().index(C)
        else: 
            return -1

    #[(1,2);(2,3);(3,4);(1,9);(9,5);(5,6);(1,7);(7,8);(8,10)]
    #2-opt:
    #DROP = (2,3); ADD = (2,5) --> [(1,2);(2,5);(5,4);(1,9);(9,3);(3,6);(1,7);(7,8);(8,10)]
    #[(1,2);(2,5);(5,4);(1,3);(3,9);(9,6);(1,7);(7,8);(8,10)]
    def swap(self, a1, a2):
        A = []
        V = self.getV()[0]
        for a in self._A:
            print("a: "+str(a))
            a1_Destino = a1.getDestino()
            a2_Destino = a2.getDestino()
            if(a.getOrigen == a1_Destino):
                a.setOrigen(a1_Destino)
            elif(a.getOrigen == a2_Destino):
                a.setOrigen(a2_Destino)
            
            if (a.getDestino() == a1_Destino):
                a.setDestino(a1_Destino)
            elif(a.getDestino() == a2_Destino):
                a.setDestino(a2_Destino)
            print(str(a))
            A.append(a)
            V.append(a.getDestino())
        
        S = Ruta([])
        S.setA(A)
        S.setV(V)
        S.setMatriz(self._matrizDistancias)

        return S



    def swapp(self, v1, v2):
        copiaV = copy.deepcopy(self._V)

        copiaV[self._V.index(v1)]=v2
        copiaV[self._V.index(v2)]=v1

        gNuevo = Grafo([])
        gNuevo.setMatriz(self.getMatriz())
        gNuevo.cargarDesdeSecuenciaDeVertices(copiaV)
        return gNuevo

    def esInterno(self, c):
        if(isinstance(c,int)):
            c = Vertice(c)
        if c in self.getV():  
            posicion = self.getV().index(c)
            if(1 < posicion and posicion < len(self.getV())-1):
                return True
            else:
                return False
        else:
            return False

class Solucion():
    def __init__(self,S=None,D=None,NV=None,C=None,I=None):
        if(isinstance(S,Solucion)):
            self.__matriz = S.getMatriz()
            self.__grado = len(self.__matriz)
            self.__V = copy.deepcopy(S.getV())
            self.__A = copy.deepcopy(S.getA())
            self.__demanda = S.getDemanda()
            self.__capacidad = S.getCapacidad()
            self.__nroVehiculos = S.getNroVehiculos()
            self.__rutas = copy.deepcopy(S.getRutas())
            self.__costoTotal = S.getCostoTotal()
            if(I is None):
                self.crearDictBusqueda()


        elif(isinstance(S,Grafo)):
            if(not D is None and not NV is None and not C is None):
                self.__matriz = S.getMatriz()
                self.__grado = len(self.__matriz)
                self.__costoTotal = S.getCostoAsociado()
                self.__V = copy.deepcopy(S.getV())
                self.__A = copy.deepcopy(S.getA())
                self.__capacidad = C
                self.__demanda = D
                self.__nroVehiculos = NV
            else:
                print("Faltan argumentos")
        else:
            print("Solución Vacía")
               
    
        if(not S is None and not I is None):
            self.__rutas = []
            self.__costoTotal = 0
            self.rutasIniciales(I,self.__nroVehiculos,self.__demanda,self.__capacidad)
            #self.rutaDePrueba()
            self.crearDictBusqueda()
            self.mostrarDictBusqueda()
            self.setCostoTotal()
            self.__tipoSolucionIni = I
        self.__costoPenalizado = 0

    def getTipoSolucionInicial(self):
        return self.__tipoSolucionIni

    def crearDictBusqueda(self):
        self.__dict = {}
        #print(self.__rutas[1])
        for r in range(0,len(self.__rutas)):
            #print("r: ",r)
            V = self.__rutas[r].getV()
            for i in range(len(V)):
                self.__dict.update({V[i].getValue():[r,i]}) #[r,v] lista con el indice de la ruta y del vértice
            
    def mostrarDictBusqueda(self):
        print(self.__dict)

    def getCostoPenalizado(self):
        return self.__costoPenalizado

    def setCostoPenalizado(self,cp):
        self.__costoPenalizado = cp


    #Actualiza todos los vértices de la ruta
    def actualizarDictBusqueda(self,r1):
        V = self.__rutas[r1].getV()
        for i in range(len(V)):
            self.__dict.update({V[i].getValue():[r1,i]})


    def buscar(self, v):
        if(isinstance(v,int)):
            return self.__dict.get(v)     
        elif(isinstance(v,Vertice)):
            return self.__dict.get(v.getValue())

    def getRutas(self):
        return self.__rutas
    
    def setRutas(self,R):
        self.__rutas = R


    def addRuta(self,R):
        self.__rutas.append(R)
        self.setCostoTotal()

    def removeRuta(self,index):
        self.__rutas.pop(index)
        self.setCostoTotal()

    def __getitem__(self,key):
        return self.__rutas[key]

    def getMatriz(self):
        return self.__matriz

    def getGrado(self):
        return self.__grado
 

    def setA(self, A):
        self.__A = A
    def setV(self, V):
        self.__V = V
    def getA(self):
        return self.__A
    def getV(self):
        return self.__V

    def getDemanda(self):
        return self.__demanda
    
    def setDemanda(self,D):
        self.__demanda = D

    def getCapacidad(self):
        return self.__capacidad

    def setCapacidad(self,C):
        self.__capacidad = C

    def getNroVehiculos(self):
        return self.__nroVehiculos

    def setNroVehiculos(self,NV):
        self.__nroVehiculos = NV

    def rutaDePrueba(self):
        seq1 = []
        seq2 = [Vertice(1)]
        for i in range(1,self.__grado+1):
            if(i < self.__grado/2):
                seq1.append(Vertice(i))
            else:
                seq2.append(Vertice(i))

        self.__rutas.append(Ruta(self.getMatriz(),seq1))
        self.__rutas.append(Ruta(self.getMatriz(),seq2))
            
    def __str__(self):
        ret = ""
        for i in range(0, len(self.__rutas)):
            ret += "\nRuta del vehiculo "+str(i+1)+":\n"+str(self.__rutas[i]) + "\n"
            ret += "Carga ruta: "+str(self[i].cargaTotal(self.getDemanda()))+"\n"
        ret += "\nCosto total: "+str(self.getCostoTotal())
        ret += "\nCosto Penalizado: "+str(self.getCostoPenalizado())
        return ret

    def setCostoTotal(self,costo=None):
        if(not costo  is None):
            self.__costoTotal = costo
        else:
            ret = 0
            for r in self.__rutas:
                ret += r.getCosto()
            self.__costoTotal = ret

    def __repr__(self):
        return str(self)

    def getCostoTotal(self):
        return self.__costoTotal

    #Longitud que debería tener cada solucion por cada vehiculo
    def longitudRutas(self, length, nroVehiculos):
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
    def rutasIniciales(self, strSolInicial, nroVehiculos, demanda, capacidad):
        rutas = []

        if(strSolInicial==0):
            print("Solución Inicial Clark-Wright")
            self.clarkWright()
        elif(strSolInicial==1):
            print("Solución Inicial Vecino Cercano")
            self.algoritmoConstructivo(nroVehiculos,demanda,capacidad)
        elif(strSolInicial==2):
            secuenciaInd = list(range(1,len(self.__matriz)))
            print("secuencia de indices de los vectores: "+str(secuenciaInd))
            self.cargar_secuencia(secuenciaInd, nroVehiculos, demanda, capacidad, rutas)
            self.__rutas = rutas

    #

    def penalizarSolucion(self,alfa):
        capacMax = self.__capacidad
        dem = self.__demanda
        costoActual = self.__costoTotal
        sumaDemRutas = self.getCapacidadDisponible()
        maxSum = max(sumaDemRutas)
        self.setCostoPenalizado(costoActual + alfa*maxSum) 

    def getCapacidadDisponible(self):
        capacMax = self.__capacidad
        dem = self.__demanda
        sumaDemRutas = []
        for Rr in self.getRutas():
            suma = 0
            for v in Rr.getV():
                if isinstance(v,Vertice):
                    suma += dem[v.getValue()-1]
                elif isinstance(v,int):
                    suma += dem[v-1]
            suma = suma - capacMax
            sumaDemRutas.append(suma)
        return sumaDemRutas

    def cargar_secuencia(self, secuencia, nroVehiculos, demanda, capacidad, rutas):
        secuenciaInd = secuencia
        sub_secuenciaInd = []
        
        for i in range(0,nroVehiculos):
            #Sin contar la vuelta (x,1)
            #nroVehiculos = 3
            #[1,2,3,4,5,6,7,8,9,10] - [1,2,3,4] - [1,5,6,7] - [1,8,9,10]
            length = self.longitudRutas(len(secuenciaInd), nroVehiculos-i)
            fin = length
            sub_secuenciaInd = self.solucion_secuencia(secuenciaInd[0:fin], capacidad, demanda)
            S = Ruta(self.__matriz)
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+sub_secuenciaInd))
            S.setCosto()
            rutas.append(S)
            secuenciaInd = [x for x in secuenciaInd if x not in set(sub_secuenciaInd)]
        if len(secuenciaInd) > 0:
            print("La solucion inicial no es factible. Implementar luego....")

    def solInicial_VecinoCercano(self, nroVehiculos, capacidad, demanda, rutas):
        visitados = []
        recorrido = []
        visitados.append(0)    #Agrego el vertice inicial
        
        for j in range(0, nroVehiculos):
            recorrido = []
            masCercano=0
            acum_demanda = 0
            for i in range(0,len(self.__matriz)-len(visitados)):
                masCercano = self.vecinoMasCercano(masCercano, visitados, acum_demanda, demanda, capacidad) #obtiene la posicion dela matriz del vecino mas cercano
                if(masCercano != 0):
                    acum_demanda += demanda[masCercano]
                    recorrido.append(masCercano)
                    visitados.append(masCercano)
                if(acum_demanda > self.__capacidad/nroVehiculos):
                    break
                i
            j
            S = Ruta(self.__matriz)
            print(recorrido)
            S.cargarDesdeSecuenciaDeVertices(S.cargaVertices([0]+recorrido))
            self.__rutas.append(S)
        
        return recorrido


    def vecinoMasCercano(self, pos, visitados, acum_demanda, demanda, capacidad):
        masCercano = self.__matriz[pos][pos]
        indMasCercano = 0
    
        for i in range(0, len(self.__matriz)):
            costo = self.__matriz[pos][i]
            if(costo<masCercano and i not in visitados and demanda[i]+acum_demanda <= capacidad):
                masCercano = costo
                indMasCercano = i
        
        return indMasCercano

        

    #secuenciaInd: secuencia de Indices
    #capacidad: capacidad maxima de los vehiculos
    #demanda: demanda de cada cliente
    def solucion_secuencia(self, secuenciaInd, capacidad, demanda):
        tam = 0                 #Tamaño de la solInicial, depende si la suma de las demandas cumple la restriccion de capacidad
        acum_demanda = 0
        sub_secuenciaInd = []
        for x in secuenciaInd:
            value = self.getV()[x].getValue()-1
            if(acum_demanda + demanda[value] <= capacidad):
                acum_demanda += demanda[value]
                sub_secuenciaInd.append(x)
                tam+=1
        
        return sub_secuenciaInd
        

    #def pVecindario(self):

    def algoritmoConstructivo(self, nroVehiculos, demanda, capacidad):
        RutaRef = Ruta(self.getMatriz())
        self.addRuta(RutaRef)
        visitados = [Vertice(1)]
        for i in range(1,nroVehiculos+1):
            origen = 1
            R = [Vertice(1)] 
            cAcum = 0
            superoMaximo = False
            k=0
            while(cAcum<capacidad and not superoMaximo):
                j = 0            
                destinos = list(self[0][origen][None]) 
                min = destinos[origen-1].getPeso() 
                jMin =0  
                while(j<len(destinos)):
                    if(destinos[j].getDestino() not in visitados):
                        if(destinos[j].getPeso()<min):
                            if(cAcum+demanda[destinos[j].getDestino().getValue()-1] < capacidad):
                                min = destinos[j].getPeso()
                                origen = destinos[j].getDestino().getValue()
                                jMin=j
                    j+=1
                k+=1
                if(k==len(destinos)):
                    superoMaximo = True
                if(jMin!=0):
                    R += [destinos[jMin].getDestino()]
                    visitados.append(destinos[jMin].getDestino())
                    cAcum += demanda[jMin]
                #print(origen)

            ruta = Ruta(self.__matriz,R)
            #print("R: "+str(R))
            #print("Ruta: "+str(ruta))
            self.addRuta(ruta)
        self.__rutas.pop(0)





    def twoExchange(self,v1,v2):
        indV1 = self.buscar(v1) #[r1,v1] indice de la ruta y del vértice
        indV2 = self.buscar(v2)
        R = self.__rutas
        
        #Para el caso de que los vértices estén en la misma rutas
        if(indV1[1]+1 == len(R[indV1[0]]) and  indV2[1]+1 == len(R[indV2[0]])):  
            aux = self[indV1[0]].getV()[indV1[1]]
            self[indV1[0]].getV()[indV1[1]] = self[indV2[0]].getV()[indV2[1]]
            self[indV2[0]].getV()[indV2[1]] = aux
            self[0].cargarDesdeSecuenciaDeVertices(self[0].getV())
            self[1].cargarDesdeSecuenciaDeVertices(self[1].getV())            
        else:
            inferiorR1 = self[indV1[0]].getV()[:indV1[1]+1]
            superiorR1 = self[indV1[0]].getV()[indV1[1]+1:]
            inferiorR2 = self[indV2[0]].getV()[:indV2[1]]
            superiorR2 = self[indV2[0]].getV()[indV2[1]:]
            if(superiorR1==[]):
                print("No se puede este caso por ahora ¬¬")
            else:
                r1 = inferiorR1 + superiorR2
                r2 = inferiorR2 + superiorR1
                self[0].cargarDesdeSecuenciaDeVertices(r1)
                self[1].cargarDesdeSecuenciaDeVertices(r2)
        self.actualizarDictBusqueda(0)
        self.actualizarDictBusqueda(1)
        self[0].setCosto()
        self[1].setCosto()
        self.setCostoTotal()

    def customerInsertion(self,v1,v2):
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 
        indV2= self.buscar(v2)  #igual pero de v2
        r1 = indV1[0]
        r2 = indV2[0]
        c1 = indV1[1]
        c2 = indV2[1]        

        a = self[r1].getA()[c1]  
        anteriorA = self[r1].getA()[c1-1]
        b = self[r2].getA()[c2]
        anteriorB = self[r2].getA()[c2-1]

        anteriorA.setDestino(a.getDestino())
        anteriorA.setPeso(self[r1][anteriorA.getOrigen()][a.getDestino()])
        a.setDestino(b.getOrigen())
        anteriorB.setDestino(a.getOrigen())

        a.setPeso(self[r1][a.getOrigen()][b.getOrigen()])
        anteriorB.setPeso(self[r1][anteriorB.getOrigen()][a.getOrigen()])
        
        self[r2].getA().insert(c2,a)
        self[r1].getA().remove(a)

        self[r1].cargarDesdeSecuenciaDeAristas(self[r1].getA())
        self[r2].cargarDesdeSecuenciaDeAristas(self[r2].getA())

        self.actualizarDictBusqueda(0)
        self.actualizarDictBusqueda(1)
        self.setCostoTotal()

    #PENDIENTE ACTUALIZAR PESOS
    def exchange(self,v1,v2):
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 
        indV2= self.buscar(v2)  #igual pero de v2
        r1 = indV1[0]
        r2 = indV2[0]
        c1 = indV1[1]
        c2 = indV2[1]

        a = self[r1].getA()[c1]  
        b = self[r2].getA()[c2]
        anteriorB = self[r2].getA()[c2-1]
        siguienteB = self[r2].getA()[c2+1]

        anteriorB.setDestino(siguienteB.getDestino())
        siguienteB.setDestino(a.getDestino())
        a.setDestino(b.getOrigen())

        self[r1].getA().insert(c1+1,b)
        self[r1].getA().insert(c1+2,siguienteB)
        self[r2].getA().remove(b)
        self[r2].getA().remove(siguienteB)



        self[r1].cargarDesdeSecuenciaDeAristas(self[r1].getA())
        self[r2].cargarDesdeSecuenciaDeAristas(self[r2].getA())

        self.actualizarDictBusqueda(0)
        self.actualizarDictBusqueda(1)
        self.setCostoTotal()

    def esUltimo(self,r1,v1):
        if(isinstance(v1,int)):
            return v1+1 == len(self[r1])
        elif(isinstance(v1,Vertice)):
            return v1.getValue()+1 == len(self[r1])
    #PENDIENTEEEEE
    def customerSwap(self, v1,v2):
        indV2 = self.buscar(v2)  #igual pero de v2
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 
        condV2EsDeposito = False
        if(isinstance(v2,Vertice)):
            if(v2.getValue()==1):
                condV2EsDeposito = True
        elif(isinstance(v2,int)):
            if(v2==1):
                condV2EsDeposito = True
        if(isinstance(v1,Vertice) ):
            if(v1.getValue()==1):
                r1=indV2[0]
            else:
                r1 = indV1[0]
        elif(isinstance(v1,int)):
            if(v1==1):
                r1=indV2[0]
            else:
                r1 = indV1[0]

        if(condV2EsDeposito == False):
            r2 = indV2[0]
            c1 = indV1[1]
            c2 = indV2[1]

            a = self[r1].getA()[c1]  
            b = self[r2].getA()[c2]
            anteriorB = self[r2].getA()[c2-1]
            if(self.esUltimo(r1,c1) or self.esUltimo(r2,c2)):
                    
                anteriorB.setDestino(b.getDestino())   
                b.setDestino(a.getDestino())
                a.setDestino(b.getOrigen())

                anteriorB.setPeso(self[r1][anteriorB.getOrigen()][anteriorB.getDestino()])
                b.setPeso(self[r1][b.getOrigen()][b.getDestino()])
                a.setPeso(self[r1][a.getOrigen()][a.getDestino()])

                if(self.esUltimo(r2,c2)):
                    self[r2].getA().remove(self[r2].getA()[c2])
                    self[r1].getA().insert(c1+1,b)
                else:
                    self[r1].getA().insert(c1+1,b)
                    self[r2].getA().remove(b)

                # print("r1: ",self[r1].getA())
                # print("r2: ",   self[r2].getA())
                self[r1].cargarDesdeSecuenciaDeAristas(self[r1].getA())
                self[r2].cargarDesdeSecuenciaDeAristas(self[r2].getA()) 
                self.actualizarDictBusqueda(r1)
                self.actualizarDictBusqueda(r2)
            else:
                siguienteA = self[r1].getA()[c1+1]
                siguienteB = self[r2].getA()[c2+1]
                anteriorB.setDestino(a.getDestino())
                b.setDestino(siguienteA.getDestino())
                a.setDestino(b.getOrigen())
                siguienteA.setDestino(siguienteB.getOrigen())
 


                if(self[r1].getA()[c1+1]!=self[r2].getA()[c2]):
                    self[r2].getA().remove(b)
                    self[r1].getA().remove(siguienteA)

                    a.setPeso(self[r1][a.getOrigen()][a.getDestino()])
                    anteriorB.setPeso(self[r1][anteriorB.getOrigen()][anteriorB.getDestino()])
                    siguienteA.setPeso(self[r1][siguienteA.getOrigen()][siguienteA.getDestino()])
                    b.setPeso(self[r1][b.getOrigen()][b.getDestino()])  

                    self[r1].getA().insert(c1+1,b)
                    self[r2].getA().insert(c2,siguienteA) 

                    self[r1].cargarDesdeSecuenciaDeAristas(self[r1].getA())
                    self[r2].cargarDesdeSecuenciaDeAristas(self[r2].getA()) 
                    self.actualizarDictBusqueda(r1)
                    self.actualizarDictBusqueda(r2)
                else:
                    a.setPeso(self[r1][a.getOrigen()][a.getDestino()])
                    anteriorB.setPeso(self[r1][anteriorB.getOrigen()][anteriorB.getDestino()])
                    siguienteA.setPeso(self[r1][siguienteA.getOrigen()][siguienteA.getDestino()])
                    b.setPeso(self[r1][b.getOrigen()][b.getDestino()])
                    self[r1].cargarDesdeSecuenciaDeAristas(self[r1].getA())
                    self.actualizarDictBusqueda(r1)

            self.setCostoTotal()
    
       
    def customerSwap2(self, v1,v2):
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 
        indV2= self.buscar(v2)  #igual pero de v2

        r1 = indV1[0]
        r2 = indV2[0]
        c1 = indV1[1]
        c2 = indV2[1]

        a = self[r1].getA()[c1]  
        b = self[r2].getA()[c2]
        siguienteA = self[r1].getA()[c1+1]
        siguienteB = self[r2].getA()[c2+1]
        anteriorB = self[r2].getA()[c2-1]

        anteriorB.setDestino(a.getOrigen())
        b.setDestino(a.getDestino())
        a.setDestino(siguienteA.getOrigen())
        siguienteA.setDestino(siguienteB.getOrigen())

        self[r1].getA().remove(siguienteA)
        self[r2].getA().remove(b)

        a.setPeso(self[r1][a.getOrigen()][a.getDestino()])
        anteriorB.setPeso(self[r1][anteriorB.getOrigen()][anteriorB.getDestino()])
        siguienteA.setPeso(self[r1][siguienteA.getOrigen()][siguienteA.getDestino()])
        b.setPeso(self[r1][b.getOrigen()][b.getDestino()])


        self[r1].getA().insert(c1+1,b)
        self[r2].getA().insert(c2,siguienteA)

        
        self[r1].cargarDesdeSecuenciaDeAristas(self[r1].getA())
        self[r2].cargarDesdeSecuenciaDeAristas(self[r2].getA())

        self.actualizarDictBusqueda(0)
        self.actualizarDictBusqueda(1)
        self.setCostoTotal()       

    def solucionToList(self):
        rutas =[]
        for r in self.getRutas():
            ruta = []
            for v in r.getV():
                ruta.append(v.getValue())
            rutas.append(ruta)
        return rutas

    def evaluarCapacidad(self,v1,v2,alfa):
        indV2 = self.buscar(v2)  #igual pero de v2
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 
        
        if(isinstance(v1,Vertice)):
            if(v1.getValue()==1):
                r1=indV2[0]
            else:
                r1 = indV1[0]
        elif(isinstance(v1,int)):
            if(v1==1):
                r1=indV2[0]
            else:
                r1 = indV1[0]

        r2 = indV2[0]
        c1 = indV1[1]
        c2 = indV2[1]

        dem = self.getDemanda()
        if(r1 != r2):
            cr1 = copy.deepcopy(self[r1].getV())
            cr2 = copy.deepcopy(self[r2].getV())
            b = cr2[c2]
            if(self.esUltimo(r1,c1)):
                cr1.insert(0,b) 
                cr2.remove(b)
            else:
                sigA = cr1[c1+1]
                cr2.remove(b)
                cr2.insert(0,sigA)
                cr1.insert(0,b)
                cr1.remove(sigA)
            rutas = [self.getRutas()[r] for r in range(len(self.getRutas())) if r != r1 and r!=r2]
            rutas.insert(r1,cr1)
            rutas.insert(r2,cr2)

        else:
            rutas = self.getRutas()

        sumaDemRutas=[]
        capacMax=self.getCapacidad()
        for Rr in rutas:
            suma = 0
            if isinstance(Rr,Ruta):
                for v in Rr.getV():
                    suma += dem[v.getValue()-1]
                suma = suma - capacMax
                sumaDemRutas.append(suma)
            elif isinstance(Rr,list):
                for v in Rr:
                    suma += dem[v.getValue()-1]
                suma = suma - capacMax
                sumaDemRutas.append(suma)
        maxSum = max(sumaDemRutas)

        return maxSum*alfa

    def evaluarCostoSwapCustomer(self,v1,v2):
        indV2 = self.buscar(v2)  #igual pero de v2
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 


        condV2EsDeposito = False
        if(isinstance(v2,Vertice)):
            if(v2.getValue()==1):
                condV2EsDeposito = True
        elif(isinstance(v2,int)):
            if(v2==1):
                condV2EsDeposito = True

        if(isinstance(v1,Vertice)):
            if(v1.getValue()==1):
                r1=indV2[0]
            else:
                r1 = indV1[0]
        elif(isinstance(v1,int)):
            if(v1==1):
                r1=indV2[0]
            else:
                r1 = indV1[0]

        if(condV2EsDeposito == False):
            r2 = indV2[0]
            c1 = indV1[1]
            c2 = indV2[1]

            a = self[r1].getA()[c1]  
            b = self[r2].getA()[c2]
            anteriorB = self[r2].getA()[c2-1]

            costoSwap = 0
            costoActual = self.getCostoTotal()  
            if(self.esUltimo(r1,c1) or self.esUltimo(r2,c2)):
                costoActual -= self[r1][anteriorB.getOrigen()][anteriorB.getDestino()]
                costoActual -= self[r1][b.getOrigen()][b.getDestino()]
                costoActual -= self[r1][a.getOrigen()][a.getDestino()]
                costoSwap += self[r1][anteriorB.getOrigen()][b.getDestino()]   
                costoSwap += self[r1][b.getOrigen()][a.getDestino()]
                costoSwap += self[r1][a.getOrigen()][b.getOrigen()]
            else:
                siguienteA = self[r1].getA()[c1+1]
                siguienteB = self[r2].getA()[c2+1]
                costoActual -= self[r1][anteriorB.getOrigen()][anteriorB.getDestino()]
                costoActual -= self[r1][b.getOrigen()][b.getDestino()]
                costoActual -= self[r1][a.getOrigen()][a.getDestino()]
                costoActual -= self[r1][siguienteA.getOrigen()][siguienteA.getDestino()]
                costoSwap += self[r1][anteriorB.getOrigen()][a.getDestino()]
                costoSwap += self[r1][b.getOrigen()][siguienteA.getDestino()]
                costoSwap += self[r1][a.getOrigen()][b.getOrigen()]
                costoSwap += self[r1][siguienteA.getOrigen()][siguienteB.getOrigen()]

        if(condV2EsDeposito == False):
            return costoActual+costoSwap
        else:
            return float("inf")


    def buscarMejorMovimiento(self,listaA,q,alfa,costoActual=None,listaTabu=None):
        factibles = []
        for f in listaA:
            cap = self.getCapacidadDisponible()
            evaluacion = self.evaluarCapacidad(f.getOrigen(),f.getDestino(),alfa)
            if(evaluacion<=self.getCostoTotal()):
                factibles.append(f)
        if(costoActual is None and listaTabu is None): #Este control es por si se quiere usar listaTabu o no para buscar
            if factibles != []:
                muestra = random.sample(factibles,int(len(factibles)*q))
                if(muestra==[]):
                    muestra = random.sample(factibles,1)[0]
                else:
                    mejor = muestra[0] 
                for a in muestra[1:]:
                    #print("(%d,%d)=%f"%(a.getOrigen().getValue(),a.getDestino().getValue(),self.evaluarCostoSwapCustomer(a.getOrigen(),a.getDestino())))
                    evaluacionActual = self.evaluarCostoSwapCustomer(a.getOrigen(),a.getDestino())
                    evaluacionMejor = self.evaluarCostoSwapCustomer(mejor.getOrigen(),mejor.getDestino())
                    if(evaluacionActual<evaluacionMejor):
                        mejor = a
                return mejor
            else: 
                return False
        else:
            if factibles != []:
                muestra = random.sample(factibles,int(len(factibles)*q))
                if muestra == []:
                    mejor = random.sample(factibles,1)[0]
                else:
                    mejor = muestra[0]
                for a in muestra:
                    #print("(%d,%d)=%f"%(a.getOrigen().getValue(),a.getDestino().getValue(),self.evaluarCostoSwapCustomer(a.getOrigen(),a.getDestino())))
                    evaluacionActual = self.evaluarCostoSwapCustomer(a.getOrigen(),a.getDestino())
                    evaluacionMejor = self.evaluarCostoSwapCustomer(mejor.getOrigen(),mejor.getDestino())
                    if(evaluacionActual<evaluacionMejor):
                        if(a in listaTabu): 
                            if(evaluacionActual<costoActual): #Si pertenece a la listaTabu, pero mejora la solución se acepta el movimiento.
                                mejor = a
                        else:
                            mejor = a
                return mejor
            else:
                return False

    def aristasTabu(self,v1,v2):
        indV2 = self.buscar(v2)  #igual pero de v2
        indV1 = self.buscar(v1) #Par ordenado (r,i) donde r es el índice de la ruta y de la arista de v1 

        if(isinstance(v1,Vertice)):
            if(v1.getValue()==1):
                r1=indV2[0]
            else:
                r1 = indV1[0]
        elif(isinstance(v1,int)):
            if(v1==1):
                r1=indV2[0]
            else:
                r1 = indV1[0]
        r2 = indV2[0]
        c1 = indV1[1]
        c2 = indV2[1]
        a = self[r1].getA()[c1]  
        b = self[r2].getA()[c2]
        anteriorB = self[r2].getA()[c2-1]
        
        if(self.esUltimo(r1,c1) or self.esUltimo(r2,c2)):
            return (anteriorB,a,b)
        else:
            siguienteA = self[r1].getA()[c1+1]
            siguienteB = self[r2].getA()[c2+1]
            return (a,b,siguienteA,siguienteB,anteriorB)

        

    def obtenerAhorros(self):
        M = self.getMatriz()
        ahorros = []
        for i in range(0,len(M)):
            for j in range(0,len(M)):
                if(i!=j and i!=0 and j!=0 and i<j):
                    s = M[i][0]+ M[0][j]-M[i][j] 
                    s = round(s,3)
                    t = (i+1,j+1,s)
                    ahorros.append(t)
        ahorros = sorted(ahorros, key=lambda x: x[2], reverse=True)
        return ahorros
    
    def obtenerAhorro(self,v1,v2):
        pass 

    def removerAhorros(self,lista,i,c):
        ret = [x for x in lista if x[i]!=c]
        return ret

    def mezclarRuta(self,r1,r2):
        #r1 y r2 son índices de las rutas.
        self[r1].cargarDesdeSecuenciaDeVertices(self[r1].getV() + self[r2].getV()[1:])
        
    def ordenarRutasPorCarga(self, inverso=None):
        if(inverso is None):
            inverso = False
        self.__rutas =  sorted(self.getRutas(),key=lambda x: x.cargaTotal(self.getDemanda()),reverse=inverso)

    def getRutasOrdenadasPorCosto(self,inverso=None):
        if(inverso is None):
            inverso = False
        return sorted(self.getRutas(),key=lambda x: x.getCostoAsociado(),reverse=inverso)

    def clarkWright2(self):
        ahorros = self.obtenerAhorros()
        dem = self.getDemanda()
        print(ahorros)
        self.__rutas = []
        for i in range(2,self.getGrado()+1):
            R = Ruta(self.getMatriz())
            R.addCliente(i)
            self.addRuta(R)
        self.crearDictBusqueda()
        self.mostrarDictBusqueda()

        iteracion = 0
        while(len(ahorros)!=1):
            mejorAhorro = ahorros.pop(0)
            i = self.buscar(mejorAhorro[0]) # i = (r1,c1) índice de la ruta en la que se encuentra 
            j = self.buscar(mejorAhorro[1]) # igual que i
            r = self[i[0]]
            cargaRuta = r.cargaTotal(dem)
            demCliente = dem[mejorAhorro[1]-1]
            esInterno = self[j[0]].esInterno(mejorAhorro[1])
            if(cargaRuta+demCliente < self.getCapacidad() and not esInterno):
                r.addCliente(Vertice(mejorAhorro[1]))
                rutas = self.getRutas()
                ahorros = self.removerAhorros(ahorros,0,mejorAhorro[0])
                ahorros = self.removerAhorros(ahorros,1,mejorAhorro[1])
                self.removeRuta(j[0])
                self.crearDictBusqueda()
            iteracion += 1    
            self.getCostoTotal()

        if(len(self.getRutas())>self.getNroVehiculos()):
            nRutasSobrantes = len(self.getRutas())-self.getNroVehiculos()

            while(nRutasSobrantes!=0):
                self.ordenarRutasPorCarga(True)
                print("RUTAS ORDENADAS")
                print(self.getRutas())
                print(self.getRutasOrdenadasPorCosto())
    


    def clarkWright(self):
        ahorros = self.obtenerAhorros()
        dem = self.getDemanda()
        self.__rutas = []
        for i in range(2,self.getGrado()+1):
            R = Ruta(self.getMatriz())
            R.addCliente(i)
            self.addRuta(R)
        self.crearDictBusqueda()
        self.mostrarDictBusqueda()

        # primerAhorro = ahorros.pop(0)
        # R = Ruta(self.getMatriz())
        # R.addCliente(primerAhorro[0])
        # R.addCliente(primerAhorro[1])
        
        iteracion = 0
        while(len(ahorros)!=1 and len(self.getRutas())!=self.getNroVehiculos()):
            mejorAhorro = ahorros.pop(0)
            i = self.buscar(mejorAhorro[0]) # i = (r1,c1) índice de la ruta en la que se encuentra 
            j = self.buscar(mejorAhorro[1]) # igual que i
            IesInterno = self[i[0]].esInterno(mejorAhorro[0])
            JesInterno = self[j[0]].esInterno(mejorAhorro[1])
            demCliente = dem[mejorAhorro[1]-1]
            capacidad = self.getCapacidad()
            ruta = self.getRutas()
            if (len(self[i[0]]) == 2 and len(self[j[0]]) == 2) or (self.estaEnUnRutaNoVacia(i[0]) and not IesInterno and self.estaEnUnRutaNoVacia(j[0]) and not JesInterno and i[0]!=j[0]):
                carga1 = self[i[0]].cargaTotal(dem)
                carga2 = self[j[0]].cargaTotal(dem)
                if(carga1 + carga2 <= capacidad):
                    self.mezclarRuta(i[0],j[0])
                    self.removeRuta(j[0])
                    self.crearDictBusqueda()
            else: 
                if(self.estaEnUnRutaNoVacia(i[0]) and not self.estaEnUnRutaNoVacia(j[0]) and not IesInterno):
                    demCliente = dem[mejorAhorro[1]-1]
                    cargaRuta = self[i[0]].cargaTotal(dem)
                    if(cargaRuta+demCliente <= capacidad):
                        self[i[0]].addCliente(mejorAhorro[1],V=mejorAhorro[0])
                        self.removeRuta(j[0])
                        self.crearDictBusqueda()
                        i = self.buscar(mejorAhorro[0])
                        IesInterno = self[i[0]].esInterno(mejorAhorro[0])
                        JesInterno = self[i[0]].esInterno(mejorAhorro[1])
                        # if(IesInterno or JesInterno):
                        #     if(IesInterno):
                        #         ahorros = self.removerAhorros(ahorros,0,mejorAhorro[0])
                        #         ahorros = self.removerAhorros(ahorros,1,mejorAhorro[0])
                        #     elif(JesInterno):
                        #         ahorros = self.removerAhorros(ahorros,0,mejorAhorro[1])
                        #         ahorros = self.removerAhorros(ahorros,1,mejorAhorro[1])
                        self.crearDictBusqueda()

                        self.setCostoTotal()
                elif(self.estaEnUnRutaNoVacia(j[0]) and  not self.estaEnUnRutaNoVacia(i[0]) and not JesInterno):
                    demCliente = dem[mejorAhorro[0]-1]
                    cargaRuta = self[j[0]].cargaTotal(dem)
                    if(cargaRuta+demCliente <= capacidad):
                        if(j[1]==1):
                            self[j[0]].addCliente(mejorAhorro[0],index=1)
                        else:
                            self[j[0]].addCliente(mejorAhorro[0],V=mejorAhorro[1])
                        self.removeRuta(i[0])
                        self.crearDictBusqueda()
                        j = self.buscar(mejorAhorro[1])
                        JesInterno = self[j[0]].esInterno(mejorAhorro[0])
                        IesInterno = self[j[0]].esInterno(mejorAhorro[1])
                        # if(IesInterno or JesInterno):
                        #     if(IesInterno):
                        #         ahorros = self.removerAhorros(ahorros,0,mejorAhorro[1])
                        #         ahorros = self.removerAhorros(ahorros,1,mejorAhorro[1])
                        #     elif(JesInterno):
                        #         ahorros = self.removerAhorros(ahorros,0,mejorAhorro[0])
                        #         ahorros = self.removerAhorros(ahorros,1,mejorAhorro[0])
                        self.crearDictBusqueda()

                        self.setCostoTotal()

            iteracion +=1
            


    

    def estaEnUnRutaNoVacia(self,v1):
        return len(self[v1])>2 

if __name__ == "__main__":
    
    arg = Ingreso(sys.argv)
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

    #G = Grafo(matriz)
    G = Grafo(arg.M)
    #D demanda; NV nro de vehículos; C capacidad. G: Grafo, podría ser una matriz también
    S = Solucion(G,arg.D,arg.NV,arg.C,arg.I)
    S.penalizarSolucion(1)
    #S = Solucion(G,dem,3,16,0)
    S.clarkWright()
    print(S)
    #g1 = Grafico(arg.coordenadas,S.solucionToList(),arg.nombreArchivo)
    

    #print("Se cargó la")
    #print(S.getDemanda())
    #print(S.getCapacidadDisponible())
    #print(S)   
    #print(S.clarkWright())
    #print(S.getCapacidad())
    #print(S.getMatriz())
    #print(S[0][2][3])
    #print(S.getMatriz()[14][17])
    #print(S.getMatriz())
        
    # print(S[0])
    # print(S[1])
    #print(S)
    #print("evaluación: ", S.evaluarCapacidad(9,7))
    
    #S.customerSwap(9,7)
    #S.penalizarSolucion(1)
    # print(S[0])
    # print(S[1])
    #print(S)
    #S.buscarMejorMovimiento()
    
    #g2 = Grafico(arg.coordenadas,S.solucionToList(),arg.nombreArchivo)

















    #g = Ruta(arg.M)
    #v1 = Vertice(4)
    #v2 = Vertice(2)

    # print(g[None][v1])
    # print(" ")
    # print(g[v2][None])
    # print(" ")
    # print(g[None][None])
    # print(g[2][5])  #6
    # print(g[v1][3]) #7
    # print(g[2][v2]) #4
    # print(g[v1][v2])#5 

    # print(g[2][v2]) #4
    # print(g[v1][v2])#5 
