#!/usr/bin/python3

from actuators import Actuators, RWType

SPEED_REG = "SpeedCmd {} (.+) (.+) (.+)"
POS_REG = "PosCmd {} (.+) (.+)"
POS_ORIENT_REG = "PosCmdOrient {} (.+) (.+) (.+)"
ACTUATOR_CMD = "ActuatorCmd {} (.+) (.+)"
ACTUATORS_REQUEST = "ActuatorsRequest {}"

ACTUATOR_DECL = "ActuatorDecl {} {} {} {} {} {} {}"
POS_REPORT = "PosReport {} {} {} {}"
ACTUATOR_REPORT = "ActuatorReport {} {} {}"

KILL_CMD = "Shutdown {}"


class Interface():
    """
        Abstract class that needs to be inherited with any "outside" connection/interface (Serial, Ivy,..)
        in order to communicate with the simulator
    """
    def __init__(self, robot_name):
        self.robot_name = robot_name
        pass

    
    def start(self, *args):
        raise NotImplementedError()

    def process_com(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def send(self, topic, type, msg): 
        raise NotImplementedError()
        
    def register_msg_callback(self, topic_name, callback):
        """
        Function to call preferably when initialising the simulator,
        a callback function from the simulator is called with the arguments provided from the interface depending on the msg type
        exemple : update_speed, SpeedCmd
        :param topic_name:
        :param callback:
        :return:
        """
        raise NotImplementedError()


