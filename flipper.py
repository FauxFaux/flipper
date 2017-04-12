import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# controller
GPIO.setup(4, GPIO.OUT)

# light
GPIO.setup(21, GPIO.OUT)

# button
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def light(status: bool) -> None:
    GPIO.output(21, GPIO.HIGH if status else GPIO.LOW)

def controller(status: bool) -> None:
    GPIO.output(4, GPIO.HIGH if status else GPIO.LOW)

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
