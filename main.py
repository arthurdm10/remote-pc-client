from local_pc.local_pc import LocalPc
import json
import pyqrcode
import threading
import argparse
from time import sleep

parser = argparse.ArgumentParser()







localPc = LocalPc("fc58161e6b0da8e0cae8248f40141165", "localhost")

while True:
    sleep(2)
    localPc.run()


# qrContent = json.dumps({"remote_server": localPc.remoteServerUrl, "pc_key": localPc.key})
# qrcode = pyqrcode.create(qrContent)


# qrThread = threading.Thread(target=qrcode.show, args=(1000,))
# qrThread.start()
