#!/usr/bin/python3
from ivy.std_api import *
import time
from enum import Enum
import sys
from navigation import Navigation
from ivy_interface import IvyInterface
from actuators import Actuators
import messages_pb2 as m

BUS = "127.255.255.255:2010"


class Robot:
    
    class Modules(Enum):
        NAV = 0
        ODOM_REPORT = 1
        ACTUATORS = 2

    def __init__(self, robot_name, bus=BUS, pos_init=(1500, 1000, 0)):
        self.com = IvyInterface(robot_name, bus)
        self.nav = Navigation(pos_init)
        self.actuators = Actuators()
        self.com.register_msg_cb(self.nav.set_speed, m.SpeedCommand)
        self.com.register_msg_cb(self.nav.set_pos_objective, m.PosCommand)
        self.com.register_msg_cb(self.actuators.handle_cmd, Actuators)
        self.com.start()
        self.modules_period = {}
        self.modules_update = {}
        self.modules_update_time = {}
        self.register_module(Robot.Modules.NAV, 0.05, self.nav.update)
        self.register_module(Robot.Modules.ODOM_REPORT, 0.1, self.update_odom_report)
        self.register_module(Robot.Modules.ACTUATORS, 1, self.update_actuators)

        time.sleep(0.1)
        for ac in self.actuators.actuators:
            self.com.declare_actuator(ac)

    def __enter__(self):
        return self

    def __exit__(self, t, value, traceback):
        self.com.stop()
    
    def register_module(self, module, period, update):
        self.modules_period[module] = period
        self.modules_update[module] = update
        self.modules_update_time[module] = time.time()
    
    def update(self):
        for module in Robot.Modules:
            now = time.time()
            dt = now - self.modules_update_time[module]
            if dt >= self.modules_period[module]:
                self.modules_update[module](dt)
                self.modules_update_time[module] = now

    def update_odom_report(self, dt):
        x, y, theta = self.nav.pos
        odom_report = m.OdomReport()
        odom_report.pos_x = x
        odom_report.pos_y = y
        odom_report.pos_theta = theta
        self.com.send_message(odom_report)

    def update_actuators(self, dt):
        self.actuators.update()
        for ac in self.actuators.actuators:
            if ac.val_changed == True:
                ac.val_changed=False
                self.com.report_actuator(ac)
        
    def run(self):
        while True:
            self.update()
            time.sleep(0.01)
        

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ./simu_robot.py robot_name")
        exit(-1)
    with Robot(sys.argv[1]) as robot:
        robot.run()
