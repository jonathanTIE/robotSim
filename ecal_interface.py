#!/usr/bin/python3
from interface import Interface
import messages_pb2 as m
# from actuators import Actuators, RWType

from time import time
from ecal.core import core as ecal_core
from ecal.core.publisher import ProtoPublisher
from ecal.core.subscriber import ProtoSubscriber
from functools import partial


class EcalInterface(Interface):

    def __init__(self, robot_name, actuators=None):
        Interface.__init__(self, robot_name)
        # Contains (protoPublisher, get_data_callback, rate)
        self.publishers = {}
        self.running = True

    def start(self, *args):
        ecal_core.initialize(list(args), self.robot_name)
        # Actuator : self.pub = ProtoPublisher(
        self.speed_pub = ProtoPublisher('speed', m.SpeedCommand)
        self.speed_cmd = ProtoSubscriber('speed_cmd', m.SpeedCommand)
        self.pos_cmd = ProtoSubscriber('position_cmd', m.PosCommand)
        self.time = time()
        # self.rid = robot_name
        # self.actuators = actuators
        # self.bus = bus
        # self.running = True
        # IvyBindMsg(self.on_speed_cmd,      SPEED_REG.format(self.rid))
        # IvyBindMsg(self.on_pos_cmd,        POS_REG.format(self.rid))
        # IvyBindMsg(self.on_pos_orient_cmd, POS_ORIENT_REG.format(self.rid))
        # IvyBindMsg(self.on_actuator_cmd,   ACTUATOR_CMD.format(self.rid))
        # IvyBindMsg(lambda *args: self.declare_actuators(),   ACTUATORS_REQUEST.format(self.rid))
        # IvyBindMsg(self.on_kill_cmd, KILL_CMD.format (self.rid))

    def process_com(self):
        pass

    def stop(self):
        ecal_core.finalize()

    def send(self, topic:str, type, msg):
        if topic not in self.publishers: 
            self.publishers[topic] = ProtoPublisher(topic, type)
        print(topic, type,msg)
        self.publishers[topic].send(msg)

    def register_msg_callback(self, service_name, callback):
        """
        Function to call preferably when initialising the simulator,
        a callback function from the simulator is called with the arguments provided from the interface depending on the msg type
        exemple : update_speed, SpeedCmd
        :param callback:
        :param service_type:
        :return:
        """
        if service_name == "speed_cmd":
            def nav_speed_callack(topic_name, msg, time):
                callback((msg.vx, msg.vy, msg.vtheta))
            self.speed_cmd.set_callback(nav_speed_callack)
        elif service_name == "position_cmd":
            self.pos_cmd.set_callback(callback)
        else:
            raise NotImplementedError()
