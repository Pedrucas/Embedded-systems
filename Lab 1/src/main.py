# Imports
from machine import Pin, ADC, PWM, SoftI2C
import neopixel
from utime import sleep
from time import time
import urandom
import ssd1306

# Mapeamento da matriz de LEDs com a origem no canto inferior direito
LED_MATRIX = [
    [24, 23, 22, 21, 20],    
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# Função que acende a matriz de led, recebendo os parâmetros de posição x,y e cor RGB
def leds(x, y, r=20, g=20, b=20):
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

# Função que apaga a matriz de LED
def apagar():
    np.fill((0,0,0))
    np.write()

# Função que retorna que o usuário errou a interação
def errado():
    red_led.duty_u16(20000)
    green_led.duty_u16(0)
    blue_led.duty_u16(0)
    
    buzzer.freq(349) 
    buzzer.duty_u16(1000)
    
    oled.fill(0)
    oled.text("ERRADO!", 35, 32)
    oled.show()
    sleep(0.5)
    buzzer.duty_u16(0)  #Para o som
    buzzer.deinit()
    sleep(1)

# Função que retorna que o usuário acertou a interação    
def certo():
    red_led.duty_u16(0)
    green_led.duty_u16(11000)
    blue_led.duty_u16(0)
    
    buzzer.freq(880)  
    buzzer.duty_u16(1000)
    
    oled.fill(0)
    oled.text("CERTO!", 40, 32)
    oled.show()
    sleep(0.5)
    buzzer.duty_u16(0)  #Para o som
    buzzer.deinit()
    sleep(1)

# Função que desenha uma seta para cima na matriz de LED      
def seta_cima(r,g,b):
    apagar()
    leds(2, 0, r,g,b)
    leds(1, 1, r,g,b)
    leds(2, 1, r,g,b)
    leds(3, 1, r,g,b)
    for i in range(0,5):
        leds(i, 2, r,g,b)
    leds(2, 3, r,g,b)
    leds(2, 4, r,g,b)

# Função que desenha uma seta para baixo na matriz de LED       
def seta_baixo(r,g,b):
    apagar()
    leds(2, 0, r,g,b)
    leds(2, 1, r,g,b)
    for i in range(0,5):
        leds(i, 2, r,g,b)
    for i in range(1,4):
        leds(i, 3, r,g,b)
    leds(2, 4, r,g,b)
  
# Função que desenha uma seta para esquerda na matriz de LED  
def seta_esquerda(r,g,b):
    apagar()
    leds(0, 2, r,g,b)
    for i in range(1,4):
        leds(1, i, r,g,b)
    for i in range(0,5):
        leds(2, i, r,g,b)
    leds(3, 2, r,g,b)
    leds(4, 2, r,g,b)
    
# Função que desenha uma seta para direita na matriz de LED 
def seta_direita(r,g,b):
    apagar()
    leds(0, 2, r,g,b)
    leds(1, 2, r,g,b)
    for i in range(0,5):
        leds(2, i, r,g,b)
    for i in range(1,4):
        leds(3, i, r,g,b)
    leds(4, 2, r,g,b)

# Função que desenha um 'A' na matriz de LED     
def botao_a(r,g,b):
    apagar()
    for i in range(1,4):
        leds(i, 0, r,g,b)
    leds(1, 1, r,g,b)
    leds(3, 1, r,g,b)
    for i in range(1,4):
        leds(i, 2, r,g,b)
    leds(1, 3, r,g,b)
    leds(3, 3, r,g,b)
    leds(1, 4, r,g,b)
    leds(3, 4, r,g,b)
  
# Função que desenha um 'B' na matriz de LED   
def botao_b(r,g,b):
    apagar()
    for i in range(1,4):
        leds(i, 0, r,g,b)
    leds(1, 1, r,g,b)
    leds(3, 1, r,g,b)
    for i in range(1,3):
        leds(i, 2, r,g,b)
    leds(1, 3, r,g,b)
    leds(3, 3, r,g,b)
    for i in range(1,4):
        leds(i, 4, r,g,b)
  
# Contagem de acertos (pontos)      
def pontos(n):
    oled.fill(0)
    oled.text("pontos = "+str(n), 10, 32)
    oled.show()
    sleep(1)

# Função que apaga o LED
def zera_led():
    red_led.duty_u16(0)
    green_led.duty_u16(0)
    blue_led.duty_u16(0)

# Vetor dos desenhos possíveis
funcoes = [seta_cima, seta_baixo, seta_esquerda, seta_direita, botao_a, botao_b]
    
# Configurações iniciais 
NUM_LEDS = 25 # Número total de LEDs na matriz 5x5
PIN = 7 # Pino onde a matriz Neopixel está conectada
np = neopixel.NeoPixel(Pin(PIN), NUM_LEDS)

# Configuração dos pinos do joystick
vrx = ADC(Pin(27)) # Eixo X
vry = ADC(Pin(26)) # Eixo Y
sw = Pin(22, Pin.IN, Pin.PULL_UP) # Botão

# Configuração dos botões A e B
button_a = Pin(5, Pin.IN, Pin.PULL_UP)
button_b = Pin(6, Pin.IN, Pin.PULL_UP)

# Configuração buzzer
buzzer = PWM(Pin(4))

# Configuração Display OLED
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# Configuração do LED RGB
red_led = PWM(Pin(12, Pin.OUT))
green_led = PWM(Pin(11, Pin.OUT))
blue_led = PWM(Pin(13, Pin.OUT))

# Desligando o LED RGB e a matriz inicialmente
zera_led()
r=0
apagar()
while True:    
    #Início
    zera_led()
    
    oled.fill(0)
    oled.text("Pressione A", 20, 20)
    oled.text("para comecar!", 20, 40)
    oled.show()

    pts = 0 #pontos zerados
    
    # Começa ao pressionar o botão
    if button_a.value() == 0:
        vel = 0.8
        while True:
            desenho = urandom.choice(funcoes) #escolhe um desenho aleatório
            
            #parte 1, em vermelho
            desenho(250,0,0)
            oled.fill(0)
            oled.text("3", 64, 32)
            oled.show()
            sleep(vel)
            
            #parte 2, em amarelo
            desenho(250,250,00)
            oled.fill(0)
            oled.text("2", 64, 32)
            oled.show()
            sleep(vel)
            
            #parte 3, em verde
            desenho(50,250,20)
            oled.fill(0)
            oled.text("1", 64, 32)
            oled.show()
            sleep(vel)
            
            #parte 4: valendo
            oled.fill(0)
            oled.text("Valendo!", 32, 32)
            oled.show()
            sleep(vel+0.1)
            apagar()
            
            # Lê a entrada do joystick
            x_val = vrx.read_u16()
            y_val = vry.read_u16()
            print(x_val)
            print(y_val)

            # O botão precisa ser pressionado e segurado

            # Caso desenho 'A'
            if desenho == botao_a:
		    # Acerto
                if button_a.value() == 0:
                    certo()
                    apagar()
                    pts += 1
                    pontos(pts)
		        # Erro
                else:
                    errado()
                    apagar()
                    break

	        # Caso desenho 'B'
            elif desenho == botao_b:
		        # Acerto
                if button_b.value() == 0:
                    certo()
                    apagar()
                    pts += 1
                    pontos(pts)
		        # Erro
                else:
                    errado()
                    apagar()
                    break

	        # Caso desenho 'seta para cima'
            elif desenho == seta_cima:
                if x_val >= 30000 and x_val <= 36000 and y_val <= 500:
		      # Acerto			
                    certo()
                    apagar()
                    pts += 1
                    pontos(pts)
                else:
		      # Erro
                    errado()
                    apagar()
                    break

	        # Caso desenho 'seta para baixo'
            elif desenho == seta_baixo:
                if x_val >= 32000 and x_val <= 33000 and y_val >= 6000:
		      # Acerto
                    certo()
                    apagar()
                    pts += 1
                    pontos(pts)
                else:
		      # Erro
                    errado()
                    apagar()
                    break

	        # Caso desenho 'seta para esquerda'
            elif desenho == seta_esquerda:
                if x_val >= 60000 and y_val <= 36000 and y_val >= 31000:
		      # Acerto
                    certo()
                    apagar()
                    pts += 1
                    pontos(pts)
                else:
		      # Erro
                    errado()
                    apagar()
                    break

     # Caso desenho 'seta para direita'
            elif desenho == seta_direita:
                if x_val <= 500 and y_val <= 35000 and y_val >= 30000:
		      # Acerto
                    certo()
                    apagar()
                    pts += 1
                    pontos(pts)
                else:
		      # Erro
                    errado()
                    apagar()
                    break

	     # Preparo para o próximo desenho
            zera_led() 
            buzzer.duty_u16(0)  #Para o som
            buzzer.deinit()

	     # Diminuição da velocidade entre desenhos
            if vel > 0.2:
                vel-=0.05

	 # Fim e contagem de pontos totais
        buzzer.freq(349) 
        buzzer.duty_u16(1000)
        sleep(0.2)
        buzzer.freq(300)  
        buzzer.duty_u16(1000)
        sleep(0.2)
        buzzer.freq(250) 
        buzzer.duty_u16(1000)
        sleep(0.2)
        buzzer.duty_u16(0)  #Para o som
        buzzer.deinit()
        oled.fill(0)
        oled.text("pontos totais ", 10, 32)
        oled.text(str(pts), 30, 42)
        oled.show()
        sleep(3)
