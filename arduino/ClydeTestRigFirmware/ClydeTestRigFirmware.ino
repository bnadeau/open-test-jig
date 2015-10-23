/**
 * @name    Clyde Test Rig Firmware
 * @brief   Clyde Test Rig Firmware
 * @file    ClydeTestRigFirmware.ino
 * @version 0.5
 * @Author  Angela Gabereau (angela@fabule.com)
 * @date    February 7, 2014
 * @copyright GNU Public License.
 *
 * Clyde Eye Test Rig Firmware. Uses SerialCommand library to send a recieve commands.
 *
 * Copyright (c) 2013-2014, Fabule Fabrications Inc, All rights reserved.
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation, version 3.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General
 * Public License along with this library.
 */
#include <SerialCommand.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <MPR121.h>
#include <SoftwareSerial.h>
#include <Clyde.h>
#include <EEPROM.h>

#define INA219_5V_ADDRESS  0x40
#define INA219_3V3_ADDRESS 0x41

float firmwareVersion = 0.6;

//set the PCB that this Arduino is testing
//this is used to set the correct input/output pins for the test shield
//and is read by the Raspberry PI to run the script matching the PCB under test
String boardType =
//  "EYE";
//  "TOUCH";
//  "AFRAID";
  "MAIN";

int greenLED = -1;   // Green LED on test rig
int redLED = -1;   // Red LED on test rig
int whiteLED = -1;   // White LED on test rig

//Pin limits
//digital pin number range.
int digitalPinRangeLow = 0;
int digitalPinRangeHigh = 13;
//analog pin number range.
int analogPinRangeLow = 0;
int analogPinRangeHigh = 5;

boolean debug = false; //Debug flag, controls output of debugging 

SerialCommand sCmd;     // The SerialCommand object
Adafruit_INA219 ina219_5V;
Adafruit_INA219 ina219_3V3;

void setup() {
  if (debug) delay(5000);
  
  Serial.begin(9600);

  initSerialCommands();

  ina219_5V = Adafruit_INA219(INA219_5V_ADDRESS);
  ina219_3V3 = Adafruit_INA219(INA219_3V3_ADDRESS);
  ina219_5V.begin();
  ina219_3V3.begin();

  initBoard(boardType);

  if(debug){
    Serial.print("I am ");
    Serial.print(boardType);
    Serial.print(" Test Rig Firmware v");
    Serial.print(firmwareVersion);
    Serial.println(".  I am ready.");
  }
  else{
    sendSuccessResponse();
  }
}

boolean initBoard(String type) {
  //Valid Arguments
  String eye = "EYE", touch =  "TOUCH", afraid = "AFRAID", main = "MAIN";

  //Check arguments
  if ( type != eye && type != touch && type != afraid && type != main ) {
    if(debug){
      Serial.println("---- SET BOARD -----");
      Serial.print("board type: INVALID");
      Serial.println("-------------------");
    }
    return false;
  }
  
  //Set parameters
  if (type == eye) {
    greenLED = 9;
    redLED = 10;
    whiteLED = -1;
  }
  else if (type == touch || type == afraid) {
    greenLED = A5;
    redLED = A4;
    whiteLED = A3;
  }
  else if (type == main) {  
  }

  boardType = type;

  //Debug message.
  if(debug){
    Serial.println("---- SET BOARD -----");
    Serial.print("board type: ");
    Serial.println(boardType);
    Serial.println("-------------------");
  }
  
  return true;
}

/**
 * Initial serial commands.
 * Map a set of commands to functions.  Creates the serial protocol.
 */
