from machine import Pin, I2C
from imu import MPU6050
import time

# Inicializa o I2C nos pinos GPIO4 (SDA) e GPIO5 (SCL)
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
devices = []
while devices == []:
    # Verifica dispositivos I2C conectados
    devices = i2c.scan()
    print("Dispositivos I2C encontrados:", devices)

# Inicializa o sensor MPU6050
mpu = MPU6050(i2c)

while True:
    ax, ay, az = mpu.get_accel()
    print('Aceleração: X={}, Y={}, Z={}'.format(ax, ay, az))
    time.sleep(1)

