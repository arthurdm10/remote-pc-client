import sys
sys.path.append("..")
# print(sys.path)

from remote_pc_py.local_pc import local_pc
import unittest


class TestLocalPc(unittest.TestCase):
    def test_server_url(self):
        localPc = local_pc.LocalPc("123", "localhost")
        self.assertEqual(localPc.wsConn.url,
                         "ws://localhost:9002/create/123")
    
if __name__ == '__main__':

    unittest.main()
