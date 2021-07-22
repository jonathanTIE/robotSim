import rclpy
from rclpy.node import Node


class RosInterface(Node):

    #[[nameOfData, get_data_callback, rate], ...]
    #{data:fonction associée}
    def __init__(self, node_name = "robotSim"):
        super().__init__(node_name)

    def update_speed_reading_rate(self, rate = 0): #if 0 : stop publishing
        self.publisher_speed = self.create_publisher(type, 'speed_reading', 10) #le 10 est arbitraire et fait référence à un "QoS setting", voir ici https://docs.ros2.org/foxy/api/rclpy/api/node.html#rclpy.node.Node.create_publisher
        self.speedTimer = self.create_timer(rate, self.publish_speed_reading)

    def publish_speed_reading(self):
        self.publisher_speed.publish(data)



    """
    Recevoir dans un action si on doit déclencher ou stopper ou changer le rate 
    d'un publisher
    """