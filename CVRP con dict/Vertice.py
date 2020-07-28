class Vertice():

    def __init__(self,V, D=None):
        self._value = V
        if D is None:
            self._demanda = 0
        else:
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

    def __hash__(self):
        return hash(self.getValue())

if __name__ == "__main__":
    v1 = Vertice(1,4)
    v2 = Vertice(2,4)

    print(hash(v2))
