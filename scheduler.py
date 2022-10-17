""" Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""
import json, datetime, time, requests
from meraki import DashboardAPI

#Read data from json file
def getJson(filepath):
	with open(filepath, 'r') as f:
		json_content = json.loads(f.read())
		f.close()

	return json_content

#Write data to json file
def writeJson(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f)
    f.close()

def turn_off_ssid(network, name, ssid):
    print(f"Turning on SSID: {name}")
    settings = getJson('settings.json')

    url = f"https://api.meraki.com/api/v1/networks/{network}/wireless/ssids/{ssid}"
    headers = {
        "Content-Type" : "application/json",
        "Accept" : "application/json",
        "X-Cisco-Meraki-API-Key" : settings['apikey']
    }
    body = {
        "name": name,
        "enabled": False
    }

    resp = requests.put(url, headers=headers, json=body)
    resp.raise_for_status()

def turn_on_ssid(network, name, ssid):
    print(f"Turning on SSID: {name}")
    settings = getJson('settings.json')

    url = f"https://api.meraki.com/api/v1/networks/{network}/wireless/ssids/{ssid}"
    headers = {
        "Content-Type" : "application/json",
        "Accept" : "application/json",
        "X-Cisco-Meraki-API-Key" : settings['apikey']
    }
    body = {
        "name": name,
        "enabled": True
    }

    resp = requests.put(url, headers=headers, json=body)
    resp.raise_for_status()

def check_for_shutdown():
    networks = getJson('networks.json')
    time_hour = datetime.datetime.now().hour
    time_minutes = datetime.datetime.now().minutes
    for n in networks:
        for start_time in n['planning']:
            hour = int(start_time[:2])
            minutes = int(start_time[3:])
            if time_hour == hour and minutes < time_minutes < (minutes+15):
                turn_on_ssid(n['networkid', n['name'], n['number']])
            else: 
                turn_off_ssid(n['networkid', n['number']])

if __name__ == "__main__":
    while True:
        check_for_shutdown()
        time.sleep(300) # Run every 5 minutes