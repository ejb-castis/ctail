#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import unittest
import jtail as ctail


class CtailTests(unittest.TestCase):
    def setUp(self):
        self.dir = "unittest/test"
        self.file_name = "test.txt"
        self.file_path = self.dir + "/" + self.file_name
        self.another_file_name = "another.test.txt"
        self.another_file_path = self.dir + "/" + self.another_file_name
        try:
            exist = os.path.exists(self.dir)
            if exist == False:
                os.makedirs(self.dir)
        except OSError as e:
            print ("error : {}, {}".format(self.dir, e))
        else:
            print ("made dir : {}".format(self.dir))

    def tearDown(self):
        # os.remove(self.file_path)
        # os.remove(self.another_file_path)
        # os.removedirs(self.dir)
        print ("removed dir : {}".format(self.dir))
        pass

    def newFile(self, end):
        try:
            f = open(self.file_path, "w")
            for i in range(1, end+1):
                print >> f, "{:07}".format(i)
        finally:
            if f is not None:
                f.close()

    def appendFile(self, begin, end):
        try:
            f = open(self.file_path, "aw")
            for i in range(begin, end+1):
                print >> f, "{:07}".format(i)
        finally:
            if f is not None:
                f.close()

    def newAnotherFile(self, end):
        try:
            f = open(self.another_file_path, "w")
            for i in range(1, end+1):
                print >> f, "{:07}".format(i)
        finally:
            if f is not None:
                f.close()

    def appendAnotherFile(self, begin, end):
        try:
            f = open(self.another_file_path, "aw")
            for i in range(begin, end+1):
                print >> f, "{:07}".format(i)
        finally:
            if f is not None:
                f.close()


    # 파일 크기가 2048보다 작거나 같은 경우
    def test_the_filesize_eqless_than_2048(self):
        self.newFile(256)
        f = None
        try:
            ctail._verbose = False

            f, error = ctail.open_tail(self.file_path)
            self.assertEqual(False, error)

            offset = f.tell()
            size = os.path.getsize(self.file_path)
            #print("open, file path:{}, size:{}, offset:{}".format(self.file_path, size, offset))

            self.assertEqual(2048, size)
            self.assertEqual(0, offset)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    # 파일 크기가 2048보다 큰경우
    def test_the_filesize_greater_than_2048(self):
        self.newFile(257)
        f = None
        try:
            ctail._verbose = False

            f, error = ctail.open_tail(self.file_path)
            self.assertEqual(False, error)

            offset = f.tell()
            size = os.path.getsize(self.file_path)
            #print("open, file path:{}, size:{}, offset:{}".format(self.file_path, size, offset))

            self.assertEqual(2056, size)
            self.assertEqual(size - 2048, offset)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    # tail 중인 파일에 변화가 없는 경우
    def test_keep_tail_not_touched_file(self):
        self.newFile(1)
        f = None
        try:
            ctail._verbose = False

            f, error = ctail.open_tail(self.file_path)
            self.assertEqual(False, error)

            offset = f.tell()
            size = os.path.getsize(self.file_path)
            #print("open, file path:{}, size:{}, offset:{}".format(self.file_path, size, offset))
            self.assertEqual(8, size)
            self.assertEqual(0, offset)

            # 첫 번째 tail
            offset, error = ctail.keep_tail(f)
            #print("tail, file path:{}, size:{}, offset:{}".format(self.file_path, size, offset))
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

            # 두 번째 tail
            offset, error = ctail.keep_tail(f)
            #print("tail, file path:{}, size:{}, offset:{}".format(self.file_path, size, offset))
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    # tail 중인 파일에 변화가 있는 경우
    def test_keep_tail_touched_file(self):
        self.newFile(1)
        f = None
        try:
            ctail._verbose = False

            f, error = ctail.open_tail(self.file_path)
            self.assertEqual(False, error)

            offset = f.tell()
            size = os.path.getsize(self.file_path)
            #print("open, file path:{}, size:{}, offset:{}".format(self.file_path, size, offset))
            self.assertEqual(8, size)
            self.assertEqual(0, offset)

            # 첫 번째 tail
            offset, error = ctail.keep_tail(f)
            size = os.path.getsize(self.file_path)
            #print("tail, file path:{}, size:{}, offset:{}".format(self.file_path, size, offset))
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

            # 두 번째 tail
            offset, error = ctail.keep_tail(f)
            size = os.path.getsize(self.file_path)
            #print("tail, file path:{}, size:{}, offset:{}".format(self.file_path, size, offset))
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

            # file 변경 후 tail
            self.appendFile(2, 2)
            offset, error = ctail.keep_tail(f)
            size = os.path.getsize(self.file_path)
            #print("tail, file path:{}, size:{}, offset:{}".format(self.file_path, size, offset))
            self.assertEqual(False, error)
            self.assertEqual(16, size)
            self.assertEqual(16, offset)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    # file이 있는 folder 내의 최신 파일 찾기
    def test_find_the_newest_file(self):
        self.newFile(1)
        time.sleep(1)
        self.newAnotherFile(1)
        f = None
        try:
            ctail._verbose = False

            target, exist = ctail.get_tail_filename(self.file_path, False)
            abs_another_file_path = os.path.join(ctail.get_path_of(self.another_file_path), self.another_file_name)
            self.assertEqual(True, exist)
            self.assertEqual(abs_another_file_path, target)
            #print("get the newest file path:{} ".format(target))

            time.sleep(1)
            self.appendFile(2,2)

            target, exist = ctail.get_tail_filename(self.file_path, False)
            abs_file_path = os.path.join(ctail.get_path_of(self.file_path), self.file_name)
            self.assertEqual(True, exist)
            self.assertEqual(abs_file_path, target)
            #print("get the newest file path:{} ".format(target))

            time.sleep(1)
            self.appendAnotherFile(2,2)
            target, exist = ctail.get_tail_filename(self.file_path, False)
            abs_another_file_path = os.path.join(ctail.get_path_of(self.another_file_path), self.another_file_name)
            self.assertEqual(True, exist)
            self.assertEqual(abs_another_file_path, target)
            #print("get the newest file path:{} ".format(target))

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()


if __name__ == '__main__':
    unittest.main()
