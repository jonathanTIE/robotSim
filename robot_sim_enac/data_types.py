class data_type():
    def __init__(self):
       pass
    def get_interface_type(self):
        raise NotImplementedError()

class PositionOriented(data_type):
    def __init__(self, x, y, theta):
        super().__init__()
        self.x = x
        self.y = y
        self.theta = theta
    pass

class StrMsg(data_type):
    pass