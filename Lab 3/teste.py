from machine import Pin, ADC, PWM, SoftI2C, I2C, UART
import neopixel
from utime import sleep
from time import time, sleep_ms
import urandom
import ssd1306
from imu import MPU6050
from os import listdir, chdir
import uasyncio as asyncio

# Mapeamento da matriz de LEDs com a origem no canto inferior direito
LED_MATRIX = [
    [24, 23, 22, 21, 20],    
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]


def leds(x, y, r=20, g=20, b=20):
    """ acende o led na posicao (x,y) com a intensidade 
        pre-definida (20,20,20) ou setada pelo caller
    """
    if 0 <= x <= 4 and 0 <= y <= 4 and r <= 255 and g <=255 and b <= 255:
        led_index = LED_MATRIX[4-y][x]
        np[led_index] = (r, g, b)
        np.write()
        return f'Posicao: (x={x},y={y}) na cor: ({r},{g},{b})'
    elif x > 4:
        return f'Valor escolhido x={x} invalido, escolha um valor entre 0 e 4'
    elif y > 4:
        return f'Valor escolhido y={y} invalido, escolha um valor entre 0 e 4'
    elif r > 255 or g > 255 or b > 255:
        return f'Valor escolhido de cor ({r},{g},{b}) inválido, escolha um valor entre 0 e 255 para cada cor'
    else:
        return f'Coordenadas invalidas, escolha um valor x<=4 e y<=4 e valores para R G B <= 255.'
    
def apagar():
    """
    Função apagar, digite apagar() parar apagar todos os bitmaps da matriz 5x5
    """
    np.fill((0,0,0))
    np.write()
    
def desenha_seta_diagonal(x, y, dx, dy, r=20, g=20, b=20):
    apagar()

    # Corpo: 3 LEDs em linha reta
    for i in range(4):
        cx = x + i * dx
        cy = y + i * dy
        if 0 <= cx <= 4 and 0 <= cy <= 4:
            leds(cx, cy, r, g, b)

    # Ponta em diagonal
    px = x +  dx + dy
    py = y +  dy + dx
    if 0 <= px <= 4 and 0 <= py <= 4:
        leds(px, py, r, g, b)

# Lista com posições (x, y) iniciais e direção (dx, dy)
# A posição (x, y) é onde começa o corpo da seta
# A direção indica o sentido da seta
# Trajeto corrigido para formar um circuito pela borda no sentido horário
# (x, y, dx, dy) onde dx/dy define direção do corpo
trajeto = [
    (0, 4, 1, 0),  # topo: esquerda → direita
    (1, 4, 1, 0),
    (2, 4, 1, 0),

    (4, 4, 0, -1), # direita: topo → base
    (4, 3, 0, -1),
    (4, 2, 0, -1),

    (4, 0, -1, 0), # base: direita → esquerda
    (3, 0, -1, 0),
    (2, 0, -1, 0),

    (0, 0, 0, 1),  # esquerda: base → topo
    (0, 1, 0, 1),
    (0, 2, 0, 1)
]
def desenha_z(r=20, g=20, b=20):
    apagar()
    # Linha superior
    for x in range(5):
        leds(x, 4, r, g, b)

    # Diagonal descendente
    leds(3, 3, r, g, b)
    leds(2, 2, r, g, b)
    leds(1, 1, r, g, b)
    

    # Linha inferior
    for x in range(5):
        leds(x, 0, r, g, b)


NUM_LEDS = 25# Número total de LEDs na matriz 5x5
PIN = 7# Pino onde a matriz Neopixel está conectada
np = neopixel.NeoPixel(Pin(PIN), NUM_LEDS)
# Loop de animação
while True:
    for (x, y, dx, dy) in trajeto:
        desenha_z(3,2,5)
        sleep(0.25)