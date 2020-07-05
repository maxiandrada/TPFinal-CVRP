from Vertice import Vertice

class Arista():
    def __init__(self,origen,destino,peso):
        self._origen = origen
        self._destino = destino
        self._peso = peso
        self._frecuencia = 0
        self._id = 0
    
    def incFrecuencia(self):
        self._frecuencia+=1

    def getFrecuencia(self):
        return self._frecuencia

    def setOrigen(self, origen):
        self._origen = origen
            
    def setDestino(self, destino):
        self._destino = destino

    def setPeso(self, peso):
        self._peso = peso
    
    def getOrigen(self):
        return self._origen

    def getDestino(self):
        return self._destino

    def getPeso(self):
        return self._peso

    def setId(self, fila, col, tam):
        if(fila<col):
            id = fila*tam + col
        else:
            id = col*tam + fila
        self._id = id

    def getId(self):
        return self._id

    def tieneOrigen(self,V):
        return (V == self.getOrigen())
    
    def tieneDestino(self,V):
        return (V == self.getDestino())

    def invertir(self):
        dest = self._destino
        self._destino = self._origen
        self._origen = dest
    
    def __eq__(self, A):
        eq = ((self.getOrigen() == A.getOrigen()) and (self.getDestino() == A.getDestino())) or ((self.getOrigen() == A.getDestino()) and (self.getDestino() == A.getOrigen()))
        return ((self.__class__ == A.__class__) and eq)

    def __ne__(self, A):
        neq = self.getOrigen() != A.getOrigen() and self.getDestino() != A.getDestino() and self.getOrigen() != A.getDestino() and self.getDestino() != A.getOrigen()
        return((self.__class__ == A.__class__) & neq)

    def __str__(self):
        return "(" + str(self._origen) + "," + str(self._destino) + "," + str(self._peso) + ")"

    def __repr__(self):
        return str(self)

     