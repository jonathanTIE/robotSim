#!/usr/bin/python3

class Interface:
    
    def __init__(self):
        self.cbs = {}

    def register_msg_cb(self, cb, msg_type):
        if msg_type not in self.cbs:
            self.cbs[msg_type] = []
        self.cbs[msg_type].append(cb)
    
    def start(self, *args):
        raise NotImplementedError()
    
    def stop(self):
        raise NotImplementedError()

