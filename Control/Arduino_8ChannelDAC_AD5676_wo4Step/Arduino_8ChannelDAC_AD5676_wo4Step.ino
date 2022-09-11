//Arduino controlled 8-channel DAC for 2 full thermal MEMS chip control
//8-channel DAC used is AD5676 EVAL board, which connects via SPI and chip having 24-bit data input
//16 data bits, 4 command bits and 4 address bits for all 8 channels (max value 65535)
//serial input form LabView, 47 characters for single mirror change instruction, example "<50000,00000,00000,00000,00000,00000,00000,00000>" 
//when getting automated data transfered for 3 angles 3 phases, this goes to 48*9 characters + 4 characters (number of exposures) + 4 characters (exposure time) + 4 characters (wait time) = 443 characters
//when getting automated data transfered for 1 angle 3 phases, this goes to 48*3 characters + 4 characters (number of exposures) + 4 characters (exposure time) + 4 characters (wait time) = 155 characters

//#include <Wire.h>
#include <SPI.h>
#define CS 8 //digital pin 8 as chip select for SPI
#define trigger_o 10 //trigger output on pin 10
#define RSET 2 //digital pin 2 as reset

SPISettings settingsA(10000000, MSBFIRST, SPI_MODE1);

//int ad5676_address = 0x55; //Address for board needs to be checked with i2c_scanner!!

const uint16_t numChars = 445; //max length of serial read
char receivedChars[numChars];

uint16_t expTime = 0;
uint16_t waitTime = 0;
uint16_t frameNo = 0;
uint16_t stepDelay = 300; //time for steps in 4 step position change in microseconds - overall 3*this time value for full pos change
uint16_t Pos1[8], Pos2[8], Pos3[8], Pos4[8], Pos5[8], Pos6[8], Pos7[8], Pos8[8], Pos9[8]; //integers to write to DAC
uint16_t CurrentPos[8] = {0,0,0,0,0,0,0,0}; //initialise previous channel values to 0
uint16_t receivedNo = 0;

boolean newData = false;

//================================================

void setup() {
  Serial.begin(115200);
  Serial.println("8-channel DAC AD5676EVAL");

//  Wire.begin(); //initiate i2c comms
  pinMode(CS, OUTPUT);
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  digitalWrite(CS, HIGH);

  pinMode(RSET, OUTPUT);
  digitalWrite(RSET, HIGH);

  SPI.beginTransaction(settingsA);
  digitalWrite(CS, LOW);
  SPI.transfer(0b0111);
  SPI.transfer((0x00 >> 8) & 0xFF);
  SPI.transfer((0x01) & 0xFF);
  digitalWrite(CS, HIGH);

  pinMode(trigger_o, OUTPUT);
  digitalWrite(trigger_o, LOW);

  Serial.println(SERIAL_BUFFER_SIZE);

}

//================================================

