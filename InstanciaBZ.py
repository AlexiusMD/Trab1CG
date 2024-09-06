# ************************************************
#   InstanciaBZ.py
#   Define a classe Instancia
#   Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
# ************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Ponto import *
import random

""" Classe Instancia """
class InstanciaBZ:   
    def __init__(self, curva):
        self.posicao = Ponto (0,0,0) 
        self.escala = Ponto (1,1,1)
        self.rotacao:float = 0.0
        self.modelo = None
        self.t = 0.0
        self.curva = curva
        self.forward = True
    
    """ Imprime os valores de cada eixo do ponto """
    # Faz a impressao usando sobrecarga de funcao
    # https://www.educative.io/edpresso/what-is-method-overloading-in-python
    def imprime(self, msg=None):
        if msg is not None:
            pass 
        else:
            print ("Rotacao:", self.rotacao)

    """ Define o modelo a ser usada para a desenhar """
    def setModelo(self, func):
        self.modelo = func

    def update_position(self):
        if self.curva:
            self.posicao = self.curva.Calcula(self.t)

    def moveUpCurve(self):
        if self.forward:
            self.increaseT()
        else:
            self.decreaseT()

    def moveDownCurve(self):
        if self.forward:
            self.decreaseT()
        else:
            self.increaseT()

    def increaseT(self):
        self.t += 0.05 if self.t < 1 else 0
        self.update_position()

    def decreaseT(self):
        self.t -= 0.05 if self.t > 0 else 0
        self.update_position()

    # def updateCurve(self):
    #     adj = self.curva.getAdjacentCurvesAtEnd()
    #     self.curva = random.choice(adj)

    def switchCurve(self, next_curve):
        next_curve_start = next_curve.getPC(0)
        next_curve_end = next_curve.getPC(2)

        self.curva = next_curve
        if self.t > 1:
            self.posicao = next_curve_end
            self.t = 1
            self.forward = not self.forward
        
        if self.t < 0:
            self.posicao = next_curve_start
            self.t = 0
            self.forward = not self.forward
    

    def Desenha(self):
        # print ("Desenha")
        # self.escala.imprime("\tEscala: ")
        print ("\tRotacao: ", self.rotacao)

        if self.t > 1:
            next_curve = random.choice(self.curva.getAdjacentCurvesAtEnd())
            self.switchCurve(next_curve)

        if self.t < 0:
            next_curve = random.choice(self.curva.getAdjacentCurvesAtStart())
            self.switchCurve(next_curve)

        glPushMatrix()
        glTranslatef(self.posicao.x, self.posicao.y, 0)
        glRotatef(self.rotacao, 0, 0, 1)
        glScalef(self.escala.x, self.escala.y, self.escala.z)
        self.modelo()
        glPopMatrix()

    
