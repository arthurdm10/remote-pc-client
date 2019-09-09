import sys
sys.path.append("..")
# print(sys.path)

from remote_pc_py.local_pc import commands
import unittest


class TestCommands(unittest.TestCase):
    testFolder = "./test/test_folder"
    def test_ls_dir(self):
        files = commands.list_dir([self.testFolder])
        
        self.assertIsInstance(files, list)

        for file in files:
            self.assertEqual(list(file.keys()), ["name", "is_dir", "size"])
            self.assertIsNotNone(file["name"])
            self.assertIsNotNone(file["is_dir"])
            self.assertIsNotNone(file["size"])

    def test_delete_file(self):
        fileName = f"{self.testFolder}/file000"
        file = open(fileName, "w")
        file.close()

        success = commands.delete_file([fileName])
        self.assertTrue(success)

if __name__ == '__main__':

    unittest.main()
