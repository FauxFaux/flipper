Sample code for interacting with a relay which presents as USB Serial,
from a Raspberry Pi-like device.


## Devices

My tested devices is labelled `http://www.icstation.com/`. I purchased
it on eBay, from China/Hong Kong, for <£5. These relays typically have
"serial port" in the listing title, and some reference to the magic
constants (below) in the description.

The devices have two lights, one of which is always on, and one of
which flickers when commands are arriving. If you connect a charging
cable, not a data cable, only one light lights, and nothing happens.
(Yes, I did this twice before realising.)

Linux speaks like this:

```
usb 3-3.1.3: new full-speed USB device number 15 using xhci_hcd
usb 3-3.1.3: New USB device found, idVendor=067b, idProduct=2303
usb 3-3.1.3: New USB device strings: Mfr=1, Product=2, SerialNumber=0
usb 3-3.1.3: Product: USB-Serial Controller
usb 3-3.1.3: Manufacturer: Prolific Technology Inc.
usbcore: registered new interface driver usbserial
usbcore: registered new interface driver usbserial_generic
usbserial: USB Serial support registered for generic
usbcore: registered new interface driver pl2303
usbserial: USB Serial support registered for pl2303
pl2303 3-3.1.3:1.0: pl2303 converter detected
usb 3-3.1.3: pl2303 converter now attached to ttyUSB0
```

## Notation

I'm using Python 3.6 syntax, so `0b_1111_1111` is the 8-bit byte
with all bits set (also known as `255`). `'\xff'` is the string
containing this byte, as `ff` is `255` in hex.


## Protocol

 * Open the device as serial, at 9600 baud.
 * Write '\x50' to the device: *Who are you?*
 * it will respond with its size:

| response | size |
| -------- | ---- |
| `\xad`   | 2    |
| `\xab`   | 4    |
| `\xac`   | 8    |

You can ignore the response, as we're never going to read anything
else from the device.

 * Write `\x51` to the device: *Enter switching mode!*

From here on, every byte is interpreted as "set the state to..".
A high bit ('1') means "off", a low bit ('0') means "on". This is
the opposite way around to what you might think.

For my 4-port relay, the relay furthest from the controller is relay
`0`. As such, if you send the device the byte `0b_1111_1110`, it
will switch "on" the furthest relay.


## Circuit

The test program is for the following controller:

 * 12V battery pack, connected to:
   * 5V "UBEC" voltage regulator, connected to:
     * RPI GPIO pin `4` and `6` (5V and Ground).
   * The load, via the relay.
 * RPI GPIO pin `40` and `39` (GPIO 21 and Ground), connected to:
   * a 1kΩ resistor and an "status" LED
 * RPI GPIO pin `37` and `34` (GPIO 26 and Ground), connected to:
   * a push-button switch, directly
 * The relay module connected to the RPI via. USB.

I additionally added an LED (and its 1kΩ resistor) in parallel with
the load, for testing. My load required a current of 0.25A, so also
had a 48Ω resistor.


## Test program

`flipper.py` waits for a button press, then flips relay `3` to on.
After 15 minutes, the relay is switched back off. When the relay is
off, the "status" LED is lit. Pushing the button immediately toggles
the state. Holding the button causes the relay to pulse once per
second.

