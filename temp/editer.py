import eventlet
eventlet.monkey_patch()

from unittest import result
from flask import Flask, render_template, redirect
from flask import request
from subprocess import call
from flask_socketio import SocketIO,send,emit
from reportbro import Report, ReportBroError
from db import Databse
import time
import json

app = Flask(__name__)
app.secret_key = "mysecret"

@app.route('/')
def report():
    if request.method == 'GET':
        print('this log run')
        result={}
        result['report_definition'] = json.dumps(None)
        print(result)
        return render_template('report.html', **result)
@app.route('/run')
def run():
    print('this log run')
    result = {}
    result['report_definition'] = json.dumps(None)
    print(result)
    return render_template('report.html', result=result)

if __name__ == '__main__':
    print('server run start')
    app.run(host='0.0.0.0', port=8000, debug='True')
