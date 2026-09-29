#include <SimpleFOC.h>
#include <PciManager.h>
#include <PciListenerImp.h>

#define INH1 A0
#define INH2 A1
#define INH3 A2 // enable pins

#define IN1 3
#define IN2 5
#define IN3 9 // pwm pins for each phase

#define HALLA 7
#define HALLB 12 
#define HALLC 13 // hall sensor pins

#define CSA A3
#define CSB A4 //ADC pins for current sensing

BLDCMotor motor = BLDCMotor(15);
BLDCDriver3PWM driver = BLDCDriver3PWM(IN1,IN2,IN3,INH1,INH2,INH3);

HallSensor sensor = HallSensor(HALLA, HALLB, HALLC, 15);
InlineCurrentSense current_sense = InlineCurrentSense(0.001,50.0, CSA, NOT_SET, CSB);

//Commander command = Commander(Serial);
//void doMotor(char* cmd) { command.motor(&motor, cmd); }

void doA(){sensor.handleA();}
void doB(){sensor.handleB();}
void doC(){sensor.handleC();}

PciListenerImp listenA(sensor.pinA, doA);
PciListenerImp listenB(sensor.pinB, doB);
PciListenerImp listenC(sensor.pinC, doC);

void setup() {
  Serial.begin(9600);
  while(!Serial);
  SimpleFOCDebug::enable(&Serial);
  
  sensor.init();
  PciManager.registerListener(&listenA);
  PciManager.registerListener(&listenB);
  PciManager.registerListener(&listenC); 
  // link the motor to the sensor
  motor.linkSensor(&sensor);

  driver.voltage_power_supply = 12;
  driver.voltage_limit = 12;
  driver.pwm_frequency = 32000;

  driver.init();

  motor.linkDriver(&driver);

  current_sense.linkDriver(&driver);
  current_sense.init();

  motor.linkCurrentSense(&current_sense);

  motor.current_limit = 25;
  motor.voltage_limit = 12;
  motor.voltage_sensor_align = 3;
  
  motor.controller = MotionControlType::angle;

  motor.PID_velocity.P = 0.3;
  motor.PID_velocity.I = 5;
  motor.PID_velocity.D = 0.001;

  motor.P_angle.P = 20;
  //motor.P_angle.I = 10;
  //motor.P_angle.D = 0.001;

  //motor.useMonitoring(Serial);
 // motor.monitor_downsample = 100;
  //motor.monitor_variables = _MON_VOLT_Q | _MON_CURR_Q | _MON_CURR_D;

  motor.init();
  motor.initFOC();

  motor.target = 10;

  //command.add('M', doMotor, "Motor");

  //Serial.println(F("Motor ready."));
  //Serial.println(F("Set the target using serial terminal and command M:"));
  _delay(1000);

}

void loop() {
  
  motor.loopFOC();

  motor.move();

  //motor.monitor();

  //command.run();
}
