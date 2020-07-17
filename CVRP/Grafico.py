import matplotlib.pyplot as plot
import numpy as np
import math

class Grafico():
    def __init__(self,clientes,rutas,titulo=None):
        self.clientes = clientes
        self.rutas = rutas
        self.dibujarRutas()
        self.dibujarClientes()
        plot.set_ = titulo
        self.mostrarGrafico()

    
    def dibujarClientes(self):
        for c in self.clientes:
            if(c[0]==1):
                plot.plot(c[1],c[2],"ro")
                plot.text(c[1]+1, c[2]+1, str(c[0])) 
            else:
                plot.plot(c[1],c[2],"ko")
                plot.text(c[1]+1, c[2]+1, str(c[0])) 

    def dibujarRutas(self):
        c = self.clientes
        coordenadasRutas = []
        for r in self.rutas:
            cx = []
            cy = []
            for i in range(len(r)):
                cli = c[r[i]-1]
                cx.append(cli[1])
                cy.append(cli[2])
            cx.append(c[0][1])
            cy.append(c[0][2])
            coord = [cx,cy]
            coordenadasRutas.append(coord)
            
        
        i=1
        for r in coordenadasRutas:
            plot.plot(r[0],r[1],label="ruta"+str(i))
            i+=1
        plot.legend()
        # for r in coordenadasRutas:
        #     plot.plot(r[0][0:2],r[1][0:2],"w--")


    def mostrarGrafico(self):
        plot.show()

    def solucionToList(self, solucion):
        rutas =[]
        for r in solucion.getV():
            ruta = []
            for v in r.getV():
                ruta.append(v.getValue())
            rutas.append(ruta)
        return rutas