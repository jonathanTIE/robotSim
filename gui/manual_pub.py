import ecal.core.core as ecal_core
from ecal.core.publisher import StringPublisher
from ecal.core.publisher import ProtoPublisher
from proto.game_actions_pb2 import get_us_readings_out

from time import sleep

if __name__ == "__main__":

    ecal_core.initialize([], "Manual Publisher for debug")

    pub = ProtoPublisher("get_us_readings") #, get_us_readings_out)    -- not included due to mismatch err msg in c++ code 
    readings = get_us_readings_out()
    readings.us1 = 10
    sleep(0.5)

    pub.send(readings)
    sleep(1.0)
    ecal_core.finalize()

