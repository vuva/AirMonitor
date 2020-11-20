# Copyright (c) 2020 Vu Anh Vu
#
# This file is part of IndoorClimateControl.
#
# IndoorClimateControl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IndoorClimateControl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IndoorClimateControl.  If not, see <https://www.gnu.org/licenses/>.

import requests;


API_KEY_FILE = "ifttt_webhook.key"
event_key_turn_on_purifier = "turn_on_purifier";
event_key_turn_off_purifier = "turn_off_purifier";

PURIFIER = "purifier"
HUMIDIFIER = "humidifier"
HEATER = "heater"

def get_api_key():
    try:
        with open(API_KEY_FILE, 'r') as key_file:
            api_key = key_file.read().replace('\n', '')
            return api_key
    except:
        # handling exception
        print('An Error')
        if key_file.closed == False:
            print('File is not closed')
        else:
            print('File is closed')
    return None

def turn_on_device(device_name):
    api_key = get_api_key()
    if api_key is None:
        return False

    if device_name == PURIFIER:
        print("Turning on purifier ...")
        req = requests.get("https://maker.ifttt.com/trigger/" + event_key_turn_on_purifier + "/with/key/" + api_key);
        # print ("https://maker.ifttt.com/trigger/" + event_key_turn_on_purifier + "/with/key/" + api_key)
    elif device_name == HUMIDIFIER:
        print("Turning on humidifier ...")
    elif device_name == HEATER:
        print("Turning on heater ...")

    print(req.status_code)
    if req.status_code == 200:
        print ("Device turned on successfully !")
        return True
    else:
        print("Device turned on failed!")
        return False


def turn_off_device(device_name):
    api_key = get_api_key()
    if api_key is None:
        return False

    if device_name == PURIFIER:
        print ("Turning off purifier ...")
        req = requests.get("https://maker.ifttt.com/trigger/" + event_key_turn_off_purifier + "/with/key/" + api_key);
    elif device_name == HUMIDIFIER:
        print("Turning off purifier ...")
    elif device_name == HEATER:
        print("Turning off purifier ...")

    print(req.status_code)
    if req.status_code == 200:
        print("Device turned off successfully !")
        return True
    else:
        print("Device turned off failed!")
        return False