void initSerialCommands(){
  // Setup callbacks for SerialCommand commands
  sCmd.addCommand("VERSION",   cmdGetVersion);    // Get the firmware version, the version of this file
  //sCmd.addCommand("SET_BOARD",   cmdSetBoardType);     // Set the name of the type of board that this firmare tests.
  sCmd.addCommand("GET_BOARD",   cmdGetBoardType);     // Get the name of the type of board that this firmare tests.
  //sCmd.addCommand("SET_LED",   cmdSetLedPin);     // Set the pin number for specified LED
  sCmd.addCommand("LED",   cmdLed);     // Turn led on/off
  sCmd.addCommand("RELAY",   cmdRelay);     // Turn on/off relay on specified pin.  Sets pin mode to output and writes HIGH/LOW.
  sCmd.addCommand("READ_ANALOG",   cmdReadAnalog);     // Set specified analog pin to input mode and read value.
  sCmd.addCommand("READ_DIGITAL",   cmdReadDigital);     // Set specified digital pin to input mode and read value.
  sCmd.addCommand("WRITE_ANALOG",   cmdWriteAnalog);     // Set specified analog pin to output mode and write value.
  sCmd.addCommand("WRITE_DIGITAL",   cmdWriteDigital);     // Set specified analog pin to input mode and write value.
  sCmd.addCommand("READ_CURRENT",   cmdReadCurrent);     // 
  //sCmd.addCommand("TEST_SHORT",   cmdTestShort); //Test pin for short. Sets specified digital pin to output mode, and writes high value to that pin.
  sCmd.addCommand("ID_MODULE",   cmdIDModule); //Identity the module connected to the DUT.
  sCmd.addCommand("READ_LIGHT",   cmdReadLight); //Read light sensor value
  sCmd.addCommand("INIT_MPR121",   cmdInitMpr121); //Initial MPR121, Send I2c commands, get acknowledgement
  sCmd.addCommand("WAIT_TOUCH",  cmdWaitTouch);
  sCmd.addCommand("PIN_MODE",   cmdPinMode);     // Set the pin mode
  sCmd.addCommand("DEBUG",   cmdSetDebug);     // Turns debug messages on/off
  sCmd.addCommand("RESET_EEPROM", cmdResetEEPROM);
  sCmd.setDefaultHandler(cmdUnrecognized);      // Handler for command that isn't matched  (says "What?")
}

/**
 * Main Loop.
 * Constantly read and process the serial commands.
 */
void loop() {
  sCmd.readSerial();     // Process serial commands   
}

/********************************************//**
 *  COMMANDS
 ***********************************************/

/**
 * Command: VERSION
 * Get the version number of this Arduino sketch. This is used to make sure that we use the correct last version matched with the python script.
 */
void cmdGetVersion() {

  //Debug message.
  if(debug){
    Serial.print("VERSION: ");
  }
  sendSuccessResponse(firmwareVersion);
}

/**
 * Command: SET_BOARD [EYE/TOUCH/LOUD/MAIN]
 * Set the type of board that this Arduino firmware tests.
 */
/*void cmdSetBoardType() {

  char *param1;

  //Get arguments
  param1 = sCmd.next();    // First argument [EYE/TOUCH/LOUD/MAIN]

  String type = param1;
  
  //Check arguments
  if ( param1 == NULL || !initBoard(type)) {
    //You've got the wrong format. Correct format: SET_BOARD [EYE/TOUCH/LOUD/MAIN]
    sendErrorResponse(108);
  }
  else {
    sendSuccessResponse(boardType);
  }
}
*/
/**
 * Command: BOARD TYPE
 * Get the type of board that this Arduino firmware tests.
 */
void cmdGetBoardType() {

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Debug message.
  if(debug){
    Serial.print("BOARD TYPE: ");
  }
  sendSuccessResponse(boardType);

}

/**
 * Command: SET_LED [RED/GREEN/WHITE] [pin number: 0-13]
 * Set the pin number for specified LED
 */
/*void cmdSetLedPin() {

  char *param1, *param2;
  String led;
  int pin;

  //Get arguments
  param1 = sCmd.next();    // First argument  [RED/GREEN/WHITE]
  param2 = sCmd.next();    // Second argument  [0-13]

  //Valid Arguments
  String red = "RED", green =  "GREEN", white = "WHITE";

  //Assign Parameters
  led = param1; //cast to String
  pin = atoi(param2);    // Converts a char string to an integer

  //Check arguments
  if ( led == NULL || param2 == NULL || (led != red && led != green && led != white) ) {
    //You've got the wrong format. Correct format: SET_LED [RED/GREEN/WHITE] [pin number: 0-13]
    sendErrorResponse(110);
  }
  else if ( pin<digitalPinRangeLow || digitalPinRangeHigh<pin ) {
    //Pin number out of range.  Must be between 0 and 13
    sendErrorResponse(104);

  }
  else{

    //Get pin
    if(led == red){
      redLED = pin;
    }
    else if(led == green){
      greenLED = pin;
    }
    else if(led == white){
      whiteLED = pin;
    }
    sendSuccessResponse();

    //Debug message.
    if(debug){
      Serial.println("---- SET LED -----");
      Serial.print("led: ");
      Serial.print(led);
      Serial.print(" pin: ");
      Serial.println(pin);
      Serial.println("-------------------");
    }
  }
}*/

