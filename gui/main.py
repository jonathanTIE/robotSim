import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox


import ecal.core.core as ecal_core
from ecal.core.publisher import StringPublisher
from ecal.core.subscriber import ProtoSubscriber
from proto.game_actions_pb2 import get_pose_out

from time import sleep

#### CONSTANTS  #####
ROBOT_ANGLE_OFFSET = 0

def on_textbox_submit(text):
    print("submitted")
    lua_path_pub.send(text)

##### Matplotlib setup #####
fig, ax = plt.subplots()
ax.figure.subplots_adjust(bottom=0.11)
axbox = fig.add_axes([0.1, 0.01, 0.8, 0.05])
initial_text = "D:/Sync/Code/Robotique/CDR2024/robotSim/lua_scripts/main.lua"
text_box = TextBox(axbox, 'lua_input_path', initial=initial_text, textalignment='right')
axbox.annotate('PAS DE HOT RELOAD -> Restart runner)', xy=(0, 0.5), color='red') 

##### Matplotlib functions #####
def update_robot_plot(x: float, y:float, theta:float):
    ax.clear()
    ax.plot(x, y, marker=(3, 0, theta), markersize=10, linestyle='None')
    ax.set_xlim(    [0.0, 3000.0]    )
    ax.set_ylim(    [0.0, 2000.0]    )
    plt.draw()

##### eCAL functions #####
def on_pose(topic_name, msg: get_pose_out, time):
    update_robot_plot(msg.x, msg.y, msg.theta)

##### eCAL setup #####
ecal_core.initialize([], "robotsim_gui")
lua_path_pub = StringPublisher("lua_path_loader")
pose_sub = ProtoSubscriber("get_pose", get_pose_out)
sleep(0.5)


if __name__ == "__main__":
    ##### CB setup #####
    pose_sub.set_callback(on_pose)
    text_box.on_submit(on_textbox_submit)


    plt.show()

    while ecal_core.ok():
        sleep(1.0)
    ecal_core.finalize()