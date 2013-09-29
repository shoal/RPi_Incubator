Raspberry Pi Egg Incubator
=============

RPi controlled egg incubator using DHT22 sensors.  The code assumes you're comfortable hacking around in Python + hardware to get this to work.  There is next to no documentation for now.

It's a mash-up of a few things, held together with some Python.

The temperature & humidity are sensed using DHT22 sensors.  The values are read using a slightly modified version of an Adafruit_DHT library (to make it a bit more reliable).

Build & Run
-----------
You'll first need the broadcom low level drivers (google: "low level BCM2835 C Library"), and the RPi.GPIO library (google that too).


To build the Adafruit_DHT app, call 'make'.

To run the incubator software, call "sudo python Controller.py"


There are some command line options when running the incubator controller, use -h to get them.

'Alarms' are threshold values that cause the alarm pin to get set if the temp/sensor errors exceed a level.
'Pins' are the GPIO numbers that the sensor/outputs are connected to.
When using the logging option, be careful that you dont exceed the storage space on the device (it might crash the app, leaving the environment uncontrolled)

You can run multiple instances of the incubator software, as long as they have seperate pin cofigurations.

General Design
-------------
In general, there is a sensor input pin (or several), a fault output (when condition exceed extremes), and temp output (to turn the temp up/down).  The outputs are all binary (on/off), although I use relays, which can be on-on.

In my design, the GPIO output pins are connected to ULN2030 darlington drivers (ie relay drivers) which drive relays.  The temperature relay turns on/off a light bulb (currently assuming room temperature is lower than incubator temperature).  The alarm shines an LED, but an airhorn would be better :)

There is currently no humidity control (it was there, but got removed).  At the moment I'll use a 'calibrated' wet sponge.  If I want to increase the humidity, I'll add another one.

It is recommended that fans are wired in 'always on' to gently keep the air moving around the incubator to prevent temp/humidity traps.

My design uses a simple light bulb on/off to control the temperature.  The PID controller would allow for much finer control of the temperature, but I haven't found it necessary.


TODO
-------

Log-rotate style logging (but it's only for diagnosis & optimising PID - do we care?)

PID tuning options (we probably dont need PID, so probably not important for us)

Send an email as well as set fault output.

Add humidity control

Add simple egg turner

