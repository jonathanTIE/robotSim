# plotting robot & map 

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use('TkAgg')

fig, ax = plt.subplots()
ax.set_xlim(    [0.0, 3000.0]    )
ax.set_ylim(    [0.0, 2000.0]    )
robot_marker = ax.plot(100, 20, marker=(3, 0, 0), markersize=10, linestyle='None') 

def update_robot_plot(x: float, y:float, theta:float):
    global robot_marker
    robot_marker[0].remove()
    robot_marker = ax.plot(x, y, marker=(3, 0, theta), markersize=10, linestyle='None')
    plt.draw()

def draw_figure(canvas):
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg