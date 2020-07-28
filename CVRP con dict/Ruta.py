from Vertice import Vertice as V
from Arista import Arista as A
from Grafo import Grafo

class Ruta(Grafo):
    def __init__(self, M, Demanda, capacidadMax,dictA = None):
        super(Ruta, self).__init__(M, Demanda)
        self.capacidad = 0
        self.capacidadMax = capacidadMax
        self.dictAristasRuta = {} #Contiene las aristas de busqueda
        if not dictA is None:
            self.dictA = dictA 
    
    def __str__(self):
        return str(self.getV())


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
        self.capacidadMax = capMax

    def setCapacidad(self, capacidad):
        self.capacidad = capacidad

    def getCapacidad(self):
        return self.capacidad

    def getCapacidadMax(self):
        return self.capacidadMax


    def mostrarDictAristasRuta(self):
        for i in self.dictAristasRuta.keys():
            print(f"{i}: {self.dictAristasRuta.get(i)}")

    #Retorna la arista que se está buscando, si se encuentra retorna la arista y si no retorna None
    #Se le puede pasar directamente la arista, o una tupla 
    def buscarAristaEnRuta(self,a):
        return self.dictAristasRuta.get(hash(a))
    

    #Verdadero si se encuentra "a" se encuentra en la ruta 
    def estaAristaEnRuta(self,a):
        buscado = self.buscarAristaEnRuta(a)
        if(buscado is None):
            return False
        else:
            return True

    def getCapacidadPorCliente(self):
        cad = ""
        for v in self.getV():
            cad+=(f"\nEl cliente {v.getValue()} tiene demanda {v.getDemanda()}")
        return cad 