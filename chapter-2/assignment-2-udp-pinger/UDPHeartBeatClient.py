import socket
import time

# Setup UDB socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(1)
serverHostname = 'localhost'
serverPort = 1502
sequence = 0
while True:
    try:
        # Send UDP ping packet
        localTime = time.localtime()
        message = 'Ping ' + str(sequence) + ' {:.3f}'.format(time.time())
        address = (serverHostname, serverPort)
        clientSocket.sendto(message.encode(), address)
        print('Sent:', message)
        sequence = sequence + 1
        time.sleep(1)
    except KeyboardInterrupt:
        break
clientSocket.close()