void loop() {
  // serial read to get commandline input or input from Labview
  receivedNo = receivedWithMarkers();

  if (receivedNo == 47 && newData == true) //check if sent instructions are for single change of both mirrors
  {
    char * strtokIndx; //used by strtok as index
    strtokIndx = strtok(receivedChars, ","); Pos1[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[5] = atoi(strtokIndx);
    //order of Pos1 allocation changed to map physical output channels on MEMS correctly

    writeToDAC(Pos1);
   // Serial.println("single");
  }
  if (receivedNo == 155 && newData == true) // check if sent instructions are for automated run with only 1 angle
  {
    char * strtokIndx; //used by strtok as index
    strtokIndx = strtok(receivedChars, ","); Pos1[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); frameNo = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); expTime = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); waitTime = atoi(strtokIndx);

    writeToDAC(Pos1);
    for (int u=0;u<8;u++)
    {
      CurrentPos[u] = Pos1[u];
    }
    
    Serial.println("1-position");
    
    for (int i=0;i<frameNo;i++)
    {
      writeToDAC(Pos1);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
      
      writeToDAC(Pos2);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
      
      writeToDAC(Pos3);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
    }
  }
  if (receivedNo == 443 & newData == true) //check if sent instructions are for automated operation with all 3 angles
  {
    char * strtokIndx; //used by strtok as index
    strtokIndx = strtok(receivedChars, ","); Pos1[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos1[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos2[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos3[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos4[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos4[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos4[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos4[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos4[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos4[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos4[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos4[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos5[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos5[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos5[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos5[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos5[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos5[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos5[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos5[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos6[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos6[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos6[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos6[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos6[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos6[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos6[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos6[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos7[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos7[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos7[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos7[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos7[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos7[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos7[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos7[5] = atoi(strtokIndx);    
    strtokIndx = strtok(NULL, ","); Pos8[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos8[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos8[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos8[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos8[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos8[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos8[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos8[5] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos9[2] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos9[3] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos9[0] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos9[1] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos9[6] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos9[7] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos9[4] = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); Pos9[5] = atoi(strtokIndx);    
    strtokIndx = strtok(NULL, ","); frameNo = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); expTime = atoi(strtokIndx);
    strtokIndx = strtok(NULL, ","); waitTime = atoi(strtokIndx);

    writeToDAC(Pos1);
    for (int u=0;u<8;u++)
    {
      CurrentPos[u] = Pos1[u];
    }

    Serial.println("3-positions");
    
    for (int i=0;i<frameNo;i++)
    {
      writeToDAC(Pos1);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
      
      writeToDAC(Pos2);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
      
      writeToDAC(Pos3);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
      
      writeToDAC(Pos4);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
            
      writeToDAC(Pos5);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
            
      writeToDAC(Pos6);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);   
            
      writeToDAC(Pos7);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);   
            
      writeToDAC(Pos8);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
            
      writeToDAC(Pos9);
      delay(waitTime);
      digitalWrite(trigger_o, HIGH);
      delayMicroseconds(100);
      digitalWrite(trigger_o, LOW);
      delay(expTime);
    }
  }
  memset(receivedChars, 0, sizeof(receivedChars));
  newData = false;
  receivedNo = 0;
}

//=======================================
uint16_t receivedWithMarkers() {
    static boolean recvInProgress = false;
    static uint16_t ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    ndx = 0;
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
               // Serial.print(rc);
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                newData = true;
               // Serial.println();
               // Serial.println(ndx);
                return ndx;
            }
        }
        else if (rc == startMarker) {
            recvInProgress = true;
        }
        delay(5);
    }
}

//=======================================
void writeToDAC(uint16_t posData[8]) {
    uint8_t cmdByte[8] = {0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37}; //command of 0011 to write to DAC channel n, with 0000 to 0111 being the channels
    uint16_t prevPos[8];
    uint16_t posWrite;
    
    float a[4] = {0.05, 0.5, 0.95, 1};
    float b[4] = {0.95, 0.5, 0.05, 0};

    for (int u=0;u<8;u++)
    {
      prevPos[u] = CurrentPos[u];
    }
    
    //Wire.beginTransmission(ad5676_address);
    SPI.beginTransaction(settingsA);

    for (int j=0;j<8;j++)
    {
      //for (int m=0;m<4;m++)
      //{
       if (posData[j] != CurrentPos[j] && posData[j] < 50000)
        {
          //if (posData[j]>prevPos[j])
          //{
          //  posWrite = (uint16_t) (((posData[j]-prevPos[j])*a[m]) + prevPos[j]);  
          //}
          //else
          //{
          //  posWrite = (uint16_t) (((prevPos[j]-posData[j])*b[m]) + posData[j]);  
          //}
          posWrite = (uint16_t) posData[j];
          digitalWrite(CS, LOW);
          SPI.transfer(cmdByte[j]);
          SPI.transfer((posWrite >> 8) & 0xFF);
          SPI.transfer((posWrite) & 0xFF);
          digitalWrite(CS, HIGH);
          CurrentPos[j] = posWrite;
          //Serial.println(CurrentPos[j]);
        }
      //}
      delayMicroseconds(stepDelay);
      
    }
   //Wire.endTransmission();
}
