import websocket
import json
from .commands import available_cmds
from urllib.parse import urlparse
import threading


class LocalPc:


    def __init__(self, key, remoteServer, remotePort=9002):
        self.remoteServerUrl = f"ws://{remoteServer}:{remotePort}/connect/{key}"
        self.connectionUrl = f"ws://{remoteServer}:{remotePort}/access/{key}"
        self.key = key
        
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
         header={"X-Username": "username", "X-Password": "passwd"})

    def run(self):
        self.wsConn.run_forever()
    
    def _on_data(self, ws, data, dataType, continues):
        OPCODE_TEXT = 0x1
        OPCODE_BINARY = 0x2
        
        if dataType == OPCODE_TEXT:
            jsonData = json.loads(data)
            requestType = jsonData["type"]
            if requestType == "command":
                self.handle_command(jsonData)
            elif requestType == "info":
                print(jsonData)
            elif requestType == "cancel_stream":
                # cancel the current running stream
                if self.streamThread.is_alive():
                    self.streamCanceledEvent.set()

        elif dataType == OPCODE_BINARY:
            print("received binary data")

    def handle_command(self, cmdData):
        cmd = cmdData["cmd"]

        if cmd in available_cmds:
            cmdFunc = available_cmds[cmd]
            cmdArgs = cmdData["args"]
            print(cmdData)
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
                    # response = {"cmd_response": cmd, "error_code": 0xffcc, "error_msg": str(e)}

                self.wsConn.send(json.dumps(response))
            else:
                self.streamThread = threading.Thread(target=cmdFunc, args=(cmdArgs, self.wsConn, self.streamCanceledEvent))
                self.streamThread.start()
                # cmdFunc(cmdArgs, self.wsConn)
        else:
            print(f"command '{cmd}' not found")
            self.wsConn.send(json.dumps({"error": "Invalid command"}))


    def _on_error(self, ws, error):
        pass
        # print(f"Error: {error}")

    def _on_close(self, ws):
        self.wsConn.run_forever()

    def _on_open(self, ws):
        print("Connected to remote server")


