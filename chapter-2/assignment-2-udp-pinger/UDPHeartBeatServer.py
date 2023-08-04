import socket
import time

# Create server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.settimeout(5)
serverPort = 1502
serverSocket.bind(('', serverPort))
# Client address to check for heart beat
clientHostName = 'localhost'
clientPort = 1502
lastSequence = -1
while True:
    try:
        message, clientAddress = serverSocket.recvfrom(1024)
        receivedSequence = int(message.decode().split()[1])
        receivedTimeStamp = float(message.decode().split()[2])
        delay = (time.time() - receivedTimeStamp) * 1e3
        if(receivedSequence - 1 != lastSequence):
            for i in range(lastSequence + 1, receivedSequence):
                print('Lost packet sequence {:d}'.format(i))
        print('Received sequence {:d}'.format(receivedSequence), 'Delay: {:.3f} ms'.format(delay))
        lastSequence = receivedSequence
    except socket.timeout:
        print('No heartbeat from client!')
        break
serverSocket.close()
