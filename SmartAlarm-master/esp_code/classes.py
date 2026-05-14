from machine import Pin, PWM, ADC
import time
import utime
from hcsr04 import HCSR04
import media
import uasyncio as asyncio
from _thread import allocate_lock

hc=HCSR04(5,18)

class BUZZER:
    def __init__(self): 
        self.pwm = PWM(Pin(23, Pin.OUT),freq=2000)
        self.pwm.duty(0)
        
    def play(self, note, wait, duty,stop_callback=None):
        for unity in range(0,10):
            if note == 0:
                self.pwm.duty(0)
            else:
                self.pwm.freq(note)
                self.pwm.duty(duty)
            time.sleep_ms(wait)
            if hc.distance_cm() <= 5:
                self.stop()
                if stop_callback:
                    stop_callback()
                break
            self.stop()    
    def stop(self):
        self.pwm.duty(0)

class STEPMOTOR:
    def __init__(self):
        self.IN1=Pin(26, Pin.OUT)
        self.IN2=Pin(25,Pin.OUT)
        self.IN3=Pin(33,Pin.OUT)
        self.IN4=Pin(32,Pin.OUT)
        self.stepper_pins = [self.IN1, self.IN2, self.IN3, self.IN4]
        self.step_sequence=[
            [1, 0, 0, 1],
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 1],
        ]
        self.step_index=0
        self.stato = -1 #1 aperta, -1 chiusa
        self.is_moving = False
        self.last_step = 0
        self.lock = allocate_lock()
    
    def step(self,direction, steps, delay):
        with self.lock:
            if self.is_moving:
                return
            self.is_moving = True
        try:
            for i in range(steps):
                with self.lock:
                    if not self.is_moving:
                        break
                    self.step_index=(self.step_index + direction)%len(self.step_sequence)
                    for pin_index in range(len(self.stepper_pins)):
                        pin_value=self.step_sequence[self.step_index][pin_index]
                        self.stepper_pins[pin_index].value(pin_value)
                time.sleep(delay)
                self.last_step += 1
            with self.lock:
                self.stato=direction
                self.is_moving = False
                print("Finito")
        finally:
            with self.lock:
                self.is_moving=False
            self.ferma()
            self.stato=direction
            print("Finito")

    def getStato(self):
        return self.stato
    
    def ferma(self):
        with self.lock:
            self.is_moving=False
        for pin in self.stepper_pins:
            pin.value(0)
        
    def modalitaNaturale(self,treshold,current, client):
        print("Entrato nella modalità luce naturale!")
        with self.lock:
            if self.is_moving:
                return
        if current < treshold and self.stato != -1:
            print("C'è luce fuori, mi apro...")
            self.step(-1, 2*2048,0.01)
            client.publish(topic.MQTT_TOPIC_SUB10,str(1))
        elif current > treshold and self.stato != 1:
            print("Non c'è luce fuori, mi chiudo...")
            self.step(1,2*2048,0.01)
            client.publish(topic.MQTT_TOPIC_SUB10,str(0))
        else:
            return
    
    def step_reset(self):
        self.step_index=0

            




