import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

import robot_sim_enac.interface
from robot_sim_enac.data_types import data_type, PositionOriented, StrMsg

# from interface import Interface
from random import randint


def get_ros_type(dataType):
    if dataType == PositionOriented:
        return Twist
    elif dataType == StrMsg:
        return String
    else:
        return NotImplementedError()


def convert_to_type_ros(to_convert):
    converted = None
    if type(to_convert) == PositionOriented:
        converted = Twist()
        converted.linear.x = to_convert.x
        converted.linear.y = to_convert.y
        converted.angular.z = to_convert.theta
    elif type(to_convert) == StrMsg:
        converted = String()
        converted.data = str(to_convert)
    else:
        print(to_convert)
        print(type(to_convert))
        raise NotImplementedError()
    return converted


def convert_to_data_type(to_convert):
    if type(to_convert) == Twist:
        return PositionOriented(to_convert.linear.x,
                                to_convert.linear.y,
                                to_convert.angular.z
                                )
    elif type(to_convert) == String:
        return StrMsg(to_convert)
    else:
        raise NotImplementedError()


class RosInterface(Node):  # , Interface): #Keep this order (Node then Interface) because super() need to init node

    # {data:fonction associée}

    def __init__(self, node_name="robotSim"):  # TODO : add args
        rclpy.init()  # (args=args)
        print("rclpy initiated in ros_interface !")
        super().__init__(node_name)

    def start(self, args=None):
        pass

    def process_com(self):
        rclpy.spin_once(self)

    def stop(self):
        self.destroy_node()
        rclpy.shutdown()

    def update_data_continuous(self, name: str, dataType: data_type, get_data_callback, rate: float):
        """

        :param name:
        :param dataType: string (should be an enum) that is used in publish_data
        :param get_data_callback: returned format should be the one corresponding to type_msg and must be parsable in publish_data
        :param rate: times per second
        :return:
        """
        ros_type = get_ros_type(dataType)
        publisher = self.create_publisher(ros_type, name,
                                          10)  # le 10 est arbitraire et fait référence à un "QoS setting", voir ici https://docs.ros2.org/foxy/api/rclpy/api/node.html#rclpy.node.Node.create_publisher
        for i in self.publishers:
            print(i.topic)

        callback_timer = lambda: self.publish_data(dataType, publisher, get_data_callback)
        self.create_timer(rate, callback_timer)

    def publish_data(self, dataType, publisher, get_data_callback):
        msg = convert_to_type_ros(get_data_callback())
        # self.get_logger().info('Publishing: "%s"' % msg.data)

        # self.get_logger().info('Publishing: twist data')

        publisher.publish(msg)

    def register_msg_callback(self, name: str, dataType:data_type, set_data_callback):
        """

        """
        ros_type = get_ros_type(dataType)

        def set_data(x):
            a = set_data_callback(convert_to_data_type(x))
            self.get_logger().info(str(x))
            self.get_logger().info(str(convert_to_data_type(x)))
            self.get_logger().info(str(type(set_data_callback)))
        #set_data = lambda x: set_data_callback(convert_to_data_type(x))#set_data_callback(type(x)(x))  # convert from rosType to data_type associated
        self.create_subscription(
            ros_type,
            name,
            set_data,
            10  # QOS chelou ?
        )
        self.get_logger().info('subscribing from robotSim : ' + name)

    def read_data(self, request, response):
        # execute request, and do response
        pass

    """
    Recevoir dans un action si on doit déclencher ou stopper ou changer le rate 
    d'un publisher
    """


def send_garbage_data():
    return randint(1, 10)


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = RosInterface()
    minimal_publisher.update_data_continuous("test_data", "string", send_garbage_data, 1)
    print(dir(minimal_publisher))
    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
