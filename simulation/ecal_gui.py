#hijack image panel from foxglove to display map of game + robot on it + obstacles + graphs

from foxglove_schemas_protobuf import ImageAnnotations_pb2 as img_pb
from foxglove_schemas_protobuf import CircleAnnotation_pb2 as circle_pb
from foxglove_schemas_protobuf import TextAnnotation_pb2 as text_pb
from foxglove_schemas_protobuf import PointsAnnotation_pb2 as pts_pb
from foxglove_schemas_protobuf import Point2_pb2 as pt_pb
from foxglove_schemas_protobuf import CompressedImage_pb2 as comp_img_pb
from foxglove_schemas_protobuf import Color_pb2 as color_pb

import google.protobuf.timestamp_pb2 as timestamp_pb2

from messages_pb2 import Position


from ecal.core import core as ecal_core
from ecal.core.publisher import ProtoPublisher
from ecal.core.subscriber import ProtoSubscriber
from math import cos, sin

import time
map_img_file = "C:\\Users\\Jonathan\\Documents\\robotSim\\simulation\\Picture1.png"#vinyle_table_2024_FINAL_V1.png"

class NodePlotter():
    def __init__(self, fixed_txt_pos, color, scale=0.3, heading=False):
        self.fixed_txt_pos = fixed_txt_pos
        self.color = color
        self.half_transp_color = color_pb.Color(r=color.r, g=color.g, b=color.b, a=100)
        self.scale = scale

    def gen_dyn_txt(self, obj_pos, stamp):
        return text_pb.TextAnnotation(timestamp=timestamp_pb2.Timestamp(seconds=int(stamp/1000000)),
            position=pt_pb.Point2(x=obj_pos[0] * self.scale, y=(obj_pos[1] * self.scale)-20),
            text=f"{obj_pos[0]} {obj_pos[1]}",
            font_size=10.0,
            text_color=self.color,
            background_color=color_pb.Color(r=0, g=0, b=0, a=100)
            )
    def gen_circle(self, obj_pos, stamp):
        return circle_pb.CircleAnnotation(
            timestamp=timestamp_pb2.Timestamp(seconds=int(stamp/1000000)),
            position=pt_pb.Point2(x=obj_pos[0] * self.scale, y=obj_pos[1] * self.scale),
            thickness=1,
            diameter=50,
            fill_color=self.half_transp_color,
            outline_color=self.color,
            )

    def gen_fix_txt(self, obj_pos, stamp):
        return text_pb.TextAnnotation(timestamp=timestamp_pb2.Timestamp(seconds=int(stamp/1000000)),
            position=pt_pb.Point2(x=self.fixed_txt_pos[0] * self.scale, y=self.fixed_txt_pos[1] * self.scale),
            text=f"{obj_pos[0]} {obj_pos[1]}",
            font_size=21.0,
            text_color=self.color,
            background_color=color_pb.Color(r=0, g=0, b=0, a=255)
            )
    
    def gen_heading(self, obj_pos, stamp):
        x_draw = (obj_pos[0]+50*cos(obj_pos[2])) * self.scale
        y_draw = (obj_pos[1]+50*sin(obj_pos[2])) * self.scale
        return circle_pb.CircleAnnotation(
            timestamp=timestamp_pb2.Timestamp(seconds=int(stamp/1000000)),
            position=pt_pb.Point2(x=x_draw, y=y_draw),
            thickness=1,
            diameter=10,
            fill_color=color_pb.Color(r=128, g=128, b=128, a=255),
        )

class Display():
    def __init__(self, scale = 0.3):
        ecal_core.initialize([""], "display")
        self.img_pub = ProtoPublisher("map", comp_img_pb.CompressedImage)
        self.draw_robot_pub = ProtoPublisher("draw_robot", img_pb.ImageAnnotations)

        self.pos = ProtoSubscriber("get_pose", Position)
        self.pos.set_callback(self.draw_robot)

        self.robot_plotter = NodePlotter([0,0], color_pb.Color(r=0, g=0, b=255, a=255))
        self.scale = scale #pixels per millimeter

    def send_map_pic(self):
        with open(map_img_file, "rb") as f:
            map_img = f.read()
            msg = comp_img_pb.CompressedImage()
            msg.data = map_img
            msg.format = "png"
            self.img_pub.send(msg)
            print("sent map img")

    def draw_robot(self, topic_name, msg_call, time): #CB to Position
        robot_pos = [msg_call.x, msg_call.y, msg_call.theta]
        circle = self.robot_plotter.gen_circle(robot_pos, time)
        mobile_txt = self.robot_plotter.gen_dyn_txt(robot_pos, time)
        fixed_txt = self.robot_plotter.gen_fix_txt(robot_pos, time)
        heading = self.robot_plotter.gen_heading(robot_pos, time)
        msg = img_pb.ImageAnnotations(
            circles = [circle, heading],
            texts = [mobile_txt, fixed_txt]
        )

        self.draw_robot_pub.send(msg)

    def draw_obstacles(self, topic_name, msg_call, time):
        pass

    def draw_path(self, topic_name, msg_call, time):
        pass




d = Display()
time.sleep(1)
d.send_map_pic()
while ecal_core.ok():
    time.sleep(0.5)

ecal_core.finalize()



"""
        cam_cal = cam_calib_pb2.CameraCalibration(
            timestamp=timestamp_pb2.Timestamp(seconds=(int(time.time()))),
            frame_id="",
            width=3000,
            height=2000,
            #distortion_model="plumb_bob",
            #D=[0.0, 0.0, 0.0, 
            #    0.0, 0.0, 0.0, 
            #    0.0, 0.0, 1.0],
            P=[1.0, 0.000000, 0.0, 0.000000,
                0.000000, 1.0, 0.0, 0.000000,
                0.000000, 0.000000, 1.000000, 0.000000]

        )
        self.cal_pub.send(cam_cal)
        
        msg_pt_cloud = pt_cloud_pb.PointCloud(
            timestamp=timestamp_pb2.Timestamp(seconds=time),
            frame_id="",
            pose=pose_pb.Pose(
                position=vec3_pb.Vector3(x=0.0, y=0.0, z=0.0), 
                orientation=quat_pb.Quaternion(x=0.0, y=0.0, z=0.0, w=0.0)),
            point_stride=4+4,
            fields= [packed_pb.PackedElementField(name='x', offset=0, type=packed_pb.PackedElementField.NumericType.INT16),
                    packed_pb.PackedElementField(name='y', offset=4, type=packed_pb.PackedElementField.NumericType.INT16),
            ],
            data=(1).to_bytes(4, byteorder='big')+(1).to_bytes(4, byteorder='big'),
        )

        self.pt_cloud_pub.send(msg_pt_cloud)
"""