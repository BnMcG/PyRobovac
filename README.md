# PyRobovac
Python library for controlling the Eufy RoboVac 11c.

## Usage
```python
from robovac.robovac import Robovac

my_robovac = Robovac('ROBOVAC_IP', 'ROBOVAC_LOCAL_CODE')

# Cleaning modes
my_robovac.start_auto_clean()
my_robovac.start_edge_clean()
my_robovac.start_single_room_clean()
my_robovac.start_spot_clean()

# Set cleaning speed
my_robovac.use_normal_speed()
my_robovac.use_max_speed()

# Stop cleaning
my_robovac.stop()

# Return to charging base
my_robovac.go_home()

# Activate "find me" mode, plays a tone until deactivated
my_robovac.start_find_me()
my_robovac.stop_find_me()

# Move in a given direction
my_robovac.go_forward()
my_robovac.go_backward()
my_robovac.go_left()
my_robovac.go_right()

# Get RoboVac status
my_robovac.get_status()
```

## Local code
The API authenticates with the Robovac using a unique local code.
This is a 16 character string that's unique to the RoboVac. Currently,
the easiest way to find this code is to connect to your Android phone via ADB,
and run Logcat while running the Eufy Home app. 

You can then search through the log output for "localcode" to find
the local code for your device.

## Notes & Acknowledgements
This library can only be used when on the same LAN as the RoboVac.
The library has only been tested with the Eufy RoboVac 11c. It may or
may not work with other models.

Thanks to @mjg59 for his work on decrypting packets received
from Eufy devices. See it here: [google/python-lakeside](https://github.com/google/python-lakeside)
