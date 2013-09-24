from time import sleep
import subprocess
from PID import PID
import time
import sys, getopt
import RPi.GPIO as GPIO

tempPID = PID()
humidPID = PID()

# Initialise the PIDs
def initialisePID():
    # Create a PID controller for temperature
    tempPID = PID(1.0, 0.1, 0.0)
    tempPID.setPoint(37.5)
    
    # Create a PID controller for humidity
    humidPID = PID(1.0, 0.0, 0.0)
    humidPID.setPoint(55.0)

# Retrieve a sensor reading
def getSensorValues():
    # Use the (modified) Adafruit DHT library
    proc = subprocess.Popen(["./Adafruit_DHT 22 14"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    if out == "":
        print "No values read!"
        raise ValueError
    else:
        # Output format: TT.t,HH.h
        return out.split(",")

# Save values to file to plot later.
def logActivity(temp, pidTemp, humid, pidHumid, logToFile):
    logLine = ''.join( str(x) for x in [int(time.time()) , "," , temp , ",", pidTemp, "," , humid, "," , pidHumid, "\n"] )
    
    if logToFile == True:
        with open("log.txt", "a") as myLog:
            line = ''.join( str(x) for x in [int(time.time()) , "," , temp , ",", pidTemp, "," , humid, "," , pidHumid, "\n"] )
            myLog.write(line)

# Initialise alarm output.
def initAlarmOutput():
    """ Initialise an alarm output. """
    
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18, False)


# Raise alarm if all gone wrong
def raiseAlarm():
    """ If all gone wrong, set an output to raise alarm. """
    GPIO.output(18, True)



# Start prog from here:
#

# Preset options.
saveToLogFile = False
minTempAlarm = 0.0
maxTempAlarm = 100.0
minHumidAlarm = 0.0
maxHumidAlarm = 100.0
maxErrCnt = 0

# Get options (just log to file or not for now)
opts, args = getopt.getopt(sys.argv[1:],"hl", ["mint=","maxt=","minh=","maxh=","errcnt="])

for opt,arg in opts:
    if opt == "-h":
        print "-h\t\tPrint this message & exit."
        print "-l\t\tSave PID in/output to file for diagnostics."
        print "--mint <num>\tMinimum temperature alarm (default 0.0)"
        print "--maxt <num>\tMaximum temperature alarm (default 100.0)"
        print "--minh <num>\tMinimum humidity alarm (default 0.0)"
        print "--maxh <num>\tMaximum humidity alarm (default 100.0)"
        print "--errcnt <num>\tMaximum sensor reading error limit. 0 = off (default 0)"
        sys.exit()
    elif opt == "-l":
        saveToLogFile = True
    elif opt == "--mint":
        minTempAlarm = float(arg)
    elif opt == "--maxt":
        maxTempAlarm = float(arg)
    elif opt == "--minh":
        minHumidAlarm = float(arg)
    elif opt == "--maxh":
        maxHumidAlarm = float(arg)
    elif opt == "--errcnt":
        maxErrCnt = int(arg)


# Now get on with the real work;
initialisePID()
initAlarmOutput()

sensorErrorCount = 0

while(1):
    
    # The Adafruit thing seems unreliable,
    try:
        sensVals = getSensorValues()
        valueValid = True;
    except ValueError:
        valueValid = False;
        sensVals = [100.0, 100.0]   # If in doubt, freeze them not cook (not that we intend to do anything)
    
    # Only do PID if we think values are ok.
    if valueValid:
        temp = float(sensVals[0])
        humid= float(sensVals[1])
        
        tempOutput = tempPID.update(temp)
        humidOutput= humidPID.update(humid)
        
        print "Temp: ", temp, " Humid: ", humid, "Drive change required: ", tempOutput , "/", humidOutput
        
        logActivity(temp, tempOutput, humid, humidOutput, saveToLogFile)
        
        if minTempAlarm > temp:
            print "Temperature too low."
            raiseAlarm()
        if temp > maxTempAlarm:
            print "Temperature too high."
            raiseAlarm()
        if minHumidAlarm > humid:
            print "Humidity too low."
            raiseAlarm()
        if humid > maxHumidAlarm:
            print "Humidity too high."
            raiseAlarm()
        
        sensorErrorCount = 0
    else:
        sensorErrorCount = sensorErrorCount + 1
    
    # Finally, check retry limits.
    if maxErrCnt > 0 and sensorErrorCount >= maxErrCnt:
        print "Sensor failures too often."
        raiseAlarm()
    
    sleep(1)
