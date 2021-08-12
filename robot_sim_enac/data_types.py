#A importer : PositionOriented, StrMsg
import numpy as np



class data_type():
    def __init__(self):
       pass
    def get_interface_type(self):
        raise NotImplementedError()

class PositionOriented(data_type):
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta
    pass

class Speed(data_type):
    def __init__(self, vx, vz):
        self.vx = vx
        self.vz = vz

class PositionOrientedTimed(PositionOriented, Speed):
    """
    Unit in mm, ROS in m, theta in radian, stamp in ?? (not used inside the sim, only for ros, so unit not defined)
    """
    def __init__(self, x, y, theta, vx, vz, stamp): #vx -> speed in x axis,  stamp -> timestamp
        PositionOriented.__init__(self, x, y, theta)
        Speed.__init__(self, vx, vz)
        self.stamp = stamp

#WARNING : StrMsg doesn't have an init and can't be used
class StrMsg(data_type):
    """
    !! don't use without an init, it's useless !!
    """
    pass