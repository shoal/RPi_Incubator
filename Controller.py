from time import sleep
import subprocess
from PID import PID
import time
import sys, getopt
import RPi.GPIO as GPIO


# Preset options.
requiredTemp = 37.5
requiredHumid = 55.0

saveToLogFile = False
minTempAlarm = 0.0
maxTempAlarm = 100.0
maxErrCnt = 0

# Pin asignments
sensorPin = 14
alarmOutputPin = 22
tempOutputPin = 23
humidOutputPin = 24


tempPID = PID(1.0, 0.0, 0.0)
humidPID = PID(1.0, 0.0, 0.0)


# Retrieve a sensor reading
def getSensorValues():
    # Use the (modified) Adafruit DHT library
    proc = subprocess.Popen(' '.join(["./Adafruit_DHT 22",str(sensorPin)]), stdout=subprocess.PIPE, shell=True)
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

# Initialise alarm, temp & humid output pins.
def initOutputPins():
    """ Initialise outputs. """
    
    GPIO.setup(alarmOutputPin, GPIO.OUT)
    GPIO.output(alarmOutputPin, False)

    GPIO.setup(tempOutputPin, GPIO.OUT)
    GPIO.output(tempOutputPin, False)

    GPIO.setup(humidOutputPin, GPIO.OUT)
    GPIO.output(humidOutputPin, False)

# Raise alarm if all gone wrong
def raiseAlarm():
    """ If all gone wrong, set an output to raise alarm. """
    GPIO.output(alarmOutputPin, True)

# Increase/decrease temp.
def controlTemp(makeHot):
    if makeHot:
        GPIO.output(tempOutputPin, True)
    else:
        GPIO.output(tempOutputPin, False)

# Increate/decrease humidity
def controlHumid(makeWet):
    if makeWet:
        GPIO.output(humidOutputPin, True)
    else:
        GPIO.output(humidOutputPin, False)




# Start prog from here:
#


# Get options (just log to file or not for now)
opts, args = getopt.getopt(sys.argv[1:],"hl", ["mint=","maxt=","minh=","maxh=","errcnt=","alarm-pin=","sensor-pin=","temp-pin=","humid-pin=","reqt=","reqh="])

for opt,arg in opts:
    if opt == "-h":
        print "-h\t\t\tPrint this message & exit"
        print "-l\t\t\tSave PID in/output to file for diagnostics"
        print "--reqt <num>\t\tRequired temperature ( default",requiredTemp,")"
        print "--reqh <num>\t\tRequired humidity ( default",requiredHumid,")"
        print "--mint <num>\t\tMinimum temperature alarm ( default",minTempAlarm, ")"
        print "--maxt <num>\t\tMaximum temperature alarm ( default", maxTempAlarm,")"
        print "--errcnt <num>\t\tMaximum sensor reading error limit, 0 = off ( default",maxErrCnt,")"
        print "--alarm-pin <num>\tGPIO pin for alarm output ( default",alarmOutputPin,")"
        print "--sensor-pin <num>\tGPIO pin for DHT22 sensor input ( default",sensorPin,")"
        print "--temp-pin <num>\tGPIO pin for temperature output ( default",tempOutputPin,")"
        print "--humid-pin <num>\tGPIO pin for humidity output ( default",humidOutputPin,")"
        sys.exit()
    elif opt == "-l":
        saveToLogFile = True
    elif opt == "--mint":
        minTempAlarm = float(arg)
    elif opt == "--maxt":
        maxTempAlarm = float(arg)
    elif opt == "--errcnt":
        maxErrCnt = int(arg)
    elif opt == "--alarm-pin":
        alarmOutputPin = int(arg)
    elif opt == "--sensor-pin":
        sensorPin = int(arg)
    elif opt == "--temp-pin":
        tempOutputPin = int(arg)
    elif opt == "--humid-pin":
        humidOutputPin = int(arg)
    elif opt == "--reqt":
        requiredTemp = float(arg)
    elif opt == "--reqh":
        requiredHumid = float(arg)

# Now get on with the real work;
tempPID.setPoint(requiredTemp)
humidPID.setPoint(requiredHumid)

initOutputPins()

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
        
        tempPIDResult = tempPID.update(temp)
        humidPIDResult= humidPID.update(humid)
         
        if float(tempPIDResult) > 0.0:
            controlTemp(makeHot = True)
        else:
            controlTemp(makeHot = False)
        
        if humidPIDResult > 0.0:
            controlHumid(makeWet = True)
        else:
            controlHumid(makeWet = False)
        
        
        print "Temp: ", temp, " Humid: ", humid, "Drive change required: ", tempPIDResult , "/", humidPIDResult
        
        logActivity(temp, tempPIDResult, humid, humidPIDResult, saveToLogFile)
        
        if minTempAlarm > temp:
            print "Temperature too low."
            raiseAlarm()
        if temp > maxTempAlarm:
            print "Temperature too high."
            raiseAlarm()
        
        sensorErrorCount = 0
    else:
        sensorErrorCount = sensorErrorCount + 1
    
    # Finally, check retry limits.
    if maxErrCnt > 0 and sensorErrorCount >= maxErrCnt:
        print "Sensor failures too often."
        raiseAlarm()
    
    sleep(1)
