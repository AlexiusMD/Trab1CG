# ***********************************************************************************
#   ExibePoligonos.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa cria um conjunto de INSTANCIAS
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Sugere-se consultar também as páginas listadas
#   a seguir:
#   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#
#   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#   conforme a descrição que está nestes links:
#   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
# ***********************************************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import *
from InstanciaBZ import *
from Bezier import *
from ListaDeCoresRGB import *
import time
import random
# ***********************************************************************************

global current_curve

NUM_ENEMIES = 10
ValidCurves = {}
aux_points = []

# Modelos de Objetos
MeiaSeta = Polygon()
Mastro = Polygon()
Mapa = Polygon()
Control = Polygon()

# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()

# lista de instancias do Personagens
Personagens = [] 

# ***********************************************************************************
# Lista de curvas Bezier
Curvas = []

angulo = 0.0

start_time = None
last_frame_time = None
DELAY_BEFORE_MOVEMENT = 3

# ***********************************************************************************
#
# ***********************************************************************************
def CarregaModelos():
    global MeiaSeta, Mastro
    MeiaSeta.LePontosDeArquivo("MeiaSeta.txt")
    Mastro.LePontosDeArquivo("Mastro.txt")
    Mapa.LePontosDeArquivo("EstadoRS.txt")
    Control.LePontosDeArquivo("Control.txt")
    A, B = Mapa.getLimits()
    print("Limites do Mapa")
    A.imprime()
    B.imprime()

# ***********************************************************************************
def DesenhaPersonagem():
    SetColor(YellowGreen)
    glTranslatef(0,0,0)
    Mastro.desenhaPoligonoPreenchido()

def DesenhaInimigo():
    SetColor(Red)
    glTranslatef(0,0,0)
    Mastro.desenhaPoligonoPreenchido()

# ***********************************************************************************
# Esta função deve instanciar todos os personagens do cenário
# ***********************************************************************************
def CriaInstancias():
    global Personagens

    available_curves = list(range(0, len(Curvas)))
    curve = random.choice(available_curves)
    available_curves.remove(curve)

    Personagens.append(InstanciaBZ(Curvas[curve], "player"))
    Personagens[0].modelo = DesenhaPersonagem
    Personagens[0].rotacao = 0
    Personagens[0].posicao = Ponto(0,0)
    Personagens[0].escala = Ponto (1,1,1) 
    Personagens[0].velocity = 0

    for i in range(1, NUM_ENEMIES + 1):
        curve = random.choice(available_curves)
        available_curves.remove(curve)
        
        enemy = InstanciaBZ(Curvas[curve], "enemy")
        enemy.modelo = DesenhaInimigo
        enemy.rotacao = 0
        enemy.t = 0.5
        enemy.posicao = Curvas[curve].Calcula(enemy.t)
        enemy.escala = Ponto(1, 1, 1)
        
        Personagens.append(enemy)

# ***********************************************************************************
def CriaCurvas():
    global Curvas

    #Bezier(Começo, Controle, Fim)
    with open('Curves.txt') as f:
        lines = f.readlines()
        for line in lines[1:]:
            text = line.split()
            line_start = int(text[0])
            line_control = int(text[1])
            line_end = int(text[2])

            p1 = Control.getVertice(line_start)
            p2 = Control.getVertice(line_control)
            p3 = Control.getVertice(line_end)

            curve = Bezier(p1, p2, p3)

            Curvas.append(curve)
            addToValidCurves(curve, line_start)
            addToValidCurves(curve, line_end)

    for curva in Curvas:
        start = curva.Coords[0]
        end = curva.Coords[2]

        for curva_aux in Curvas:
            start_aux = curva_aux.Coords[0]
            end_aux = curva_aux.Coords[2]

            if start.x == start_aux.x and start.y == start_aux.y and curva_aux is not curva:
                curva.adjacentAtStart.append(curva_aux)
            if end.x == end_aux.x and end.y == end_aux.y and curva_aux is not curva:
                curva.adjacentAtEnd.append(curva_aux)

            # or (end.x == start_aux.x and end.y == start_aux.y)

# ***********************************************************************************

def addToValidCurves(curve, point):
    if point not in ValidCurves.keys():
        ValidCurves[point] = []

    ValidCurves[point].append(curve)


# ***********************************************************************************
def init():
    global Min, Max, start_time, last_frame_time
    # Define a cor do fundo da tela
    glClearColor(1, 1, 1, 1)

    CarregaModelos()
    CriaCurvas()
    CriaInstancias()

    d:float = 100
    Min = Ponto(-d,-d)
    Max = Ponto(d,d)

    start_time = time.time()
    last_frame_time = start_time

# ****************************************************************
def animate():
    global angulo
    angulo = angulo + 1
    glutPostRedisplay()

# ****************************************************************
def DesenhaLinha (P1, P2):
    glBegin(GL_LINES)
    glVertex3f(P1.x,P1.y,P1.z)
    glVertex3f(P2.x,P2.y,P2.z)
    glEnd()

# ****************************************************************
def RotacionaAoRedorDeUmPonto(alfa: float, P: Ponto):
    glTranslatef(P.x, P.y, P.z)
    glRotatef(alfa, 0,0,1)
    glTranslatef(-P.x, -P.y, -P.z)

