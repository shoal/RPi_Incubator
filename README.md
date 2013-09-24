RPi_Incubator
=============

RPi controlled egg incubator using DHT22 sensors.  The code assumes you're comfortable hacking around in Python + hardware to get this to work.  There is next to no documentation for now.

It's a mash-up of a few things, held together with some Python.

The temperature & humidity are sensed using DHT22 sensors.  The values are read using a slightly modified version of an Adafruit_DHT library (to make it a bit more reliable).

To build the Adafruit_DHT app, call 'make'

To run the incubator software, call "sudo python Controller.py"  There are some other options, use -h to get them.  The majority of options are concerned with raising an alarm if the temperature/humidity goes out of spec.

Pins for sensor inputs & outputs are burried deep in the code (sorry, I haven't made it easy for you!)
