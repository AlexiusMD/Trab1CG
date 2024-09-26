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
        self.entry_at_line_start = True
        self.inverted = False
    
    """ Imprime os valores de cada eixo do ponto """
    # Faz a impressao usando sobrecarga de funcao
    # https://www.educative.io/edpresso/what-is-method-overloading-in-python
    def imprime(self, msg=None):
        if msg is not None:
            print(msg)

    """ Define o modelo a ser usada para a desenhar """
    def setModelo(self, func):
        self.modelo = func

    def update_position(self):
        if self.curva:
            self.posicao = self.curva.Calcula(self.t)

    def moveOnCurve(self, is_moving_forward):
        print(f"entry: {self.entry_at_line_start} movement: {is_moving_forward}")
        if not (is_moving_forward ^ self.entry_at_line_start):
            self.increaseT(is_moving_forward)
        else:
            self.decreaseT(is_moving_forward)

    def increaseT(self, is_moving_forward):
        self.t += 0.05
        if self.t > 1:
            self.t = 1
            self.switchCurve(is_moving_forward)
        self.update_position()

    def decreaseT(self, is_moving_forward):
        self.t -= 0.05
        if self.t < 0:
            self.t = 0
            self.switchCurve(is_moving_forward)
        self.update_position()

    def switchCurve(self, is_moving_forward):
        next_curve = self.selectCurves(is_moving_forward)
        self.curva = next_curve

    def selectCurves(self, is_moving_forward):
        if not (self.entry_at_line_start ^ is_moving_forward):
            self.entry_at_line_start = not self.entry_at_line_start
            return random.choice(self.curva.getAdjacentCurvesAtEnd())
        
        self.entry_at_line_start = not self.entry_at_line_start
        return random.choice(self.curva.getAdjacentCurvesAtStart())
    
    def Desenha(self):
        glPushMatrix()
        glTranslatef(self.posicao.x, self.posicao.y, 0)
        glRotatef(self.rotacao, 0, 0, 1)
        glScalef(self.escala.x, self.escala.y, self.escala.z)
        self.modelo()
        glPopMatrix() 
