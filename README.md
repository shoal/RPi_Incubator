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


There are some command line options when running the incubator controller, use -h to get them.  The majority of options are concerned with raising an alarm if the temperature/humidity goes out of spec.

Configuration
-------------
Pins for sensor inputs & outputs are burried deep in the code (sorry, I haven't made it easy for you!).  In general, there is a sensor input pin (set where the Python code calls the Adafruit_DHT executable), a fault output (called from raiseFault), and temp/humidity outputs.

General Design
--------------
In my design, the GPIO output pins are connected to ULN2030 darlington drivers (ie relay drivers) which drive relays.  The temperature relay turns on/off a light bulb (currently assuming room temperature is lower than incubator temperature).  The humidity control part is yet to be seriously designed, but short term it will turn on an extractor fan if the humidity is too high, and a different fan blows air over a damp sponge if it is too dry.
