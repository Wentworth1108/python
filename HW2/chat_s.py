import socket
import sys
import json
import threading

info = {'wen': {'password': '1234', 'friends': ['john', 'mary'], 'statue': 'offline', 'message': 'empty', 'friendname': 'empty', 'filename': 'empty', 'sock': 0},
        'john': {'password': '2345', 'friends': ['mary', 'tom'], 'statue': 'offline', 'message': 'empty', 'friendname': 'empty', 'filename': 'empty', 'sock': 0},
        'mary': {'password': '3456', 'friends': ['john', 'tom'], 'statue': 'offline', 'message': 'empty', 'friendname': 'empty', 'filename': 'empty', 'sock': 0},
        'tom': {'password': '4567', 'friends': ['john', 'mary'], 'statue': 'offline', 'message': 'empty', 'friendname': 'empty', 'filename': 'empty', 'sock': 0}}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 9999))
s.listen(5)
print('Waiting for connection...')


def client_thread(sock, addr):
    while True:
        # Wait for a connection
        try:
            print('connection from', addr, file=sys.stderr)
            while True:
                data = sock.recv(1024)
                print('received "%s"' % data, file=sys.stderr)
                if data:
                    print('sending data back to the client', file=sys.stderr)
                    json_data = json.loads(data.decode('utf-8'))
                    if json_data["command"] == "login":
                        for key in info:
                            if json_data["value"]["username"] == key and json_data["value"]["password"] == \
                                    info[key]['password']:
                                current_client_name = key
                                info[key]['sock'] = sock
                                info[key]['statue'] = 'online'
                                message = '{"code":"100","message":"login success"}'
                                break
                            else:
                                message = '{"code":"99","message":"Wrong username or password"}'

                        sock.sendall(message.encode('utf-8'))

                        if info[key]['message'] != 'empty':
                            news = info[current_client_name]['message']
                            print(news)
                            sock.sendall(news.encode('utf-8'))
                            info[current_client_name]["message"] = 'empty'

                    elif json_data["command"] == "friend list":
                        friend_list = info[current_client_name]['friends']
                        print(friend_list)
                        i = 0
                        while i < len(friend_list):
                            friend_name = friend_list[i]
                            statue = info[friend_name]['statue']
                            message = '{"command":"friend_list","friend_name":"' + friend_name + '","statue":"' + statue + '"}'
                            i += 1
                            sock.sendall(message.encode('utf-8'))

                    elif json_data["command"] == "friend add":
                        friend_name = json_data['value']['friend_name']
                        info[current_client_name]['friends'].append(friend_name)
                        message = '{"command":"add", "friend_name":"' + friend_name + '"}'
                        sock.sendall(message.encode('utf-8'))

                    elif json_data["command"] == "friend rm":
                        friend_list = info[current_client_name]['friends']
                        friend_name = json_data['value']['friend_name']
                        index = friend_list.index(friend_name)
                        friend_list.pop(index)
                        message = '{"command":"rm", "friend_name":"' + friend_name + '"}'
                        sock.sendall(message.encode('utf-8'))

                    elif json_data["command"] == "send message":
                        friend_name = json_data['value']['friend_name']
                        news = json_data['value']['news']
                        friend_sock = info[friend_name]['sock']
                        statue = info[friend_name]['statue']
                        if statue == 'online':
                            message = '{"command":"send message", "message":"' + current_client_name + ': ' + news + '"}'
                            friend_sock.sendall(message.encode('utf-8'))
                        else:
                            message = '{"command":"offline message", "message":"' + current_client_name + ': ' + news + '"}'
                            info[friend_name]["message"] = message

                    elif json_data["command"] == "send file":
                        friend_name = json_data['value']['friend_name']
                        response = json_data['value']['response']
                        if response == 'empty':
                            filename = json_data['value']['filename']
                            username = json_data['value']['username']
                            friend_sock = info[friend_name]['sock']
                            info[friend_name]["friendname"] = username
                            info[friend_name]["filename"] = filename
                            message = '{"command":"send file", "filename":"' + filename + '", "friend_name":"' + friend_name + '", "response":"empty"}'
                            friend_sock.sendall(message.encode('utf-8'))
                        elif response == 'yes':
                            username = info[friend_name]["friendname"]
                            friend_sock = info[username]['sock']
                            filename = info[friend_name]["filename"]
                            message = '{"command":"send file", "filename":"' + filename + '", "friend_name":"' + friend_name + '", "response":"yes"}'
                            friend_sock.sendall(message.encode('utf-8'))
                        elif response == 'no':
                            username = info[friend_name]["friendname"]
                            friend_sock = info[username]['sock']
                            message = '{"command":"send file", "friend_name":"' + username + '", "response":"no"}'
                            friend_sock.sendall(message.encode('utf-8'))

                    elif json_data["command"] == "talk":
                        friend_name = json_data['value']['friend_name']
                        friend_sock = info[friend_name]['sock']
                        news = json_data['value']['message']
                        message = '{"command":"talk", "value":{"friend name":"' + current_client_name + '", "news":"' + news + '"}}'
                        friend_sock.sendall(message.encode('utf-8'))

                    elif json_data["command"] == "log out":
                        info[current_client_name]['statue'] = 'offline'

                else:
                    print('no more data from', addr, file=sys.stderr)
                    break

        finally:
            sock.close()
            print('Connection from %s:%s closed.' % addr)


while True:
    sock, addr = s.accept()
    t = threading.Thread(target=client_thread, args=(sock, addr))
    t.start()
