import requests
import time


def get_latest_data(Node="USER", user="USER-01"):

    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/AE-EV/{Node}/{user}/Transactions/la"

    payload = {}
    headers = {
        'X-M2M-Origin': 'dev_guest:dev_guest',
        'Accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    return response


def post_txn_data(Node="USER", user="USER-01", data=None):
    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/AE-EV/{Node}/{user}/Transactions"
    data = [time.time(), data["Txn_Amount"], data["Txn_Balance"]]
    payload = "{\n    \"m2m:cin\":{\n        \"lbl\":[\n            \"Transation_data-Time\",\n            \"Transaction Amount(IN RS)\",\n            \"Current Amount in User Account(IN RS)\"\n        ],\n        \"con\":\"%s\"\n\n    }\n}\n\n" % (
        data)
    headers = {
'X-M2M-Origin': 'dev_guest:dev_guest',
        'Content-Type': 'application/json;ty=4'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response


def post_charger_txn_data(Node="CHARGER", user="CHARGER-1", data=None):
    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/AE-EV/{Node}/{user}/Transactions"
    payload = "{\n    \"m2m:cin\":{\n        \"lbl\":[\n            \n        ],\n        \"con\":\"%s\"\n\n    }\n}\n\n" % (
        data)
    headers = {
'X-M2M-Origin': 'dev_guest:dev_guest',
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


def get_users(Node="AE-EV"):

    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/{Node}/USER?rcn=4"

    payload = {}
    headers = {
        'X-M2M-Origin': 'dev_guest:dev_guest',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    false = False
    nan = 0
#     print(response.text)
    dict_resp = eval(response.text)
    dict_resp = eval(str(dict_resp['m2m:cnt']))
    dict_resp = eval(str(dict_resp['m2m:cnt']))
    # print(dict_resp)
#     print(len(dict_resp))

    User_list = {}
    # print(f"User List dict: {dict_resp}")
    for i in range(len(dict_resp)):
        User_list[dict_resp[i]["rn"]] = (dict_resp[i]["lbl"][-1])

    return User_list


def get_chargers(Node="AE-EV"):

    url = f"http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/{Node}/CHARGER?rcn=4"

    payload = {}
    headers = {
        'X-M2M-Origin': 'dev_guest:dev_guest',
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    false = False
    nan = 0
#     print(response.text)

    dict_resp = eval(response.text)
    dict_resp = eval(str(dict_resp['m2m:cnt']))
    dict_resp = eval(str(dict_resp['m2m:cnt']))
    # print(dict_resp)
#     print(len(dict_resp))

    charger_list = {}

    # print(f"Charger List dict: {dict_resp}")
    for i in range(len(dict_resp)):
        charger_list[dict_resp[i]["rn"]] = (dict_resp[i]["lbl"][1])

    return charger_list


def get_unit_price(charger_list, msg):
    key_list = list(charger_list.keys())
    val_list = list(charger_list.values())
    position = key_list.index(str(msg["Chargerid"]))
    # print(position)
    # print(key_list[position])
    response = get_latest_data(Node="CHARGER", user=key_list[position])
    # print(response.text)
    data_of_charger = eval(eval(response.text)['m2m:cin']['con'])

    return data_of_charger[-1], key_list[position]


def verify_transaction(msg):

    # msg = {"Amount": 99, "VehicleidTag": "216950627631",
    #        "Time": time.time(), "Chargerid": 1}

    User_list = get_users()
    charger_list = get_chargers()

    unit_price, charger_name = get_unit_price(charger_list, msg)
    # print(f"Unit Price: {unit_price}")
    # print(User_list.values())
    # print(msg["VehicleidTag"])
    

    if(msg["VehicleidTag"] in User_list.values()):
        # print("User Found")
        user_key_list = list(User_list.keys())
        user_val_list = list(User_list.values())
        user_position = user_val_list.index(msg["VehicleidTag"])
        # print(user_key_list[user_position])

        response = get_latest_data(
            Node="USER", user=user_key_list[user_position])

        data_of_user = eval(eval(response.text)['m2m:cin']['con'])

        if check_sufficient_balance(data_of_user, msg):
            # print("Sufficient Balance")
            # print("Transaction Approved")
            Txn_data = {"Txn_Amount": msg["Amount"],
                        "Txn_Balance": data_of_user[2] - msg["Amount"]}
            # print(f"Txn data: {Txn_data}")
            Charger_Txn_data = [unit_price, msg["Amount"],
                                msg["VehicleidTag"], time.time()]

            response = post_txn_data(Node="USER",user=user_key_list[user_position], data=Txn_data)

            response = post_charger_txn_data(Node="CHARGER",
                                  user=charger_name, data=Charger_Txn_data)
            # print(f"Response: {response}")


            return "Transaction Approved"
        else:
            print("Insufficient Balance")
            print("Transaction Declined")
            return "Insufficient Balance"
        


if __name__ == "__main__":
    get_chargers()
    get_users()
