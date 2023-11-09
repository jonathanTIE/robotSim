#!/usr/bin/python3
import time
import random
from enum import Enum

class RWType(Enum):
    R = 0
    RW = 2


class Actuator:
    def __init__(self, name, min, max, step, unit, rwtype, value):
        self.name=name
        self.min=min
        self.max=max
        self.step=step
        self.unit=unit
        self.rwtype=rwtype
        self.value=value
        self.val_changed=True


class Actuators:

    def __init__(self):
        self.actuators = []
        for _ in range(random.randint(2,5)):
            if random.random() < 0.1:
                ac = self.make_pump()
            elif  random.random() < 0.2:
                ac = self.make_EV()
            elif random.random() < 0.3:
                ac = self.make_servo()
            elif random.random() < 0.4:
                ac = self.make_dynamixel()
            elif random.random() < 0.5:
                ac = self.make_led()
            elif random.random() < 0.6:
                ac = self.make_pressure()
            elif random.random() < 0.7:
                ac = self.make_switch()
            elif random.random() < 0.8:
                ac = self.make_elevator()
            elif random.random() < 0.9:
                ac = self.make_elevator()
            else:
                ac = self.make_led()
        print([ac.name for ac in self.actuators])

    def make_pump(self):
        ac = Actuator(name="pump"+str(len(self.actuators)), min=0, max=1, step=1, unit="None", rwtype=RWType.RW, value=0)
        self.actuators.append(ac)

    def make_EV(self):
        ac = Actuator(name="EV"+str(len(self.actuators)), min=0, max=1, step=1, unit="None", rwtype=RWType.RW, value=0)
        self.actuators.append(ac)

    def make_servo(self):
        min = random.randint(0, 100)
        max = random.randint(min, 180)
        ac = Actuator(name="Servo"+str(len(self.actuators)), min=min, max=max, step=1, unit="°", rwtype=RWType.RW, value=min)
        self.actuators.append(ac)

    def make_dynamixel(self):
        min = random.randint(0, 500)
        max = random.randint(min, 1024)
        ac = Actuator(name="Dynamixel"+str(len(self.actuators)), min=min, max=max, step=1, unit="None", rwtype=RWType.RW, value=min)
        self.actuators.append(ac)

    def make_led(self):
        ac = Actuator(name="LED"+str(len(self.actuators)), min=0, max=1, step=1, unit="None", rwtype=RWType.RW, value=0)
        self.actuators.append(ac)

    def make_pressure(self):
        ac = Actuator(name="Baro"+str(len(self.actuators)), min=0, max=1024, step=1, unit="None", rwtype=RWType.R, value=0)
        self.actuators.append(ac)

    def make_switch(self):
        ac = Actuator(name="Switch"+str(len(self.actuators)), min=0, max=1, step=1, unit="None", rwtype=RWType.R, value=0)
        self.actuators.append(ac)

    def make_elevator(self):
        ac = Actuator(name="Elevator"+str(len(self.actuators)), min=0, max=200, step=1, unit="mm", rwtype=RWType.RW, value=200)
        self.actuators.append(ac)

    def update(self):
        for ac in self.actuators:
            if (ac.rwtype==RWType.R and random.random()<0.3) or (ac.rwtype==RWType.RW and random.random()<0.1):
                val = random.random()*(ac.max-ac.min)+ac.min
                ac.value = round(val/ac.step)*ac.step
                ac.val_changed = True

    def handle_cmd(self, name, value):
        for ac in self.actuators:
            if ac.name == name and ac.rwtype == RWType.RW:
                ac.value = value
                ac.val_changed = True
                print("ac ", ac, "changed to value ", value)
                break

