
import serial
import select
import socket  # Import socket module




def monitor_BR(ser): 
	# Create a serial connection
	sock_port = 6000 # Reserve a port for your service.
	# Create a socket object
	socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socks.bind((socket.gethostname(), sock_port))  # Bind to the port
	socks.listen(5)



	while True:
		# Establish connection with client.
		clientsocket, cli_address = socks.accept()
		print("Got a connection from %s" % str(cli_address))
		if ser.is_open:
			print("Serial port is open.")

			# Create a file descriptor for the serial port
			fd = ser.fileno()

			# Create lists for input and output
			inputs = [fd]
			outputs = []

		# Monitor the serial port for input and output
			while True:
				# Use select to monitor the file descriptors
				readable, writable, exceptional = select.select(
					inputs, outputs, inputs)

				# Handle readable file descriptors (input available to read)
				for file_descriptor in readable:
					if file_descriptor == fd:
						# Read data from the serial port
						data = ser.readline()
						print("Received:", data.decode().strip())
						clientsocket.send(data.decode().strip().encode())


				# Handle exceptional conditions
				for file_descriptor in exceptional:
					print("An exceptional condition occurred.")

			# Close the serial port
			ser.close()
			clientsocket.close()
			print("Serial port is closed. Client socket is closed.")
		else:
			print("Failed to open serial port.")
