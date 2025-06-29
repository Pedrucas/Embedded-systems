from machine import Pin, ADC, PWM, SoftI2C, I2C
import neopixel
from utime import sleep
from time import time, sleep_ms
import urandom
import ssd1306
from imu import MPU6050
from os import listdir, chdir

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

def errado():
    """ Função que dispara som de errado e led vermelho
    """
    red_led.duty_u16(20000)
    green_led.duty_u16(0)
    blue_led.duty_u16(0)
    
    buzzer.freq(349)  # nota Fá
    buzzer.duty_u16(volume)
    
    oled.fill(0)
    oled.text("ERRADO!", 35, 32)
    oled.show()
    sleep(0.5)
    buzzer.duty_u16(0)  #Para o som
    sleep(1)
    
def certo():
    """ Função que dispara som de certo e led verde
    """
    red_led.duty_u16(0)
    green_led.duty_u16(1000)
    blue_led.duty_u16(0)
    
    buzzer.freq(880)  # nota Lá
    buzzer.duty_u16(volume)
    
    oled.fill(0)
    oled.text("CERTO!", 40, 32)
    oled.show()
    sleep(0.5)
    buzzer.duty_u16(0)  #Para o som
    #buzzer.deinit()
    sleep(1)
      
#Desenhos para serem feitos na matriz de LED
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
      
def seta_baixo(r,g,b):
    apagar()
    leds(2, 0, r,g,b)
    leds(2, 1, r,g,b)
    for i in range(0,5):
        leds(i, 2, r,g,b)
    for i in range(1,4):
        leds(i, 3, r,g,b)
    leds(2, 4, r,g,b)
    
def seta_esquerda(r,g,b):
    apagar()
    leds(0, 2, r,g,b)
    for i in range(1,4):
        leds(1, i, r,g,b)
    for i in range(0,5):
        leds(2, i, r,g,b)
    leds(3, 2, r,g,b)
    leds(4, 2, r,g,b)
    
def seta_direita(r,g,b):
    apagar()
    leds(0, 2, r,g,b)
    leds(1, 2, r,g,b)
    for i in range(0,5):
        leds(2, i, r,g,b)
    for i in range(1,4):
        leds(3, i, r,g,b)
    leds(4, 2, r,g,b)
    
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
        
def pontos(n):
    oled.fill(0)
    oled.text("pontos = "+str(n), 30, 30)
    oled.show()
    sleep(1)

def zera_led():
    red_led.duty_u16(0)
    green_led.duty_u16(0)
    blue_led.duty_u16(0)

def modo1():
    """ Modo de semaforo, os comandos aparecem em vermelho, amarelo e verde
        Quando estah no verde eh o momento de apertar o batao ou mexer o joystick
        
        Modo sequencial (soh acaba quando erra)
    """
    vel = 0.8
    pts = 0
    while True:
        desenho = urandom.choice(funcoes) #escolhe um desenho aleatório
        
        #parte 1
        desenho(10,0,0)
        oled.fill(0)
        oled.text("3", 64, 32)
        oled.show()
        sleep(vel)
        
        #parte 2
        desenho(10,10,0)
        oled.fill(0)
        oled.text("2", 64, 32)
        oled.show()
        sleep(vel)
        
        #parte 3
        desenho(2,10,1)
        oled.fill(0)
        oled.text("1", 64, 32)
        oled.show()
        sleep(vel)
        
        #parte 4
        oled.fill(0)
        oled.text("Valendo!", 32, 32)
        oled.show()
        sleep(vel+0.1)
        apagar()
        
        x_val = vrx.read_u16()
        y_val = vry.read_u16()

        #Pressione e segure o botão
        if desenho == botao_a:
            if button_a.value() == 0:
                certo()
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                apagar()
                break
        elif desenho == botao_b:
            if button_b.value() == 0:
                certo()
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                apagar()
                break
        elif desenho == seta_cima:
            if x_val >= 30000 and x_val <= 36000 and y_val <= 500:
                certo()
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                apagar()
                break
        elif desenho == seta_baixo:
            if x_val >= 32000 and x_val <= 33000 and y_val >= 60000:
                certo()
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                apagar()
                break
        elif desenho == seta_esquerda:
            if x_val >= 60000 and y_val <= 36000 and y_val >= 31000:
                certo()
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                apagar()
                break
        elif desenho == seta_direita:
            if x_val <= 500 and y_val <= 35000 and y_val >= 30000:
                certo()
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                apagar()
                break
        zera_led() 
        buzzer.duty_u16(0)
        if vel > 0.1:
            vel-=0.05
            
    notas = [349, 300, 250]
    for f in notas:
        buzzer.freq(f)
        buzzer.duty_u16(volume)
        sleep(0.2)
    buzzer.duty_u16(0)
    buzzer.deinit()
    oled.fill(0)
    oled.text("GAME OVER", 30, 20)
    oled.text("TOTAL: ", 20, 42)
    oled.text(str(pts) + " pts", 70, 42)
    oled.show()
    sleep(3)
    return
    
