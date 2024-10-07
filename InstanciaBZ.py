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
import math

class InstanciaBZ:   
    def __init__(self, curva, type):
        self.type = type
        self.posicao = Ponto(0, 0, 0)
        self.escala = Ponto(1, 1, 1)
        self.rotacao: float = 0.0
        self.modelo = None
        self.t = 0.0
        self.curva = curva
        self.entry_at_line_start = True
        self.is_moving_forward = True
        self.previous_movement_direction = None
        self.next_curve = curva
        self.is_next_curve_set = False
        self.inverted = False
        self.center = Ponto(0, 4.67, 0)
        self.velocity = 0.7
        self.curve_list = self.curva.getAdjacentCurvesAtEnd()

    def imprime(self, msg=None):
        if msg is not None:
            print(msg)

    def setModelo(self, func):
        self.modelo = func

    def update_position(self):
        if self.curva:
            self.posicao = self.curva.Calcula(self.t)

    def moveOnCurve(self, is_moving_forward):
        self.is_moving_forward = is_moving_forward
        if self.previous_movement_direction != is_moving_forward:
            self.is_next_curve_set = False

        self.previous_movement_direction = is_moving_forward

        if not (is_moving_forward ^ self.entry_at_line_start):
            self.increaseT()
        else:
            self.decreaseT()

    def increaseT(self):
        deltaT = self.velocity / self.curva.ComprimentoTotalDaCurva
        self.t += deltaT
        if self.t >= 0.5 and not self.is_next_curve_set:
            self.next_curve = self.selectCurves()
        if self.t > 1:
            self.t = 1
            self.switchCurve()
        self.update_position()

    def decreaseT(self):
        deltaT = self.velocity / self.curva.ComprimentoTotalDaCurva
        self.t -= deltaT
        if self.t <= 0.5 and not self.is_next_curve_set:
            self.next_curve = self.selectCurves()
        if self.t < 0:
            self.t = 0
            self.switchCurve()
        self.update_position()

    def switchCurve(self):
        self.is_next_curve_set = False
        self.entry_at_line_start = not self.entry_at_line_start
        self.curva = self.next_curve

    def selectCurves(self):
        self.is_next_curve_set = True
        if not (self.entry_at_line_start ^ self.is_moving_forward):
            self.curve_list = self.curva.getAdjacentCurvesAtEnd()
            return random.choice(self.curva.getAdjacentCurvesAtEnd())
        
        self.curve_list = self.curva.getAdjacentCurvesAtStart()
        return random.choice(self.curva.getAdjacentCurvesAtStart())

    def calculateTangent(self):
        delta = 0.001
        t_next = min(self.t + delta, 1.0)
        current_pos = self.curva.Calcula(self.t)
        next_pos = self.curva.Calcula(t_next)
        tangent = Ponto(next_pos.x - current_pos.x, next_pos.y - current_pos.y, 0)
        return tangent

    def calculateRotation(self):
        tangent = self.calculateTangent()
        angle = math.atan2(tangent.y, tangent.x)
        
        if angle == 0:
            return self.rotacao

        if not (self.entry_at_line_start ^ self.is_moving_forward):
            return math.degrees(angle) - 90
        return math.degrees(angle) + 90
    
    def onDemandCurve(self):
        current_index = self.curve_list.index(self.next_curve)
        next_curve_index = (current_index + 1) % len(self.curve_list)
        self.next_curve = self.curve_list[next_curve_index]

    def Desenha(self):
        self.rotacao = self.calculateRotation()
        
        glPushMatrix()
        glTranslatef(self.posicao.x, self.posicao.y, 0)
        glRotatef(self.rotacao, 0, 0, 1)
        glTranslatef(-self.center.x, -self.center.y, 0)
        glScalef(self.escala.x, self.escala.y, self.escala.z)
        self.modelo()
        glPopMatrix()