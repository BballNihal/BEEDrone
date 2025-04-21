#include <ESPAsyncWebServer.h>
#include "esp_camera.h"
#include <WiFi.h>

// Camera model
#define CAMERA_MODEL_AI_THINKER // Has PSRAM
#include "camera_pins.h"

// WiFi Credentials
const char *ssid = "capstone";
const char *password = "capstone";
//const char *ssid = "Verizon_T4C6VN";
//const char *password = "otter-cpu4-silt";

// Define LED pin
#define LED_PIN 2

// Create AsyncWebServer instance
AsyncWebServer server(85);

void startCameraServer();

void setup() {
  Serial.begin(115200);  // Debugging (USB Serial)
  Serial1.begin(9600, SERIAL_8N1, 14, 15);  // TX = GPIO14, RX = GPIO15 (Connect to Arduino)

  Serial.println("\nStarting ESP32-CAM...");
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // Ensure LED is off initially

  // Initialize Camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;  
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (psramFound()) {
    config.jpeg_quality = 10;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  // Set Static IP
  IPAddress local_IP(192, 168, 1, 133);
  IPAddress gateway(192, 168, 1, 1);
  IPAddress subnet(255, 255, 255, 0);
  WiFi.config(local_IP, gateway, subnet);

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  // Start camera server
  startCameraServer();

  // LED Control Endpoints
  server.on("/led_on", HTTP_GET, [](AsyncWebServerRequest *request) {
    digitalWrite(LED_PIN, HIGH);
    Serial1.println("led_on"); // Send to Arduino
    request->send(200, "text/plain", "LED ON");
  });

  server.on("/led_off", HTTP_GET, [](AsyncWebServerRequest *request) {
    digitalWrite(LED_PIN, LOW);
    Serial1.println("led_off"); // Send to Arduino
    request->send(200, "text/plain", "LED OFF");
  });

  // Movement Control Endpoint
  server.on("/move", HTTP_GET, [](AsyncWebServerRequest *request) {
    if (request->hasParam("dir")) {
      String direction = request->getParam("dir")->value();
      direction.toLowerCase();
  
      if (direction == "forward" || direction == "backward" || direction == "left" ||
          direction == "right" || direction == "up" || direction == "down" || direction == "stop" || direction == "wait") {
        
        Serial1.println(direction); // Send direction to Arduino
        request->send(200, "text/plain", "Direction: " + direction);
      } else {
        request->send(400, "text/plain", "Invalid direction");
      }
    } else {
      request->send(400, "text/plain", "Missing 'dir' parameter");
    }
  });

  // Arm/Disarm Endpoints
  server.on("/arm", HTTP_GET, [](AsyncWebServerRequest *request) {
    Serial1.println("arm");
    request->send(200, "text/plain", "Armed");
  });

  server.on("/dearm", HTTP_GET, [](AsyncWebServerRequest *request) {
    Serial1.println("dearm");
    request->send(200, "text/plain", "Disarmed");
  });

  // Switch Control Endpoints
  server.on("/switch_on", HTTP_GET, [](AsyncWebServerRequest *request) {
    Serial1.println("switch_on");
    request->send(200, "text/plain", "Switch turned ON");
  });

  server.on("/switch_off", HTTP_GET, [](AsyncWebServerRequest *request) {
    Serial1.println("switch_off");
    request->send(200, "text/plain", "Switch turned OFF");
  });

  server.begin();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
}

void loop() {
  delay(10000); // Keep the ESP32 running
}
