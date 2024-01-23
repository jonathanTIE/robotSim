# plotting robot & map 

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import re

matplotlib.use('TkAgg')

table_coordinates, edges = {}, {}
waypoint_plot, edges_plot = [], []

fig, ax = plt.subplots()
ax.set_xlim(    [0.0, 3000.0]    )
ax.set_ylim(    [0.0, 2000.0]    )
robot_marker = ax.plot(100, 20, marker=(3, 0, 0), markersize=10, linestyle='None') 

def parse_path_settings(path_file_lua):
    global table_coordinates, edges
    items_regex = r"(\w+)\s*=\s*{([^{}]+)}"
    coords_regex = r"(x\s*=\s*)(\d+)\s*,\s*(y\s*=\s*)(\d+)"
    edges_regex = r"\s*[\"'](\w+)"
    with open(path_file_lua, 'r') as f:
        content = f.read()
        matches = re.findall(items_regex, content)
        for match in matches:
            key = match[0]
            value = re.split(coords_regex, match[1]) #try to match coordinates
            if len(value) > 1: # example : ['', 'x=', '200', 'y= ', '200', '']
                x = int(value[2])
                y = int(value[4])
                table_coordinates[key] = (x, y)
            else: #if edges  example : (['"S6", "A8"'])
                value = re.findall(edges_regex, match[1])
                if len(value) == 0:
                    raise Exception(f"Error while parsing path settings file \
                        - invalid edges for {key}   {value}")
                edges[key] = value

def toggle_waypoint_draw():
    global waypoint_plot
    if waypoint_plot == []:
        names = [x for x in table_coordinates]
        x = [table_coordinates[name][0] for name in names]
        y = [table_coordinates[name][1] for name in names]
        waypoint_plot = ax.plot(x, y, marker="^", markersize=3, linestyle='None', color='green')
        for name in names:
            waypoint_plot.append(ax.annotate(name, table_coordinates[name]))
    else:
        for plot in waypoint_plot:
            plot.remove()
        waypoint_plot = []
    plt.draw()

def toggle_path_draw():
    global edges_plot
    if edges_plot == []:
        for edge in edges:
            for end_point in edges[edge]:
                x = [table_coordinates[edge][0], table_coordinates[end_point][0]]
                y = [table_coordinates[edge][1], table_coordinates[end_point][1]]
                edges_plot.append(ax.plot(x, y, color='green', linestyle='dotted'))
    else:
        for plot in edges_plot:
            plot.remove()
        edges_plot = []
    plt.draw()

def set_vinyle_img(path):
    global ax
    ax.imshow(plt.imread(path), extent=[0, 3000, 0, 2000])
    
def update_robot_plot(x: float, y:float, theta:float):
    global robot_marker
    robot_marker[0].remove()
    robot_marker = ax.plot(x, y, marker=(3, 0, theta), markersize=10, linestyle='None', color='blue')
    plt.draw()

def draw_figure(canvas):
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg