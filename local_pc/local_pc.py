import websocket
import json
from .commands import available_cmds
from urllib.parse import urlparse


class LocalPc:


    def __init__(self, key, remoteServer, remotePort=9002):
        remoteServerUrl = f"ws://{remoteServer}:{remotePort}/create/{key}"
        
        on_open = lambda ws: self._on_open(ws)
        on_data = lambda ws, data, dataType, continues: self._on_data(ws,data, dataType, continues)
        on_error = lambda ws, error: self._on_error(ws, error)
        on_close = lambda ws: self._on_close(ws)


        self.wsConn = websocket.WebSocketApp(remoteServerUrl, on_open=on_open, on_data=on_data, on_close=on_close, on_error=on_error)

    def run(self):
        self.wsConn.run_forever()
    
    def _on_data(self, ws, data, dataType, continues):
        OPCODE_TEXT = 0x1
        OPCODE_BINARY = 0x2
        
        if dataType == OPCODE_TEXT:
            jsonData = json.loads(data)
            if jsonData["type"] == "command":
                self.handle_command(jsonData)
            elif jsonData["type"] == "info":
                print("received info")

        elif dataType == OPCODE_BINARY:
            print("receveid binary data")

    def handle_command(self, cmdData):
        cmd = cmdData["cmd"]

        if cmd in available_cmds:
            cmdFunc = available_cmds[cmd]
            try:
                output = cmdFunc(cmdData["args"])
                response = {"cmd_response": cmd, "data": output}
            except Exception as e:
                response = {"cmd_response": cmd, "error": str(e)}

            self.wsConn.send(json.dumps(response))

        else:
            print(f"command '{cmd}' not found")
            self.wsConn.send(json.dumps(output))


    def _on_error(self, ws, error):
        print(error)

    def _on_close(self, ws):
        print("### closed ###")

    def _on_open(self, ws):
        print("Connected to remote server")


