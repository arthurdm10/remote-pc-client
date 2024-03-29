import os
from websocket import WebSocketApp
from websocket._abnf import ABNF
from threading import Event
from io import BytesIO
import pyscreenshot as pySs
import json
import psutil
import shutil
from tempfile import gettempdir

DEFAULT_BUFFER_SIZE = 8 * 1024

#TODO: IMPROVE ERROR HANDLING

def list_dir(args: list) -> list:
    
    fileToJson = lambda file: {
        "name": file.name,
        "is_dir": file.is_dir(),
        "size": file.stat().st_size
    }

    files = os.scandir(args[0])
    return list(map(fileToJson, list(files)))


def create_dir(args: list) -> None:
    os.mkdir(args[0])


def delete_file(args: list) -> bool:
    path = args[0]
    
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path, ignore_errors=True)
    return True




def rename_file(args: list) -> bool:
    src, dst = args[0], args[1]
    
    os.rename(src, dst)
    return True
    


# return a list of running processes, total usage of cpu and memory
def list_processes(_) -> dict:
    data = dict()
    mem = psutil.virtual_memory()
    data["memory"] = {"total": mem.total, "percent": mem.percent, "used": mem.used, "free": mem.available}
    data["cpu"] = {"percent": psutil.cpu_percent(0.2, True)}
    data["processes"] = list(map(lambda proc: proc.as_dict(attrs=['pid', 'name', 'memory_percent', 'cpu_percent']), list(psutil.process_iter())))
    return data

def kill_process(args: list) -> bool:
    if len(args) == 0:
        return False

    pid = args[0]

    if pid is None or pid <= 0:
        return False

    proc = psutil.Process(args[0])
    proc.kill()

    return proc.is_running()


def _send_cmd_response(wsConn: WebSocketApp, cmd: str, responseKey: str, response):
    wsConn.send(json.dumps({"cmd_response":cmd, responseKey: response}))

def _send_stream_canceled(wsConn: WebSocketApp, cmd: str):
    _send_cmd_response(wsConn, cmd, "canceled", True)


# download_file send a local file or a screnshot
# TODO: SEND FILE HASH
def download_file(args: list, wsConn: WebSocketApp, event: Event):
    fileName = args[0]
    
    if len(fileName) == 0 and args[1] == True:
        return screenshot(args, wsConn, event)

    if os.path.exists(fileName):
        isDir = os.path.isdir(fileName)
        if isDir:
            zipFileName = gettempdir() + "/" + os.path.basename(fileName)
            shutil.make_archive(zipFileName, "zip", fileName)
            fileName = zipFileName + ".zip"

        fileStat = os.stat(fileName)
        fileSize = fileStat.st_size

        if fileSize < 0:
            _send_cmd_response(wsConn, "download_file", "error", "File is empty")
        else:
            _send_cmd_response(wsConn, "download_file", "size", fileSize)

            with open(fileName, "rb") as file:
                bufferSize = DEFAULT_BUFFER_SIZE
                
                if fileSize < DEFAULT_BUFFER_SIZE:
                    bufferSize = fileSize
                    
                complete = _stream_data(file, bufferSize, wsConn, event)
                if not complete:
                    _send_stream_canceled(wsConn, "download_file")
                else:
                    # wsConn.send(json.dumps({"cmd_response": "download_file", "file_hash":"123"}))
                    _send_cmd_response(wsConn, "download_file", "file_hash", "123")
                    print("file sent")
                    
                    # if it is a directory, remove the temporary .zip file created
                    if isDir:
                        try:
                            os.remove(fileName)
                        except:
                            print(f"Failed to remove temporary file {fileName}")
    
    else:
        _send_cmd_response(wsConn, "download_file", "error", "Invalid file")


def screenshot(args: list, wsConn: WebSocketApp, event: Event):
    img = pySs.grab()
    buff = BytesIO()
    img.save(buff, format="jpeg", quality=30)
    _send_cmd_response(wsConn, "download_file", "size", buff.getbuffer().nbytes)

    buff.seek(0)

    complete = _stream_data(buff, DEFAULT_BUFFER_SIZE, wsConn, event)
    buff.close()

    if not complete:
        _send_stream_canceled(wsConn, "download_file")
    else:
        _send_cmd_response(wsConn, "download_file", "file_hash", "123")
        

#Send binary data from buffer through websocket
#event is used to cancel the stream
def _stream_data(buffer, bufferSize: int, wsConn: WebSocketApp, event: Event) -> bool:
    while True:
        data = buffer.read(bufferSize)
        if not data:
            break
        elif event.is_set():
            event.clear()
            return False
        
        wsConn.send(data, ABNF.OPCODE_BINARY)

    return True


available_cmds = {
	"ls_dir":      list_dir,
    "create_dir":   create_dir,
	"delete_file": delete_file,
	"rename_file": rename_file,
    "download_file": download_file,
    "screenshot": screenshot,
    "ls_ps": list_processes,
    "kill_ps": kill_process,
}