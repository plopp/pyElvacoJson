#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth
import json
import time
import os

def sendRPC(**kwargs):
    data = {
        "jsonrpc":"2.0",
        "id":1
    }

    for key, value in kwargs.iteritems():
        data[key] = value

    headers = {
        "Content-Type":"application/json-rpc"
    }
    
    try:
        #Used for find fiding the .credentials file when run from CRON.
        scriptDirectory = os.path.dirname(os.path.realpath(__file__))
        credentialsFilePath = os.path.join(scriptDirectory, ".credentials")
        with open(credentialsFilePath, 'r') as f:
            file_data = f.read()
            creds = file_data.split(',')
            url = creds[0]
            user = creds[1]
            passw = creds[2].replace('\n','')
    except:
        print "Error opening credentials file."
        raise

    res = requests.post(url, 
        auth=HTTPBasicAuth(user, passw), 
        data=json.dumps(data), 
        headers=headers)

    return json.dumps(res.json())
    
all = sendRPC(method="pdb.browse")
all = json.loads(all)

allpids = []
allchannels = {}
for channel in all["result"]["points"]:
    allpids.append(channel["pid"])
    allchannels[channel["pid"]]={
        "unit":channel["attr"],
        "desc":channel["desc"]
    }

elm1 = sendRPC(method="pdb.getvalue",params=allpids)
elm1dict = json.loads(elm1)

todbdict = {}
for pid in elm1dict["result"]["points"]:
    todbdict[pid["pid"]]=pid["value"]
    allchannels[pid["pid"]]["value"] = pid["value"]
    allchannels[pid["pid"]]["time"] = elm1dict["result"]["timet"]

todbdict["time"]=elm1dict["result"]["timet"]

points = []
for pid in allchannels:
    pido = allchannels[pid]
    point = {
        "measurement": pido["desc"],
        "tags": {
            "unit": pido["unit"].encode("utf-8"),
            "pid": pid
        },
        "time": pido["time"],
        "fields": {
            "value": pido["value"]
        }
    }
    point = ''.join([pido["desc"].encode("utf-8"),",unit=",pido["unit"].encode("utf-8"),",pid=",pid.encode("utf-8")," value=",str(pido["value"])," ",str(pido["time"])])
    points.append(point)
psend = '\n'.join(points)

import requests
r = requests.post('http://localhost:8086/write?db=vameb&user=root&precision=ms',data=psend)
