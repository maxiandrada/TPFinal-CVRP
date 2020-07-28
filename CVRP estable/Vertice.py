class Vertice():

    def __init__(self,V, D):
        self._value = V
        self._demanda = D

    def getValue(self):
        return self._value
    def setValue(self, V):
        self._value = V
    def setDemanda(self, D):
        self._demanda = D
    def getDemanda(self):
        return self._demanda
    def __str__(self):
        #return "("+str(self._value)+","+str(self._demanda)+")"
        return str(self._value)
    def __repr__(self):
        return str(self)
    def __ne__(self,otro):
        if(self.__class__ != otro.__class__ ):
            return (int(self.getValue()) != int(otro))
        return (self.__class__ == otro.__class__ and str(self.getValue()) != str(otro.getValue()))
    def __eq__(self,otro):
        if(self.__class__ != otro.__class__ ):
            return (int(self.getValue()) == int(otro))
        return (self.__class__ == otro.__class__ and str(self.getValue()) == str(otro.getValue()))
    def __le__(self,otro):
        if(self.__class__ != otro.__class__ ):
            return (int(self.getValue()) <= int(otro))
        return (self.__class__ == otro.__class__ and str(self.getValue()) <= str(otro.getValue()))
    def __ge__(self,otro):
        if(self.__class__ != otro.__class__ ):
            return (int(self.getValue()) >= int(otro))
        return (self.__class__ == otro.__class__ and str(self.getValue()) >= str(otro.getValue()))