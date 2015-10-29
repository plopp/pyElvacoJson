#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth
import json
import time
from influxdb import InfluxDBClient

client = InfluxDBClient('localhost', 8086, 'root', 'root', 'vameb')

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
        with open('.credentials', 'r') as f:
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
        "time": pido["time"]*1000*1000,
        "fields": {
            "value": pido["value"]
        }
    }
    points.append(point)

client.write_points(points,time_precision='n')