import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
t = [-2.0, 2.0, 1.0]
s = t
initial_text = "t ** 2"
l, = plt.plot(t, s, lw=2)


def submit(text):
    print("shit")
    plt.draw()

axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
text_box = TextBox(axbox, 'Evaluate', initial=initial_text)
text_box.on_submit(submit)

plt.show()