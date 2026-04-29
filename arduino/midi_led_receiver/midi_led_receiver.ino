#include <Adafruit_NeoPixel.h>

#define PIN 6         // Pin connected to the data line of the WS2812 LED strip
#define NUM_LEDS 100

const int CHUNK_SIZE = 4;
const int MAX_CHUNKS = 88; // Adjust as needed
const int TOTAL_BYTES = CHUNK_SIZE * MAX_CHUNKS;
const int UNUSED_LED_OFFSET = 0; //Adjust as needed

byte buffer[TOTAL_BYTES];
int bytesRead = 0;
bool readyToProcess = false;

Adafruit_NeoPixel strip(NUM_LEDS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
  Serial.begin(115200);
  Serial.setTimeout(1000 / 60);
  while (!Serial); // Wait for Serial to connect (if needed)
  Serial.println("READY");  // Signal to Python to start

  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(7, OUTPUT);
  digitalWrite(3, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(5, HIGH);
  digitalWrite(7, HIGH);
}

void loop() {
  if (Serial.available() && !readyToProcess) {
    bytesRead = Serial.readBytes(buffer, TOTAL_BYTES);
    if (bytesRead % CHUNK_SIZE == 0) {
      readyToProcess = true;
    }
  }

  if (readyToProcess) {
    for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(0, 0, 0));
    }
    // Process all received 4-byte chunks
    for (int i = 0; i < bytesRead; i += CHUNK_SIZE) {
        int ledNum = buffer[i + 0];
        int red = buffer[i + 1];
        int green = buffer[i + 2];
        int blue = buffer[i + 3];
        if (ledNum < NUM_LEDS) {
          strip.setPixelColor(ledNum + UNUSED_LED_OFFSET, strip.Color(red, green, blue));
        }
    }
    strip.show();

    // Reset state
    readyToProcess = false;
    bytesRead = 0;

    // Signal Python we're done
    Serial.println("DONE");
  }
}
