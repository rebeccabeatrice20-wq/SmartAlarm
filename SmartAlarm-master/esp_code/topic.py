""" File che si occupa della comunicazione MQTT: sottoscrizioen ai topic e reazioni ai messaggi ricevuti """
import network,time,dht,ujson
from umqtt.simple import MQTTClient
from machine import Pin, I2C, RTC
import ssd1306,framebuf,utime,freesans20,media, gestoreSveglia
from writer import Writer
import classes
import _thread
import machine

#inizializzazione dispositivi
step=classes.STEPMOTOR()
led1 = Pin(14, Pin.OUT)
led2 = Pin(13, Pin.OUT)
led3 = Pin(15, Pin.OUT)
led4 = Pin(27, Pin.OUT)

#parametri MQTT
MQTT_CLIENT_ID = "projectiot"
MQTT_BROKER = "192.168.223.17"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_TOPIC = 'sveglia'
MQTT_TOPIC_SUB0 = b'sveglia/luci/esp32'
MQTT_TOPIC_SUB1 = 'sveglia/sensore/meteo'
MQTT_TOPIC_SUB2=b'sveglia/gestionesveglia/aggiunta'
MQTT_TOPIC_SUB3=b'sveglia/gestionesveglia/rimozione'
MQTT_TOPIC_SUB4='sveglia/gestionesveglia/suonata'
MQTT_TOPIC_SUB5='sveglia/stato/serrandaAperta'
MQTT_TOPIC_SUB6='sveglia/stato/luciaccese'
MQTT_TOPIC_SUB7=b'sveglia/serranda/esp32'
MQTT_TOPIC_SUB8 = b'sveglia/oracorrente'
MQTT_TOPIC_SUB9 = b'sveglia/modalita/naturale'
MQTT_TOPIC_SUB10 = 'sveglia/modalita/naturale/stato/serrandaAperta'

#variabili utilizzate nella ricezione dei messaggi MQTT
enabled=0
realtime=0
treshold=0
sveglie=gestoreSveglia.SVEGLIE()

#Si occupa della connessione MQTT e la sottoscrizione ai topic di interesse, ritorna il client
def connessione():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
    client.set_callback(sub_callback)
    client.connect()
    #Sottoscrizione ai topic di interesse
    client.subscribe(MQTT_TOPIC_SUB0)#luci
    client.subscribe(MQTT_TOPIC_SUB2)#aggiunta sveglia
    client.subscribe(MQTT_TOPIC_SUB3)#rimozione sveglia
    client.subscribe(MQTT_TOPIC_SUB7)#serranda
    client.subscribe(MQTT_TOPIC_SUB9)#modalità naturale
    client.subscribe(MQTT_TOPIC_SUB8)
    return client

#Si occupa delle azioni da intraprendere quando si ricevono messaggi su determinati topic
def sub_callback(topic,msg):
    global treshold, enabled,sveglie
    print(topic,msg)
    
    #Topic relativo all'accensione delle luci
    if topic == MQTT_TOPIC_SUB0:
        if msg == b'1':
            led1.on()
            led2.on()
            led3.on()
            led4.on()
        elif msg == b'0':
            led1.off()
            led2.off()
            led3.off()
            led4.off()
            
    #Topic relativo all'impostazione di una sveglia
    elif topic == MQTT_TOPIC_SUB2:
        try:
            print(msg)
            data_str = msg.decode('utf-8')
            data = ujson.loads(data_str)
            print (data)
            id=data["id"]
            nome=data["name"]
            giorno=data["day"]
            mese=data["month"]
            anno=data["year"]
            ora=data["hour"]
            minuti=data["minute"]
            suoneria=data["melody"]
            luci=data["lights"]
            serranda=data["window"]
            sveglie.aggiungisveglia(id,nome,giorno,mese,anno,ora,minuti,suoneria,luci,serranda)
            print(id,nome,giorno,mese,anno,ora,minuti,suoneria,luci,serranda)
        except Exception as e:
            print("Errore nel parsing o nell'accesso ai dati:", e)
            
    #Topic relativo alla rimozione di una sveglia (da interfaccia)
    elif topic == MQTT_TOPIC_SUB3:
        print(msg)
        ids = msg.decode() 
        sveglie.rimuovisveglia(int(ids))
        
    #Topic relativo all'apertura/chiusura della serranda (da interfaccia)
    elif topic == MQTT_TOPIC_SUB7:
        print(topic,msg)
        if msg == b'1':
             _thread.start_new_thread(step.step,(1,2*2048, 0.01))
        else:
             _thread.start_new_thread(step.step,(-1,2*2048, 0.01))
    #Topic relativo alla ricezione della data di partenza per l'orologio
    elif topic == MQTT_TOPIC_SUB8:
        data_str = msg.decode('utf-8')
        data = ujson.loads(data_str)
        anno=data["year"]
        mese=data["month"]
        giorno=data["day"]
        ora=data["hour"]
        minuti=data["minute"]
        secondi=data["second"]
        rtc_time=(anno, mese, giorno, 0, ora, minuti, secondi, 0)
        machine.RTC().datetime(rtc_time)
        print(utime.gmtime(1748548115))
        
    #Topic relativo all'attivazione/disattivazione della modalità luce naturale (da interfaccia)
    elif topic == MQTT_TOPIC_SUB9:
        data = msg.decode()
        data_dec = ujson.loads(data)
        enabled=data_dec["enabled"]
        treshold=int(data_dec["treshold"])
        print(enabled,treshold)

def getSveglie():
    return sveglie

def getEnabled():
    return enabled

def getTreshold():
    return treshold