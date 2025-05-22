
import socket
import serial
import time
import select

# This file sits between our UI and Wi-SUN Node.
# It communicates serially via the Wi-SUN node and through a server to our UI script.

def sendBR(port=6002):
    print("BRscript: Starting BR communication script...")
    time.sleep(1)

    try:
        # Create a serial connection - For communicating to Wi-SUN Node
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Timeout added for better responsiveness

        # Socket connection to communicate with the UI script.
        sock_port = port  # Reserve a port for your service.
        socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socks.bind((socket.gethostname(), sock_port))  # Bind to the port
        socks.listen(5)
        print(f"BRscript: Listening for incoming connections on port {sock_port}...")

        while True:
            # Establish connection with client.
            clientsocket, cli_address = socks.accept()
            print("BRscript: Got a connection from %s" % str(cli_address))

            if ser.is_open:
                print("BRscript: Socket connection and Serial port are open.")

                # Create file descriptors for the serial port and client socket
                inputs = [ser, clientsocket]

                # Monitor both the serial port and client socket for input
                while True:
                    try:
                        readable, _, exceptional = select.select(inputs, [], inputs, 1)  # Timeout for select

                        # Handle readable file descriptors (input available to read)
                        for source in readable:
                            if source is ser:
                                # Read data from the serial port and send it to the client
                                data = ser.readline().decode().strip()
                                if data:
                                    print(f"BRscript: Received from serial: {data}")
                                    clientsocket.send(data.encode())

                            elif source is clientsocket:
                                # Read data from the client and write it to the serial port
                                data = clientsocket.recv(1024).decode().strip()
                                if data:
                                    print(f"BRscript: Received from client: {data}")
                                    ser.write((data + '\n').encode())  # Adding newline to ensure proper sending to serial

                        # Handle exceptional conditions
                        for source in exceptional:
                            print("BRscript: An exceptional condition occurred.")
                            inputs.remove(source)
                            source.close()

                            # Exit the inner loop to wait for a new connection if the client disconnected
                            break

                    except Exception as e:
                        print(f"BRscript: Exception occurred while reading/writing: {e}")
                        clientsocket.close()
                        break

            else:
                print("BRscript: Failed to open serial port.")
                break

    except serial.SerialException as e:
        print(f"BRscript: SerialException: {e}")
    except socket.error as e:
        print(f"BRscript: Socket error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
        print("BRscript: Serial port is closed.")
        if 'clientsocket' in locals():
            clientsocket.close()
        print("BRscript: Client socket is closed.")