def modo2():
    """ Modo de memoria, setas e botoes vao aparecendo e usuario deve aperta-los no
        momento certo
        
        Modo sequencial (soh acaba quando erra)
    """
    
    vel = 0.8
    sequencia = [] 
    pts = 0
    
    while True:
        novo_desenho = urandom.choice(funcoes)  # Escolhe um desenho aleatório
        sequencia.append(novo_desenho) 
        
        # Mostra a sequência para o jogador
        for desenho in sequencia:
            desenho(2, 2, 15)
            oled.fill(0)
            oled.text("Memorize!", 30, 30)
            oled.show()
            sleep(vel)
            apagar()
            sleep(0.3)
            
        # Jogador tenta repetir a sequência
        for seta_esperada in sequencia:
            sucesso = False
            tempo_limite = time() + 3  # 3 segundos para responder
            
            while time() < tempo_limite:
                             
                x_val = vrx.read_u16()
                y_val = vry.read_u16()
                
                a_pressionado = button_a.value() == 0
                b_pressionado = button_b.value() == 0
                
                repouso_x = 30000 <= x_val <= 36000
                repouso_y = 30000 <= y_val <= 36000

                if seta_esperada == botao_a:
                    if a_pressionado and not b_pressionado and repouso_x and repouso_y:
                        sucesso = True
                        break
                    if b_pressionado or not repouso_x or not repouso_y:
                        break
                elif seta_esperada == botao_b:
                    if not a_pressionado and b_pressionado and repouso_x and repouso_y:
                        sucesso = True
                        break
                    if a_pressionado or not repouso_x or not repouso_y:
                        break
                elif seta_esperada == seta_cima:
                    if not a_pressionado and not b_pressionado and repouso_x and y_val <= 500:
                        sucesso = True
                        break
                    if a_pressionado or b_pressionado or not repouso_x or y_val > 37000:
                        break
                elif seta_esperada == seta_baixo:
                    if not a_pressionado and not b_pressionado and repouso_x and y_val >= 60000:
                        sucesso = True
                        break
                    if a_pressionado or b_pressionado or not repouso_x or y_val < 30000:
                        break
                elif seta_esperada == seta_esquerda:
                    if not a_pressionado and not b_pressionado and x_val >= 60000 and repouso_y:
                        sucesso = True
                        break
                    if a_pressionado or b_pressionado or x_val < 30000 or not repouso_y:
                        break
                elif seta_esperada == seta_direita:
                    if not a_pressionado and not b_pressionado and x_val <= 500 and repouso_y:
                        sucesso = True
                        break
                    if a_pressionado or b_pressionado or x_val > 37000 or not repouso_y:
                        break

                sleep(0.05)

            if sucesso:
                certo()
                zera_led() 
                apagar()
            else:
                errado()
                apagar()
                notas = [349, 300, 250]
                for f in notas:
                    buzzer.freq(f)
                    buzzer.duty_u16(volume)
                    sleep(0.2)
                buzzer.duty_u16(0)
                buzzer.deinit()
                oled.fill(0)
                oled.text("GAME OVER", 30, 20)
                oled.text("TOTAL: ", 20, 42)
                oled.text(str(pts) + " pts", 70, 42)
                oled.show()
                sleep(3)
                return
            
        pts += 1
        red_led.duty_u16(0)
        green_led.duty_u16(1000)
        blue_led.duty_u16(0)
        notas = [880, 988, 1047]
        for f in notas:
            buzzer.freq(f)
            buzzer.duty_u16(volume)
            sleep(0.2)
        buzzer.duty_u16(0)
        zera_led()

