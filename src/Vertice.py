class Vertice():

    def __init__(self,V):
        self._value = V

    def getValue(self):
        return self._value
    def setValue(self, V):
        self._value = V
    def __str__(self):
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