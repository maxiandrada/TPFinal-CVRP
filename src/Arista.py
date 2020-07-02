from Vertice import Vertice

class Arista():
    def __init__(self,origen,destino, peso):
        if(isinstance(origen,int)):
            origen = Vertice(origen)
        if(isinstance(origen,int)):
            destino = Vertice(destino)
        self._origen = origen
        self._destino = destino
        self._peso = peso
        self._frecuencia = 0
    
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

    def tieneOrigen(self,V):
        return (V == self.getOrigen())
    
    def tieneDestino(self,V):
        return (V == self.getDestino())
    
    def __eq__(self, A):
        if ((self.__class__ == A.__class__) & (self.getOrigen() == A.getOrigen())):
            if(self.getDestino() == A.getDestino()):
                if (A.getPeso()!= None):
                    return (self.getPeso() == A.getPeso())
                else:
                    return True
            else:
                return False
        else:
            return False

    def __ne__(self, A):
        return((self.__class__ == A.__class__) & (self.getOrigen() != A.getOrigen()) & (self.getDestino() != A.getDestino()))

    def __str__(self):
        return "(" + str(self._origen) + "," + str(self._destino) + "," + str(self._peso) + ")"

    def __repr__(self):
        return str(self)



    