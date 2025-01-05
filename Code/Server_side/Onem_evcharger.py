
import requests
import time

import re
import ast
import json

def get_latest_data(Node="AE-EV",device="CHARGER", user="USER-02"):

    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/{Node}/{device}/{user}/Transactions/la"

    payload = {}
    headers = {
        'X-M2M-Origin': 'dev_guest:dev_guest',
	'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response


def post_txn_data(Node="AE-EV", device = "USER",user="USER-02", data=None):
    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/{Node}/{device}/{user}/Transactions"
    # print(data)
    payload = "{\n    \"m2m:cin\":{\n        \"lbl\":[\n            \n        ],\n        \"con\":\"%s\"\n\n    }\n}\n\n" % (
        data)
    headers = {
        'X-M2M-Origin': 'dev_guest:dev_guest',
	'Content-Type': 'application/json;ty=4'
    
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # print("user data" + str(response))
    return response




def post_charger_txn_data(Node="AE-EV",device="CHARGER", charger='EV-L001-04', data=None):
    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/{Node}/{device}/{charger}/Transactions"
    print(url,data)
    payload = "{\n    \"m2m:cin\":{\n        \"lbl\":[\n            \n        ],\n        \"con\":\"%s\"\n\n    }\n}\n\n" % (
        data)
    headers = {
        'X-M2M-Origin': 'dev_guest:dev_guest',
	'Content-Type': 'application/json;ty=4'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)
    return response


def check_sufficient_balance(user_data, msg):
    # data_of_user = [Transaction_time, Transaction_amount, User_balance]
    if user_data[-1] >= msg["Amount"]:
        return True
    else:
        return False


def get_users(Node="AE-EV"):

    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/{Node}/USER?rcn=4"
    
    payload = {}
    
    
    headers = {
        'X-M2M-Origin': 'dev_guest:dev_guest',
	'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    false = False
    nan = 0
    dict_resp = eval(response.text)
    dict_resp = eval(str(dict_resp['m2m:cnt']))
    dict_resp = eval(str(dict_resp['m2m:cnt']))

    print(dict_resp)
    print(len(dict_resp))

    User_list = {}

    for i in range(len(dict_resp)):
        User_list[dict_resp[i]["rn"]] = (dict_resp[i]["lbl"][3])

    return User_list

def get_chargers(Node="AE-EV"):

    #url = f"http://192.168.137.1:8080/~/in-cse/in-name/{Node}?rcn=4"
    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/{Node}/CHARGER?rcn=4"

    payload = {}
    headers = {
        'X-M2M-Origin': 'dev_guest:dev_guest',
	'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    false = False
    nan = 0
    print(response.text)
    dict_resp = eval(response.text)
    dict_resp = eval(str(dict_resp['m2m:cnt']))
    dict_resp = eval(str(dict_resp['m2m:cnt']))
    # print(dict_resp)
#     print(len(dict_resp))

    charger_list = {}

    for i in range(len(dict_resp)):
        charger_list[dict_resp[i]["rn"]] = (dict_resp[i]["lbl"][0])

    return charger_list




def get_unit_price(charger_list, msg):
    key_list = list(charger_list.keys())
    val_list = list(charger_list.values())

    position = key_list.index(str(msg["Chargerid"]))
    response = get_latest_data(Node="AE-EV", device="CHARGER", user=key_list[position])

    try:
        response_data = json.loads(response.text)  # Parse JSON response
        charger_content = response_data['m2m:cin']['con']
        # Safely convert to list
        data_of_charger = eval(charger_content)
        print(data_of_charger)

        return data_of_charger[-2], key_list[position]
    except (KeyError, ValueError, SyntaxError) as e:
        print(f"Error parsing response: {e}")
        return None, None




def verify_transaction(msg):

    User_list = get_users()
    charger_list = get_chargers()

    unit_price, charger_name = get_unit_price(charger_list, msg)
    print(unit_price)
    print(charger_list)
    print(User_list)
    
    msg["VehicleidTag"] = '7053'

    if(msg["VehicleidTag"] in User_list.values()):
        print("User Found")
        user_key_list = list(User_list.keys())
        user_val_list = list(User_list.values())
        user_position = user_val_list.index(msg["VehicleidTag"])
        print(user_key_list[user_position])

        response = get_latest_data(
            Node="AE-EV",device="USER",user=user_key_list[user_position])

        data_of_user = eval(eval(response.text)['m2m:cin']['con'])

        if check_sufficient_balance(data_of_user, msg):
            print("Sufficient Balance")
            print("Transaction Approved")
             # Format Txn_data
            Txn_data = [
                int(msg["Time"]),
                msg["VehicleidTag"],
                charger_name,
                msg["Amount"],
                unit_price,
                round(msg["Amount"] / unit_price, 2),
                data_of_user[-1] - msg["Amount"]
            ]
            
            # Format Txn_data
            # Txn_data = [
            #     int(msg["Time"]),
            #     msg["VehicleidTag"],
            #     charger_name,
            #     msg["Amount"],
            #     unit_price,
            #     round(msg["Amount"] / unit_price, 2),
            #     100000000
            # ]

   
            # Format Charger_Txn_data
            Charger_Txn_data = [
                int(msg["Time"]),  # Timestamp
                charger_name,      # Charger_ID
                msg["VehicleidTag"],  # User_ID
                msg["Amount"],     # Transaction_Amount
                unit_price,        # Unit_Price
                round(msg["Amount"] / unit_price, 2)  # Units_Consumed
            ]

             # Format Charger_Txn_data
            # Charger_Txn_data = [
            #     int(msg["Time"]),  # Timestamp
            #     charger_name,      # Charger_ID
            #     msg["VehicleidTag"],  # User_ID
            #     msg["Amount"],     # Transaction_Amount
            #     unit_price,        # Unit_Price
            #     round(msg["Amount"] / unit_price, 2)  # Units_Consumed
            # ]

            post_txn_data(Node="AE-EV",device='USER',user=user_key_list[user_position], data=Txn_data)

            post_charger_txn_data(Node="AE-EV",device = "CHARGER",charger=charger_name, data=Charger_Txn_data)

            return "Transaction Approved"
        else:
            print("Insufficient Balance")
            print("Transaction Declined")
            return "Insufficient Balance"
            
            
if __name__ == '__main__':
    msg = {
        "Amount": 100,
        "VehicleidTag": "7053",
        "Time": time.time(),
        "Chargerid": "EV-L001-04"
    }
     
    charger_name = msg["Chargerid"]
    unit_price =10

    #  # Format Txn_data
    # Txn_data = [
    #     int(msg["Time"]),
    #     msg["VehicleidTag"],
    #     charger_name,
    #     msg["Amount"],
    #     unit_price,
    #     round(msg["Amount"] / unit_price, 2),
    #     100000000
    # ]
    # post_txn_data(Node="AE-EV",device='USER',user="USER-01", data=Txn_data)

    verify_transaction(msg)
    # unit_price, charger_name = get_unit_price(get_chargers(), msg)
    # print(unit_price, charger_name)