/**
 * Command: LED [RED/GREEN/WHITE] [ON/OFF]
 * Turn on/off the red or green LEDs.  Sets red/green/white pin mode to output and writes HIGH/LOW
 */
void cmdLed() {

  int pin = -1;
  int value = LOW;
  char *param1, *param2;
  String led, lightSwitch;
  //Valid Arguments
  String green =  "GREEN", red =  "RED", white =  "WHITE", on = "ON", off = "OFF";

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Get arguments
  param1 = sCmd.next();    // First argument [RED/GREEN/WHITE]
  param2 = sCmd.next();    // Second argument [ON/OFF]

  //Assign Parameters, cast to String
  led = param1;
  lightSwitch = param2;

  //Check arguments
  if ( led == NULL || (led != red && led != green && led != white) 
    || lightSwitch == NULL || (lightSwitch != on && lightSwitch != off)  ) {
    //"You've got the wrong format. Correct format: LED [RED/GREEN/WHITE] [ON/OFF]"
    sendErrorResponse(105);
  }
  else if (boardType == "MAIN") {
    pinMode(5, OUTPUT);
    pinMode(6, OUTPUT);
    pinMode(9, OUTPUT);
    
    if (lightSwitch == off) {
      analogWrite(5, 0);
      analogWrite(6, 0);
      analogWrite(9, 0);
    }
    else if (led == red) {
      analogWrite(5, 255);
      analogWrite(6, 0);
      analogWrite(9, 0);      }
    else if (led == green) {
      analogWrite(5, 0);
      analogWrite(6, 255);
      analogWrite(9, 0);
    }
    else if (led == white) {
      analogWrite(5, 255);
      analogWrite(6, 255);
      analogWrite(9, 255);  
    }
    
    sendSuccessResponse();
    
    //Debug message.
    if(debug){
      Serial.println("---- TURN LED -----");
      Serial.print("led: ");
      Serial.print(led);
      Serial.print(" turned ");
      Serial.print(lightSwitch);
      Serial.println("-------------------");
    }
  }
  else{

    //Get pin
    if(led == red){
      pin =  redLED;
    }
    else if(led == green){
      pin = greenLED;
    }
    else if(led == white) {
      pin = whiteLED;
    }
    
    //Get value
    if(lightSwitch == on){
      value = HIGH;
    }
    else if(lightSwitch == off){
      value = LOW;
    }

    //Do it.
    pinMode(pin, OUTPUT);
    digitalWrite(pin, value);
    sendSuccessResponse();

    //Debug message.
    if(debug){
      Serial.println("---- TURN LED -----");
      Serial.print("led: ");
      Serial.print(led);
      Serial.print(" turned ");
      Serial.print(lightSwitch);
      Serial.print(" on pin ");
      Serial.println(pin);
      Serial.println("-------------------");
    }
  }

}

/**
 * Command: RELAY [pin number: 0-13] [ON/OFF]
 * Turn on/off relay on specified pin.  Sets pin mode to output and writes HIGH/LOW
 */
