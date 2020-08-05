import copy
class camino():
    def __init__(self, s, g):
        self.__s = s
        self.__g = g
        self.__indS = [0,1] #(ruta, vertice)
        self.__indG = [0,1]
        self.__cond1 = self.igualesTam()
        self.__cond2 = self.igualesRec()

    def getInd(self): #retorna tupla
        return self.__indS

    def igualesTam(self):
        i = 0
        while i < len(self.__s) and len(self.__s[i]) == len(self.__g[i]):
            i += 1
        if i<len(self.__s):
            return False
        else:
            return True

    def igualesRec(self):
        indS = [0,1]
        indG = [0,1]
        band = True
        while band and indS!= None and indG!=None:
            if self.__s[indS[0]][indS[1]] != self.__g[indG[0]][indG[1]]:
                band = False
            indS = self.incIndS(indS)
            indG = self.incIndG(indG)
        if band:
            return True
        else:
            return False

    def pathRelinking (self):
        # print ("----inicio pr----")
        aux1 = -1
        aux2 = -1
        if not self.iguales():
            if not self.__cond2:
                aux1 = self.__s[self.__indS[0]][self.__indS[1]]
                aux2 = self.__g[self.__indG[0]][self.__indG[1]]
                self.__s[self.__indS[0]][self.__indS[1]] = self.__g[self.__indG[0]][self.__indG[1]] #Recordar que hacer con indG
                indS=self.incIndS(self.__indS) 
                indG=self.incIndG(self.__indG)
                if indS!=None and indG!=None:
                    # print ("Los indices no son None")
                    self.__indS=self.incIndS(self.__indS) 
                    self.__indG=self.incIndG(self.__indG)            
                    # print ("indices:"+str(self.__indS)+str(self.__indG))
                    band = True
                    while indS!=None and band:
                        if self.__s[indS[0]][indS[1]] == aux2:
                            self.__s[indS[0]][indS[1]] = aux1
                            band = False
                        indS = self.incIndS(indS)
                    self.__cond2 = self.igualesRec()
                    return self.__s
                else:
                    self.__cond2 = self.igualesRec()
                    return self.__s
            elif not self.__cond1:
                i = 0
                b = True
                while b and i < len(self.__s):
                    if len(self.__s[i]) < len(self.__g[i]):
                        self.__s[i].append(self.__s[i+1].pop(1))
                        b = False
                    elif len(self.__s[i]) > len(self.__g[i]):
                        self.__s[i+1].insert(1, self.__s[i].pop(-1))
                        b = False
                    else:
                        i+=1
                self.__cond1 = self.igualesTam()
                return self.__s
            else:
                print ("Ya llegamos a la solución guía")
                return []
        else:
            print ("Ya llegamos a la solución guía")
            return []

# [[1,4,5,2][1,9,8][1,3,6,7]]

# [[1,2,5,4][1,9,8][1,3,6,7]] 2
# [[1,2,3,4][1,9,8][1,5,6,7]] 5
# [[1,2,3,4][1,5,8][1,9,6,7]] 9
# [[1,2,3,4][1,5,6][1,9,8,7]] 8
# [[1,2,3,4][1,5,6][1,7,8,9]] 9
# [[1,2,3][1,4,5,6][1,7,8,9]]
# [[1,2][1,3,4,5,6][1,7,8,9]]

# [[1,2][1,3,4,5,6,7][1,8,9]]

    def incIndS(self, indS):
        ind = copy.deepcopy(indS)
        if ind != None:
            if ind[1]+1 < len(self.__s[ind[0]]):
                ind[1]+=1
                return ind
            else:
                if ind[0]+1 < len(self.__s):
                    ind[0]+=1
                    ind[1]=1
                    return ind
                else:
                    return None #es el último de la secuencia
        else:
            return None

    def incIndG(self, indG):
        ind = copy.deepcopy(indG)
        if ind != None:
            if ind[1]+1 < len(self.__g[ind[0]]):
                ind[1]+=1
                return ind
            else:
                if ind[0]+1 < len(self.__g):
                    ind[0]+=1
                    ind[1]=1
                    return ind
                else:
                    return None #es el último de la secuencia
        else:
            return None

    def iguales(self):
        if self.__cond1 and self.__cond2:
            return True
        else:
            return False
    
    # def chequeaConsistencia(self):
    #     if len(self.__s) == len(self.__g):
    #         countS = 0
    #         band = True
    #         for r in self.__s:
    #             countS += len(r)
    #             if r[0] != 1:
    #                 band = False 
    #         countG = 0
    #         for r in self.__g:
    #             countG += len(r)
    #             if r[0] != 1:
    #                 band = False 
    #         if countG == countS and band:
                
    #         else:
    #             return False
    #     else:
    #         return False
#### SECCION DE PRUEBAS ####
s = [[1,4,5,2],[1,9,8],[1,3,6,7,10]]
g = [[1,2],[1,3,4,5,6,7],[1,8,9,10]]

caminito = camino(s, g)
c = caminito.pathRelinking()
ind =[0,1]
while c!=[]:
    print (str(c)+str(caminito.iguales()))
    c = caminito.pathRelinking()

print (str(caminito.iguales()))