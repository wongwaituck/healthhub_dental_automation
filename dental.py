#!/usr/bin/env python3

import requests
import datetime
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

from dotenv import load_dotenv

load_dotenv()

LANDING_URL = "https://eservices.healthhub.sg/appointments"

# this checks for dental appointments in bukit panjang polyclinic, you should modify this if you are checking for other service types 
DASHBOARD_URL = f"https://eservices.healthhub.sg/Appointments/Dashboard/Index/{os.environ['USER_HASH']}"
NEW_APP_URL = "https://eservices.healthhub.sg/Appointments/NewAppointment"
SELECT_POLYCLINIC_URL = "https://eservices.healthhub.sg/Appointments/NewAppointment/SelectPolyclinic?clusterCode=NUP"
BUKIT_PANJANG_URL = "https://eservices.healthhub.sg/Appointments/NewAppointment/SelectService/?InstCode=BPJ&CCode=NUP"
SELECT_SERVICE_URL = "https://eservices.healthhub.sg/Appointments/NewAppointment/PostSelectService"
APPOINTMENT_URL = "https://eservices.healthhub.sg/Appointments/NewAppointment/SelectSlot/?consultType=&serviceTypeId=117022180&checkPostSelectService=False"
SLOTS_URL = "https://eservices.healthhub.sg/Appointments/NewAppointment/GetAvailableSlots"

if __name__=="__main__":
    webdriver_service = Service("/usr/bin/chromedriver")
    browser = webdriver.Chrome(service=webdriver_service)

    browser.get(LANDING_URL)

    awsalb = WebDriverWait(browser, timeout=300).until(lambda d: d.get_cookie('AWSALB'))['value']

    # navigate to the specific booking because they store that information in the session
    browser.get(DASHBOARD_URL)
    browser.get(NEW_APP_URL)
    browser.get(SELECT_POLYCLINIC_URL)
    browser.get(BUKIT_PANJANG_URL)
    browser.get(SELECT_SERVICE_URL)
    browser.get(APPOINTMENT_URL)

    cookies = browser.get_cookies()

    final_cookie = ''
    for cookie in cookies:
        if cookie['domain'].endswith('healthhub.sg'):
            final_cookie += f'{cookie["name"]}={cookie["value"]}; '
    headers = {
        'Cookie': final_cookie
    }

    browser.close()

    date_i = datetime.datetime.now()

    for i in range(300):
        date_i += datetime.timedelta(days=1)
        date_s = date_i.strftime("%a %b %d %Y")
        data = {
            "appointmentDate": date_s,
            "lastSlotId": 0,
            "resourceCode": "",
            "lastSlotDate": ""
        }

        resp = requests.post(SLOTS_URL, json=data, headers=headers).text
        if 'high demand' in resp:
            print(f'[*] {date_s} not available')
        elif 'item_details' in resp:
            print(f'[+] {date_s} available!')
        elif 'no slots' in resp:
            print(f'[-] No more slots available :(')
            exit(-1)
        else:
            print(f'[-] Encountered an error for {date_s}')
            print(resp)
        