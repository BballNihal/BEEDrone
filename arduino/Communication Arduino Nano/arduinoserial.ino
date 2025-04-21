#include <Servo.h>

Servo throttleChannel;
Servo yawChannel;
Servo pitchChannel;
Servo rollChannel;

// PPM I/O settings
const int ppmOutputPin = 10;
const int ppmInputPin = 2; // External PPM input
const int ppmChannels = 12;
int ppmValues[ppmChannels] = {1500, 1500, 1000, 1500, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000}; // [roll, pitch, throttle, yaw...]

const int ppmSyncPulse = 400;     // Sync pulse length in microseconds
const int ppmFrameLength = 22500; // Total PPM frame length in microseconds

#define SW_PIN 12
#define dispense_pin 4

volatile bool generateMode = true; // true = generate PPM, false = pass-through

void setup() {
  delay(2000); // Optional boot delay
  pinMode(SW_PIN, OUTPUT);
  digitalWrite(SW_PIN, LOW);
  pinMode(dispense_pin, OUTPUT);
  digitalWrite(dispense_pin, LOW);
  Serial.begin(9600);

  throttleChannel.attach(3);
  yawChannel.attach(5);
  pitchChannel.attach(6);
  rollChannel.attach(9);

  pinMode(ppmOutputPin, OUTPUT);
  pinMode(ppmInputPin, INPUT);
  digitalWrite(ppmOutputPin, HIGH); // Idle state

  Serial.println("PWM + PPM Controller Ready");

  // Default PWM setup
  throttleChannel.writeMicroseconds(ppmValues[0]);
  yawChannel.writeMicroseconds(ppmValues[1]);
  pitchChannel.writeMicroseconds(ppmValues[2]);
  rollChannel.writeMicroseconds(ppmValues[3]);
}

void loop() {
  if (generateMode) {
    generatePPM();
  } else if (!generateMode){
    forwardPPM();
  }

  // Serial control
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    Serial.print("Received: ");
    Serial.println(command);

    if (command == "forward") {
      updateChannels(1500, 1600, 1300, 1500);
      Serial.println("Command: forward");
    } else if (command == "backward") {
      updateChannels(1500, 1400, 1300, 1500);
      Serial.println("Command: backward");
    } else if (command == "left") {
      updateChannels(1400, 1500, 1300, 1500);
      Serial.println("Command: left");
    } else if (command == "right") {
      updateChannels(1600, 1500, 1300, 1500);
      Serial.println("Command: right");
    } else if (command == "up") {
      updateChannels(1500, 1500, 1400, 1500);
      Serial.println("Command: up");
    } else if (command == "down") {
      updateChannels(1500, 1500, 1200, 1500);
      Serial.println("Command: down");
    } else if (command == "stop") {
      updateChannels(1500, 1500, 1300, 1500);
      Serial.println("Command: stop");
      delay(1000);
      updateChannels(1500, 1500, 1400, 1500);
      delay(1000);
      updateChannels(1500, 1500, 1300, 1500);
      digitalWrite(dispense_pin, HIGH);
      delay(1000);
      digitalWrite(dispense_pin, LOW);
    } else if (command == "wait") {
      updateChannels(1500, 1500, 1300, 1500);
      Serial.println("Command: wait");
    } else if (command == "arm") {
      updateChannels(1500, 1500, 1000, 2000);
      Serial.println("Command: arm");
    } else if (command == "dearm") {
      updateChannels(1500, 1500, 1000, 1000);
      Serial.println("Command: dearm");
    } else if (command == "switch_on") {
      generateMode = true;
      digitalWrite(SW_PIN, HIGH);
      Serial.println("Command: switch_on - generating PPM");
    } else if (command == "switch_off") {
      generateMode = false;
      digitalWrite(SW_PIN, LOW);
      Serial.println("Command: switch_off - pass-through PPM");
    } else {
      Serial.println("Command: Unknown");
    }
  }
}

void updateChannels(int roll, int pitch, int throttle, int yaw) {
  rollChannel.writeMicroseconds(roll);
  pitchChannel.writeMicroseconds(pitch);
  throttleChannel.writeMicroseconds(throttle);
  yawChannel.writeMicroseconds(yaw);
  ppmValues[0] = roll;
  ppmValues[1] = pitch;
  ppmValues[2] = throttle;
  ppmValues[3] = yaw;
}

void generatePPM() {
  unsigned long totalPulseTime = 0;

  digitalWrite(ppmOutputPin, LOW);
  delayMicroseconds(ppmSyncPulse);
  digitalWrite(ppmOutputPin, HIGH);

  for (int i = 0; i < ppmChannels; i++) {
    int pulseWidth = ppmValues[i];
    int space = pulseWidth - ppmSyncPulse;

    delayMicroseconds(space);
    digitalWrite(ppmOutputPin, LOW);
    delayMicroseconds(ppmSyncPulse);
    digitalWrite(ppmOutputPin, HIGH);

    totalPulseTime += pulseWidth;
  }

  int remainingTime = ppmFrameLength - totalPulseTime;
  if (remainingTime > 0) delayMicroseconds(remainingTime);
}

// Simple PPM pass-through (bit-banging based)
void forwardPPM() {
  // Wait for start of frame
  while (digitalRead(ppmInputPin) == HIGH);
  while (digitalRead(ppmInputPin) == LOW);

  // Echo signal until mode changes
  while (!generateMode) {
    int state = digitalRead(ppmInputPin);
    digitalWrite(ppmOutputPin, state);

    // Check for serial input to break out
    if (Serial.available()) {
      String command = Serial.readStringUntil('\n');
      command.trim();

      if (command == "switch_on") {
        generateMode = true;
        digitalWrite(SW_PIN, HIGH);
        Serial.println("Command: switch_on - generating PPM");
        return;  // Exit forwardPPM
      } else {
        Serial.print("Received: ");
        Serial.println(command);
        Serial.println("Command ignored while in pass-through mode. Use 'switch_on' to resume generating.");
      }
    }
  }
}
