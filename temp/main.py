import eventlet
eventlet.monkey_patch()

from unittest import result
from flask import Flask, render_template, redirect, Blueprint
from flask import request
from subprocess import call
from flask_socketio import SocketIO,send,emit

from db import Databse
import time
import cups
from weasyprint import HTML, CSS
import json

from modules.led import Led_module
from modules.ardu_serial import ArduSerial
from modules.ir import IrModule

from threading import Lock, Thread

"""
Background Thread
"""
thread = None
thread_lock = Lock()
threads = []

led = Led_module()

'''
ir = IrModule()
t1 = Thread(target= ir.start)
t1.start()
threads.append(t1)
for t in threads:
    t.join()


serial = ArduSerial()
'''
conn = cups.Connection()
default_printer = conn.getDefault()
cups.setUser('pi')
print(default_printer)

app = Flask(__name__)
app.secret_key = "mysecret"

socketio = SocketIO(app, async_mode='eventlet')
#print(__name__)

def print_func(data):
    print('this log print func')
    print(data)
    with open('html_report.html', 'w') as f:
        f.write(data)
    file_name = 'weasyprint_pdf_report.pdf'
    css = CSS(string='''
        @page {size: A4; margin: 1cm;} 
        th, td {border: 1px solid black;}
        ''')
    HTML('html_report.html').write_pdf(file_name, stylesheets=[css])
    conn.printFile(default_printer, file_name, "test", {'fit-to-page': 'True'})
    redirect('/print_end')

def background_thread():
    print("Generating random sensor values")
    while True:
        socketio.emit('updateSensorData', {'value': serial.get_data()})
        socketio.sleep(1)

@app.route('/')
def index():
    if request.method == 'GET':
        param = {"printer": default_printer}
        return render_template('index.html', data=param)

@app.route('/view_table')
def view_table():
    db=Databse()
    sql_all=db.show()
    param = {
        "list": sql_all,
        "printer": default_printer
    }
    return render_template('view_table.html', data=param)

@app.route('/print', methods = ['POST','GET'])
def print_start():
    if request.method == 'POST':
        db=Databse()
        sql_all=db.show()
        print('print start')
        print_data = render_template('template.html', list=sql_all)
        print_func(print_data)
        render_temp = render_template('print.html', data="printing....")
        return render_temp
            
@app.route('/print_end', methods = ['POST','GET'])
def print_end():
    if request.method == 'GET':
        return render_template('print.html', data='print success')

@app.route('/search', methods = ['POST','GET'])
def search():
    if request.method == 'POST':
        print(request.form)
        db=Databse()
        st = request.form.get('startTime')
        ed = request.form.get('endTime')
        sql_all=db.query_search(st, ed)
        return render_template('template.html',list=sql_all)

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(data, methods=['GET', 'POST']):
    print('received my event: ')
    emit('my response', data, callback=messageReceived)

@socketio.on('connect')
def test_connect():
    global thread
    print('Client connected')
    global thread
    
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print('server run start')
    app.run(host='0.0.0.0',debug='True')
    socketio.run(app, debug='True')    
