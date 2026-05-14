# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

"""File avviato nel momento in cui si attiva l'ESP che si occupa delle connessioni wi-fi"""
import network,time
from umqtt.simple import MQTTClient
from machine import Pin, I2C
import ssd1306,framebuf,utime,freesans20,media
from writer import Writer
import topic

#parametri del display
WIDTH = 128
HEIGHT = 64
SCL_PIN = 22
SDA_PIN = 21

#lista di immagini da caricare durante la connessione al wifi
image_list=[media.wifi1,media.wifi2,media.wifi3]
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
display = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

#Connessione Wi-fi
print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('S20 FE di Miggi', 'gcdd6850')

#illustrazioni Wi-fi durante la connessione
while not sta_if.isconnected():
    print(".", end="")
    for im in image_list:
        fb = framebuf.FrameBuffer(im, 128, 64, framebuf.MONO_HLSB)
        display.fill(0)
        display.blit(fb, 8, 0)
        display.show()
        time.sleep(1)
        
fb = framebuf.FrameBuffer(media.wificonnesso, 128, 64, framebuf.MONO_HLSB)
display.fill(0)
display.blit(fb, 0, -6)
display.text("Connected!",30,53,1)
display.show()
print(" Connected!")

