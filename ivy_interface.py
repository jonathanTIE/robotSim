#!/usr/bin/python3
from ivy.std_api import *
from interface import Interface

BUS = "127.255.255.255:2010"

#SPEED_REG = "SpeedCmd (.+) (.+) (.+)"
SPEED_REG = "Direction (.+),(.+),(.+)"
POS_REG =  "Go to linear (.+),(.+)"
POS_ORIENT_REG = "Go to orient (.+),(.+),(.+)"
#POS_REG   = "PosCmd (.+) (.+) (.+) (.+)"

POS_REPORT = "Update robot pose {};{};{}"


class IvyInterface(Interface):

    def __init__(self, bus=BUS):
        Interface.__init__(self)
        IvyInit("Robot", "TestIvy OK!")
        self.bus = bus
        IvyBindMsg(self.on_speed_cmd,      SPEED_REG)
        IvyBindMsg(self.on_pos_cmd,        POS_REG)
        IvyBindMsg(self.on_pos_orient_cmd, POS_ORIENT_REG)
    
    def start(self):
        IvyStart(self.bus)

    def stop(self):
        IvyStop()
    
    def send_pos_report(self, pos):
        x, y, theta = pos
        IvySendMsg(POS_REPORT.format(x, y, theta))
    
    def on_speed_cmd(self, sender, vx, vy, vtheta):
        print("sender", sender)
        speed = (float(vx) * 300, float(vy) * 300, float(vtheta) * 1.0)
        for cb in self.speed_cb:
            cb(speed)

    def on_pos_cmd(self, sender, x, y):
        pos = (float(x), float(y), None)
        for cb in self.pos_cb:
            cb(pos)
    
    def on_pos_orient_cmd(self, sender, x, y, theta):
        pos = (float(x), float(y), float(theta))
        for cb in self.pos_cb:
            cb(pos)

