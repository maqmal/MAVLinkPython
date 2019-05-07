from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import math
#Set up option parsing to get connection string

connection_string = "127.0.0.1:14550"
sitl = None

#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect(connection_string, wait_ready=True)


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.
    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print "Basic pre-arm checks"
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
        time.sleep(1)

        
    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True    

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:      
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print " Altitude: ", vehicle.location.global_relative_frame.alt 
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: 
            print "Reached target altitude"
            break
        time.sleep(1)

arm_and_takeoff(10)

print "Set default/target airspeed to 3"
vehicle.airspeed = 3

print "Going towards first point..."
point1 = LocationGlobalRelative(-6.970994, 107.627233, 20)
vehicle.simple_goto(point1)

# sleep so we can see the change
time.sleep(10)

print "Going towards second point (groundspeed set to 10 m/s) ..."
point2 = LocationGlobalRelative(-6.971633, 107.631029, 20)
vehicle.simple_goto(point2, groundspeed=10)

# sleep so we can see the change
time.sleep(10)

print "Going towards third point (groundspeed set to 15 m/s) ..."
point3 = LocationGlobalRelative(-6.975881, 107.632215, 20)
vehicle.simple_goto(point2, groundspeed=15)
time.sleep(5)

print "-Check- Go to point 1"
vehicle.simple_goto(point1)
finished = False
while not finished:
    print("waiting...")
    currentGlobalRelative = vehicle.location.global_relative_frame
    distancePoint1 = get_distance_metres(point1, currentGlobalRelative)
    distancePoint2 = get_distance_metres(point2, currentGlobalRelative)
    distancePoint3 = get_distance_metres(point3, currentGlobalRelative)
    print("distance point 1 : %f") % distancePoint1
    print("distance point 2 : %f") % distancePoint2
    print("distance point 3 : %f") % distancePoint3

    if distancePoint1 < 5:
        # go to waypoint 2
        print("go to point 2")
        vehicle.simple_goto(point2)
    elif distancePoint2 < 5:
        # go to waypoint 3
        print("go to point 3")
        vehicle.simple_goto(point3)
    elif distancePoint3 < 5:
        # finish return to home
        finished = True
    else:
        print("On the way to way point ")

    print "Current Location: %s" % currentGlobalRelative

    time.sleep(1)

print "Returning to Launch"
vehicle.mode = VehicleMode("RTL")

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()
