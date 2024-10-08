import socket
import wisun_comms
import Onem_evcharger

HOST_IP = "fd12:3456::1"

UDP_send_IP = "fd12:3456::5232:5fff:fe42:615b"

UDP_send_PORT = 5001
UDP_rec_PORT = 5005

sock_recv = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)  # UDP
sock_recv.bind((HOST_IP, UDP_rec_PORT))

sock_send = socket.socket(socket.AF_INET6,  # Internet
                          socket.SOCK_DGRAM)  # UDP

valid_id = ["216950627631"]

while True:
    data, addr = sock_recv.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message: %s" % data)
    data = data.decode('utf-8')

    # Example: "{'Amount': 99, 'VehicleidTag': '216950627631', 'Time': 1620000000, 'Chargerid': 'EV-L001-03'}"
    txn_response = Onem_evcharger.verify_transaction(eval(data))

    if "idTag" in str(data):
        if txn_response == "Transaction Approved":
            wisun_comms.send_toserver(
                "valid_yes", sock_send, UDP_send_IP, UDP_send_PORT)
        elif txn_response == "Insufficient Balance":
            wisun_comms.send_toserver(
                "valid_insuff", sock_send, UDP_send_IP, UDP_send_PORT)
        else:
            wisun_comms.send_toserver(
                "valid_not", sock_send, UDP_send_IP, UDP_send_PORT)