void cmdRelay() {

  int relay = -1;
  int value = -1;
  char *param1, *param2;
  String relaySwitch;
  //Valid Arguments
  String on = "ON", off = "OFF";

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Get arguments
  param1 = sCmd.next();    // Second argument [pin number: 0-13]
  param2 = sCmd.next();    // First argument [ON/OFF]

  //Assign Parameters
  relay = atoi(param1);    // Converts a char string to an integer
  relaySwitch = param2; // cast to String

  //Check arguments
  if (param1 == NULL || relaySwitch == NULL || (relaySwitch != on && relaySwitch != off)  ) {
    //You've got the wrong format. Correct format: RELAY [pin number: 0-13] [ON/OFF]
    sendErrorResponse(107);
  }
  else if ( relay<digitalPinRangeLow || digitalPinRangeHigh<relay ) {
    //Pin number out of range.  Must be between 0 and 13
    sendErrorResponse(104);

  }
  else{

    //Get value
    if(relaySwitch == on){
      value = HIGH;
    }
    else if(relaySwitch == off){
      value = LOW;
    }

    //Do it.
    pinMode(relay, OUTPUT);
    digitalWrite(relay, value);
    sendSuccessResponse();

    //Debug message.
    if(debug){
      Serial.println("---- RELAY -----");
      Serial.print("relay pin: ");
      Serial.print(relay);
      Serial.print(" turned ");
      Serial.println(relaySwitch);  
      Serial.println("-------------------");
    }
  }

}

/**
 * Command: READ_ANALOG [pin number: 0-5]
 * Read the input on an analog pin. Sets specified analog pin to input mode, reads the value, returns value as integer on serial.
 */
void cmdReadAnalog() {
  int pin, value;
  char *param1;

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Get arguments
  param1 = sCmd.next();    // First argument [0-5]
  pin = atoi(param1);    // Converts a char string to an integer

  //Check arguments
  if ( param1 == NULL ) {
    //You've got the wrong format. Correct format: READ_ANALOG [pin number: 0-5]
    sendErrorResponse(101);
  }
  else if ( pin<analogPinRangeLow || analogPinRangeHigh<pin ) {
    //Pin number out of range.  Must be between 0 and 5
    sendErrorResponse(102);
  }
  else{

    //Do it.
    //setAnalogPinMode(pin, INPUT);
    value = analogRead(pin);
    sendSuccessResponse(value);

    //Debug message.
    if(debug){
      Serial.println("---- READ ANALOG -----");
      Serial.print("pin: ");
      Serial.println(pin);
      Serial.print("value: ");
      Serial.println(value);
      Serial.println("-------------------");
    }
  }

}

/**
 * Command: READ_DIGITAL [pin number: 0-13]
 * Read the input on a digital pin. Sets specified digital pin to input mode, reads the value, returns value as integer on serial.
 */
void cmdReadDigital() {

  int pin, value;
  char *param1;

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Get arguments
  param1 = sCmd.next();    // First argument [0-13]
  pin = atoi(param1);    // Converts a char string to an integer

  //Check arguments
  if ( param1 == NULL ) {
    //You've got the wrong format. Correct format: READ_DIGITAL [pin number: 0-13]
    sendErrorResponse(103);
  }
  else if ( pin<digitalPinRangeLow || digitalPinRangeHigh<pin ) {
    //Pin number out of range.  Must be between 0 and 13
    sendErrorResponse(104);
  }
  else{

    //Do it.
    pinMode(pin, INPUT);
    value = digitalRead(pin);
    sendSuccessResponse(value);

    //Debug message.
    if(debug){
      Serial.println("---- READ DIGITAL -----");
      Serial.print("pin: ");
      Serial.println(pin);
      Serial.print("value: ");
      Serial.println(value);
      Serial.println("-------------------");
    }
  }

}


/**
 * Command: WRITE_ANALOG [pin number: 0-5] [VALUE]
 * Write the value to the analog pin. Sets specified analog pin to output mode and writes the value.
 */
void cmdWriteAnalog() {

  int pin, value;
  char *param1, *param2;

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Get arguments
  param1 = sCmd.next();    // Digital pin [0-13]
  param2 = sCmd.next();    // PWM value
  pin = atoi(param1);    // Converts a char string to an integer
  value =  atoi(param2);    // Converts a char string to an integer

  //Check arguments
  if ( param1 == NULL || param2 == NULL ) {
    //You've got the wrong format. Correct format: WRITE_ANALOG [pin number: 0-5] [value]
    sendErrorResponse(115);
  }
  else if ( pin<digitalPinRangeLow || digitalPinRangeHigh<pin ) {
    //Pin number out of range.  Must be between 0 and 13
    sendErrorResponse(102);
  }
  else{

    //Do it.
    pinMode(pin, OUTPUT);
    analogWrite(pin, value);
    sendSuccessResponse();

    //Debug message.
    if(debug){
      Serial.println("---- WRITE ANALOG -----");
      Serial.print("pin: ");
      Serial.println(pin);
      Serial.print("value: ");
      Serial.println(value);
      Serial.println("-------------------");
    }
  }

}

