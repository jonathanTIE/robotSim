#!/usr/bin/python3

import messages_pb2 as m
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




class CommandParser:
    """
        take as input one of the command in the format above, and trigger the simulator or vice-versa
    """


    #region send
    #commands that return data

    def __init__(self, robot_name="1"):
        self.rid = robot_name
        self.cbs = {}


    def register_msg_cb(self, cb, msg_type):
        if msg_type not in self.cbs:
            self.cbs[msg_type] = []
        self.cbs[msg_type].append(cb)

    def read_msg(self, msg:bytes):
        parserMsgType = m.TopLevelMsg()
        parserMsgType.ParseFromString(msg)
        return getattr(parserMsgType, parserMsgType.WhichOneof('msg') ).value

    def send_msg(self, msg) -> bytes:
        top_msg = m.TopLevelMsg()
        if type(msg) == m.SpeedCommand:
            top_msg.speed.vx = msg.vx
            top_msg.speed.vy = msg.vy
            top_msg.speed.vtheta = msg.vtheta
        elif type(msg) == m.PosCommand:
            top_msg.pos.x = msg.x
            top_msg.pos.y = msg.y
            top_msg.pos.theta = msg.theta
        elif type(msg) == m.OdomReport:
            top_msg.odom.pos_x = msg.pos_x
            top_msg.odom.pos_y = msg.pos_y
            top_msg.odom.pos_theta = msg.pos_theta
        elif type(msg) == m.IHM:
            top_msg.ihm.tirette = msg.tirette
            top_msg.ihm.color = msg.color
        elif type(msg) == m.BuoyCatcher:
            top_msg.buoy.height  = msg.height
            top_msg.buoy.grab = msg.grab
        elif type(msg) == m.FlagServo:
            top_msg.servo.pos = msg.pos
        else:
            raise NotImplementedError("trying to send an unsupported protobuf message !")
        return top_msg.SerializeToString()



    def on_report_pos(self):
        ivymsg = POS_REPORT.format(self.rid, msg.pos_x, msg.pos_y, msg.pos_theta)
        pass

    def on_actuator_request(self, ac):
        return ACTUATOR_REPORT.format(self.rid, ac.name, ac.value)

    def on_invalid_msg(self):
        raise NotImplementedError("impossible to receive invalid message : need an interface !")

    def on_robot_description(self):
        #actuators :
        for ac in self.actuators.actuators:
            rights = "READ" if ac.rwtype == RWType.R else "RW"
            ivymsg = ACTUATOR_DECL.format(self.rid, ac.name, ac.min, ac.max, ac.step, rights, ac.unit)
            IvySendMsg(ivymsg)

    #endregion

    #region noReturn
    #commands that don't return data

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

    def on_pos_orient_cmd(self, sender, x, y, theta):
        pos = m.PosCommand()
        pos.x = float(x)
        pos.y = float(y)
        pos.theta = float(theta)
        for cb in self.cbs.get(m.PosCommand, []):
            cb(pos)

    def on_actuator_cmd(self, sender, name, value):
        for cb in self.cbs.get(Actuators, []):
            cb(name, value)

    def on_kill_cmd(self, *args):
        self.running = False

    # endregion

class Interface(CommandParser):
    """
        Abstract class that needs to be inherited with any "outside" connection/interface (Serial, Ivy,..)
        in order to communicate with the simulator
    """
    def __init__(self, robot_name):
        """

        :param robot_name: an unique identifier to use, in case of multiple simulators

        Attributes
            cbs : commands, function to execute when receiving a certain command
        """
        super(CommandParser, robot_name).__init__()

        #TODO : get actuators from simulator
        self.actuators = None

    
    def start(self, *args):
        raise NotImplementedError()
    
    def stop(self):
        raise NotImplementedError()

    def send_msg(self, msg):
        raise NotImplementedError()

    def read_msg(self):
        raise NotImplementedError()


