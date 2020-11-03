import os
import unittest
import jtail as ctail


class CtailTests(unittest.TestCase):
    def setUp(self):
        self.dir = "unittest/test"
        self.file_name = "test.txt"
        self.file_path = self.dir + "/" + self.file_name
        try:
            exist = os.path.exists(self.dir)
            if exist == False:
                os.makedirs(self.dir)
        except OSError as e:
            print ("error : {}, {}".format(self.dir, e))
        else:
            print ("made dir : {}".format(self.dir))

    def tearDown(self):
        os.remove(self.file_path)
        os.removedirs(self.dir)
        print ("removed dir : {}".format(self.dir))
        pass

    def newFile(self):
        try:
            f = open(self.file_path, "w")
            print >> f, "line:1"
        finally:
            if f is not None:
                f.close()

    def appendFile(self):
        try:
            f = open(self.file_path, "aw")
            print >> f, "line:1"
        finally:
            if f is not None:
                f.close()

    # -f, 파일 크기가 2048보다 작은 경우
    def test_the_file_deleted_while_tailing_a_file(self):
        self.newFile()

        f = None
        try:
          ctail._verbose = False

          f, error = ctail.open_tail(self.file_path)
          self.assertEqual(False, error)


          offset = f.tell()
          #print("file path:{}, offset:{}".format(self.file_path, offset))
          #제일 처음 부터 읽어들여야 함
          self.assertEqual(0, offset)

        except Exception as e:
          self.assertTrue(False, "error, {}".format(e))
        finally:
          if f is not None:
            f.close()


# -f, tail 중인 파일이 지워지는 경우

if __name__ == '__main__':
    unittest.main()
