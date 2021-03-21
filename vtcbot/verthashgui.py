import subprocess
import json
from flask import Flask, render_template,request
import os
from subprocess import Popen
import requests
import socket
import _thread
import webbrowser





class batFile():
    def __init__(self):
        self.path = "run.bat"
        self.proc = None

    def start(self):
        if self.proc is None:
            self.proc = Popen(["run.bat"])

    def stop(self):
        if self.proc is not None:
            self.proc.kill()
            os.system("taskkill /f /im  VerthashMiner.exe")
            self.proc = None


batProcess = batFile()


def write_json(data):
    with open("data.json", 'w') as f:
        json.dump(data, f, indent=4)

app = Flask(__name__)

@app.route("/",methods=['POST','GET'])
def index():

    if request.method == "GET":
        f = open('data.json', )
        data = json.load(f)
        pubKey = data['vtcpubkey']
        r = requests.get(f"https://vtc.suprnova.cc/index.php?page=api&action=getuserbalance&api_key={pubKey}")
        if r.status_code == 200:

            requestJson = r.json()
            balence = requestJson['getuserbalance']['data']['confirmed']
            unconfirmed = requestJson['getuserbalance']['data']['unconfirmed']
            return render_template('index.html',amt=balence,pending=unconfirmed,pubKey=pubKey)
        else:
            return render_template('index.html')


@app.route("/start",methods=['POST'])
def start():
    get_data = request.form.to_dict(flat=False)

    if 'vtc' in get_data:
        publicKey = get_data['vtc'][0]
    else:
        publicKey = None

    if 'btc' in get_data:
        btcpubKey = get_data['btc'][0]
    else:
        btcpubKey = None




    with open('data.json', 'r') as f:
        data = json.load(f)
        if publicKey != None:
            data['vtcpubkey'] = publicKey
        if btcpubKey != None:
            data['btcpubkey'] = btcpubKey

    write_json(data)
    set_bat_cfg()

    batProcess.start()
    return '200'

@app.route("/stop",methods=['POST'])
def stop():

    batProcess.stop()
    return '200'

def set_bat_cfg():
    f = open('data.json',)
    data = json.load(f)
    pubKey = data['vtcpubkey']
    myBat = open('run.bat','w+')

    pool = "stratum+tcp://vtc.suprnova.cc:1776"

    home = os.path.expanduser('~')[9:]
    myBat.write(r'VerthashMiner.exe -u '+pubKey+f" -p x -o {pool} --verthash-data "+r"C:\users"+r"\""[:-1]+home+r"\appdata\roaming\vertcoin-ocm\verthash.dat --all-cl-devices --all-cu-devices"+"\npause")
    myBat.close()

url = socket.gethostbyname(socket.gethostname())
webbrowser.open("http://"+url+":5000/")
app.run(host='0.0.0.0')
