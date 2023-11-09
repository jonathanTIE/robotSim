import foxglove_schemas_protobuf.CircleAnnotation_pb2 as m
import simulation.__simu_robot as sim
import sys

#add path
sys.path.insert(0, "./simulation")
with sim.Robot(sim.EcalInterface("aaaa"), True) as robot:
        robot.run()
