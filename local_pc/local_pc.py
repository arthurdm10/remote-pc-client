import websocket
import json
from .commands import available_cmds
from urllib.parse import urlparse
import threading
import requests
from os import getcwd
from hashlib import sha256

class LocalPc:


    def __init__(self, username, password, key, remoteServer, initialDir=None):
        self.remoteServer = remoteServer
        self.remoteServerUrl = f"ws://{remoteServer}/connect/{key}"
        self.connectionUrl = f"ws://{remoteServer}/access/{key}"
        self.key = key
        
        
        self.initialDir = getcwd() if initialDir is None else initialDir


        on_open = lambda ws: self._on_open(ws)
        on_data = lambda ws, data, dataType, continues: self._on_data(ws,data, dataType, continues)
        on_error = lambda ws, error: self._on_error(ws, error)
        on_close = lambda ws: self._on_close(ws)

        self.streamThread = None
        self.streamCanceledEvent = threading.Event()

        self.wsConn = websocket.WebSocketApp(self.remoteServerUrl,
         on_open=on_open,
         on_data=on_data,
         on_close=on_close, 
         on_error=on_error,
         header=_credential_headers(username, password))

    def run(self):
        self.wsConn.run_forever()
    
    def _on_data(self, ws, data, dataType, continues):
        OPCODE_TEXT = 0x1
        OPCODE_BINARY = 0x2
        
        if dataType == OPCODE_TEXT:
            jsonData = json.loads(data)
            requestType = jsonData["type"]
            if requestType == "command":
                if jsonData["cmd"] == "initial_dir":
                    response = {"cmd_response": "initial_dir", "response": self.initialDir}
                    self.wsConn.send(json.dumps(response))
                else:
                    self.handle_command(jsonData)

            elif requestType == "info":
                if jsonData["code"] == 252:
                    print("New user connected!")

            elif requestType == "cancel_stream":
                if self.streamThread.is_alive():
                    self.streamCanceledEvent.set()

        elif dataType == OPCODE_BINARY:
            # no usage for now
            print("received binary data")
    
    def handle_command(self, cmdData):
        cmd = cmdData["cmd"]

        if cmd in available_cmds:
            cmdFunc = available_cmds[cmd]
            cmdArgs = cmdData["args"]
            
            if not cmdData["stream"]:
                response = {"cmd_response": cmd, "error_code": 0xffcc}
                try:
                    output = cmdFunc(cmdArgs)
                    response = {"cmd_response": cmd, "response": output}
                    self.wsConn.send(json.dumps(response))
                    return
                except FileNotFoundError:
                    response["error_msg"] = "File/directory not found"
                except FileExistsError:
                    response["error_msg"] = "File/directory already exists"
                except:
                    response["error_msg"] = "Unknown error"

                self.wsConn.send(json.dumps(response))
            else:
                self.streamThread = threading.Thread(target=cmdFunc, args=(cmdArgs, self.wsConn, self.streamCanceledEvent))
                self.streamThread.start()
        else:
            
            self.wsConn.send(json.dumps({"error": "Invalid command"}))


    def _on_error(self, ws, error):
        
        if error.status_code == 403:
            print("[!] Access Denied")
            exit(1)

        print(f"Error: {error}")
        exit(1)

    def _on_close(self, ws):
        self.wsConn.run_forever()

    def _on_open(self, ws):
        print(f"Connected to remote server: {self.remoteServer}")


    @staticmethod
    def register_pc(remoteServer, adminUsername, adminPassword, username, password, key: str) -> int:
        return _register("pc", remoteServer, adminUsername, adminPassword, username, password, key)

            

    # Create a new user that can be used to access this PC
    # adminUsername, adminPassword: Credentials defined on the remote server
    # key: The key used to register this PC
    @staticmethod
    def register_user(remoteServer, adminUsername, adminPassword, username, password, key: str) -> int:
        return _register("user", remoteServer, adminUsername, adminPassword, username, password, key)


    @staticmethod
    def set_user_permission(permissionsFile, remoteServer, adminUsername, adminPassword, key: str):
        try:
            with open(permissionsFile, "r") as file:
                permissions = json.loads(file.read())
                response = requests.post(f"http://{remoteServer}/set_user_permissions/{key}",
                                            headers=_credential_headers(adminUsername, adminPassword),
                                            json=permissions)
                return response.status_code
        except FileNotFoundError:
            print(f"File '{permissionsFile} not found!")
        except Exception as err:
            print(err)
        return -1    

def _credential_headers(username, password: str) -> dict:
    return {"X-Username":  _hash_sha256(username), "X-Password": _hash_sha256(password)}

def _hash_sha256(data: str) -> str:
    sha = sha256()
    sha.update(data.encode("utf-8"))
    return sha.hexdigest()

def _register(userType, remoteServer, adminUsername, adminPassword, username, password, key: str) -> int:
        path = "create_pc" if userType == "pc" else "create_user"
        
        jsonBody = {"username": _hash_sha256(username), "password": _hash_sha256(password)}
        
        if userType == "pc":
            jsonBody["key"] = key

        try:
            response = requests.post(f"http://{remoteServer}/{path}/{key}",
                                     headers=_credential_headers(adminUsername, adminPassword),
                                    json=jsonBody)
            return response.status_code
        except Exception as err:
            print(err)
        
        return 0
