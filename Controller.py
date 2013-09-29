from time import sleep
import subprocess
from PID import PID
import time
import sys, getopt
import RPi.GPIO as GPIO


# Preset options.
requiredTemp = 37.5

saveToLogFile = False
minTempAlarm = 0.0
maxTempAlarm = 100.0
maxTempDiff = 100.0

# Pin asignments
sensorPins = []
alarmOutputPin = 0
tempOutputPin = 0

tempPID = PID(1.0, 0.0, 0.0)


# Retrieve a sensor reading
def getSensorValues(sensorPin):
    # Use the (modified) Adafruit DHT library
    proc = subprocess.Popen(' '.join(["./Adafruit_DHT 22",str(sensorPin)]), stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    if out == "":
        raise ValueError
    else:
        # Output format: TT.t,HH.h
        vals = out.split(",")
        return float(vals[0]), float(vals[1])

# Save values to file to plot later.
def logActivity(temp, pidTemp, humid, logToFile):
    logLine = ''.join( str(x) for x in [int(time.time()) , "," , temp , ",", pidTemp, "," , humid, "\n"] )
    
    if logToFile == True:
        with open("log.txt", "a") as myLog:
            line = ''.join( str(x) for x in [int(time.time()) , "," , temp , ",", pidTemp, "," , humid, "\n"] )
            myLog.write(line)

# Initialise alarm, temp output pins.
def initOutputPins():
    """ Initialise outputs. """
    
    try:
        if alarmOutputPin != 0:
            GPIO.setup(alarmOutputPin, GPIO.OUT)
            GPIO.output(alarmOutputPin, False)
        
        if tempOutputPin != 0:
            GPIO.setup(tempOutputPin, GPIO.OUT)
            GPIO.output(tempOutputPin, False)
        
    except IOError:
        print "Unable to configure output pins.  Are you root?"
        exit(1)
    except InvalidPinException:
        print "Invalid pin selection."
        exit(1)

# Raise alarm if all gone wrong
def raiseAlarm():
    """ If all gone wrong, set an output to raise alarm. """
    if alarmOutputPin != 0:
        GPIO.output(alarmOutputPin, True)

# Increase/decrease temp.
def controlTemp(makeHot):
    if tempOutputPin != 0:
        if makeHot:
            GPIO.output(tempOutputPin, True)
        else:
            GPIO.output(tempOutputPin, False)



# Start prog from here:
#


# Get options (just log to file or not for now)
opts, args = getopt.getopt(sys.argv[1:],"hl", ["mint=","maxt=","alarm-pin=","sensor-pin=","temp-pin=","reqt=","maxdiff="])

for opt,arg in opts:
    if opt == "-h":
        print "-h\t\t\tPrint this message & exit"
        print "-l\t\t\tSave PID in/output to file for diagnostics"
        print "--mint <num>\t\tMinimum temperature alarm ( currently",minTempAlarm, ")"
        print "--maxt <num>\t\tMaximum temperature alarm ( currently", maxTempAlarm,")"
        print "--maxdiff <num>\t\tMaximum difference between temperature on different sensors ( currently", maxTempDiff,")"
        print "--alarm-pin <num>\tGPIO pin for alarm output (0 = unused, currently",alarmOutputPin,")"
        print "--sensor-pin <num>\tGPIO pin for DHT22 sensor input (THERE MUST BE AT LEAST ONE)"
        print "--temp-pin <num>\tGPIO pin for temperature output (0 = unused, currently",tempOutputPin,")"
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
        sensorPins.append(int(arg))
    elif opt == "--temp-pin":
        tempOutputPin = int(arg)
    elif opt == "--reqt":
        requiredTemp = float(arg)
    elif opt == "--maxdiff":
        maxTempDiff = float(arg)

if not sensorPins:
    print "No sensors specified using \"--sensor-pin\""
    exit(1)


# Now get on with the real work;
tempPID.setPoint(requiredTemp)

initOutputPins()

while(1):
    
    sensVals = []
    valueValid = False
    for pin in sensorPins:
        try:
            # The Adafruit thing seems unreliable,
            sensVals.append(getSensorValues(pin))
            valueValid = True;
        except ValueError:
            print "Unable to read from sensor",pin


    # Only do PID if we think values are ok.
    if valueValid:
        #Munge all of the values together.

        tempAvg = sum(float(first) for first, second in sensVals)/len(sensVals)
        humidAvg = sum(float(second) for first, second in sensVals)/len(sensVals)
        
        tempPIDResult = tempPID.update(tempAvg)
        
        if float(tempPIDResult) > 0.0:
            controlTemp(makeHot = True)
        else:
            controlTemp(makeHot = False)
        
        
        print "Temp:", tempAvg, "( PID out:",tempPIDResult, ")  Humidity:", humidAvg 
        
        logActivity(tempAvg, tempPIDResult, humidAvg, saveToLogFile)
        
        if minTempAlarm > tempAvg:
            print "Temperature too low."
            raiseAlarm()
        if tempAvg > maxTempAlarm:
            print "Temperature too high."
            raiseAlarm()

        # Make sure the difference between min-max temp isnt too great.
        tMax = max(first for first, second in sensVals)
        tMin = min(first for first, second in sensVals)
        if tMax - tMin > maxTempDiff:
            print "Sensor difference too high (min:",tMin,"max:",tMax,")"
            raiseAlarm()
        
        
        sleep(1)

