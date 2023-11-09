import ecal.core.core as ecal_core
from ecal.core.publisher import ProtoPublisher
import messages_pb2 as m
import time

# lua.eval('python.eval("sleep(1)")')
#remplace delay with ^^^^^^
ecal_core.initialize([""], "lua_interpreter")

set_position = ProtoPublisher("set_pose", m.Position)

while ecal_core.ok():
    set_position.send(m.Position(x=100, y=200, theta=0))

    time.sleep(0.5)

ecal_core.finalize()