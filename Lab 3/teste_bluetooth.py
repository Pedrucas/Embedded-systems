  
from machine import Pin
import bluetooth
from ble_advertising import advertising_payload
from micropython import const
import struct
import time

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")  # UART Service
RX_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")       # RX Characteristic (write)
TX_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")       # TX Characteristic (notify)

_RX_CHAR = (RX_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE)
_TX_CHAR = (TX_UUID, bluetooth.FLAG_NOTIFY)
_UART_SERVICE = (SERVICE_UUID, (_TX_CHAR, _RX_CHAR))

class BLEPeripheral:
    def __init__(self, ble, name="LuvaBLE"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._payload = advertising_payload(name=name, services=[SERVICE_UUID])
        self._advertise()

    def _irq(self, event, data):
        print("IRQ recebido:", event)
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            print("Conectado:", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            print("Desconectado:", conn_handle)
            self._connections.remove(conn_handle)
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, attr_handle = data
            print("Escrita detectada no handle:", attr_handle)
            if attr_handle == self._rx_handle:
                try:
                    msg = self._ble.gatts_read(self._rx_handle)
                    decoded = msg.decode("utf-8")
                    print("Recebido:", decoded)

                    # Exemplo: responder se recebeu "ping"
                    if decoded.strip() == "ping":
                        self.enviar("pong\n")
                except Exception as e:
                    print("Erro ao ler mensagem:", e)



    def enviar(self, msg):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, msg)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)
        print("Anunciando como BLE")

# Inicialização
ble = bluetooth.BLE()
peripheral = BLEPeripheral(ble)

# Exemplo: envio periódico de mensagem
while True:
    try:
        peripheral.enviar("Olá!\n")
        print("enviando msg")
    except Exception as e:
        print("Erro ao enviar:", e)
    time.sleep(2)

    
