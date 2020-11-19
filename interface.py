#!/usr/bin/python3

class Interface:
    
    def __init__(self):
        self.speed_cb = []
        self.pos_cb = []
    
    def register_speed_cb(self, cb):
        self.speed_cb.append(cb)

    def register_pos_cb(self, cb):
        self.pos_cb.append(cb)
    
    def send_pos_report(self, pos):
        raise NotImplementedError()
    
    def start(self, *args):
        raise NotImplementedError()
    
    def stop(self):
        raise NotImplementedError()

