#!/usr/bin/python3
import time
from math import cos, sin, atan2, sqrt, pi
from enum import Enum
from robot_sim_enac.data_types import PositionOriented, Speed



def normalize_angle(angle):
    a = angle
    while a >= pi:
        a -= 2*pi
    while a < -pi:
        a += 2*pi
    return a


class Navigation:

    class NavMode(Enum):
        SPEED = 0
        POSITION = 1
    
    class PosControlState(Enum):
        INITIAL_TURN = 0
        CRUISE = 1
        FINAL_TURN = 2
    
    def __init__(self, pos_init):
        self.pos = pos_init
        self.pos_obj = (0, 0, None)
        self.speed = (0, 0, 0)
        self.mode = Navigation.NavMode.SPEED
        self.pos_control_state = Navigation.PosControlState.INITIAL_TURN
        self.last_distance_to_obj = 0
    
    def set_speed(self, speed: Speed):
        self.speed = (speed.vx, 0, speed.vz)
        self.mode = Navigation.NavMode.SPEED
    
    def set_pos_objective(self, pos: PositionOriented):

        self.pos_obj = (pos.x, pos.y, None)
        self.mode = Navigation.NavMode.POSITION
        self.pos_control_state = Navigation.PosControlState.INITIAL_TURN
    
    def update_pos_control(self):
        x, y, theta = self.pos
        x_obj, y_obj, theta_obj = self.pos_obj
        route = atan2(y_obj - y, x_obj - x)
        
        if self.pos_control_state == Navigation.PosControlState.FINAL_TURN and theta_obj is not None:
            theta_diff = theta_obj - theta
        else:
            theta_diff = route - theta
        
        #theta_diff = (theta_diff + 180) % 360 - 180
        theta_diff = normalize_angle(theta_diff)
        distance = sqrt((x_obj - x)**2 + (y_obj - y)**2)
        
        vtheta = 0
        if theta_diff > 0.1:
            vtheta = 0.8
        elif theta_diff < -0.1:
            vtheta = -0.8
        
        if(self.pos_control_state == Navigation.PosControlState.INITIAL_TURN):
            self.speed = (0, 0, vtheta)
            if abs(theta_diff) < 0.1:
                self.pos_control_state = Navigation.PosControlState.CRUISE
                self.last_distance_to_obj = distance

        if(self.pos_control_state == Navigation.PosControlState.CRUISE):
            if(distance > self.last_distance_to_obj):
                self.speed = (0, 0, 0)
                self.pos_control_state = Navigation.PosControlState.FINAL_TURN
            else:
                self.speed = (300, 0, vtheta)
                self.last_distance_to_obj = distance
        if self.pos_control_state == Navigation.PosControlState.FINAL_TURN:
            if theta_obj is None or abs(theta_diff) < 0.1:
                self.speed = (0, 0, 0)
                self.pos_control_state = Navigation.PosControlState.INITIAL_TURN
                self.mode = Navigation.NavMode.SPEED
            else:
                self.speed = (0, 0, vtheta)
    
    def update_speed_control(self, dt):
        # destructuring position ans speed tuples
        x, y, theta = self.pos
        vxr, vyr, vtheta = self.speed
        
        # take the average angle of the robot during the last period
        theta_avr = theta + vtheta*dt/2
        
        # convert speed from robot reference system to table reference system
        vx0 = cos(theta_avr) * vxr - sin(theta_avr) * vyr
        vy0 = sin(theta_avr) * vxr + cos(theta_avr) * vyr
        
        # update position
        x += vx0*dt
        y += vy0*dt
        theta += vtheta*dt
        self.pos = (x, y, normalize_angle(theta))

    def update(self, dt):
        if self.mode == Navigation.NavMode.POSITION:
            self.update_pos_control()

        self.update_speed_control(dt)

