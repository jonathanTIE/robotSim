import ecal.core.core as ecal_core
from ecal.core.subscriber import ProtoSubscriber
import messages_pb2 as m

import numpy as np
import matplotlib.pyplot as plt
from time import sleep
from math import cos, sin


fig, ax = plt.subplots()
plt.ylim(0, 2000)
plt.xlim(0, 3000)
vectors_plot = None

#source : https://pythonforundergradengineers.com/quiver-plot-with-matplotlib-and-jupyter-notebooks.html
def on_pos_update(new_pos: m.PosCommand):
    x, y, theta = new_pos.x, new_pos.y, new_pos.theta
    x_origin = np.array([x, x, x])
    y_origin = np.array([y, y, y])

    #rotating angles if needed
    x_top = -1 * sin(theta)
    y_top = 1 * cos(theta)
    x_bottom_left = -1 * cos(theta) + 1 * sin(theta)
    y_bottom_left = -1 * sin(theta) - 1 * cos(theta)
    x_bottom_right = 1 * cos(theta) + 1 * sin(theta)
    y_bottom_right = 1 * sin(theta) - 1 * cos(theta)
    x_direct = np.array([x_top, x_bottom_left, x_bottom_right])
    y_direct = np.array([y_top, y_bottom_left, y_bottom_right])

    #real-time updating vectors
    global vectors_plot
    if vectors_plot is not None:
        vectors_plot.remove()
    vectors_plot = ax.quiver(
        x_origin, y_origin, x_direct, y_direct,
        color=['black', 'red', 'green'], scale=15)
    fig.canvas.draw() 
    fig.canvas.flush_events()
    
    


if __name__ == '__main__':
    ecal_core.initialize([], "basic_robotSim_plotter")
    robot_pos_sub = ProtoSubscriber("position", m.PosCommand)
    def ecal_pos_update(topic_name, msg, time):
        on_pos_update(msg) 
    robot_pos_sub.set_callback(ecal_pos_update)
    plt.show()
    print("waiting for first data from topic 'position' to plot... ")
    while True:
        sleep(0.01)
