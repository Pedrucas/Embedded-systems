#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEClient.h>
#include <BLEAdvertisedDevice.h>
#include <Wire.h>
#include <MPU6050_light.h>

/* To run this code use Arduino IDE with:
 * MPU6050_light.h
 * installed
 */

static BLEUUID serviceUUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E");   // UART Service
static BLEUUID    charRXUUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"); // RX (Write)
static BLEUUID    charTXUUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"); // TX (Notify)

static boolean deviceFound = false;
static BLEAdvertisedDevice* myDevice;
bool deveResponder = false;
BLEClient* pClient = BLEDevice::createClient();
MPU6050 mpu(Wire);  

class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    Serial.print("Dispositivo encontrado: ");
    Serial.println(advertisedDevice.toString().c_str());

    if (advertisedDevice.haveServiceUUID() && advertisedDevice.isAdvertisingService(serviceUUID)) {
      Serial.println("Dispositivo com serviço UART encontrado!");
      myDevice = new BLEAdvertisedDevice(advertisedDevice);
      deviceFound = true;
    }
  }
};

static bool doConnect = false;
static BLERemoteCharacteristic* pTXCharacteristic;
static BLERemoteCharacteristic* pRXCharacteristic;

static void notifyCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic,
  uint8_t* pData,
  size_t length,
  bool isNotify) {
    Serial.print("Notificação recebida: ");
    Serial.write(pData, length);
    Serial.println();
    String recebido = String((char*)pData);
    if (recebido.startsWith("manda")) {
      Serial.println("Preparando para enviar xyz");
      deveResponder = true;
    }
    if (recebido.startsWith("para")) {
      Serial.println("Preparando para parar enviar xyz");
      deveResponder = false;
    }

}

void connectToServer() {
  Serial.println("Conectando ao servidor BLE...");

  BLEClient* newClient = BLEDevice::createClient();
  pClient = newClient;

  if (!pClient->connect(myDevice)) {
    Serial.println("Falha na conexão.");
    return;
  }

  Serial.println("Conectado. Buscando serviço...");
  BLERemoteService* pService = pClient->getService(serviceUUID);
  if (pService == nullptr) {
    Serial.println("Serviço não encontrado.");
    pClient->disconnect();
    return;
  }

  pRXCharacteristic = pService->getCharacteristic(charRXUUID);
  pTXCharacteristic = pService->getCharacteristic(charTXUUID);

  if (pTXCharacteristic && pTXCharacteristic->canNotify()) {
    pTXCharacteristic->registerForNotify(notifyCallback);
  }

  if (pRXCharacteristic && pRXCharacteristic->canWrite()) {
    Serial.println("Enviando comando para a LuvaBLE...");
    pRXCharacteristic->writeValue("start\n");
  } else {
    Serial.println("Característica RX inválida.");
  }
}


void setup() {
  Serial.begin(115200);
  Serial.println("Inicializando BLE Central (ESP32-C3)...");

  BLEDevice::init("");
  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true);
  pBLEScan->start(5, false);

  Serial.println("Escaneando por 5 segundos...");
  // Inicia I2C nos pinos 6 (SDA) e 7 (SCL)
  Wire.begin(6, 7);
  delay(100)
  Serial.println("Inicializando MPU6050...");
  byte count = 0;
  for (byte address = 1; address < 127; ++address) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
      Serial.print("Encontrado dispositivo I2C no endereço 0x");
      Serial.println(address, HEX);
      count++;
      delay(5);
    }
  }

  if (count == 0) Serial.println("Nenhum dispositivo I2C encontrado!");
  else Serial.println("Escaneamento completo.");

  byte status = mpu.begin();
  Serial.print("MPU6050 status: ");
  Serial.println(status); // 0 = sucesso
  
  if (!mpu.testConnection()) {
    Serial.println("Falha ao conectar com o MPU6050!");
  } else {
    Serial.println("MPU6050 conectado com sucesso!");
  }

  if (status != 0) {
    Serial.println("Erro ao iniciar o MPU6050!");
    while (1);
  }

  Serial.println("Calibrando...");
  delay(1000);
  mpu.calcOffsets();  // Calibra com base na posição atual
  Serial.println("Pronto!");
}

unsigned long tempoUltimoEvento = millis();
char posicao[40];

void loop() {
  if (deviceFound && !doConnect) {
    doConnect = true;
    connectToServer();
    tempoUltimoEvento = millis();
  }
  if (millis() - tempoUltimoEvento > 150000) {
    Serial.println("Sem evento por 150s. Rebootando ESP...");
    delay(1000);
    esp_restart();
  }
  
  if (!pClient || !pClient->isConnected()) {
    Serial.println("Cliente desconectado. Tentando reconectar...");
    doConnect = false;
    delay(1000);
    return;
  }

  mpu.update();
  float x = mpu.getAccX();
  float y = mpu.getAccY();
  float z = mpu.getAccZ();

  // Monta a string no formato desejado
  snprintf(posicao, sizeof(posicao), "X:%.2f,Y:%.2f,Z:%.2f", x, y, z);

  // Envia pela serial (ou Bluetooth depois)
  Serial.println(posicao);

  // Envio seguro
  if (deveResponder && pRXCharacteristic && pRXCharacteristic->canWrite()) {
    Serial.println("Respondendo com xyz'");
    pRXCharacteristic->writeValue((uint8_t*)posicao, strlen(posicao), false);
    Serial.println("pos resposta com xyz");

  }

  delay(100);
}

