import sys
sys.path.append("..")
# print(sys.path)

from remote_pc_py.local_pc.local_pc import LocalPc
import unittest


class TestLocalPc(unittest.TestCase):
    def test_pc_register(self):
       
       response = LocalPc.register_pc("localhost:9002", "admin", "admin", "userpc", "passwd", "mykey123")
       self.assertEqual(response, 201)

    def test_pc_register_fail_key_already_exists(self):
       response = LocalPc.register_pc("localhost:9002", "admin", "admin", "userpc", "passwd", "mykey123")
       self.assertEqual(response, 400)

    def test_user_register(self):
       response = LocalPc.register_user("localhost:9002", "admin", "admin", "user000", "passwd", "mykey123")
       self.assertEqual(response, 201)

    def test_user_register_fail_username_already_exists(self):
       response = LocalPc.register_user("localhost:9002", "admin", "admin", "user000", "passwd", "mykey123")
       self.assertEqual(response, 400)
       

if __name__ == '__main__':

    unittest.main()
