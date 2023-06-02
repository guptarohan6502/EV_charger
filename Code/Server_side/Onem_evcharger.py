
import requests
import time


def get_latest_data(Node="AE-EVcharger", user="User-1"):

    url = f"http://192.168.0.112:8080/~/in-cse/in-name/{Node}/{user}/Transactions/la"

    payload = {}
    headers = {
        'X-M2M-Origin': 'admin:admin',
        'Accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    return response


def post_txn_data(Node="AE-EVcharger", user="User-1", data=None):
    url = f"http://192.168.0.112:8080/~/in-cse/in-name/{Node}/{user}/Transactions"
    data = [time.time(), data["Txn_Amount"], data["Txn_Balance"]]
    payload = "{\n    \"m2m:cin\":{\n        \"lbl\":[\n            \"Transation_data-Time\",\n            \"Transaction Amount(IN RS)\",\n            \"Current Amount in User Account(IN RS)\"\n        ],\n        \"con\":\"%s\"\n\n    }\n}\n\n" % (
        data)
    headers = {
        'X-M2M-Origin': 'admin:admin',
        'Content-Type': 'application/json;ty=4'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def post_charger_txn_data(Node="Charger-Info", user="CHARGER-1", data=None):
    url = f"http://192.168.0.112:8080/~/in-cse/in-name/{Node}/{user}/Transactions"
    payload = "{\n    \"m2m:cin\":{\n        \"lbl\":[\n            \n        ],\n        \"con\":\"%s\"\n\n    }\n}\n\n" % (
        data)
    headers = {
        'X-M2M-Origin': 'admin:admin',
        'Content-Type': 'application/json;ty=4'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def check_sufficient_balance(user_data, msg):
    # data_of_user = [Transaction_time, Transaction_amount, User_balance]
    if user_data[2] >= msg["Amount"]:
        return True
    else:
        return False


def get_users(Node="AE-EVcharger"):

    url = f"http://192.168.0.112:8080/~/in-cse/in-name/{Node}?rcn=4"

    payload = {}
    headers = {
        'X-M2M-Origin': 'admin:admin',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    false = False
    nan = 0
#     print(response.text)
    dict_resp = eval(response.text)
    dict_resp = eval(str(dict_resp['m2m:ae']))
    dict_resp = eval(str(dict_resp['m2m:cnt']))
    # print(dict_resp)
#     print(len(dict_resp))

    User_list = {}

    for i in range(len(dict_resp)):
        User_list[dict_resp[i]["rn"]] = (dict_resp[i]["lbl"][0])

    return User_list


def get_chargers(Node="Charger-Info"):

    url = f"http://192.168.0.112:8080/~/in-cse/in-name/{Node}?rcn=4"

    payload = {}
    headers = {
        'X-M2M-Origin': 'admin:admin',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    false = False
    nan = 0
    # print(response.text)
    dict_resp = eval(response.text)
    dict_resp = eval(str(dict_resp['m2m:ae']))
    dict_resp = eval(str(dict_resp['m2m:cnt']))
    # print(dict_resp)
#     print(len(dict_resp))

    charger_list = {}

    for i in range(len(dict_resp)):
        charger_list[dict_resp[i]["rn"]] = (dict_resp[i]["lbl"][0])

    return charger_list


def get_unit_price(charger_list, msg):
    msg["Chargerid"]
    key_list = list(charger_list.keys())
    val_list = list(charger_list.values())
    position = val_list.index(str(msg["Chargerid"]))
    response = get_latest_data(Node="Charger-Info", user=key_list[position])
    data_of_charger = eval(eval(response.text)['m2m:cin']['con'])

    return data_of_charger[0], key_list[position]


def verify_transaction(msg):

    # msg = {"Amount": 99, "VehicleidTag": "216950627631",
    #        "Time": time.time(), "Chargerid": 1}

    User_list = get_users()
    charger_list = get_chargers()

    unit_price, charger_name = get_unit_price(charger_list, msg)
    print(unit_price)
    print(charger_list)
    print(User_list)

    if(msg["VehicleidTag"] in User_list.values()):
        print("User Found")
        user_key_list = list(User_list.keys())
        user_val_list = list(User_list.values())
        user_position = user_val_list.index(msg["VehicleidTag"])
        print(user_key_list[user_position])

        response = get_latest_data(
            Node="AE-EVcharger", user=user_key_list[user_position])

        data_of_user = eval(eval(response.text)['m2m:cin']['con'])

        if check_sufficient_balance(data_of_user, msg):
            print("Sufficient Balance")
            print("Transaction Approved")
            Txn_data = {"Txn_Amount": msg["Amount"],
                        "Txn_Balance": data_of_user[2] - msg["Amount"]}

            Charger_Txn_data = [unit_price, msg["Amount"],
                                msg["VehicleidTag"], time.time()]

            post_txn_data(Node="AE-EVcharger",
                          user=user_key_list[user_position], data=Txn_data)

            post_charger_txn_data(Node="Charger-Info",
                                  user=charger_name, data=Charger_Txn_data)

            return "Transaction Approved"
        else:
            print("Insufficient Balance")
            print("Transaction Declined")
            return "Insufficient Balance"