def modo3():
    """ Modo de movimento, setas  vao aparecendo e usuario deve mexer acelerometro
        no momento certo e com precisao para ganhar os pontos
        
        Modo fixo acaba quando chega em 10
    """
    vel = 1.0
    pts = 0
    
    oled.fill(0)
    oled.text("Configurando...", 5, 30)
    oled.show()
    sleep(1)
    
    #lê o acelerômetro
    #ref = mpu.read_accel_data()
    ref = {"x":mpu.accel.x, "y":mpu.accel.y, "z":mpu.accel.z}
    refX = ref["x"]
    refY = ref["y"]
    oled.fill(0)
    oled.text("x: " + str(refX), 15, 15)
    oled.text("y: " + str(refY), 15, 45)
    oled.show()
    sleep(1)
    
    tentativas=0
    while True:
        if tentativas == 10:
            break
        tentativas += 1
        desenho = urandom.choice(funcoes_2) #escolhe um desenho aleatório
        
        print("tentativas: " + str(tentativas)) #debug
        #parte 1
        desenho(5,5,5)
        oled.fill(0)
        oled.text("Valendo!", 30, 30)
        oled.show()
        sleep(vel)
        print("-" * 50)
        #lê o acelerômetro
        #atual = mpu.read_accel_data()
        atual = {"x":0 , "y":0, "z":0}
        for i in range(0,100):
            atual["x"] += mpu.accel.x
            atual["y"] += mpu.accel.y
            atual["z"] += mpu.accel.z
        
        atual["x"] /= 100
        atual["y"] /= 100
        atual["z"] /= 100
        dx = atual["x"] - ref["x"]
        dy = atual["z"] - ref["z"]
        margem = 0.1
        
        print("ref x = " + str(ref["x"]))
        #print("ref y = " + str(ref["y"]))
        print("ref z = " + str(ref["z"]))
        print("atual x = " + str(atual["x"]))
        #print("atual y = " + str(atual["y"]))
        print("atual z = " + str(atual["z"]))
        print("dx = " + str(dx))
        print("dy = " + str(dy))
        
        if desenho == seta_cima:
            print("cima")
            #not atual["x"] > margem and not atual["x"] < -margem -> ideia boa, mas vou congelar por enquanto
            if atual["z"] < ref["z"] and abs(dx) < abs(dy): #isso ficou melhor no fim das contas
                certo()
                print("certo")
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                print("errado")
                apagar()
        elif desenho == seta_baixo:
            print("baixo")
            if atual["z"] > ref["z"] and abs(dx) < abs(dy):
                certo()
                print("certo")
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                print("errado")
                apagar()
        elif desenho == seta_esquerda:
            print("esquerda")
            if atual["x"] < ref["x"] and abs(dx) > abs(dy):
                certo()
                print("certo")
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                print("errado")
                apagar()
        elif desenho == seta_direita:
            print("direta")
            if atual["x"] > ref["x"] and abs(dx) > abs(dy):
                certo()
                print("certo")
                apagar()
                pts += 1
                pontos(pts)
            else:
                errado()
                print("errado")
                apagar()
        zera_led() 
        buzzer.duty_u16(0) 
        if vel > 0.2:
            vel-=0.05
        
            
    notas = [349, 300, 250]
    for f in notas:
        buzzer.freq(f)
        buzzer.duty_u16(volume)
        sleep(0.2)
    buzzer.duty_u16(0)  #Para o som
    buzzer.deinit()
    oled.fill(0)
    oled.text("GAME OVER", 30, 20)
    oled.text("TOTAL: ", 20, 42)
    oled.text(str(pts) + " pts", 70, 42)
    oled.show()
    sleep(3)
    return

