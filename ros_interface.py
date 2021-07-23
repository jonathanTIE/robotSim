import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


#from interface import Interface
from random import randint


class RosInterface(Node):#, Interface): #Keep this order (Node then Interface) because super() need to init node


    #{data:fonction associée}

    def __init__(self, node_name = "robotSim"):
        super().__init__(node_name)

    def start(self):
        pass

    def stop(self):
        self.destroy_node()
        rclpy.shutdown()


    def update_data_continuous(self, name : str, type_msg_str: str, get_data_callback, rate : float):
        """

        :param name:
        :param type_msg: string (should be an enum) that is used in publish_data
        :param get_data_callback: returned format should be the one corresponding to type_msg and must be parsable in publish_data
        :param rate:
        :return:
        """

        type_msg = None
        if type_msg_str == "string":
            type_msg = String
        elif type_msg_str == "position":
            type_msg = Twist
        else:
            raise NotImplementedError()

        publisher = self.create_publisher(type_msg, name, 10)        #le 10 est arbitraire et fait référence à un "QoS setting", voir ici https://docs.ros2.org/foxy/api/rclpy/api/node.html#rclpy.node.Node.create_publisher
        for i in self.publishers:
            print(i.topic)


        callback_timer = lambda: self.publish_data(type_msg, publisher, get_data_callback)
        self.create_timer(rate, callback_timer)

    def publish_data(self, type_msg, publisher, get_data_callback):
        msg = type_msg()
        if type_msg == String:
            msg.data = str(get_data_callback())
        elif type_msg == Twist:
            to_parse = get_data_callback()
            msg.linear.x = to_parse[0]
            msg.linear.y = to_parse[1]
            msg.angular.z = to_parse[2]
        else:
            raise NotImplementedError()

        publisher.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)

    def register_msg_cb(self, cb, msg_type):
        pass
        #self.[[DYNAMICNAME]] = self.create_subscription(
    # msg_type,
    # 'name_of_topic',
    #cb,
    # 10)

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