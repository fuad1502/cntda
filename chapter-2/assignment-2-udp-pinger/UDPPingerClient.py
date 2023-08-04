import socket
import time

# Setup UDB socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(1)
serverHostname = 'localhost'
serverPort = 12000
nSend = 10
nLoss = 0
minDelay = 1
maxDelay = 0
averageDelay = 0
for i in range(nSend):
    # Send UDP ping packet
    localTime = time.localtime()
    message = 'Ping ' + str(i) + ' ' + time.strftime("%H:%M:%S", localTime) 
    address = (serverHostname, serverPort)
    clientSocket.sendto(message.encode(), address)
    timeSend = time.time()
    try:
        # Try to receive
        message, address = clientSocket.recvfrom(1024)
        # Calculate round-trip time and message
        timeReceive = time.time()
        delay = (timeReceive - timeSend) * 1e3
        print(message.decode(), 'RTT: ', '{:.3f}'.format(delay), ' ms')
        if(delay > maxDelay):
            maxDelay = delay
        elif(delay < minDelay):
            minDelay = delay
        averageDelay += delay
    except socket.timeout:
        # Handle request timeout
        print('Request timed out')
        nLoss += 1
# Print statistics
averageDelay = averageDelay / (nSend - nLoss)
lossRate = nLoss / nSend
print('Minimum delay:', '{:.3f}'.format(minDelay), 'ms, Maximum delay:', '{:.3f}'.format(maxDelay),\
      'ms, Average delay:', '{:.3f}'.format(averageDelay), 'ms, Packet loss:', '{:.3f}%'.format(lossRate * 100))
clientSocket.close()