def desenha_menu(selecao):
    oled.fill(0)
    if selecao == 0:
        oled.fill_rect(0, 9, 128, 10, 1)
    elif selecao == 1:
        oled.fill_rect(0, 24, 128, 10, 1)
    elif selecao == 2:
        oled.fill_rect(0, 39, 128, 10, 1)
    oled.text("Modo:Semaforo", 5, 10, 0 if selecao == 0 else 1)
    oled.text("Modo:Memoria", 5, 25, 0 if selecao == 1 else 1)
    oled.text("Modo:Movimento", 5, 40, 0 if selecao == 2 else 1)
    oled.text("<-B", 5, 55)
    oled.text("A->", 95, 55)
    oled.show()

def desenha_menu_2(selecao):
    oled.fill(0)
    oled.text("Bem-vindo!", 22, 5)
    if selecao == 0:
        oled.fill_rect(0, 22, 128, 10, 1)
    elif selecao == 1:
        oled.fill_rect(0, 37, 128, 10, 1)
    oled.text("Modos de jogo", 5, 23, 0 if selecao == 0 else 1)
    oled.text("Configuracoes", 5, 38, 0 if selecao == 1 else 1)
    oled.text("A->", 95, 55)
    oled.show()
    
def wheel(pos):
    """roleta de cores RGB que aparece antes de cada jogo"""
    if pos < 85:
        r, g, b = pos * 3, 255 - pos * 3, 0
    elif pos < 170:
        pos -= 85
        r, g, b = 255 - pos * 3, 0, pos * 3
    else:
        pos -= 170
        r, g, b = 0, pos * 3, 255 - pos * 3

    return (int(r * 0.1), int(g * 0.1), int(b * 0.1))

def escolhe_menu():
    """menu de escolha de modos
    """
    selecao = 0
    sleep(0.5)
    while True:
        #Início
        red_led.duty_u16(0)
        green_led.duty_u16(0)
        blue_led.duty_u16(0)
        
        desenha_menu(selecao)
        x_val = vrx.read_u16()
        y_val = vry.read_u16()
        sele_vol = 0
        if volume >300:
            sele_vol = volume - 300
        if y_val >= 60000:  # Joystick para baixo
            selecao += 1
            buzzer.freq(100)
            buzzer.duty_u16(sele_vol)
            sleep(0.01)
            buzzer.duty_u16(0)
            if selecao > 2:
                selecao = 0
            desenha_menu(selecao)
            sleep(0.3)

        elif y_val <= 500:  # Joystick para cima
            selecao -= 1
            buzzer.freq(100)
            buzzer.duty_u16(sele_vol)
            sleep(0.01)
            buzzer.duty_u16(0)
            if selecao < 0:
                selecao = 2
            desenha_menu(selecao)
            sleep(0.3)
        
        if button_a.value() == 0:
            notas = [600, 700, 800, 1000]
            duracoes = [0.2, 0.2, 0.24, 0.36]
            num_leds = 25
            i = 0
            for f, d in zip(notas, duracoes):
                buzzer.freq(f)
                buzzer.duty_u16(volume)
                for j in range(num_leds):
                    cor = wheel((i * 50 + j * 10) % 255)  # cor variando por posição e tempo
                    np[j] = cor
                np.write()
                sleep(d)
                buzzer.duty_u16(0)
                sleep(0.05)
                i = i + 1
            if selecao == 0:
                modo1()
            elif selecao == 1:
                modo2()
            elif selecao == 2:
                modo3()
        elif button_b.value() == 0:
            return
        
