from flask import Flask, render_template, request
import ecal.core.core as ecal_core
from ecal.core.publisher import ProtoPublisher
import messages_pb2 as m

app = Flask(__name__)

speedPub = None 
@app.route("/", methods=['GET', 'POST'])
def hello_world():
    x = 0
    y = 0
    theta = 0
    if request.method == 'POST':
        x = request.form['x']
        y = request.form['y']
        theta = request.form['theta']
        speed = m.SpeedCommand()
        try:
            speed.vx = float(x)
        except ValueError:
            speed.vx = 0.0
        try:
            speed.vy = float(y)
        except ValueError:
            speed.vy = 0.0
        try:
            speed.vtheta = float(theta)
        except ValueError:
            speed.vtheta = 0.0
        speed_pub.send(speed)

    return render_template("index.html", x=x, y=y, theta=theta)


if __name__ == "__main__":
    ecal_core.initialize(args=[], unit_name="basic_flask_teleop")
    speed_pub = ProtoPublisher("speed_cmd", m.SpeedCommand)
    app.run(debug=True)