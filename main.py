from local_pc.local_pc import LocalPc
import json
import pyqrcode
import threading
import argparse
import sys
from time import sleep
from getpass import getpass
from uuid import uuid4
from hashlib import sha256

def random_key(n=8):
    return uuid4().hex[:n]

def read_admin_credentials():
    adminUsername = getpass("Admin username:")
    adminPassword = getpass("Admin password:")
    return (adminUsername, adminPassword)

# returns remoteServer, username and password
def get_args(start=2,n=3):
    return sys.argv[start:start+n]

def print_usage_and_quit():
    name = sys.argv[0]
    print(f'''
python {name} <server:port> <key>


To register this PC:
 python {name} register <server:port> <username> <password> [key]
\t<server:port>: Remote server
\t<username> <password>: Credentials used to connect to remote server
\t[key]: Used to connect to this PC - If not provided, a random key will be generated

To register a user:
 python {name} register-user <server:port> <username> <password> <key>
\t<server:port>: Remote server
\t<username> <password>: Users credentials used to connect to this PC
\t<key>: The key used when this PC was registered

To set users permissions:
python {name} user-permissions <permissions.json> <server:port> <key>
\t<permissions.json>: File with users permissions
\t<server:port>: Remote server
\t<key>: The key used when this PC was registered
''')
    exit(1)

argc = len(sys.argv)
if argc > 1:

    action = sys.argv[1]
    
    if action == "help":
        print_usage_and_quit()
    
    args = sys.argv[2:]
    argc = len(args)
    
    if action == "register":
        # key is optional
        if argc >= 3:
            remoteServer, username, password = get_args()

            # generate random key if not specified
            key = args[3] if argc >= 4 else  random_key()
            adminUsername, adminPassword = read_admin_credentials()


            responseCode = LocalPc.register_pc(remoteServer, adminUsername, adminPassword, username, password, key)
            
            if responseCode == 201:
                print('''[+] PC Registered!''')
                print(f"Your key is {key}, this key is used to identify your PC")
            elif responseCode == 403:
                print("[!] Permission denied")
            
            exit(0)
        else:
            print_usage_and_quit()
            
    elif action == "register-user":
        # key is required
        if argc >= 4:
            remoteServer, username, password, key = get_args(2, 4)
            adminUsername, adminPassword = read_admin_credentials()

            responseCode = LocalPc.register_user(remoteServer, adminUsername, adminPassword, username, password, key)

            if responseCode == 201:
                print("[+] User created")
            elif responseCode == 403:
                print("[!] Permission denied")
            elif responseCode == 404:
                print("[!] Could not find PC with key " + key)

            exit(0)
        else:
            print_usage_and_quit()

    elif action == "user-permissions":

        if argc < 3:
            print_usage_and_quit()

        permissionsFile, remoteServer, key = get_args(2, 3)
        adminUsername, adminPassword = read_admin_credentials()
        responseCode = LocalPc.set_user_permission(permissionsFile, remoteServer, adminUsername, adminPassword, key)
        
        if responseCode == 200:
            print("[+] User permissions updated!")
        elif responseCode == 403:
            print("[!] Permission denied")
        else:
            print("[!] Failed to set users permissions!")
        exit(0)



if len(sys.argv) < 3:
    print_usage_and_quit()



remoteServer, key = get_args(1,2)
username = getpass("Username:")
password = getpass("Password:")

localPc = LocalPc(username, password, key, remoteServer)

qrContent = json.dumps({"remote_server": remoteServer, "key": key})
qrcode = pyqrcode.create(qrContent)

qrcode.png("remote_pc_code.png", scale=4)


while True:
    localPc.run()
    sleep(2)


