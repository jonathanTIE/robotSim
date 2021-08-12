import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from builtin_interfaces.msg import Time
from geometry_msgs.msg import Twist, Pose, Quaternion, TransformStamped, Transform
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from tf2_ros import TransformBroadcaster


import robot_sim_enac.interface
from robot_sim_enac.data_types import data_type, PositionOriented, Speed, PositionOrientedTimed, StrMsg

# from interface import Interface
from random import randint
import numpy as np

def euler_to_quaternion(yaw, pitch, roll) -> Quaternion:
    """
    Re-implementation stolen from https://stackoverflow.com/questions/53033620/how-to-convert-euler-angles-to-quaternions-and-get-the-same-euler-angles-back-fr
    couldn't find tf2.transformations to do it using ros2 libraries...
    :param yaw:
    :param pitch:
    :param roll:
    :return:
    """
    quat = Quaternion()
    quat.x = np.sin(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) - np.cos(roll / 2) * np.sin(pitch / 2) * np.sin(yaw / 2)
    quat.y = np.cos(roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2)
    quat.z = np.cos(roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2) - np.sin(roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2)
    quat.w = np.cos(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.sin(pitch / 2) * np.sin(yaw / 2)

    return quat

def speed_to_twist(speed : Speed):
    converted = Twist()
    converted.linear.x = float(speed.vx) / 1000
    converted.angular.z = float(speed.vz)
    return converted

def posoriented_to_pose(posOriented : PositionOriented):
    converted = Pose()
    converted.position.x = float(posOriented.x) / 1000
    converted.position.y = float(posOriented.y) / 1000
    converted.orientation = euler_to_quaternion(posOriented.theta, 0, 0)
    return converted

def posoriented_to_tf(posOriented : PositionOriented):
    tf = Transform()
    tf.translation.x = float(posOriented.x) / 1000
    tf.translation.y = float(posOriented.y) / 1000
    tf.rotation = euler_to_quaternion(posOriented.theta, 0, 0)
    return tf

def get_ros_type(dataType):
    if dataType == PositionOrientedTimed: #PositionOrientedTimed inherit from PositionOriented, so PosOrienTimed must be placed before
        return Odometry
    elif dataType == PositionOriented:
        return TFMessage
    elif dataType == Speed:
        return Twist
    elif dataType == StrMsg:
        return String
    else:
        return NotImplementedError()



def convert_to_data_type(to_convert):
    if type(to_convert) == Twist:
        return Speed(
            to_convert.linear.x * 1000,
            to_convert.angular.z
        )
    elif type(to_convert) == TFMessage:
        raise NotImplementedError("check rotation is it correct")
        return PositionOriented(
            to_convert.translation.x * 1000,
            to_convert.translation.y * 1000,
            to_convert.rotation.z
        )
    elif type(to_convert) == Odometry:
        raise NotImplementedError()
        return PositionOrientedTimed(
            to_convert.position.x * 1000,
            to_convert.position.y * 1000,
            to_convert.orientation.z, #TODO : ça ne marchera pas, il faut convertir de quaternion vers radian
            to_convert.linear.x * 1000,
            to_convert.angular.z, #IDEM ORIENTATION
            to_convert.stamp
        )
    elif type(to_convert) == String:
        return StrMsg(to_convert)
    else:
        raise NotImplementedError()


class RosInterface(Node):  # , Interface): #Keep this order (Node then Interface) because super() need to init node
    """
        manage a node, which can broadcast/receive many data
        converting data_type to ros2 equivalent types and passing the required additionnal datas(timestamp for example)
        Manage also tf2 broadcast (broadcast is a little different that the other ones)
    """

    def __init__(self, node_name="robotSim"):  # TODO : add args
        rclpy.init()  # (args=args)
        print("rclpy initiated in ros_interface !")
        super().__init__(node_name)
        self.tfBroadcaster = TransformBroadcaster(self)

    def start(self, args=None):
        pass

    def process_com(self):
        rclpy.spin_once(self)

    def stop(self):
        self.destroy_node()
        rclpy.shutdown()

    def convert_to_type_ros(self, to_convert): #present in this class to allow timestamp
        """
        for PositionOrientedTimed / Odometry msg, it change the timestamp to current timestamp from node
        Also convert mm from data_type to meter
        :param to_convert: must inherit data_type
        :return:
        """
        converted = None

        if type(to_convert) == PositionOrientedTimed:  # PositionOrientedTimed inherit from PositionOriented, so PosOrienTimed must be placed before
            converted = Odometry()
            #Les données de la base roulante (base_link) sont faites relativements à l'origine de "odom"
            converted.header.frame_id = "map"
            converted.child_frame_id = "odom"
            converted.header.stamp = self.get_clock().now().to_msg()
            converted.twist.twist = speed_to_twist(to_convert)
            converted.pose.pose = posoriented_to_pose(to_convert)

        elif type(to_convert) == PositionOriented: #sending a TFMessage (Transform Message)
            #from https://answers.ros.org/question/350839/publish-tf-in-data-ros2-dashing-with-python/
            converted = TFMessage()
            tf_msg = TransformStamped()
            tf_msg.header.stamp = self.get_clock().now().to_msg()
            tf_msg.header.frame_id = "map"
            tf_msg.child_frame_id = "odom"
            tf_msg.transform = posoriented_to_tf(to_convert)
            converted.transforms = [tf_msg]

        elif type(to_convert) == Speed:
            converted = speed_to_twist(to_convert)
        elif type(to_convert) == StrMsg:
            converted = String()
            converted.data = str(to_convert)
    
        else:
            print(to_convert)
            print(type(to_convert))
            raise NotImplementedError()

        return converted

    def update_data_continuous(self, name: str, dataType: data_type, get_data_callback, rate: float):
        """

        :param name:
        :param dataType: string (should be an enum) that is used in publish_data
        :param get_data_callback: returned format should be the one corresponding to type_msg and must be parsable in publish_data
        :param rate: times per second
        :return:
        """
        ros_type = get_ros_type(dataType)
        #if ros_type != TFMessage:
        publisher = self.create_publisher(ros_type, name, 10)  # le 10 est arbitraire et fait référence à un "QoS setting", voir ici https://docs.ros2.org/foxy/api/rclpy/api/node.html#rclpy.node.Node.create_publisher
        #else:
            #publisher = self.tfBroadcaster
        for i in self.publishers:
            print(i.topic)

        callback_timer = lambda: self.publish_data(dataType, publisher, get_data_callback)
        self.create_timer(rate, callback_timer)

    def publish_data(self, dataType, publisher, get_data_callback):
        msg = self.convert_to_type_ros(get_data_callback())
        """
        if type(msg) == TFMessage:
            print(msg)
            for x in msg.transforms:
                print(type(x))
            publisher.sendTransform(msg)
        else:
        """
        publisher.publish(msg)
        # self.get_logger().info('Publishing: "%s"' % msg.data)
        # self.get_logger().info('Publishing: twist data')


    def register_msg_callback(self, name: str, dataType:data_type, set_data_callback):
        """

        :param name:
        :param dataType:
        :param set_data_callback: parameters of this function callback must be the same as the one used to instantiate the dataType
        :return:
        """
        ros_type = get_ros_type(dataType)

        def set_data(x):
            a = set_data_callback(convert_to_data_type(x))
            self.get_logger().info(str(x))
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
