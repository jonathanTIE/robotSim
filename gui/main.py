import ecal.core.core as ecal_core
from ecal.core.publisher import StringPublisher

from time import sleep

if __name__ == "__main__":
    ecal_core.initialize([], "robotsim_gui")
    publisher = StringPublisher("lua_path_loader")
    sleep(1.0)
    publisher.send("D:/Sync/Code/Robotique/CDR2024/robotSim/lua_scripts/main.lua")
    while ecal_core.ok():
        sleep(1.0)
    ecal_core.finalize()