def config():
    """Menu de escolha de configuracoes"""
    global volume
    selecao = 0
    while True:
        oled.fill(0)
        oled.text("Configuracoes", 10, 5)
        oled.fill_rect(0, 24, 128, 10, 1)
        oled.text("Volume", 5, 25, 0 if selecao == 0 else 1)
        voulume_str = int(volume/100)
        oled.text("-< " + str(voulume_str) + " >+", 60, 25, 0 if selecao == 0 else 1)
        oled.text("<-B", 5, 55, 1)
        oled.show()
        x_val = vrx.read_u16()
        if x_val >= 60000:  # Joystick para esquerda
            volume -= 100
            if volume <= 0:
                volume = 0
            print(volume)
            buzzer.freq(100)
            buzzer.duty_u16(volume)
            sleep(0.01)
            buzzer.duty_u16(0)
            
            sleep(0.3)

        elif x_val <= 500:  # Joystick para direita
            volume += 100
            if volume >= 1500:
                volume = 1500
            print(volume)
            buzzer.freq(100)
            buzzer.duty_u16(volume)
            sleep(0.01)
            buzzer.duty_u16(0)
            
            sleep(0.3)
            
        if button_b.value() == 0:
            with open('volume.txt', 'w', encoding='utf-8') as f:
                print("volume:")
                print(volume)
                f.write(str(volume))
            return
  
########################        
#     main code        #
########################
funcoes = [seta_cima, seta_baixo, seta_esquerda, seta_direita, botao_a, botao_b]
funcoes_2 = [seta_cima, seta_baixo, seta_esquerda, seta_direita]
    
NUM_LEDS = 25# Número total de LEDs na matriz 5x5
PIN = 7# Pino onde a matriz Neopixel está conectada
np = neopixel.NeoPixel(Pin(PIN), NUM_LEDS)

# Configuração dos pinos do joystick
vrx = ADC(Pin(27)) # Eixo X
vry = ADC(Pin(26)) # Eixo Y
sw = Pin(22, Pin.IN, Pin.PULL_UP) # Botão

# Configuração dos botões
button_a = Pin(5, Pin.IN, Pin.PULL_UP)
button_b = Pin(6, Pin.IN, Pin.PULL_UP)

#Configurando buzzer
buzzer = PWM(Pin(4))

i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)  # Bus I2C 1, pin SDA 20, pin SCL 21, 400kHz
#Configurando acelerômetro
mpu = MPU6050(i2c)

#Configurando Display OLED
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# Configuração do LED RGB
red_led = PWM(Pin(12, Pin.OUT))
green_led = PWM(Pin(11, Pin.OUT))
blue_led = PWM(Pin(13, Pin.OUT))

red_led.freq(500)
green_led.freq(500)
blue_led.freq(500)
# Desligando o LED RGB inicialmente
red_led.duty_u16(0)
green_led.duty_u16(0)
blue_led.duty_u16(0)
r=0
apagar()
selecao = 0

with open('volume.txt', 'r', encoding='utf-8') as f:
    conteudo = f.read()
    volume = int(conteudo)
    print(conteudo)

while True:
    #Início
    red_led.duty_u16(0)
    green_led.duty_u16(0)
    blue_led.duty_u16(0)
    
    desenha_menu_2(selecao)
    x_val = vrx.read_u16()
    y_val = vry.read_u16()
    sele_vol = 0
    if volume >300:
        sele_vol = volume - 300
    if y_val >= 60000:  # Joystick para baixo
        selecao += 1
        buzzer.freq(100)
        buzzer.duty_u16(sele_vol)
        sleep(0.01)
        buzzer.duty_u16(0)
        if selecao > 1:
            selecao = 0
        desenha_menu_2(selecao)
        sleep(0.3)

    elif y_val <= 500:  # Joystick para cima
        selecao -= 1
        buzzer.freq(100)
        buzzer.duty_u16(sele_vol)
        sleep(0.01)
        buzzer.duty_u16(0)
        if selecao < 0:
            selecao = 1
        desenha_menu_2(selecao)
        sleep(0.3)
    
    if button_a.value() == 0:
        if selecao == 0:
            escolhe_menu()
        elif selecao == 1:
            config()
