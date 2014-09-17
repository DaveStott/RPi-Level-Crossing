from multiprocessing import Process, Queue  # this lets us run the fuctions in a seperate threads to allow running mutliple functions at the same time
import RPi.GPIO as io
from time import sleep          # this lets us have a time delay when required
io.setmode(io.BCM)              # set up BCM GPIO numbering

# name the pins to define use and hopefully make the code a bit easier to follow
amber_Light = 9
red_Right = 10
red_Left = 11
button = 22
pwm_pin = 18   # siren pin
motor_phase_1 = 8
motor_phase_2 = 23
motor_phase_3 = 24
motor_phase_4 = 25

#setup the GPIO pins as required
io.setup(red_Left, io.OUT)                           # set Left Red LED pin (defined above) as output
io.setup(red_Right, io.OUT)                          # set Right Red LED pin (defined above) as output
io.setup(amber_Light, io.OUT)                        # set Amber LED pin (defined above) as output
io.setup(motor_phase_1, io.OUT)                      # set motor pin 1 (defined above) as output
io.setup(motor_phase_2, io.OUT)                      # set motor pin 2 (defined above) as output
io.setup(motor_phase_3, io.OUT)                      # set motor pin 3 pin (defined above) as output
io.setup(motor_phase_4, io.OUT)                      # set motor pin 4 (defined above) as output
io.setup(pwm_pin, io.OUT)                            # set Siren pin (defined above) as output
io.setup(button, io.IN, pull_up_down=io.PUD_DOWN)    # set button pin (defined above) as input

pwm = io.PWM(pwm_pin, 800)     # create an object (pwm) for PWM on siren pin (defined above) at 800 Hertz

siren_pause = 0.25             #standard delay between siren tones
lights_pause = 0.5             #standard delay between light flashes
 
def siren():

  pwm.start(50)                # start the PWM on 50 percent duty cycle
  
  for i in range(0,39):
    sleep(siren_pause)
    pwm.ChangeFrequency(1000)  # change the frequency to 1000 Hz
    sleep(siren_pause)
    pwm.ChangeFrequency(800)   # change the frequency to 800 Hz 
    
  pwm.stop()                   # stop the PWM output

def lights():

  for i in range (1, 56):
    if i == 1:
      io.output(amber_Light, io.HIGH)   #Turn amber light to on
      sleep(3)
      io.output(amber_Light, io.LOW)    #Turn amber light to off
      sleep(1)
      io.output(red_Left, io.HIGH)
      io.output(red_Right, io.HIGH)
      sleep(2)
      io.output(red_Left, io.LOW)
      io.output(red_Right, io.LOW)
      sleep(1)
    else:
      io.output(red_Left, io.HIGH)
      io.output(red_Right, io.LOW)
      sleep(lights_pause)
      io.output(red_Left, io.LOW)
      io.output(red_Right, io.HIGH)
      sleep(lights_pause)
  
  #Make sure all lights are off after the sub has finished
  io.output(red_Left, io.LOW)
  io.output(red_Right, io.LOW)
  io.output(red_Amber, io.LOW)

def gates(p1,p2,p3,p4):
  
  motor_pause = 0.005           #standard delay between motor steps
  
  io.output(p4, io.HIGH)
  sleep(motor_pause) 
    
  for i in range (0, 128): 
    if i == 108:
      motor_pause = 0.01
    io.output(p3, io.HIGH)
    sleep(motor_pause)
    io.output(p4, io.LOW)
    sleep(motor_pause)
    io.output(p2, io.HIGH)
    sleep(motor_pause)
    io.output(p3, io.LOW)
    sleep(motor_pause)
    io.output(p1, io.HIGH) 
    sleep(motor_pause)
    io.output(p2, io.LOW)
    sleep(motor_pause)
    io.output(p4, io.HIGH)
    sleep(motor_pause)
    io.output(p1, io.LOW)
    sleep(motor_pause)
  
  # Make sure all motor pins are off / low after the sub has finished  
  io.output(motor_phase_1, io.LOW)
  io.output(motor_phase_2, io.LOW)
  io.output(motor_phase_3, io.LOW)
  io.output(motor_phase_4, io.LOW)
      
try: 
  while True:                   # this will carry on until you hit CTRL+C
    sleep(0.25)
    while not io.input(button): # run when the button is pressed
      proc1 = Process(target=siren)
      proc1.start()                   # runs the siren function in a new thread and then continues without waiting for the function to complete
      proc2 = Process(target=lights)
      proc2.start()                   # runs the lights function in a new thread and then continues without waiting for the function to complete
      sleep(14)                       # wait 14 seconds before continuing
      proc3 = Process(target=gates,args=(motor_phase_1,motor_phase_2,motor_phase_3,motor_phase_4))
      proc3.start()                   # runs the gates function in a new thread etc motors phases ordered for gates to go down
      sleep(44)                       # wait 44 seconds before continuing
      proc4 = Process(target=gates,args=(motor_phase_4,motor_phase_3,motor_phase_2,motor_phase_1))
      proc4.start()                   # runs the gates function in a new thread etc motors phases ordered for gates to go back up
      proc4.join()    # stops the program fom continuing until this function returns

finally:                        # this block will run no matter how the try block exits - not entirly sure this is true

  io.cleanup()                  # clean up after yourself