/**
 * Command: WRITE_DIGITAL [pin number: 0-13] [HIGH|LOW]
 *  Write the value to the digital pin. Sets specified digital pin to output mode and writes the value.
 */
void cmdWriteDigital() {

  int pin;
  char *param1, *param2;
  String value;
  //Valid Arguments
  String high =  "HIGH", low =  "LOW";

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Get arguments
  param1 = sCmd.next();    // First argument [0-13]
  param2 = sCmd.next();    // Second argument [HIGH|LOW]
  pin = atoi(param1);    // Converts a char string to an integer
  value = param2; //Converst to String
  //Check arguments
  if ( param1 == NULL || param2 == NULL ||  (value!=high && value!=low) ) {
    //You've got the wrong format. Correct format: WRITE_DIGITAL [pin number: 0-13] [HIGH|LOW]
    sendErrorResponse(116);
  }
  else if ( pin<digitalPinRangeLow || digitalPinRangeHigh<pin ) {
    //Pin number out of range.  Must be between 0 and 13
    sendErrorResponse(104);
  }
  else{

    //Do it.
    pinMode(pin, OUTPUT);
    if(value==high){
      digitalWrite(pin, HIGH);
    }
    else{
      digitalWrite(pin, LOW);
    }
    sendSuccessResponse();

    //Debug message.
    if(debug){
      Serial.println("---- WRITE DIGITAL -----");
      Serial.print("pin: ");
      Serial.println(pin);
      Serial.print("value: ");
      Serial.println(value);
      Serial.println("-------------------");
    }
  }

}

/**
 * Command: READ_CURRENT [5V/3V3]
 * Read the current from ina219 current sensor using the Adafruit_INA219 library.
 */
void cmdReadCurrent() {

  char *param1;
  //Valid Arguments
  String voltage, voltage5V = "5V", voltage3V3 = "3V3", voltage12V = "12V";
  int current = 0;

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }
  //Get arguments
  param1 = sCmd.next();    // First argument [5V/3V3]

  //Assign Parameters, cast to String
  voltage = param1;

  //Check arguments
  if ( voltage == NULL || (voltage != voltage5V && voltage != voltage3V3 && voltage != voltage12V)  ) {
    //You've got the wrong format.Correct format: READ_CURRENT [5V/3V3]
    sendErrorResponse(111);
  }
  else{

    if(voltage == voltage5V || voltage == voltage12V){
      //Read the 5V current
      current = int(ina219_5V.getCurrent_mA());
      sendSuccessResponse(current);
    }
    else if(voltage == voltage3V3){
      //Read the 3V3 current
      current = int(ina219_3V3.getCurrent_mA());
      sendSuccessResponse(current);
    }

    //Debug message.
    if(debug){
      Serial.println("---- READ_CURRENT -----");
      Serial.print("current: ");
      Serial.println(current);
      Serial.print("voltage: ");
      Serial.println(voltage);
      Serial.print("bus voltage: ");
      if (voltage == voltage5V) Serial.println(ina219_5V.getBusVoltage_V());
      else if (voltage == voltage3V3) Serial.println(ina219_3V3.getBusVoltage_V());
      Serial.print("shunt voltage: ");
      if (voltage == voltage5V) Serial.println(ina219_5V.getShuntVoltage_mV());
      else if (voltage == voltage3V3) Serial.println(ina219_3V3.getShuntVoltage_mV());
      Serial.println("-------------------");
    }
  }
}


/**
 * Command: TEST_SHORT [pin number: 0, 1, 8-12]
 * Test pin for short. First pins A0, A1, D8-D12 are set to INPUT_PULLUP.  Then pin the specified pin is set to LOW
 * Then we read the state of all the pins and build a bitstring to represent their state.  This is the order:
 * A0 A1 D8 D9 D10 D11 D12 This string is returned.
 * 0 is indicates A0, 1=A1, 8-12=D8-D12
 */
