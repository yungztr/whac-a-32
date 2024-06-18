# yungztrunks / weshford

import wifi
import socketpool
import ssl
import neopixel
import time
import json
from rainbowio import colorwheel
import board
import digitalio
import espnow
from adafruit_bme280 import basic as adafruit_bme280
import random

PURPLE = "\033[95m"
CYAN = "\033[96m"
DARKCYAN = "\033[36m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
END = "\033[0m"

def rainbow(delay):
    for color in range(255):
        pixel[0] = colorwheel(color)
        time.sleep(delay)

def mac2str():
    mac = wifi.radio.mac_address
    return ":".join("{:02x}".format(b) for b in mac)

def pacmac2str(mac):
    mac = str(mac)
    mac = mac.replace('b', '').replace("'", '').replace('\\', ':').replace('x', '').lstrip(':')
    return mac

def set_led(color):
    pixel[0] = color

def random_delay():
    return random.randint(1, 6)

def toggleLED():
    led.value = not led.value

def onDataReceive():
    try:
        packet = e.read()
        if packet:
            print("Nachricht erhalten: ", BLUE, packet, END, " von ", GREEN, pacmac2str(packet.mac), END)
            message = packet.msg.decode('utf-8')
            message = message.replace('b', '').replace("'", '')
            # print("Message:", message)
            return message
        else:
            return "NONE"
    except Exception as ex:
        print(RED, "Ein Fehler ist aufgetreten", END)
        print(ex)
        return False

def print_message(packet):
    b = packet.msg.replace('b', '').replace("'", '')
    print(packet.msg.decode('utf-8'))

def print_mac(packet):
    print(packet.mac)

i2c = board.I2C()
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.sea_level_pressure = 1013.25

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)

e = espnow.ESPNow()
packets = []

peer = espnow.Peer(mac=b'\x84\xf7\x03\xf1\xb1\xc6')
e.peers.append(peer)

set_led((255, 255, 0))
print("Meine MAC: ", PURPLE, mac2str(), END)

master = False
round = 1
status = "IDLE"

# connecting to andere esp
while True:
    try:
        time.sleep(0.1)
        packet = onDataReceive()
        if packet == "START":
            set_led((0, 255, 0))
            time.sleep(2)
            status = "PLAY"
            print(GREEN, "Signal angekommen. Spiel startet", END)
            break
        if not button.value:
            e.send("START".encode('utf-8'))
            set_led((0, 255, 0))
            master = True
            status = "PLAY"
            print(GREEN, "Knopf gedrückt. Spiel startet", END)
            time.sleep(2)
            break
    except Exception as ex:
        print(RED, "Ein Fehler ist aufgetreten",END)
        print(ex)
        set_led((255, 255, 255))
        time.sleep(5)
        continue

print(mac2str())

set_led((0, 0, 0))
master_humidity = 0
slave_humidity = 0
higher_hum_has = ""
# VORBEREITUNG MASTER
if master:
    time.sleep(4)
    print(DARKCYAN, "Master.")
    # time.sleep(random_delay())
    master_humidity = str(bme280.humidity)
    print("Master Feuchtigkeit:" , PURPLE, master_humidity, END)
    e.send(master_humidity)
    print(DARKCYAN, "Feuchtigkeit an Slave gesendet", END)
    time.sleep(2)
    while True:
        packet = onDataReceive()
        if packet != "NONE":
            slave_humidity = packet
            print("Slave Feuchtigkeit:", YELLOW, slave_humidity, END)
            break
        time.sleep(0.1)
    higher_hum_has = "Master" if master_humidity > slave_humidity else "Slave"
    print("Höhere Feuchtigkeit: ", BLUE, higher_hum_has, END)
    time.sleep(1.3)
    e.send("LETSGO")
    time.sleep(0.07)
    # GAME ITSELF MASTER
    if higher_hum_has == "Master":
        time.sleep(0.05)
        set_led((0, 0, 255))
        counter = 0
        while counter < 2:
            if not button.value:
                round += 1
                e.send("WON")
                set_led((0, 255, 0))
                print("Gewonnen")
                break
            else:
                packet = onDataReceive()
                if packet:
                    if packet == "WON":
                        round += 1
                        e.send("WON")
                        set_led((0, 255, 0))
                        print("WON Paket erhalten. Gewonnen")
                        break
                time.sleep(0.05)
            time.sleep(0.05)
            counter += 0.1
        if counter >= 2:
            status = "FAIL"
            e.send("FAIL")
            set_led((255, 0, 0))
            print("Timeout. Game over")
    else:
        time.sleep(0.05)
        set_led((255, 0, 0))
        counter = 0
        while counter < 2:
            if not button.value:
                status = "FAIL"
                e.send("FAIL")
                set_led((255, 0, 0))
                print("Falsch gedrückt. Game Over")
            else:
                packet = onDataReceive()
                if packet == "WON":
                    round += 1
                    set_led((0, 255, 0))
                    print("WON Paket erhalten. Gewonnen")
                    break
                time.sleep(0.05)
            time.sleep(0.05)
            counter += 0.1
        if counter >= 2:
            status = "FAIL"
            e.send("FAIL")
            set_led((255, 0, 0))
            print("Timeout. Game over.")
# VORBEREITUNG SLAVE
else:
    print(YELLOW, "Slave.")
    slave_humidity = str(bme280.humidity)
    print("Slave Feuchtigkeit:", PURPLE, slave_humidity, END)
    while True:
        packet = onDataReceive()
        if packet != "NONE":
            master_humidity = packet
            print("Master Feuchtigkeit erhalten", PURPLE, master_humidity, END)
            break
        time.sleep(1)
    time.sleep(0.1)
    higher_hum_has = "Master" if master_humidity > slave_humidity else "Slave"
    print("Höhere Feuchtigkeit: ", BLUE, higher_hum_has, END)
    e.send(slave_humidity)
    time.sleep(0.4)
    while True:
        packet = onDataReceive()
        if packet == "LETSGO":
            break
        time.sleep(0.1)
    # GAME ITSELF SLAVE
    if higher_hum_has == "Slave":
        time.sleep(0.05)
        set_led((0, 0, 255))
        while True:
            if not button.value:
                e.send("WON")
                set_led((0, 255, 0))
                print("Gewonnen")
                break
            else:
                packet = onDataReceive()
                if packet == "FAIL":
                    status = "FAIL"
                    set_led((255, 0, 0))
                    print("Game Over")
                    break
            time.sleep(0.05)
    else:
        time.sleep(0.05)
        set_led((255, 0, 0))
        while True:
            if not button.value:
                status = "FAIL"
                e.send("FAIL")
                set_led((255, 0, 0))
                print("Falsch gedrückt. Game over.")
            else:
                packet = onDataReceive()
                if packet == "FAIL":
                    status = "FAIL"
                    set_led((255, 0, 0))
                    print("FAIL Paket erhalten. Game over.")
                    break
                if packet == "WON":
                    round += 1
                    e.send("WON")
                    set_led((0, 255, 0))
                    print("WON Paket erhalten. Gewonnen")
                    break
            time.sleep(0.05)

if status == "FAIL":
    print("Du bist ein Verlierer")
    for x in range(20):
        set_led((255, 0, 0))
        time.sleep(0.3)
        set_led((0, 0, 0))
        time.sleep(0.3)

if status == "PLAY":
    print("So sehen Sieger aus")
    for x in range(20):
        rainbow(0.01)