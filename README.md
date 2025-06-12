# Overview

This is the source code repository for Project [MicroHex](https://www.youtube.com/playlist?list=PLAPTbzQ9K5TCGxGjUgji1VfkN3Fx_ZwAr), a small open-source hexapod robot. This software implements the full control system for the robot including inverse kinematics and exposes user controls through a Web-based UI. It is designed to run on the Raspberry Pi Pico W but should be compatible with any micro controller that supports MicroPython and WiFi.

# Installation

The one file that needs to be changed before installation is `src/config.py`. It contains two variables, `SSID` and `PASSWORD`, that needs to be updated to match your local WiFi settings to enable the web based UI.

All the files from the `src/` directory need to be uploaded to the root directory of your micro controller included your updated `config.py` file. We recommend using [Thonny](https://thonny.org/) to upload the files. Thonny is a Python IDE with support for working with MicroPython.

To upload the files using Thonny, first plug in your micro controller to your computer via USB. In the bottom right hand corner of Thonny, on the status bar, you should see the version of Python that it is using. Click the Python version and select an option similar to `MicroPython (Raspberry Pi Pico)`. It should also include the port where your micro controller is attached. Then click the large red `Stop/Restart backend` button near the top to connect to the micro controller.

Open the `Files` panel, if it isn't already open, by selecting `View -> Files`. There you should see the files on your local system and the files on your micro controller. Navigate to the `src\` directory of this repo on your local system.  For each file, right-click and select `Upload to \`. It should now appear on your micro controller.

You may now disconnect the USB.

# Running

With all the files uploaded, it will start running `main.py` as soon as it is powered on. It may take a few seconds for the micro controller to connect to WiFi.

To use the Web UI, first identify the IP address of the micro controller. This can be retrieved using Thonny. 

Re-connect your micro controller via USB, select the `main.py` file and click the large green `Run Current Script` button near the top. In the log output at the bottom, it should print out the current IP address that it is using.
