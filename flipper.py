import RPi.GPIO as GPIO
import time
import serial
import os
import sys

def find_device() -> str:
    options = [item for item in os.listdir('/dev') if item.startswith('ttyUSB')]
    if len(options) != 1:
        raise Exception('too many paths: ' + options)
    return '/dev/{}'.format(options[0])

def set_relays():
    print('setting relays to {0:b}'.format(state))
    fd.write(bytes([state]))


def set_on(output: int):
    global state
    state ^= (1 << output)
    set_relays()

def set_off(output: int):
    global state
    state |= (1 << output)
    set_relays()

fd = serial.Serial(find_device(), 9600, timeout=1)

if '--init' in sys.argv:
    print('communicating with serial...')
    # 0x50: hello!
    fd.write(b'\x50')

    # 0xab: I'm a 4 channel relay, woo!
    # 0xad: 2 channel
    # 0xac: 8 channel
    # or, if it's not (or we're already initialised), the timeout will get us
    assert fd.read() == b'\xab'
    print('it is there!')

    # 0x51: go into data mode FOREVER
    fd.write(b'\x51')

state = 0xff
set_relays()

GPIO.setmode(GPIO.BCM)

# light
GPIO.setup(21, GPIO.OUT)

# button
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def light(status: bool) -> None:
    GPIO.output(21, GPIO.HIGH if status else GPIO.LOW)

def controller(status: bool) -> None:
    relay = 3
    if status:
         set_on(relay)
    else:
         set_off(relay)

def button() -> bool:
    return GPIO.input(26) == False

def pause() -> None:
    time.sleep(0.5)

def await_button(max_wait=float('inf')) -> None:
    start = time.monotonic()
    while not button():
        if (time.monotonic() - start) > max_wait:
            print("timeout")
            break
        time.sleep(0.1)
    print("button pressed")

light(True)
controller(False)

try:
   while True:
       await_button()
   
       light(False)
       controller(True)
       pause()
   
       await_button(15*60)
   
       controller(False)
       light(True)
       pause()
finally:
    GPIO.cleanup()
    state = 0xff
    set_relays()

