"""
Serial to use in local, with another program in the same computer.
for debug/testing purpose with the simulator & a program in local (IHM, speed, PID,..
"""

from interface import Interface
import os, pty, serial

#https://stackoverflow.com/questions/2291772/virtual-serial-device-in-python
class local_serial(Interface):
    def __init__(self, robot_name="1"):
        Interface.__init__(self, robot_name)

    def start(self, *args):
        self.master, self.slave = pty.openpty()
        s_name = os.ttyname(self.slave)

        self.ser = serial.Serial(s_name)

    def send_msg(self, msg):
        self.ser.write(msg)

    def read_msg(self):
        os.read(self.master, 1000)

        """
        ParseFromString,
        result = parse_serial(input)
        if conformity_check(result, SPEED_REG):
            on_speed...
        elif conformirty_check(result, POS_REG):
            on_pos...
        
        
        SPEED_REG = "SpeedCmd {} (.+) (.+) (.+)"
POS_REG = "PosCmd {} (.+) (.+)"
POS_ORIENT_REG = "PosCmdOrient {} (.+) (.+) (.+)"
ACTUATOR_CMD = "ActuatorCmd {} (.+) (.+)"
ACTUATORS_REQUEST = "ActuatorsRequest {}"

ACTUATOR_DECL = "ActuatorDecl {} {} {} {} {} {} {}"
POS_REPORT = "PosReport {} {} {} {}"
ACTUATOR_REPORT = "ActuatorReport {} {} {}"

KILL_CMD = "Shutdown {}"
        """
