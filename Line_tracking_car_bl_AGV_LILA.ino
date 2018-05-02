//www.elegoo.com

//Line Tracking IO define
#define PIN_R 10
#define PIN_M 4
#define PIN_L 2

#define LT_R !digitalRead(PIN_R)
#define LT_M !digitalRead(PIN_M)
#define LT_L !digitalRead(PIN_L)

#define ENA 5
#define ENB 6
#define IN1 7
#define IN2 8
#define IN3 9
#define IN4 11
#define LED 13

#define fwdSpeed 150
#define turnSpeed 170

// Constants
#define moveRobot true
#define debug false // ONLY when not working with AGV

// Bluetooth commands
#define AGV1_AT_P10   0x30
#define AGV1_AT_P11   0x31
#define MOVE_COMMAND_AGV1 0x32
#define AGV1_MOVING   0x33

// Booleans to activate when AGV sensors detect stop
bool AGV1atP10 = false;
bool AGV1atP11 = false;
// Boolean to activate when AGV receives "move" command from RASPI
bool AGV1moving = false;
// Int to store last position
int lastPos = 1;
// uint32 for resending moving data
uint32_t tTimeout= 0;
uint32_t maxTimeoutMs = 200;
// unit32 for not checking stop after a stop
uint32_t tTimestop= 0;
uint32_t timestopMs = 500;

int vl;
int vr;

void forward(int lspeed, int rspeed){
  if(moveRobot){
    analogWrite(ENA, lspeed);
    analogWrite(ENB, rspeed);
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  }
  if(debug){Serial.println("go forward!");}
}

void lForward(int mspeed){
  if(moveRobot){
    analogWrite(ENA, mspeed);
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  }
  if(debug){Serial.println("L go forward!");}
}

void rForward(int mspeed){
  if(moveRobot){
    analogWrite(ENB, mspeed);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  }
  if(debug){Serial.println("R go forward!");}
}

void back(int mspeed){
  if(moveRobot){
    analogWrite(ENA, mspeed);
    analogWrite(ENB, mspeed);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  }
  if(debug){Serial.println("go back!");}
}

void lBack(int mspeed){
  if(moveRobot){
    analogWrite(ENA, mspeed);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  }
  if(debug){Serial.println("L go back!");}
}

void rBack(int mspeed){
  if(moveRobot){
    analogWrite(ENB, mspeed);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  }
  if(debug){Serial.println("R go back!");}
}

void left(int mspeed){
  if(moveRobot){
    analogWrite(ENA, mspeed);
    analogWrite(ENB, mspeed);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  }
  if(debug){Serial.println("go left!");}
}

void right(int mspeed){
  if(moveRobot){
    analogWrite(ENA, mspeed);
    analogWrite(ENB, mspeed);
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW); 
  }
  if(debug){Serial.println("go right!");}
} 

void stop(){
   digitalWrite(ENA, LOW);
   digitalWrite(ENB, LOW);
   if(debug){Serial.println("Stop!");}
} 



void Lmove(int mspeed){
  if(mspeed < 0){
    lBack(mspeed);
  } else {
    lForward(mspeed);
  }
}

void Rmove(int mspeed){
  if(mspeed < 0){
    rBack(-mspeed);
  } else {
    rForward(mspeed);
  }
}



void setup(){
  // Set initial speed
  vl = fwdSpeed;
  vr = fwdSpeed;
  // We begin in the road 1->0
  lastPos = 1;
  // Initialise timeouts
  tTimeout = millis();
  tTimestop = millis();
  // Initialise other stuff
  Serial.begin(9600);
  pinMode(PIN_R,INPUT);
  pinMode(PIN_M,INPUT);
  pinMode(PIN_L,INPUT);
  pinMode(LED,OUTPUT);
}




void waitForMoveCommand(int refresh_ms, uint32_t timeout_ms) {
  bool received_move_command = false;
  int received_command = 0x00;
  uint32_t tStart = millis();

  if (debug) {Serial.println("Waiting for command...");}
  // 0 - Wait until we receive a command to move
  while (not(received_move_command))
  {
    // 1 - Check for messages
    if (Serial.available())
    {
      if (debug) {Serial.println("Command received!");}
      // Make sure we are reading the newest command
      while(Serial.available())
      {
        received_command = Serial.read(); 
      }
      // Check that the command is correct, exit while loop
      if (received_command == MOVE_COMMAND_AGV1)
      {
        if (debug) {Serial.println("command = MOVE");}
        received_move_command = true;
      }
    }
    // 2 - If there are no messages and dt > timeout, resend our position
    else
    {
      if (millis() - tStart > timeout_ms)
      {
        if (debug) {Serial.println("Timeout: no command received. Resending info...");}
        // Resend position
        if (AGV1atP10)
        {
          Serial.write(AGV1_AT_P10);
        }
        else if (AGV1atP11)
        {
          Serial.write(AGV1_AT_P11);
        }
        else
        {
          if (debug) {Serial.println("Error: AGV is waiting but neither in P10 nor in P11");}
        }
        // Reset timeout
        tStart = millis();
      }
    }
    // 3 - Wait and retry
    delay(refresh_ms);
  }
  // 4 - We have received the command
  return;
}




void loop() {
  
  if(LT_L && LT_R && LT_M){ // detecting stop -> stop
    // only stop if there has passed enough time after a stop
    if (millis() - tTimestop < timestopMs)
    {
      stop();
      if (lastPos==1)
      {
        AGV1atP10 = true;
        AGV1atP11 = false;
        AGV1moving = false;
        Serial.write(AGV1_AT_P10);
        waitForMoveCommand(200, 100);
        lastPos = 0;
      }
      else
      {
        AGV1atP10 = false;
        AGV1atP11 = true;
        AGV1moving = false;
        Serial.write(AGV1_AT_P11);
        waitForMoveCommand(200, 100);
        lastPos = 1;
      }
      forward(fwdSpeed,fwdSpeed);
      // reset tTimestop
      tTimestop = millis();
    }
  }
  else
  { // no stop -> move
    AGV1atP10 = false;
    AGV1atP11 = false;
    AGV1moving = true;
    // Send message every maxTimeoutMs
    if (millis() - tTimeout > maxTimeoutMs)
    {
      Serial.write(AGV1_MOVING);
      tTimeout = millis();
    }
    if(LT_L){ // detecting left -> go left
      vr = turnSpeed;
      vl = -turnSpeed;
    } else if (LT_R) { // detecting right -> go right
      vr = -turnSpeed;
      vl = turnSpeed;
    } else if(LT_M){ // detecting middle line -> go forward
      vr = fwdSpeed;
      vl = fwdSpeed;
    } else { // not detecting anything
      vl = 0;
      vr = 0;
    }  
    Lmove(vl);
    Rmove(vr);
    //forward(vl,vr);
  }

  
  if(debug){
    Serial.print("M \t");
    Serial.print(LT_M);
    Serial.print("\t R \t");
    Serial.print(LT_R);
    Serial.print("\t L \t");
    Serial.print(LT_L);
    Serial.print("\t vl \t");
    Serial.print(vl);
    Serial.print("\t vr \t");
    Serial.print(vr);
    Serial.print("\n");
  }
}


