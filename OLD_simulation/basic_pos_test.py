from time import sleep
import ecal.core.core as ecal_core
from ecal.core.publisher import ProtoPublisher
import messages_pb2 as m


if __name__ == "__main__":
    ecal_core.initialize(args=[], unit_name="pos_test")
    pos_pub = ProtoPublisher("position", m.Position)
    position = m.Position()
    position.x = 1300.0
    position.y = 1500.0
    position.theta = 1
    while ecal_core.ok():
        sleep(0.1)
        pos_pub.send(position)
        sleep(1.0)
    