/*void cmdTestShort() {

  int pin, value;
  char *param1;
  String pinsState = "";

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Get arguments
  param1 = sCmd.next();    // First argument [0-13]
  pin = atoi(param1);    // Converts a char string to an integer

  //Check arguments
  if ( param1 == NULL || (pin != 0 && pin != 1 && pin != 8 && pin != 9 && pin != 10 && pin != 11 && pin != 12 ) ) {
    //You've got the wrong format. Correct format: TEST_SHORT [pin number: 0, 1, 8-12]
    sendErrorResponse(112);
  }
  else{

    //Set all pins that could short to input pullup.
    pinMode(A0, INPUT_PULLUP);
    pinMode(A1, INPUT_PULLUP);
    pinMode(8, INPUT_PULLUP);
    pinMode(9, INPUT_PULLUP);
    pinMode(10, INPUT_PULLUP);
    pinMode(11, INPUT_PULLUP);
    pinMode(12, INPUT_PULLUP);

    //Set the pin we are testing to low
    if(pin==0){
      pinMode(A0, OUTPUT);
      digitalWrite(A0, LOW);
    }
    else if(pin==1){
      pinMode(A1, OUTPUT);
      digitalWrite(A1, LOW);
    }
    else{
      pinMode(pin, OUTPUT);
      digitalWrite(pin, LOW);
    }

    //Read the state of all pins, build bit string representing their state.
    pinsState += digitalRead(A0);
    pinsState += digitalRead(A1);
    pinsState += digitalRead(8);
    pinsState += digitalRead(9);
    pinsState += digitalRead(10);
    pinsState += digitalRead(11);
    pinsState += digitalRead(12);

    sendSuccessResponse(pinsState);

    //Debug message.
    if(debug){
      Serial.println("---- TEST SHORT -----");
      Serial.print("pin: ");
      Serial.println(pin);
      Serial.println("-------------------");
    }
  }
}*/

/**
 * Command: ID_MODULE [pin number: 0-13] [analog pin number: 0-5]
 * Identity the module conntected to the DUT.  Enable identification relay on the pin specified by the first parameter,
 * read back and return module identifier on the pin specified by second parameter.
 */
void cmdIDModule() {

  int pin1, pin2, value;
  char *param1, *param2;

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Get arguments
  param1 = sCmd.next();    // First argument [0-13]
  param2 = sCmd.next();    // First argument [0-5]
  pin1 = atoi(param1);    // Converts a char string to an integer
  pin2 = atoi(param2);    // Converts a char string to an integer

  //Check arguments
  if ( param1 == NULL || param2 == NULL) {
    //You've got the wrong format. Correct format: IDENTIFY_MODULE [pin number: 0-13] [pin number: 0-5]
    sendErrorResponse(113);
  }
  else if ( pin1<digitalPinRangeLow || digitalPinRangeHigh<pin1 ) {
    //Pin number out of range.  Must be between 0 and 13
    sendErrorResponse(104);
  }  
  else if ( pin2<analogPinRangeLow || analogPinRangeHigh<pin2 ) {
    //Pin number out of range.  Must be between 0 and 5
    sendErrorResponse(102);
  }
  else{

    //Do it.
    pinMode(pin1, OUTPUT);
    digitalWrite(pin1, HIGH);
    value = analogRead(pin2);
    digitalWrite(pin1, LOW);
    sendSuccessResponse(value);

    //Debug message.
    if(debug){
      Serial.println("---- IDENTIFY_MODULE -----");
      Serial.print("pin1: ");
      Serial.println(pin1);
      Serial.print("pin2: ");
      Serial.println(pin2);
      Serial.println("-------------------");
    }
  }

}

/**
 * Command: READ_LIGHT [pin number: 0-13] [pin number: 0-5]
 * Read light sensor value.  Enable the relay on pin specified in first parameter to turn on light sensor,
 * read the sensor value on the pin specified in second parameter.
 */
