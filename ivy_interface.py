#!/usr/bin/python3
from ivy.std_api import *
from interface import Interface
import messages_pb2 as m
from actuators import Actuators, RWType

BUS = "127.255.255.255:2010"

SPEED_REG = "SpeedCmd {} (.+) (.+) (.+)"
POS_REG =  "PosCmd {} (.+) (.+)"
POS_ORIENT_REG = "PosCmdOrient {} (.+) (.+) (.+)"
ACTUATOR_CMD = "ActuatorCmd {} (.+) (.+)"

ACTUATOR_DECL = "ActuatorDecl {} {} {} {} {} {} {}"
POS_REPORT = "PosReport {} {} {} {}"
ACTUATOR_REPORT = "ActuatorReport {} {} {}"


class IvyInterface(Interface):

    def __init__(self, robot_name, bus=BUS):
        Interface.__init__(self)
        IvyInit(robot_name, robot_name + " ready!")
        self.rid = robot_name
        self.bus = bus
        IvyBindMsg(self.on_speed_cmd,      SPEED_REG.format(self.rid))
        IvyBindMsg(self.on_pos_cmd,        POS_REG.format(self.rid))
        IvyBindMsg(self.on_pos_orient_cmd, POS_ORIENT_REG.format(self.rid))
        IvyBindMsg(self.on_actuator_cmd,   ACTUATOR_CMD.format(self.rid))
    
    def start(self):
        IvyStart(self.bus)

    def stop(self):
        IvyStop()

    def send_message(self, msg):
        ivymsg = None
        if type(msg) == m.OdomReport:
            ivymsg = POS_REPORT.format(self.rid, msg.pos_x, msg.pos_y, msg.pos_theta)
        if ivymsg is not None:
            IvySendMsg(ivymsg)

    def declare_actuator(self, ac):
        rights = "READ" if ac.rwtype == RWType.R else "RW" 
        ivymsg = ACTUATOR_DECL.format(self.rid, ac.name, ac.min, ac.max, ac.step, rights, ac.unit)
        IvySendMsg(ivymsg)

    def report_actuator(self, ac):
        ivymsg = ACTUATOR_REPORT.format(self.rid, ac.name, ac.value)
        IvySendMsg(ivymsg)
    
    def on_speed_cmd(self, sender, vx, vy, vtheta):
        speed = m.SpeedCommand()
        speed.vx = float(vx) * 300
        speed.vy = float(vy) * 300
        speed.vtheta = float(vtheta) * 1.0
        for cb in self.cbs.get(m.SpeedCommand, []):
            cb(speed)

    def on_pos_cmd(self, sender, x, y):
        pos = m.PosCommand()
        pos.x = float(x)
        pos.y = float(y)
        for cb in self.cbs.get(m.PosCommand, []):
            cb(pos)

    def on_actuator_cmd(self, sender, name, value):
        for cb in self.cbs.get(Actuators, []):
            cb(name, value)
    
    def on_pos_orient_cmd(self, sender, x, y, theta):
        pos = m.PosCommand()
        pos.x = float(x)
        pos.y = float(y)
        pos.theta = float(theta)
        for cb in self.cbs.get(m.PosCommand, []):
            cb(pos)

