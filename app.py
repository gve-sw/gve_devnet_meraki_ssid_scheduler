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

# Import Section
from flask import Flask, render_template, request, url_for, redirect
from collections import defaultdict
import datetime
import requests
import json
from dotenv import load_dotenv
import os
#import merakiAPI
from dnacentersdk import api
from meraki import DashboardAPI

# load all environment variables
load_dotenv()


# Global variables
app = Flask(__name__)
selected_elements = {
    'network' : '',
    'ssid' : '',
    'scheduletemplate' : 'school'
}
dropdown_content = []

selected_schedule_template = 'school'
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
times = [
            '00:00', '00:15', '00:30', '00:45',
            '01:00', '01:15', '01:30', '01:45',
            '02:00', '02:15', '02:30', '02:45',
            '03:00', '03:15', '03:30', '03:45',
            '04:00', '04:15', '04:30', '04:45',
            '05:00', '05:15', '05:30', '05:45',
            '06:00', '06:15', '06:30', '06:45',
            '07:00', '07:15', '07:30', '07:45',
            '08:00', '08:15', '08:30', '08:45',
            '09:00', '09:15', '09:30', '09:45',
            '10:00', '10:15', '10:30', '10:45',
            '11:00', '11:15', '11:30', '11:45',
        ]

#Read data from json file
def getJson(filepath):
	with open(filepath, 'r') as f:
		json_content = json.loads(f.read())
		f.close()

	return json_content

#Write data to json file
def writeJson(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    f.close()


##Routes

#Index
@app.route('/template', methods=['GET', 'POST'])
def template():
    global selected_schedule_template, selected_elements
    schedule = request.form.get('templateschedule')
    selected_schedule_template = schedule
    selected_elements['scheduletemplate'] = schedule
    return redirect('/')

#Index
@app.route('/', methods=['GET', 'POST'])
def index():
    global dropdown_content, selected_elements, selected_schedule_template, days, times
    # try:
    settings = getJson('settings.json')
    if len(settings['apikey']) < 20:
        redirect('/settings')
    networks = []
    selected = []

    api = DashboardAPI(settings['apikey'])
    orgs  = api.organizations.getOrganizations()
    for org in orgs:
        for n in api.organizations.getOrganizationNetworks(org['id']):
            entry = {
                'name' : n['name'],
                'id' : n['id'],
                'ssids' : []
            }
            try:
                for ssid in api.wireless.getNetworkWirelessSsids(n['id']):
                    networks += [{
                        'name' : ssid['name'],
                        'networkid' : n['id'],
                        'number' : ssid['number'],
                        'planning' : [],
                        'networkname' : n['name'],
                        'selectedids' : []
                    }]
                    entry['ssids'] += [{
                        'name' : ssid['name'],
                        'number' : ssid['number']
                    }]
            except Exception as e:
                print(e)
            dropdown_content += [entry]
        writeJson(f"networks.json", networks)
        writeJson('dropdown.json', dropdown_content)
        selected = []
    else:
        selected = settings['selected']

    if request.method == 'POST':
        # Network and SSID input
        selected_network = request.form.get('selected_network')
        selected_ssid = request.form.get('selected_ssid')
        selected_elements = {
            'network' : selected_network,
            'ssid' : selected_ssid,
            'scheduletemplate' : selected_schedule_template
        }

        selected = []
        ids = dict(request.form.lists())
        new_networks=[]
        networks = getJson(f"networks.json")
        for n in networks:
            new_n = n
            new_n['planning'] = []
            new_n['selectedids'] = []
            new_networks += [new_n]
        for id in ids:
            vals = id.split('-')
            if len(vals)>1:
                entry = {
                    'networkid' : vals[0],
                    'number' : int(vals[1]),
                    'day' : vals[2],
                    'start_time' : vals[4]
                }
                i=0
                for n in networks:
                    if entry['networkid'] == n['networkid'] and entry['number'] == n['number']:
                        new_networks[i]['planning'] += [entry['start_time']]
                        new_networks[i]['selectedids'] += [id]
                    i+=1
        writeJson(f"networks.json", new_networks)
        writeJson('settings.json', settings)
    
    networks = getJson(f"networks.json")
    selected = []
    for n in networks:
        selected += n['selectedids']

    return render_template('index.html', templates=getJson('templates.json'), selected_elements=selected_elements, selected=selected, networks=getJson(f"networks.json"), days=days, times=times, dropdown_content=getJson('dropdown.json'))
    # except Exception as e: 
    #     print(e)  
    #     #OR the following to show error message 
    #     return render_template('index.html', networks = [], selected_elements=selected_elements)

@app.route('/loadtemplate')
def load_template():
    global selected_elements
    selected_elements['network']
    return render_template('templateconfig.html', templates = getJson('templates.json'))

@app.route('/templates')
def template_config():
    return render_template('templateconfig.html', templates = getJson('templates.json'))

@app.route('/newtemplate', methods=["GET", "POST"])
def new_template():
    global times, days
    if request.method == "POST":
        ids = dict(request.form.lists())
        name = request.form.get('templatename')
        templates = getJson('templates.json')
        id = str(len(templates))

        selected_times = []
        for id in ids:
            vals = id.split('-')
            if len(vals)>1:
                selected_times += [id]
        new_template = {
            "name" : name,
            "id" : id,
            "schedule" : selected_times
        }
        templates += [new_template]
        writeJson(f"templates.json", templates)
        return redirect('/templates')
    return render_template('newtemplate.html', times=times, days=days, error=False)

@app.route('/edittemplate', methods=["GET", "POST"])
def edit_template():
    template_id = request.args.get('templateid')
    templates = getJson('templates.json')
    if request.method == "GET":
        for t in templates:
            if t['id'] == template_id:
                selected = t
                return render_template('edittemplate.html', times=times, days=days, template = selected, error=False)
    if request.method == "POST":
        new_templates = []
        template_id = request.form.get('templateid')
        template_name = request.form.get('templatename')
        for t in templates:
            if t['id'] == template_id:
                ids = dict(request.form.lists())
                selected_times = []
                for id in ids:
                    vals = id.split('-')
                    if len(vals)>1:
                        selected_times += [id]
                new_template = {
                    "name" : template_name,
                    "id" : template_id,
                    "schedule" : selected_times
                }
                templates = getJson('templates.json')
                new_templates += [new_template]
            else:
                new_templates += [t]
        writeJson('templates.json', new_templates)
        return redirect('/templates')

@app.route('/removetemplate', methods=["GET", "POST"])
def remove_template():
    template_id = request.args.get('templateid')
    templates = getJson('templates.json')
    new_templates = []
    for t in templates:
        if not t['id'] == template_id:
            new_templates += [t]
    writeJson('templates.json', new_templates)
    return redirect('/templates')

#Settings
@app.route('/settings', methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        apikey = request.form.get('apikey')
        settings = getJson("settings.json")
        settings['apikey'] = apikey
        writeJson("settings.json", settings)
        return redirect('/')
    try:
        return render_template('settings.html', settings=getJson("settings.json"))
    except Exception as e: 
        print(e)  
        return render_template('settings.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000, debug=True)