void cmdReadLight() {

  int pin1, pin2, value;
  char *param1, *param2;

  if(boardType == ""){
    //You have not set the board type yet.  Please do.
    sendErrorResponse(109);
    return;
  }

  //Get arguments
  param1 = sCmd.next();    // First argument [0-13]
  param2 = sCmd.next();    // First argument [0-5]
  pin1 = atoi(param1);    // Converts a char string to an integer
  pin2 = atoi(param2);    // Converts a char string to an integer

  //Check arguments
  if ( param1 == NULL || param2 == NULL) {
    //You've got the wrong format. Correct format: READ_LIGHT [pin number: 0-13] [pin number: 0-5]
    sendErrorResponse(114);
  }
  else if ( pin1<digitalPinRangeLow || digitalPinRangeHigh<pin1 ) {
    //Pin number out of range.  Must be between 0 and 13
    sendErrorResponse(104);
  }  
  else if ( pin2<analogPinRangeLow || analogPinRangeHigh<pin2 ) {
    //Pin number out of range.  Must be between 0 and 5
    sendErrorResponse(102);
  }
  else{

    //Do it.
    pinMode(pin1, OUTPUT);
    digitalWrite(pin1, HIGH);
    value = analogRead(pin2);
    sendSuccessResponse(value);

    //Debug message.
    if(debug){
      Serial.println("---- READ LIGHT   -----");
      Serial.print("pin1: ");
      Serial.println(pin1);
      Serial.print("pin2: ");
      Serial.println(pin2);
      Serial.println("-------------------");
    }
  }

}

/**
 * INIT_MPR121
 * Initial MPR121, Send I2c commands, get acknowledgement
 */
void cmdInitMpr121(){
  char *param1;
  int addr;
  
  //Get argument
  param1 = sCmd.next();    // I2C address
  addr = atoi(param1);     // Converts a char string to an integer
  
  MPR121 mpr121(addr, 0x02, 0x01);
  
  if (!mpr121.testConnection()) {
    sendErrorResponse(118);
    return;
  }
  
  mpr121.initialize(false);
  sendSuccessResponse();
}

/**
 * INIT_MPR121
 * Initial MPR121, Send I2c commands, get acknowledgement
 */
void cmdWaitTouch(){
  char *param1, *param2, *param3;
  int addr;
  int pin;
  int timeout;
  
  //Get argument
  param1 = sCmd.next();    // I2C address
  param2 = sCmd.next();    // Interrupt pin
  param3 = sCmd.next();    // Timeout in millis
  addr = atoi(param1);
  pin = atoi(param2);
  timeout = atoi(param3);
  
  pinMode(pin, INPUT);
  digitalWrite(pin, LOW);

  MPR121 mpr121(addr, 0x04, 0x02);
  //mpr121.initialize(false);
    
  //if (!mpr121.testConnection()) {
  //  sendErrorResponse(118);
  //  return;
  //}
  
  long start = millis();
  //int touchStatus = 0;
  
  while(millis()-start < timeout) {
    /*if (touchStatus == 0) {
      if (!digitalRead(pin)) {
        touchStatus = mpr121.getTouchStatus();
      }
    } else {
      if (!digitalRead(pin)) {
        sendSuccessResponse(touchStatus);
        return;
      }
    }*/
    
    if (!digitalRead(pin)) {
      int newStatus = mpr121.getTouchStatus();
      //Serial.print("interrupted: ");
      //Serial.println(newStatus);
      //if (newStatus == 0 && touchStatus != 0) {
      if (newStatus != 0) {
        sendSuccessResponse(newStatus);
        return;
      }
      //else {
      //  touchStatus = newStatus;
      //}
    }
    
    //delay(5);
  }
  
  sendErrorResponse(119);
}

/**
 * PIN_MODE [ANALOG/DIGITAL] [pin number: 0-13] [INPUT/OUTPUT/INPUT_PULLUP]
 * Turns on or off debugging messages.
 */
