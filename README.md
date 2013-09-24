RPi_Incubator
=============

RPi controlled egg incubator using DHT22 sensors.  The code assumes you're comfortable hacking around in Python + hardware to get this to work.  There is next to no documentation for now.

It's a mash-up of a few things, held together with some Python.

The temperature & humidity are sensed using DHT22 sensors.  The values are read using a slightly modified version of an Adafruit_DHT library (to make it a bit more reliable).

To build the Adafruit_DHT app, call 'make'.  The original code was taken from here: http://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install note that you'll need to install the broadcom low level drivers.  While you're at it, you'll also need to install  the RPi.GPIO library.

To run the incubator software, call "sudo python Controller.py"  There are some other options, use -h to get them.  The majority of options are concerned with raising an alarm if the temperature/humidity goes out of spec.

Pins for sensor inputs & outputs are burried deep in the code (sorry, I haven't made it easy for you!).  In general, there is a sensor input pin (set where the Python code calls the Adafruit_DHT executable), a fault output (called from raiseFault), and temp/humidity outputs.
