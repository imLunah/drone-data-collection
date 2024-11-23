# Import necessary modules
from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
from aiortc import RTCPeerConnection, RTCSessionDescription
from flask_socketio import SocketIO
from threading import Thread
import cv2
import json
import uuid
import asyncio
import logging
import time
import random

# Create a Flask app instance
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'supersecret'
socketio = SocketIO(app)

# Route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html')



#######################################################################################
######################              REAL TIME DATA               ######################
#######################################################################################
flightmode = "Guided"
#getting data from px4 and kraken
def get_data():
    return

#publishing live data
def data_pub():
    global flightmode
    while True:
        time.sleep(.20)
        data = {
            "FlightMode": flightmode,
            "GPSdata": random.uniform(40.0, 60.0),
            "RCsignalstrength": random.uniform(0.0, 100.0),
            "Speed": random.uniform(0.0, 50.0),
            "Altitude": random.uniform(10.0, 30.0),
            "Roll": random.uniform(20.0, 30.0),
            "Pitch": random.uniform(20.0, 30.0),
            "Yaw": random.uniform(20.0, 30.0),
            "CurrentDraw": random.uniform(20.0, 30.0),
            "MotorSpeed": random.uniform(20.0, 30.0)
        }
        socketio.emit('data_update', data)


@socketio.on('change_flight_mode')
def handle_change_flight_mode(mode):
    global flightmode 
    flightmode = mode
    print(f"Flight mode changed to: {mode}")
    # You can add more logic here to handle flight mode change,
    # such as updating a system or sending a response back to the clienSSt.
    # For now, we'll just emit a confirmation back to the client.


@socketio.on('text_input')
def handle_text_input(text):
    print(f"Received text input: {text}")
    # You can add logic here to handle the text input, such as storing it,
    # performing some actions, or responding back to the client.
    # For now, we'll just send it back to the client as a confirmation.
#######################################################################################
######################              VIDEO STREAMING              ######################
#######################################################################################

# Set to keep track of RTCPeerConnection instances
pcs = set()

# Function to generate video frames from the camera
def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        start_time = time.time()
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Concatenate frame and yield for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
            elapsed_time = time.time() - start_time
            logging.debug(f"Frame generation time: {elapsed_time} seconds")

# Asynchronous function to handle offer exchange
async def offer_async():
    params = await request.json
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    # Create an RTCPeerConnection instance
    pc = RTCPeerConnection()

    # Generate a unique ID for the RTCPeerConnection
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pc_id = pc_id[:8]

    # Create a data channel named "chat"
    # pc.createDataChannel("chat")

    # Create and set the local description
    await pc.createOffer(offer)
    await pc.setLocalDescription(offer)

    # Prepare the response data with local SDP and type
    response_data = {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

    return jsonify(response_data)

# Wrapper function for running the asynchronous offer function
def offer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    future = asyncio.run_coroutine_threadsafe(offer_async(), loop)
    return future.result()

# Route to handle the offer request
@app.route('/offer', methods=['POST'])
def offer_route():
    return offer()

# Route to stream video frames
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



#######################################################################################
######################                RUN SERVER                 ######################
#######################################################################################
if __name__ == "__main__":
    Thread(target=data_pub, daemon=True).start()
    app.run(debug=True, host='0.0.0.0')