from Vertice import Vertice
from Arista import Arista
import sys
import re
import math 
import copy

class FilaMatrizDistancia():
    def __init__(self,F,A = None,isNone=True,primerKey=0):
        self.__F = F
        self.__A = A
        self.__isNone = isNone
        self.__primerKey = primerKey

    def __getitem__(self,key):
        if(key is None):
            if(self.__isNone):
                return self.__A
            else:
                return [x for x in self.__A if x.tieneOrigen(self.__primerKey)]
        else:
            if(self.__isNone):
                return [x for x in self.__A if x.tieneDestino(key)]
            else:
                if(isinstance(key,Vertice)):                             
                    return self.__F[key.getValue()-1]                    
                elif(isinstance(key,int)):                              
                    return self.__F[key-1]




    
    def __repr__(self):
        return self.__F


class Grafo:
    def __init__(self, M: list=None):
        self._V = []
        self._A = []
        self._costoAsociado = 0
        self._grado = 0
        self._matrizDistancias = M
        if(M!=[] and not M is None):
            self.cargarDesdeMatriz(M)
            self._grado = len(M)
        
    def getGrado(self):
        return self._grado
    def setA(self, A):
        self._A = A
    def setV(self, V):
        self._V = V
    def getA(self):
        return self._A
    def getV(self):
        return self._V
    def getCostoAsociado(self):
        return self._costoAsociado
    def __lt__(self, otro):
        return (self._costoAsociado < otro.__costoAsociado and self.__class__ == otro.__class__)
    def __le__(self, otro):
        return (self._costoAsociado <= otro.__costoAsociado and self.__class__ == otro.__class__)
    def __gt__(self, otro):
        return (self._costoAsociado > otro.__costoAsociado and self.__class__ == otro.__class__)
    def __ge__(self, otro):
        return (self._costoAsociado >= otro.__costoAsociado and self.__class__ == otro.__class__)
    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self._costoAsociado == other.__costoAsociado)
    def __ne__(self, other):
        return (self.__class__ == other.__class__ and self._costoAsociado != other.__costoAsociado)

    def __str__(self):
        salida = ""
        V = self.getV()
        #Muestra la primera fila con los vertices
        if(len(self._matrizDistancias) == len(self.getV())):
            for i in range(0,len(V)):
                if(V[i]>=10):
                    salida += "        " +  str(V[i])
                else:
                    salida += "        " +  str(V[i]) + " "

            salida = salida + "\n"
            for i in range(0,len(V)):
                if(V[i] >= 10):
                    salida += str(V[i]) + "    "
                else:
                    salida += str(V[i]) + "     "
                for j in range(0,len(V)):
                    if(self._matrizDistancias[i][j]==999999999999):
                        salida += str(0) + "         "
                    else:
                        salida += str(self._matrizDistancias[i][j]) + "    "
                salida = salida + "\n"
        else:
            for i in range(0,len(V)):
                salida += str(V[i]) + "         "

            salida = salida + "\n"
            for i in V:
                salida += str(i) + "    "
                for j in V:
                    indice = self.getCostoArista(Arista(i,j,0))
                    salida += str(self.getA()[indice].getPeso()) + "    "
                salida = salida + "\n"
        return salida
    
    def __repr__(self):
        if(self != None):
            return str(self.getV)
    
    #Compara entre 2. Se fija si hay aristas de A contenidas en si misma. Si hay aristas, se detiene
    def contieneA(self,A):
        sigue = True
        i = 0
        n = len(self.getA())
        while((sigue == True) and i < n):
            if(self.getA()[i].tieneOrigen(A.getOrigen()) and self.getA()[i].tieneDestino(A.getDestino())):
                sigue = False
                i=n
            i+=1
        return not(sigue)

    def getCostoArista(self, A):
        sigue = True
        i = 0
        n = len(self.getA())
        while((sigue == True) and i < n):
            if(self.getA()[i].tieneOrigen(A.getOrigen()) and self.getA()[i].tieneDestino(A.getDestino())):
                sigue = False
            i+=1
        return i-1

    def getAristaMinima(self,listaAristas):
        minimo = listaAristas[0]
        for i in listaAristas:
            if(i.getPeso() < minimo.getPeso()):
                minimo = i

        return minimo

    def cargaVertices(self, secuencia):
        V = []
        for x in secuencia:
            V.append(Vertice(int(x)+1))
        return V

    def cargaAristas(self):
        A=[]
        cantV = len(self._V)
        for row in range(1,cantV):
            for col in range(1, cantV):
                arista_aux = Arista(row,col,self._matrizDistancias[row][col])
                A.append(arista_aux)
        
        print("Aristas: \n",A)
        return A

    def aristasConOrigen(self, V):
        salida = []
        for arista in self.getA():
            if((arista.tieneOrigen(V)) == True):
                salida.append(arista)

        return salida

    def aristasConDestino(self, V):
        salida = []
        for arista in self.getA():
            if((arista.tieneDestino(V)) == True):
                salida.append(arista)
        return salida
    
    #Cargar las aristas
    def cargarDesdeMatriz(self, Matriz):
        for fila in range(0, len(Matriz)):
            self._V.append(Vertice(fila+1))    #V=[1,3,4] A=[(1,3)(3,4)] => sol 1->3->4->5->2
        for fila in range(0, len(Matriz)):
            for columna in range(0, len(Matriz[fila])):
                aux = Arista(self._V[fila],self._V[columna],(Matriz[fila][columna]))
                self._A.append(aux)

    def getVerticeInicio(self):
        return self._A[0].getOrigen()

    def getMatriz(self):
        return self._matrizDistancias
    
    def setMatriz(self, M):
        self._matrizDistancias = M

    #Para que cargue desde una secuencia de vertices por ej. s1= [1,3,4,5,8,9,6,7] -> s2=[1,3,9,5,8,4,6,7]
    def cargarDesdeSecuenciaDeVertices(self,seq:list):
        self._V = seq
        self._A = []
        rV = [] #Vértices de la matriz ordenados, para obtener la referencia en la matriz de distnacias
        costo = 0
        for j in range(0,len(self.getMatriz())):
            rV.append(Vertice(j+1))
        
        for i in range(0,len(seq)-1):
            dist = self[seq[i]][seq[i+1]] #Referencias en la matriz
            self.getA().append(Arista(seq[i], seq[i+1], dist))
            costo+= dist
        
        origenLast= seq[len(seq)-1]
        destinoLast= Vertice(1)
        a = Arista(origenLast,destinoLast,self[origenLast][destinoLast])
        
        self._A.append(a)

        self._costoAsociado = costo + self[origenLast][destinoLast]

    def cargarDesdeSecuenciaDeAristas(self,seq):
        self._A = seq
        self._V = []
        costo = 0
        for a in seq:
            self._V.append(a.getOrigen())
            costo += a.getPeso()

        origenLast= seq[len(seq)-1].getDestino()
        if(origenLast!=Vertice(1)):
            destinoLast= Vertice(1)
            a = Arista(origenLast,destinoLast,self[origenLast][destinoLast])
            costo += a.getPeso()
            self._A.append(a)
        self._costoAsociado = costo

    def setCosto(self, costo=None):
        suma = 0
        for a in self.getA():
            suma += a.getPeso()


        self._costoAsociado = suma


    def incrementaFrecuencia(self):
        for x in range(0,len(self.getA())):
            self.getA()[x].incFrecuencia()

    def swap_3opt(self, v1, v2, v3):
        copiaV = copy.deepcopy(self._V)

        copiaV[self._V.index(v1)]=v2    
        copiaV[self._V.index(v2)]=v3    
        copiaV[self._V.index(v3)]=v1    

        gNuevo = Grafo([])
        gNuevo.setMatriz(self.getMatriz())
        gNuevo.cargarDesdeSecuenciaDeVertices(copiaV)
        return gNuevo

    def swap_4opt(self, v1, v2, v3, v4):
        copiaV = copy.deepcopy(self._V)

        #[1,2,3,4]  -> 2opt: [2,1,4,3]
        #[1,2,3,4]  -> 4opt: [2,3,4,1]
        copiaV[self._V.index(v1)]=v2    #[2,2,3,4]
        copiaV[self._V.index(v2)]=v3    #[2,3,3,4]
        copiaV[self._V.index(v3)]=v4    #[2,3,4,4]
        copiaV[self._V.index(v4)]=v1    #[2,3,4,1]

        gNuevo = Grafo([])
        gNuevo.setMatriz(self.getMatriz())
        gNuevo.cargarDesdeSecuenciaDeVertices(copiaV)
        return gNuevo

    


#[v][v]
#[v][int]
#[int][v]
#[int][int]
#[None][int] 
#[int][None]
#[None][v]
#[v][None]
#[None][None] --> Retorna toda la lista :D 
    def __getitem__(self,key=None):
        if(key is None):
            return FilaMatrizDistancia(self.getMatriz(),self.getA(),key)
        else:
            if(isinstance(key,Vertice)):
                return FilaMatrizDistancia(self.getMatriz()[key.getValue()-1],self.getA(),False,key)
            elif(isinstance(key,int)):
                return FilaMatrizDistancia(self.getMatriz()[key-1],self.getA(),False,key)



    