void cmdPinMode() {

  char *param1, *param2, *param3;
  int pin;
  String pinType, state;
  //Valid Arguments
  String  analog = "ANALOG", digital = "DIGITAL", input = "INPUT", output = "OUTPUT",  input_pullup = "INPUT_PULLUP";

  //Get arguments
  param1 = sCmd.next();    // First argument [ANALOG/DIGITAL]
  param2 = sCmd.next();    // Second argument [pin number: 0-13]
  param3 = sCmd.next();    // Third argument [INPUT/OUTPUT]

  //Assign Parameters, cast to String
  pinType = param1;
  state = param3;
  pin = atoi(param2);    // Converts a char string to an integer

  //Check arguments
  if ( param1 == NULL || param2 == NULL || param3 == NULL || (pinType != digital && pinType != analog) || (state != input && state != output && state != input_pullup)   ) {
    //You've got the wrong format. Correct format: PIN_MODE [ANALOG/DIGITAL] [pin number: 0-13] [INPUT/OUTPUT/INPUT_PULLUP]
    sendErrorResponse(117);
  } 
  else if (pinType == digital && (pin<digitalPinRangeLow || digitalPinRangeHigh<pin ) ) {
    //Pin number out of range.  Must be between 0 and 13
    sendErrorResponse(104);
  }  
  else if (pinType == analog && ( pin<analogPinRangeLow || analogPinRangeHigh<pin ) ){
    //Pin number out of range.  Must be between 0 and 5
    sendErrorResponse(102);
  }
  else{

    if(state== "INPUT"){
      if(pinType == analog){
        setAnalogPinMode(pin, INPUT);
      }
      else{
        pinMode(pin, INPUT);
      }
    }
    else if(state == "OUTPUT"){
      if(pinType == analog){
        setAnalogPinMode(pin, OUTPUT);
      }
      else{
        pinMode(pin, OUTPUT);
      }

    }
    else if(state == "INPUT_PULLUP"){
      if(pinType == analog){
        setAnalogPinMode(pin, INPUT_PULLUP);
      }
      else{
        pinMode(pin, INPUT_PULLUP);
      }
    }

    sendSuccessResponse();

    //Debug message.
    if(debug){
      Serial.println("---- PIN MODE   -----");
      Serial.print("pin type: ");
      Serial.println(pinType);
      Serial.print("pin: ");
      Serial.println(pin);
      Serial.print("state: ");
      Serial.println(state);
      Serial.println("-------------------");
    }
  }
}

/**
 * DEBUG [ON/OFF]
 * Turns on or off debugging messages.
 */
void cmdSetDebug() {

  char *param1;
  String debugSwitch;
  //Valid Arguments
  String  on = "ON", off = "OFF";

  //Get arguments
  param1 = sCmd.next();    // First argument [ON/OFF]

  //Assign Parameters, cast to String
  debugSwitch = param1;

  //Check arguments
  if ( debugSwitch == NULL || (debugSwitch != on && debugSwitch != off)   ) {
    //"You've got the wrong format. Corret format: DEBUG [ON/OFF]"
    sendErrorResponse(106);
  }
  else{

    if(debugSwitch == on){
      debug = true;
    }
    else{
      debug = false;
    }

    sendSuccessResponse();
  }
}

void cmdResetEEPROM() {
  Clyde.eeprom()->reset();
  sendSuccessResponse();
}

/**
 * Command: [?? unrecognized ??]
 * The default serial command handler. This gets set as the default handler, and gets called when no other command matches.
 */
void cmdUnrecognized(const char *command) {
  sendErrorResponse(999);
}

/*
*  Set the analog pin to input/output or input_pullup
 */
void setAnalogPinMode(int pin, int state){
  switch (pin) {
  case 0:
    pinMode(A0, state);
    break;
  case 1:
    pinMode(A0, state);
    break;
  case 2:
    pinMode(A2, state);
    break;
  case 3:
    pinMode(A3, state);
    break;
  case 4:
    pinMode(A4, state);
    break;
  case 5:
    pinMode(A5, state);
    break;
  }
}


/********************************************//**
 * SEND RESPONSE FUNCTIONS
 ***********************************************/

/*
  Overloaded send suceess response functions
 */
void sendSuccessResponse(){
  Serial.println("OK");
}

void sendSuccessResponse(String response){
  Serial.print("OK ");
  Serial.println(response);
}

void sendSuccessResponse(int response){
  Serial.print("OK ");
  Serial.println(response);
}

void sendSuccessResponse(float response){
  Serial.print("OK ");
  Serial.println(response);
}

void sendSuccessResponse(char response){
  Serial.print("OK ");
  Serial.println(response);
}

/*
  send error response functions
 */

void sendErrorResponse(int errorCode){
  Serial.print("ERR ");
  Serial.println(errorCode);
}
