#!/usr/bin/python3
import time
from math import cos, sin, atan2, sqrt, pi
from enum import Enum

def normalize_angle(angle):
    """_summary_

    Args:
        angle (_type_): _description_

    Returns:
        _type_: _description_
    """
    a = angle
    while a >= pi:
        a -= 2*pi
    while a < -pi:
        a += 2*pi
    return a


class Navigation:
    """Manage Differential robot drive navigation
    """

    class NavMode(Enum):
        SPEED = 0
        POSITION = 1
    
    class PosControlState(Enum):
        INITIAL_TURN = 0
        CRUISE = 1
        FINAL_TURN = 2
        STATIONNARY = 3
    
    def __init__(self, pos_init, max_linear_speed = 200.0, max_angular_speed = 200.0):
        self.pos = pos_init
        self.pos_obj = (0, 0, None)
        self.speed = (0, 0, 0)
        self.max_lin_speed = max_linear_speed
        self.max_ang_speed = max_angular_speed
        self.mode = Navigation.NavMode.SPEED
        self.pos_control_state = Navigation.PosControlState.INITIAL_TURN
        self.last_distance_to_obj = 0
    
    def set_speed(self, speed: tuple[float, float, float]):
        print("setting speed")
        self.speed = speed
        self.mode = Navigation.NavMode.SPEED
    
    def set_pos_objective(self, pos: tuple[float, float, float]):
        self.pos_obj = pos
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
            vtheta = 0.8 #rad/s
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

class Forward(float, Enum): 
    LEFT = pi/3,
    BOTTOM = pi, 
    RIGHT = (5/3) * pi

class HolonomicNavigation(Navigation):
    """Inherit navigation and overwrite the functions needed to adapt to an holonomic drive robot

    Args:
        Navigation (_type_): _description_
    """
    #Source : https://joshi-bharat.github.io/blog/2016/kinematic-analysis-of-holonomic-robot/


    def __init__(self, pos_init, length_wheel_center=150.0):
        """_summary_

        Args:
            length_wheel_center (float, optional): In milimeters. Defaults to 150.
        """
        Navigation.__init__(self, pos_init)
        self.L = length_wheel_center
        self.theta_offset = pi/6 #(angle from normal heading to 'right' heading)
        self.forward = Forward.LEFT  # Holonomic side use when needing to go "forward"

    @staticmethod
    def get_closest_forward(cur_angle: float, target_angle: float)->Forward:
        #calculate the angle of the vector of each orientation of the holonomic triangular robot
        world_angle_left = normalize_angle(pi/3 + cur_angle)
        world_angle_bottom = normalize_angle(pi + cur_angle)
        world_angle_right = normalize_angle((5/3) * pi + cur_angle)

        #calculate difference between these vectors and the target angle
        diff_left = abs(target_angle - world_angle_left)
        diff_bottom = abs(target_angle - world_angle_bottom)
        diff_right = abs(target_angle - world_angle_right)

        #Return the closest holonomic orientation to go forward to the targeted angle
        if diff_left < diff_bottom and diff_right < diff_right:
            return Forward.LEFT
        elif diff_bottom < diff_right:
            return Forward.BOTTOM
        else: 
            return Forward.RIGHT
    
    def update_pos_control(self):
        if self.pos_control_state == Navigation.PosControlState.STATIONNARY:
            return

        x, y, theta = self.pos
        x_obj, y_obj, theta_obj = self.pos_obj
        route = atan2(y_obj - y, x_obj - x) - self.theta_offset

        #determine angle (and one of the three orientation) to get to position
        if self.pos_control_state == Navigation.PosControlState.FINAL_TURN and theta_obj is not None:
            theta_diff = theta_obj - theta
        else: # self.pos_control_state == Navigation.PosControlState.INITIAL_TURN:
            theta_diff = route - theta

        theta_diff = normalize_angle(theta_diff)
        distance = sqrt((x_obj - x)**2 + (y_obj - y)**2)
        
        #determine angular speed direction    
        vtheta = 0
        if theta_diff > 0.02:
            if theta_diff > 0.2:
                vtheta = self.max_ang_speed
            else:
                vtheta = self.max_ang_speed/3
        elif theta_diff < -0.02:
            if theta_diff < -0.2:
                vtheta = -self.max_ang_speed
            else:
                vtheta = -self.max_ang_speed/3

        
        #either turn to the route, go forward in the current orientation, or turn to final angle
        if(self.pos_control_state == Navigation.PosControlState.INITIAL_TURN):
            self.speed = (vtheta, vtheta, vtheta)
            if abs(theta_diff) < 0.02:
                self.pos_control_state = Navigation.PosControlState.CRUISE
                self.last_distance_to_obj = distance
        if(self.pos_control_state == Navigation.PosControlState.CRUISE):
            if(distance > self.last_distance_to_obj or distance < 20):
                self.speed = (0, 0, 0)
                self.pos_control_state = Navigation.PosControlState.FINAL_TURN
            else:
                offset = 0.0
                if abs(theta_diff) > 0.02: #trajectory correction
                    offset = 50.0
                self.speed = (-self.max_lin_speed + offset, 0, self.max_lin_speed)
                self.last_distance_to_obj = distance
        if self.pos_control_state == Navigation.PosControlState.FINAL_TURN:
            if theta_obj is None or abs(theta_diff) < 0.05 or abs(theta_diff) > 3.09:
                self.speed = (0, 0, 0)
                self.pos_control_state = Navigation.PosControlState.STATIONNARY
                self.mode = Navigation.NavMode.SPEED
            else:
                self.speed = (vtheta, vtheta, vtheta)

        pass
    

    #https://joshi-bharat.github.io/blog/2016/kinematic-analysis-of-holonomic-robot/
    def update_speed_control(self, dt):
        # destructuring position ans speed tuples
        x, y, theta = self.pos
        v_wheel1, v_wheel2, v_wheel3 = self.speed
        
        vtheta = (1/(3*self.L))*(v_wheel1 + v_wheel2 + v_wheel3)
        # take the average angle of the robot during the last period
        theta_pos_avr = theta + vtheta * dt/2 # TODO : test
        
        # convert speed from robot reference system to table reference system
        vx0 = (-2/3)*cos(theta_pos_avr) * v_wheel1 \
            + (2/3)*cos(pi/3 - theta_pos_avr) * v_wheel2 \
            + (2/3)*cos(pi/3 + theta_pos_avr) * v_wheel3
        vy0 = (-2/3)*sin(theta_pos_avr) * v_wheel1 \
            + (-2/3)*sin(pi/3 - theta_pos_avr) * v_wheel2 \
            + (2/3)*sin(pi/3+theta_pos_avr) * v_wheel3

        # update position
        x += vx0*dt
        y += vy0*dt
        theta += vtheta*dt
        self.pos = (x, y, normalize_angle(theta))

        
    def update(self, dt):
        if self.mode == Navigation.NavMode.POSITION:
            self.update_pos_control()

        self.update_speed_control(dt)

if __name__ == "__main__":
    holo = HolonomicNavigation((1500, 1000, 0.0))
    holo.set_pos_objective((100, 200, 0.0))
    while True:
        holo.update(0.01)
        time.sleep(0.01)