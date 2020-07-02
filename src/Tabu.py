from Arista import Arista
class Tabu:
    def __init__(self, E, T):
        self.__elemento = E 
        self.__tenure = T
    
    def setElemento(self, E):
        self.__elemento = E
    
    def setTenure(self, T):
        self.__tenure = T
        
    def getElemento(self):
        return self.__elemento
    
    def getTenure(self):
        return self.__tenure

    def __eq__(self,E):
        return (self.getElemento() == E.getElemento())

    def __str__(self):
        return "("+str(self.__elemento)+","+str(self.__tenure)+")"  

    def __repr__(self):
        return "("+str(self.__elemento)+","+str(self.__tenure)+")" 
    
    def decrementaT(self):
        self.__tenure = self.__tenure -1
    
    def incrementaT(self):
        self.__tenure = self.__tenure +1

class ListaTabu():
    def __init__(self):
        self.__lista = []
    
    def addTabu(self,E,T):
        if(isinstance(E,tuple)):
            for i in E:
                self.__lista.append(Tabu(i,T))
        else:
            self.__lista.append(Tabu(E,T))

    def __str__(self):
        ret = ""
        if(self.__lista == []):
            ret = "Lista Tabú Vacía"
        else:
            for e in self.__lista:
                ret += str(e)
        return ret
        
    def removeTabu(self,E):
        self.__lista.remove(E)

    def getLista(self):
        return self.__lista
    def setLista(self, L):
        self.__lista = L

    def __len__(self):
        return len(self.__lista)
        
    def decrementaTenure(self):
        i=0
        while (i < len(self)):
            elemTabu=self[i]
            if(elemTabu.getTenure()!=-1):
                elemTabu.decrementaT()
            if(elemTabu.getTenure()==0):
                self.pop(i)
                i-=1
            i+=1

    def pop(self,index):
        return self.__lista.pop(index)

    def __getitem__(self,key):
        return self.__lista[key]
    
    def __contains__(self,elem):
        if(isinstance(elem,Arista)):
            return Tabu(elem,0) in self.__lista
        elif(isinstance(elem,Tabu)):
            return elem in self.__lista

    def getListaPermitidos(self,lista):
        ret = []
        for i in lista:
            if(i not in self):
                ret.append(i)
        return ret    

    