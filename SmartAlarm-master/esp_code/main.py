import network,time,dht,ujson
from umqtt.simple import MQTTClient
from machine import Pin, I2C
import ssd1306,framebuf,utime,freesans20,media, gestoreSveglia
from writer import Writer
import classes
from hcsr04 import HCSR04
import uasyncio as asyncio
from tsl2561 import TSL2561
import _thread
import topic
from gestoreSveglia import SVEGLIE

client = topic.connessione()

#Callback che permette di stoppare la suoneria
def fermaSuoneria():
    global suonata
    suonata=1
    
#Funzioni ausiliarie per l'attivazione dei thread
def gestioneSuoneria1():
    buzzer.play(media.DS6,media.M1_wait,media.M1_duty, stop_callback=fermaSuoneria)
def gestioneSuoneria2():
    buzzer.play(media.C8,media.M2_wait,media.M2_duty, stop_callback=fermaSuoneria)


#inizializzazione variabili
suonata=0
enabled=0
realtime=0
treshold=0
sveglie=SVEGLIE()
sveglie=topic.getSveglie()
WIDTH = 128
HEIGHT = 64
SCL_PIN = 22
SDA_PIN = 21
sveglia_attiva = None

#inizializzazione dispositivi
hc=HCSR04(5,18)
buzzer=classes.BUZZER()
step=topic.getStep()
sensor = dht.DHT22(Pin(17))
led1 = Pin(14, Pin.OUT)
led2 = Pin(27, Pin.OUT)
led3 = Pin(15, Pin.OUT)
led4 = Pin(13, Pin.OUT)

#dispositivi che comunicano tramite i2c
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
display = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)
wr=Writer(display,freesans20)
sensorLux = TSL2561(i2c)

#inizializzazione led (spenti)
led1.off()
led2.off()
led3.off()
led4.off()


#Display del logo
fb = framebuf.FrameBuffer(media.image, 128, 64, framebuf.MONO_HLSB)
display.fill(0)
display.blit(fb, 8, 0)
display.show()
time.sleep(5)

print("Connected!")

#variabile relativa alle misurazioni
currentLux=0

while True:
    print(i2c.scan())
    try:
        client.check_msg()
        sensor.measure()
    except Exception as e:
        print(e)
    time.sleep(2)
    message = ujson.dumps({
        "temp": sensor.temperature(),
        "humidity": sensor.humidity(),
    })
    print(utime.localtime())
    anno1,mese1,giorno1,ore1,minuti1,_,_,_=utime.localtime()
    print(anno1,mese1,giorno1,ore1,minuti1)
    #verifica della modalità naturale
    enabled=topic.getEnabled()
    treshold=topic.getTreshold()
    if enabled == 1:
        currentLux=sensorLux.read()
        print(currentLux)
        print(treshold)
        _thread.start_new_thread(step.modalitaNaturale,(treshold, currentLux,client))
            
    #raccolta ora corrente
    print(sveglie.__str__())
    """
    Se ci sono sveglie, si verifica se vi è una corrispondenza tra l'ora della sveglia
    e quella corrente
    """
    if sveglie.dict != {}:
        print(sveglie.__str__())
        sveglia=sveglie.confrontoDataOra(giorno1,mese1,anno1,ore1,minuti1)
        print(sveglia)
        #Se ci sono corrispondenze
        if sveglia != -1 and sveglia != None:
            sveglia_attiva= sveglie.dict[sveglia].getName()
            print(sveglie.dict[sveglia].getName())
            display.show()
            #Suona la suoneria della sveglia
            if suonata == 0:
                if sveglie.dict[sveglia].getSuoneria() == 1:
                    _thread.start_new_thread(gestioneSuoneria1,())
                else:
                    _thread.start_new_thread(gestioneSuoneria2,())
                if hc.distance_cm() <= 5:
                    suonata=1
            #Si verifica se sono state impostate luci
            if sveglie.dict[sveglia].getLuci() == 1:
                led1.on()
                led2.on()
                led3.on()
                led4.on()
                client.publish(topic.MQTT_TOPIC_SUB6,str(1))
            else:
                led1.off()
                led2.off()
                led3.off()
                led4.off()
                client.publish(topic.MQTT_TOPIC_SUB6,str(0))
            #Se il valore è uguale a 1 la serranda viene aperta
            print(step.getStato())
            if sveglie.dict[sveglia].getSerranda() == 1 and step.getStato() != 1:
                _thread.start_new_thread(step.step,(1,2*2048, 0.01))
                client.publish(topic.MQTT_TOPIC_SUB5,str(1))
            elif sveglie.dict[sveglia].getSerranda() == 0 and step.getStato() != -1:
                _thread.start_new_thread(step.step,(-1,2*2048, 0.01))
                client.publish(topic.MQTT_TOPIC_SUB5,str(0))
            #Si verifica se la sveglia è stata spenta
            if suonata == 1:
                client.publish(topic.MQTT_TOPIC_SUB4,str(sveglia))
                sveglie.rimuovisveglia(sveglia)
                sveglia_attiva=None
                
    #Se è stata spenta si resetta la flag
    if suonata == 1 and sveglia not in sveglie.ids:
        suonata=0
    #Aggiornamento temperatura/umidità ed orario
    display.fill(0)
    display.text("{:.1f}C".format(sensor.temperature()),3,3, 1)
    display.text("{:.1f}%".format(sensor.humidity()),80,3, 1)
    orario="{:02}:{:02}".format(ore1,minuti1)
    display.text("{:02}/{:02}/{:0000}".format(giorno1,mese1,anno1),25,53,1)
    wr.set_textpos(display,30,40)
    wr.printstring(orario)
    if sveglia_attiva != None and sveglia in sveglie.dict:
        display.text(sveglie.dict[sveglia].getName(),30,20,1)
    display.show()
    print("Reporting to MQTT topic {}: {}".format(topic.MQTT_TOPIC_SUB1, message))
    client.publish(topic.MQTT_TOPIC_SUB1, message)
    time.sleep(3)


