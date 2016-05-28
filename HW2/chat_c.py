import socket
import threading
import sys
import json
import re
import shutil


def recv_data():
    while True:
        data = s.recv(1024)
        json_data = json.loads(data.decode('utf-8'))
        if json_data["command"] == "talk":
            global talking
            talking = True
            global friend_name
            friend_name = json_data["value"]["friend name"]
            message = json_data["value"]["news"]
            print(friend_name, ':', message, file=sys.stderr)

        elif json_data["command"] == "friend_list":
            friend_name = json_data["friend_name"]
            statue = json_data["statue"]
            print(friend_name, statue, file=sys.stderr)

        elif json_data["command"] == "add":
            friend_name = json_data["friend_name"]
            print(friend_name, "added into the friend list", file=sys.stderr)

        elif json_data["command"] == "rm":
            friend_name = json_data["friend_name"]
            print(friend_name, "removed from the friend list", file=sys.stderr)

        elif json_data["command"] == "send message":
            print(json_data["message"], file=sys.stderr)

        elif json_data["command"] == "send file":
            if json_data["response"] == "empty":
                friend_name = json_data["friend_name"]
                print(friend_name, "want transmit file to you")
                friend_name = json_data["friend_name"]
            elif json_data["response"] == "yes":
                friend_name = json_data["friend_name"]
                filename = json_data["filename"]
                shutil.copy(filename, friend_name)
                i = 0
                while i <= 100:
                    print(i,  '% of', filename, 'transmitted...', file=sys.stderr)
                    i += 25
                    if i == 100:
                        print("end of file transmission")

            else:
                print("denied from", friend_name)

        elif json_data["command"] == "offline message":
            print('Message from', json_data["message"], file=sys.stderr)

        else:
            print(json_data["error"], file=sys.stderr)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('127.0.0.1', 9999)
print('connecting to %s port %s' % server_address, file=sys.stderr)
s.connect(server_address)
login = False
talking = False

while not login:
    try:
        # Send username and password
        username = input("Please enter username: ")
        password = input("please enter password: ")
        message = '{"command":"login","value":{"username":"' + username + '","password":"' + password + '"}}'
        s.send(message.encode('utf-8'))

        data = s.recv(1024)
        json_data = json.loads(data.decode('utf-8'))
        if json_data['code'] == "100":
            login = True
            print('login success', file=sys.stderr)
        else:
            print(json_data["message"], file=sys.stderr)
    except ValueError:
        print('oops! something wrong')

t = threading.Thread(target=recv_data, args=(), daemon=True)
t.start()

command = input(">")
while command != "log out":
    try:
        if command == "friend list":
            message = '{"command":"friend list"}'
            s.send(message.encode('utf-8'))
            command = input(">")

        elif command.startswith("friend add"):
            re.split(r'\s', command)
            friend_name = re.split(r'\s', command)[2]
            message = '{"command":"friend add","value":{"friend_name":"' + friend_name + '"}}'
            s.send(message.encode('utf-8'))
            command = input(">")

        elif command.startswith("friend rm"):
            re.split(r'\s', command)
            friend_name = re.split(r'\s', command)[2]
            message = '{"command":"friend rm","value":{"friend_name":"' + friend_name + '"}}'
            s.send(message.encode('utf-8'))
            command = input(">")

        elif command.startswith("sendfile"):
            re.split(r'\s', command)
            friend_name = re.split(r'\s', command)[1]
            filename = re.split(r'\s', command)[2]
            message = '{"command":"send file","value":{"friend_name":"' + friend_name + '", "username":"' + username + '", "filename":"' + filename + '", "response":"empty"}}'
            s.send(message.encode('utf-8'))
            command = input(">")

        elif command.startswith("send"):
            re.split(r'\s', command)
            friend_name = re.split(r'\s', command)[1]
            news = re.split(r'\s', command)[2]
            message = '{"command":"send message","value":{"friend_name":"' + friend_name + '", "news":"' + news + '"}}'
            s.send(message.encode('utf-8'))
            command = input(">")

        elif command.startswith("talk"):
            re.split(r'\s', command)
            friend_name = re.split(r'\s', command)[1]
            message = '{"command":"talk","value":{"friend_name":"' + friend_name + '", "message":"'' \
            ''start a conversation with ' + username + '"}}'
            s.send(message.encode('utf-8'))
            print("start a conversation with", friend_name)
            command = input(">")

        elif talking:
            message = '{"command":"talk","value":{"friend_name":"' + friend_name + '", "message":"' + command + '"}}'
            s.send(message.encode('utf-8'))
            command = input('>')

        elif command == 'yes':
            message = '{"command":"send file","value":{"friend_name":"' + friend_name + '", "response":"yes"}}'
            s.send(message.encode('utf-8'))
            command = input('>')

        elif command == 'no':
            message = '{"command":"send file","value":{"friend_name":"' + friend_name + '", "response":"no"}}'
            s.send(message.encode('utf-8'))
            command = input('>')

        elif command == "":
            command = input(">")

        else:
            print('INVALID COMMAND!!!', file=sys.stderr)
            command = input(">")

    except ValueError:
        print('oops! something wrong')

message = '{"command":"log out"}'
s.send(message.encode('utf-8'))
print('log out', file=sys.stderr)
s.close()
