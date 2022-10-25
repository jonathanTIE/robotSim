#!/usr/bin/python3
import time
from enum import Enum
import sys
from navigation import Navigation, HolonomicNavigation
from actuators import Actuators
from interface import Interface
from ecal_interface import EcalInterface
import messages_pb2 as m
#from ros_interface import RosInterface

BUS = "127.255.255.255:2010"


class Robot:
    
    class Modules(Enum):
        NAV = 0
        ODOM_REPORT = 1
        ACTUATORS = 2

    def __init__(self, interface: Interface, is_holonomic=True, bus=BUS, pos_init=(1500, 1000, 0)):
        self.actuators = Actuators()
        #self.com = IvyInterface(robot_name, self.actuators, bus)
        self.nav = HolonomicNavigation(pos_init) if is_holonomic else Navigation(pos_init)
        self.modules_period = {}
        self.modules_update = {}
        self.modules_update_time = {}
        self.register_module(Robot.Modules.NAV, 0.05, self.nav.update)
        self.register_module(Robot.Modules.ACTUATORS, 1, self.update_actuators)
        self.register_module(Robot.Modules.ODOM_REPORT, 0.1, self.update_odom_report)

        #COMMUNICATION INIT :
        self.com = interface
        self.com.start()
        self.com.register_msg_callback('speed_cmd', self.nav.set_speed)
        self.com.register_msg_callback('position_cmd', self.nav.set_pos_objective)
        #self.com.register_msg_callback('actuator_cmd', self.actuators.handle_cmd, Actuators)
    def __enter__(self):
        return self

    def __exit__(self, t, value, traceback):
        if self.com.running:
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


    def update_actuators(self, dt):
        self.actuators.update()
        for ac in self.actuators.actuators:
            if ac.val_changed == True:
                ac.val_changed=False
                #self.com.report_actuator(ac)

    def get_odom_report(self):
        x, y, theta = self.nav.pos
        return [x,y,theta]

    def update_odom_report(self, dt):
        speed = m.PosCommand()
        odom_report = self.get_odom_report()
        speed.x = odom_report[0]
        speed.y = odom_report[0]
        speed.theta = odom_report[2]
        self.com.send("position", m.PosCommand, speed)
        
    def run(self):
        while self.com:
            self.update()
            self.com.process_com()
            time.sleep(0.01)
        # self.com.stop ()


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #    print("Usage: ./simu_robot.py robot_name")
    #    exit(-1)
    with Robot(EcalInterface("aaaa"), "aaaa") as robot:
        robot.run()
