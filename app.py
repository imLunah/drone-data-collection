from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time

# Initialize the Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Shared data (global state)
counter = 0
realtime = 0
running = True

@app.route('/')
def index():
   return render_template('index.html')

def update_realtime():
   global realtime,running
   while True:
      realtime += 1
      emit('update_realtime', {'realtime': realtime}, broadcast=True)  # Broadcast to all clients
      print(realtime)
      socketio.sleep(1)

# Handle increment event
@socketio.on('increment')
def increment_counter():
   global counter
   counter += 1
   emit('update_counter', {'counter': counter}, broadcast=True)  # Broadcast to all clients

# Handle decrement event
@socketio.on('decrement')
def decrement_counter():
   global counter
   counter -= 1
   emit('update_counter', {'counter': counter}, broadcast=True)  # Broadcast to all clients

# Run the server

   
if __name__ == '__main__':
   socketio.start_background_task(update_realtime)
   socketio.run(app, debug=True)