# --------------------------------------------------------------------------------------------------
# Author: Chinmay Hegde
# Email: hosmanechinmay@gmail.com
# Created Date: 03-05-2021
# Description: Script that checks slot available in cowin portal and sends whatsapp message if the slot is available
# License: MIT
# --------------------------------------------------------------------------------------------------

import time
import json
import datetime
import requests
from message_sender import send_message

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', 'Upgrade-Insecure-Requests': '1', 'DNT': '1', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate'}
CFG_PATH = '../config.json'
MIN_AGE_LIMIT = 18 # minimum age limit. If you want this to tune for 45+, modify to 45.
MAX_LOC = 10 #Max number of locations to restrict whatspapp message size. Increase this if you want to send all locations.
TOTAL_DURATION = 150000 #Number of iterations in monitor thread. If you want to run for 60 mins it's 60/5 = 12 
TIME_INTERVAL = 5 #1 min
MAX_MSG = 20 # Max number of messages to sent once slot is avialble. Note: Restart the script after these attempts for retry.
prev_message = None

msg_counter = 0

def get_config(cfg_path):
    with open(cfg_path, 'r') as fd:
        tmp = json.load(fd)
        return tmp["SlotMonitor"], tmp["MessageService"]

def create_source_link(source_link, district_id):
    dobj = datetime.datetime.now().date()
    cur_date = dobj.strftime('%d-%m-%Y')
    source_uri = '{}?district_id={}&date={}'.format(source_link.rstrip('/'), district_id, cur_date)
    print(source_uri)
    return source_uri

def get_slot_json(slot_cfg):
    source_uri = create_source_link(slot_cfg['source_link'], slot_cfg['district_id'])
    try:
        request_get = requests.get(source_uri, headers = HEADERS)
        if request_get.status_code == 200:
            slot_data = request_get.json()
            #NOTE: for debug only ->start
            # slot_data['centers'][0]['sessions'][0]['available_capacity'] = 1
            # slot_data['centers'][0]['sessions'][0]['min_age_limit'] = 18
            # slot_data['centers'][0]['fee_type'] = 'Paid'
            #NOTE: for debug only ->ends
            return slot_data
    except:
        print("ERROR: Network related error")
    return {}

def get_available_slots(slot_data):
    slot_details = {}
    if 'centers' in slot_data.keys():
        for center in slot_data['centers']:
            try:
                for session in center['sessions']:
                    if session['available_capacity'] > 0 and session['min_age_limit'] == MIN_AGE_LIMIT:
                        slot_details[center['center_id']] = { 'name': center['name'], 'fee_type' : center['fee_type']}
                        #print("Slot found in {}".format(center['name']))
                        break
            except KeyError:
                print(center)
    return slot_details

def get_location_split(slot_details):
    free_loc = 0
    paid_loc = 0
    paid_locations = []
    for k, v in slot_details.items():
        if v['fee_type'] == 'Free':
            free_loc += 1
        else:
            paid_loc += 1
            paid_locations.append(v['name'])
    return free_loc, paid_loc, paid_locations

def start_monitor():
    print("Enter: start_monitor")
    slot_cfg, msg_cfg = get_config(CFG_PATH)
    slot_data = get_slot_json(slot_cfg)
    if len(slot_data) > 0:
        slot_details = get_available_slots(slot_data)
        message = None
        free_loc, paid_loc, paid_locations = get_location_split(slot_details)
        if len(slot_details) <= MAX_LOC and len(slot_details) > 0: # Adding this to avoid whatsapp message size restriction
            all_locations = [v['name'] for k, v in slot_details.items()]
            message = "Slot available in {} free and {} paid Locations. The locations are {}".format(free_loc, paid_loc, ','.join(all_locations))
            print("DEBUG: {}. Time: {}".format(message, str(datetime.datetime.now())))
        elif len(slot_details) > 5:
            message = "Slots are available in more than {} locations. Check the portal. Paid locations are {}".format(MAX_LOC, ','.join(paid_locations))
            print("DEBUG: {}. Time: {}".format(message, str(datetime.datetime.now())))
        #TODO: send message
        if message != None:
            global msg_counter
            global prev_message
            if msg_counter <= MAX_MSG and prev_message != message:
                send_message(msg_cfg, message)
                msg_counter += 1
                prev_message = message
            else:
                print("Exit: start_monitor")
                if msg_counter >= MAX_MSG:
                    return False #To exit the script
        else:
            print("DEBUG: No Slots!. Time: {}!".format(str(datetime.datetime.now())))
    print("Exit: start_monitor")
    return True

print(__name__)
if __name__ == '__main__':
    print("Enter: main")
    for i in range(TOTAL_DURATION):
        if start_monitor():
            time.sleep(TIME_INTERVAL)
        else:
            break
    print("Exit: main")
