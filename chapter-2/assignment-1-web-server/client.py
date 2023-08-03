import socket
import sys

n = len(sys.argv)
if(n != 4):
    print('Supply hostname, port number, and filename as command line arguments')
    sys.exit()

# input configuration
hostname = sys.argv[1]
serverPort = int(sys.argv[2])
fileName = sys.argv[3]
# Create socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((hostname, serverPort))
# Send HTTP request
httpHeader = 'GET /' + fileName + ' HTTP/1.1\r\n\r\n'
clientSocket.send(httpHeader.encode())
# Receive response
foundContentLength = False
foundBodyStart = False
responseFinished = False
contentLength = 0
bodyStartIdx = 0
mergeResponse = ''
while not responseFinished:
    response = clientSocket.recv(1024)
    # Merge response into a single string
    mergeResponse = mergeResponse + response.decode()
    # Find content-length header
    if not foundContentLength:
        loc = mergeResponse.lower().find('content-length:')
        if loc != -1:
            contentLength = int(mergeResponse[loc:].split()[1])
            foundContentLength = True
            print('Found content-length header: ' + str(contentLength))
    # Find start of body
    elif not foundBodyStart:
        loc = mergeResponse.find('\r\n\r\n')
        if loc != -1:
            bodyStartIdx = loc + 4
            foundBodyStart = True
            print('Found start of body at: ' + str(bodyStartIdx))
    # Check if response is finished
    else:
        if(len(mergeResponse) - bodyStartIdx >= contentLength):
            responseFinished = True
# Print response
print(mergeResponse[bodyStartIdx:])