# ***********************************************************************************
def reshape(w,h):

    global Min, Max
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Cria uma folga na Janela de Selecão, com 10% das dimensoes do poligono
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    #glOrtho(Min.x-BordaX, Max.x+BordaX, Min.y-BordaY, Max.y+BordaY, 0.0, 1.0)
    glOrtho(Min.x, Max.x, Min.y, Max.y, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

# **************************************************************
def DesenhaEixos():
    global Min, Max

    Meio = Ponto(); 
    Meio.x = (Max.x+Min.x)/2
    Meio.y = (Max.y+Min.y)/2
    Meio.z = (Max.z+Min.z)/2

    glBegin(GL_LINES)
    #  eixo horizontal
    glVertex2f(Min.x,Meio.y)
    glVertex2f(Max.x,Meio.y)
    #  eixo vertical
    glVertex2f(Meio.x,Min.y)
    glVertex2f(Meio.x,Max.y)
    glEnd()

# ***********************************************************************************
def DesenhaPersonagens(deltatime):
    for I in Personagens:
        I.Desenha(deltatime)


# ***********************************************************************************
# Versao 
def DesenhaPoligonoDeControle(curva):
    glBegin(GL_LINE_STRIP)
    for v in range(0,3):
        P = Curvas[curva].getPC(v)
        glVertex2d(P.x, P.y)
    glEnd()

# ****************************************************a*******************************
def DesenhaCurvas():
    v = 0
    #for v, I in enumerate(Curvas):
    for I in Curvas:

        if I == Personagens[0].next_curve:
            glLineWidth(6)
            SetColor(SkyBlue)
        else:
            glLineWidth(3)
            SetColor(SummerSky)
        I.Traca()
        glLineWidth(2)
        #SetColor(Bronze)
        #I.TracaPoligonoDeControle()
        #DesenhaPoligonoDeControle(v)

# ****************************************************a*******************************
def MovimentaPersonagens(deltatime):
    global start_time
    
    current_time = time.time()
    elapsed_time = current_time - start_time

    Jogador = Personagens[0]
    Inimigos = Personagens[1:]
    
    Personagens[0].moveOnCurve(Jogador.is_moving_forward, deltatime)

    if elapsed_time >= DELAY_BEFORE_MOVEMENT:
        direction = True
        for I in Inimigos:
            I.Desenha(deltatime)
            I.moveOnCurve(direction, deltatime)
            direction = not direction
    else:
        for I in Inimigos:
            I.Desenha(deltatime)

# ***********************************************************************************
# Executada todo frame
def display():
    global last_frame_time

	# Limpa a tela coma cor de fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(1,0,0) # R, G, B  [0..1]
    # DesenhaEixos()q

    DesenhaCurvas()

    current_time = time.time()
    deltatime = current_time - last_frame_time
    last_frame_time = current_time


    DesenhaPersonagens(deltatime)
    MovimentaPersonagens(deltatime)

    elapsed_time = current_time - start_time
    if elapsed_time < DELAY_BEFORE_MOVEMENT:
        remaining_time = int(DELAY_BEFORE_MOVEMENT - elapsed_time) + 1
        print(remaining_time)

    handleCollisions()

    glutSwapBuffers()

# ***********************************************************************************
# The function called whenever a key is pressed. 
# Note the use of Python tuples to pass in: (key, x, y)
#ESCAPE = '\033'
ESCAPE = b'\x1b'
def keyboard(*args):
    print (args)
    # If escape is pressed, kill everything.
    if args[0] == b'q':
        os._exit(0)
    if args[0] == ESCAPE:
        os._exit(0)
    if args[0] == b' ':
        if Personagens[0].velocity == 0:
            Personagens[0].velocity = 30
        else:
            Personagens[0].velocity = 0
    if args[0] == b'c':
        Personagens[0].onDemandCurve()
# Forca o redesenho da tela
    glutPostRedisplay()

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        Personagens[0].is_moving_forward = True
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        Personagens[0].is_moving_forward = False

    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouse(button: int, state: int, x: int, y: int):
    global PontoClicado
    if (state != GLUT_DOWN): 
        return
    if (button != GLUT_RIGHT_BUTTON):
        return
    #print ("Mouse:", x, ",", y)
    # Converte a coordenada de tela para o sistema de coordenadas do 
    # Personagens definido pela glOrtho
    vport = glGetIntegerv(GL_VIEWPORT)
    mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    realY = vport[3] - y
    worldCoordinate1 = gluUnProject(x, realY, 0, mvmatrix, projmatrix, vport)

    PontoClicado = Ponto (worldCoordinate1[0],worldCoordinate1[1], worldCoordinate1[2])
    PontoClicado.imprime("Ponto Clicado:")

    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouseMove(x: int, y: int):
    #glutPostRedisplay()
    return

def handleCollisions():
    for E in Personagens[1:]:
        p1 = Personagens[0].posicao
        p2 = E.posicao

        dist = distancia(p1, p2)
        
        if dist < Personagens[0].collision_radius * 2:
            print("COLISÃO!")
            end()

def end():
    for P in Personagens:
        P.velocity = 0
    
    time.sleep(2)
    os._exit(0)

# ***********************************************************************************
# Programa Principal
# ***********************************************************************************

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(500, 500)
glutInitWindowPosition(100, 100)
wind = glutCreateWindow("Exemplo de Criacao de Curvas Bezier")
glutDisplayFunc(display)
glutIdleFunc(animate)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(arrow_keys)
glutMouseFunc(mouse)
init()

try:
    glutMainLoop()
except SystemExit:
    pass
