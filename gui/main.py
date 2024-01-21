import PySimpleGUI as sg
import graph

import ecal.core.core as ecal_core
from ecal.core.publisher import StringPublisher
from ecal.core.subscriber import ProtoSubscriber
from proto.game_actions_pb2 import get_pose_out

#INCHES_SIZE_PLOT = (4, 2) # TODO : make it settable easily
MATPLOTLIB_SIZE = (750, 500)

#TODO - UNIMPLEMENTED OFFSET 
ROBOT_ANGLE_OFFSET = 0

### setup ECAL ####
ecal_core.initialize([], "robotsim_gui")
lua_path_pub = StringPublisher("lua_path_loader")
pose_sub = ProtoSubscriber("get_pose", get_pose_out)

def on_pose(topic_name, msg: get_pose_out, time):
    graph.update_robot_plot(msg.x, msg.y, msg.theta)

pose_sub.set_callback(on_pose)

### GUI SETUP ###
sg.theme('DarkGrey2')

textbox = sg.Input(default_text="D:/Sync/Code/Robotique/CDR2024/robotSim/lua_scripts/main.lua",
                   size = (100, 20),
                   key='lua_path_input',)
layout = [[],
        [sg.Canvas(size=MATPLOTLIB_SIZE, key='-CANVAS-')],
        [textbox, sg.Button('set_lua', key='TESTER')]]

window = sg.Window('RobotSim - E.S.C.Ro.C.S 2024', layout, resizable=True, finalize=True, element_justification='center')

#graph.fig.set_size_inches(INCHES_SIZE_PLOT[0], INCHES_SIZE_PLOT[1])
graph.draw_figure(window['-CANVAS-'].TKCanvas)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == "TESTER":
        lua_path_pub.send(values['lua_path_input'])

window.close()