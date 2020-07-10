
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
