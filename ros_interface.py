import rclpy
from rclpy.node import Node


class RosInterface(Node):

    #[[nameOfData, get_data_callback, rate], ...]
    #{data:fonction associée}
    def __init__(self, node_name = "robotSim"):
        super().__init__(node_name)

    def update_data_continuous(self, name, type, get_data_callback, rate):
        self.publisher_speed = self.create_publisher(type, name, 10) #le 10 est arbitraire et fait référence à un "QoS setting", voir ici https://docs.ros2.org/foxy/api/rclpy/api/node.html#rclpy.node.Node.create_publisher
        self.speedTimer = self.create_timer(rate, self.get_data_callback)

    def publish_data(self, get_data_callback):
        self.publisher_speed.publish(get_data_callback())

    def register_msg_cb(self, cb, msg_type):
        #self.[[DYNAMICNAME]] = self.create_subscription(
    # msg_type,
    # 'name_of_topic',
    #cb,
    # 10)

    """
    Recevoir dans un action si on doit déclencher ou stopper ou changer le rate 
    d'un publisher
    """