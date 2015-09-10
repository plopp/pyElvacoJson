import requests
from requests.auth import HTTPBasicAuth
import json
import time

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
allchannels = []
for channel in all["result"]["points"]:
    allpids.append(channel["pid"])
    allchannels.append({channel["pid"]:channel["attr"]})

elm1 = sendRPC(method="pdb.getvalue",params=allpids)
elm1dict = json.loads(elm1)

todbdict = {}
for pid in elm1dict["result"]["points"]:
    todbdict[pid["pid"]]=pid["value"]

todbdict["time"]=elm1dict["result"]["timet"]
print json.dumps(todbdict)
