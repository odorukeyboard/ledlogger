from app import create_app
from threading import Lock, Thread
import eventlet
from app.modules.ardu_serial import ArduSerial
from app.modules.ir import IrModule
from flask_socketio import SocketIO,send,emit

import RPi.GPIO as GPIO
import time

eventlet.monkey_patch()

thread = None
thread_lock = Lock()
threads = []

serial = ArduSerial()

socketio, app = create_app()

if __name__ == "__main__":

    def messageReceived(methods=['GET', 'POST']):
        print('message was received!!!')

    def background_thread():
        print("Generating random sensor values")
        while True:
            socketio.emit('updateSensorData', {'value': serial.get_data()})
            socketio.sleep(1)

    @socketio.on('my event')
    def handle_my_custom_event(data, methods=['GET', 'POST']):
        print('received my event: ',data)
        emit('my response', data, callback=messageReceived)

    @socketio.on('connect')
    def test_connect():
        global thread
        print('Client connected')
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(background_thread)

    @socketio.on('disconnect')
    def test_disconnect():
        print('Client disconnected')
    
    socketio.run(app,host='0.0.0.0',debug='True')
