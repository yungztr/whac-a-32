# whac-a-32

This small project is a Whac-A-Mole kinda game running on two Feather Boards ESP32-S2. The game measures the humidity using the BME280 sensor and communicates data between the boards using ESPNOW in a (cheap?) master/slave configuration.

This was a school project. I've written it all by myself with chatgpt helping me to add debug prints because I was to lazy to type in print() on every 2nd line

### Requirements

You will need the following to deploy it on your board
+ VS Code with:
	+ CircuitPython Extension (I've used version 0.1.19, runs the best for some reason)
+ Two Featherboards  (I've had ESP32-S2, will probably work / don't work on more)
	+ Make sure you've got it installed correctly etc.
+ The included lib folder

### Deploy the Code:

**Make sure you're able to run anything at all first**
**If not, follow the steps I did here on the bottom**

1. Connect the Feather Boards to your computer.
1. Open VS Code and access the terminal (*Make sure CircuitPython Extension is installed*)
1. Select yo Board **ESP32S2** (*bottom right with CircuitPython Extension*)
1. Open your serial monitor (*bottom right, that lil plug(?) icon*)

**Do the same with the other board on another VS Code Window**

Each device will print its MAC address to the terminal when run for the first time. Modify the code to set the MAC address of the other peer device.

Restart both devices by saving the file (or by pressing `CTRL+D` in the Terminal)

### How to Run
When the code is deployed, the program should now automatically run once it's powered. I suppose you've got better things to do with your boards tho.

**Enjoy playing**

#### Hopefully Helpful Troubleshooting
+ If the code doesn't run, verify that the lib folder contains all the required libraries. If not, download them [here](https://circuitpython.org/libraries)
+ Double-check the MAC addresses and ensure they are correctly set for communication between the devices.
+ If there are issues with the BME280 sensor readings, check the sensor connections (and wiring).

##### How To Run Feather Board At All
Follow these steps:
1. Press Reset on your device
2. Press Boot after a second
3. Explorer should Pop Up. It shoud be named **FTHRS2BOOT**
4. Copy the [uf2](https://circuitpython.org/board/adafruit_feather_esp32s2/) file of your corresponding board to the opened Folder
5. When it's finished, it should restart automatically.
6. Now your Board is ready to run probably