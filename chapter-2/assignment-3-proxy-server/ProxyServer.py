import socket
import os

def receiveResponse(sock):
    sock.settimeout(2)
    responseFinish = False
    remainingContent = 1024
    # Header processing variables
    bodyFound = False
    headerText = ''
    consecutiveNewLines = 0
    # Header processing varibales
    tfEncFound = False
    tfEncIdx = 0
    chuncked = False
    contentLengthFound = False
    contentLengthIdx = 0
    contentLength = 0
    # Chunck length processing
    chunckLengthFound = False
    chunckLengthString = ''
    # Body processing variables
    consumedContentLength = 0
    responseBody = list()
    while not responseFinish:
        try:
            # Receive response
            if chunckLengthFound:
                remainingContent = contentLength - consumedContentLength + 2
            elif contentLengthFound:
                remainingContent = contentLength - consumedContentLength
            response = list(sock.recv(min(remainingContent, 1024)))
            # Consume header text
            i = 0
            while i < len(response) and not bodyFound:
                c = chr(response[i]).lower()
                headerText += c
                if(c == '\n'):
                    consecutiveNewLines = consecutiveNewLines + 1
                elif(c != '\r'):
                    consecutiveNewLines = 0
                if(consecutiveNewLines == 2):
                    bodyFound = True
                    consecutiveNewLines = 0
                i = i + 1
            # Header processing
            if not tfEncFound:
                # Find transfer-encoding header
                tfEncIdx = headerText.find("transfer-encoding:")
                if tfEncIdx != -1:
                    tfEncFound = True
                    tfEncIdx = tfEncIdx + len("transfer-encoding:") + 1
                    chuncked = "chunked" == headerText[tfEncIdx:].split()[0]
                    print("transfer-encoding: " + headerText[tfEncIdx:].split()[0])
            if not contentLengthFound:
                # Find content-length header
                contentLengthIdx = headerText.find("content-length:")
                if contentLengthIdx != -1:
                    contentLengthFound = True
                    contentLengthIdx = contentLengthIdx + len("content-length:") + 1
                    contentLength = int(headerText[contentLengthIdx:].split()[0])
                    print("content-length: " + headerText[contentLengthIdx:].split()[0])
            # Chunck length processing
            if chuncked and not chunckLengthFound:
                while i < len(response) and not chunckLengthFound:
                    c = chr(response[i]).lower()
                    if (c >= '0' and c <= '9') or (c >= 'a' and c <= 'f'):
                        chunckLengthString += c
                    elif c == '\n':
                        chunckLengthFound = True
                        contentLength = int(chunckLengthString, 16)
                        print("chunck-length: " + str(contentLength))
                    i = i + 1
            # Body processing
            if bodyFound and not (chuncked and not chunckLengthFound):
                consumeNext = min(len(response) - i, contentLength - consumedContentLength)
                responseBody += response[i:i + consumeNext]
                consumedContentLength += consumeNext
            # Check if reached end of chunck / content
            if contentLengthFound and (consumedContentLength == contentLength):
                responseFinish = True
            elif chunckLengthFound and (consumedContentLength == contentLength):
                if contentLength == 0:
                    responseFinish = True
                consumedContentLength = 0
                chunckLengthFound = False
                chunckLengthString = ''
        except socket.timeout:
            print('Timed out')
            responseFinish = True
    return responseBody

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSerPort = 1502
tcpSerSock.bind(('', tcpSerPort))
tcpSerSock.listen(1)
while 1:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    message = tcpCliSock.recv(1024).decode()
    # Extract the filename from the given message
    cacheFileName = message.split()[1].partition("/")[2]
    hostname = cacheFileName.partition("/")[0]
    filename = cacheFileName.partition("/")[2]
    print('Requested hostname: ', hostname)
    print('Requested filename: ', filename)
    # Check wether the file exist in the cache
    try:
        f = open(cacheFileName, "rb")
        outputdata = f.read()
        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
        tcpCliSock.send(("Content-length: " + str(len(outputdata)) + "\r\n").encode())
        tcpCliSock.send("\r\n".encode())
        tcpCliSock.send(outputdata)
        print('Read from cache')
    # Error handling for file not found in cache
    except IOError:
        try:
            print('Requesting from the Internet')
            # Create a socket on the proxyserver
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the socket to port 80
            c.connect((hostname, 80))
            # Send HTTP request
            httpStatus = 'GET /' + filename + ' HTTP/1.1\r\n'
            httpHeader = 'Host: ' + hostname + '\r\n'
            c.send(httpStatus.encode())
            c.send(httpHeader.encode())
            c.send('\r\n'.encode())
            # Read the response
            response = receiveResponse(c)
            # Forward the response to client
            tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
            tcpCliSock.send(("Content-length: " + str(len(response)) + "\r\n").encode())
            tcpCliSock.send("\r\n".encode())
            tcpCliSock.send(bytes(response))
            # Save response to cache
            os.makedirs(os.path.dirname(cacheFileName), exist_ok=True)
            cacheFile = open(cacheFileName, "wb")
            cacheFile.write(bytes(response))
        except:
            # Request failed
            tcpCliSock.send("HTTP/1.0 404 Not Found\r\n\r\n".encode())
            print('Request error')
    # Close the client and the server sockets
    tcpCliSock.close()
