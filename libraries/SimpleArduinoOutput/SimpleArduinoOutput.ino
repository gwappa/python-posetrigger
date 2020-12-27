#define BAUD        230400
#define POWER       11
#define SYNC        12
#define EVENT       13

//#define USE_ARDUINO

#define PIN(P)      digitalPinToBitMask(P)

#ifdef USE_ARDUINO
uint8_t     OUT_PWR, OUT_SYN, OUT_EVT;
#else
uint8_t     OUTPUT_MASK;
#endif
volatile uint8_t *_outputRegister;
volatile uint8_t *_pinModeRegister;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(BAUD);
#ifdef USE_ARDUINO
  OUT_PWR = PIN(POWER);
  OUT_SYN = PIN(SYNC);
  OUT_EVT = PIN(EVENT);
  pinMode(OUT_PWR, OUTPUT);
  digitalWrite(OUT_PWR, LOW);
  pinMode(OUT_SYN, OUTPUT);
  digitalWrite(OUT_SYN, LOW);
  pinMode(OUT_EVT, OUTPUT);
  digitalWrite(OUT_EVT, LOW);
#else 
  OUTPUT_MASK =  (PIN(POWER) | PIN(SYNC) | PIN(EVENT));
  _pinModeRegister   = (uint8_t *) portModeRegister(OUTPUT_PORT);
  *_pinModeRegister |= OUTPUT_MASK;
  _outputRegister    = portOutputRegister(OUTPUT_PORT);
  *_outputRegister  &= ~OUTPUT_MASK;
#endif
#ifndef defined(__AVR_Atmega32U4__)
// i.e. not Leonardo-like arduino
  Serial.println("ready");
#endif
}

void loop() {
  // put your main code here, to run repeatedly:
  int stat = Serial.read();
  if (stat > 0) {
    uint8_t cmd = ((char)stat) << 3;
#ifdef USE_ARDUINO
    digitalWrite(OUT_PWR, (cmd & OUT_PWR)? HIGH:LOW);
    digitalWrite(OUT_SYN, (cmd & OUT_SYN)? HIGH:LOW);
    digitalWrite(OUT_EVT, (cmd & OUT_EVT)? HIGH:LOW);
#else
      *(_outputRegister) = cmd;
#endif
    Serial.print((char)stat);
  }
}
