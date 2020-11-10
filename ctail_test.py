#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import unittest
import ctail as ctail


class CtailTests(unittest.TestCase):
    def setUp(self):
        self.dir = "unittest/test"
        self.file_name = "test.txt"
        self.file_path = self.dir + "/" + self.file_name
        self.another_file_name = "another.test.txt"
        self.another_file_path = self.dir + "/" + self.another_file_name
        self.soft_link_file_name = "softlink.txt"
        self.soft_link_file_path = self.dir + "/" + self.soft_link_file_name

        try:
            exist = os.path.exists(self.dir)
            if exist == False:
                os.makedirs(self.dir)
        except OSError as e:
            print ("error : {}, {}".format(self.dir, e))
        else:
            print ("made dir : {}".format(self.dir))

    def tearDown(self):
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)
        if os.path.isfile(self.another_file_path):
            os.remove(self.another_file_path)
        if os.path.islink(self.soft_link_file_path):
            os.remove(self.soft_link_file_path)
        os.removedirs(self.dir)

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

    def removeFile(self):
        try:
            if os.path.isfile(self.file_path):
                os.remove(self.file_path)
        except OSError as e:
            pass

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

    def removeAnotherFile(self):
        try:
            if os.path.isfile(self.another_file_path):
                os.remove(self.another_file_path)
        except OSError as e:
            pass

    def linkFile(self, original):
        try:
            if os.path.islink(self.soft_link_file_path):
                os.remove(self.soft_link_file_path)
            os.symlink(original, self.soft_link_file_path)
        except OSError as e:
            pass

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
            self.assertEqual(8, size)
            self.assertEqual(0, offset)

            # 첫 번째 tail
            offset, error = ctail.keep_tail(f)
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

            # 두 번째 tail
            offset, error = ctail.keep_tail(f)
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
            self.assertEqual(8, size)
            self.assertEqual(0, offset)

            # 첫 번째 tail
            offset, error = ctail.keep_tail(f)
            size = os.path.getsize(self.file_path)
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

            # 두 번째 tail
            offset, error = ctail.keep_tail(f)
            size = os.path.getsize(self.file_path)
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

            # file 변경 후 tail
            self.appendFile(2, 2)
            offset, error = ctail.keep_tail(f)
            size = os.path.getsize(self.file_path)
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
        time.sleep(0.1)
        self.newAnotherFile(1)
        f = None
        try:
            ctail._verbose = False
            abs_another_file_path = os.path.join(ctail.get_path_of(
                self.another_file_path), self.another_file_name)
            abs_file_path = os.path.join(
                ctail.get_path_of(self.file_path), self.file_name)

            target, exist, inode = ctail.get_tail_filename(
                self.file_path, False)
            self.assertEqual(True, exist)
            self.assertEqual(abs_another_file_path, target)

            time.sleep(0.1)
            self.appendFile(2, 2)

            target, exist, inode = ctail.get_tail_filename(
                self.file_path, False)
            self.assertEqual(True, exist)
            self.assertEqual(abs_file_path, target)

            time.sleep(0.1)
            self.appendAnotherFile(2, 2)

            target, exist, inode = ctail.get_tail_filename(
                self.file_path, False)
            self.assertEqual(True, exist)
            self.assertEqual(abs_another_file_path, target)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    # -f option 을 사용해서 최신 파일 찾기
    def test_find_the_file_with_option_f(self):
        self.newFile(1)
        time.sleep(0.1)
        self.newAnotherFile(1)
        f = None
        try:
            ctail._verbose = False
            ctail._follow_file = True

            target, exist, inode = ctail.get_tail_filename(
                self.file_path, True)
            self.assertEqual(True, exist)
            self.assertEqual(os.path.abspath(self.file_path), target)

            time.sleep(0.1)
            self.appendFile(2, 2)

            target, exist, inode = ctail.get_tail_filename(
                self.file_path, True)
            self.assertEqual(True, exist)
            self.assertEqual(os.path.abspath(self.file_path), target)

            time.sleep(0.1)
            self.appendAnotherFile(2, 2)

            target, exist, inode = ctail.get_tail_filename(
                self.file_path, True)
            self.assertEqual(True, exist)
            self.assertEqual(os.path.abspath(self.file_path), target)

            time.sleep(0.1)
            self.appendFile(3, 3)

            target, exist, inode = ctail.get_tail_filename(
                self.another_file_path, True)
            self.assertEqual(True, exist)
            self.assertEqual(os.path.abspath(self.another_file_path), target)

            time.sleep(0.1)
            self.appendAnotherFile(3, 3)

            target, exist, inode = ctail.get_tail_filename(
                self.another_file_path, True)
            self.assertEqual(True, exist)
            self.assertEqual(os.path.abspath(self.another_file_path), target)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    # -f option 을 tail 하기
    def test_keep_tail_the_file_with_option_f(self):
        self.newFile(1)
        time.sleep(0.1)
        self.newAnotherFile(1)
        f = None
        try:
            ctail._verbose = False
            ctail._follow_file = True

            target, exist, inode = ctail.get_tail_filename(
                self.file_path, True)
            self.assertEqual(True, exist)
            self.assertEqual(os.path.abspath(self.file_path), target)

            f, error = ctail.open_tail(target)
            self.assertEqual(False, error)

            offset = f.tell()
            size = os.path.getsize(target)
            self.assertEqual(8, size)
            self.assertEqual(0, offset)

            # 첫 번째 tail
            offset, error = ctail.keep_tail(f)
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

            # 두 번째 tail
            offset, error = ctail.keep_tail(f)
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

            time.sleep(0.1)
            self.appendFile(2, 2)
            time.sleep(0.1)
            self.appendAnotherFile(2, 2)

            # 세 번째 tail
            offset, error = ctail.keep_tail(f)
            size = os.path.getsize(target)
            self.assertEqual(False, error)
            self.assertEqual(16, size)
            self.assertEqual(16, offset)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    # open 할 때 error
    def test_first_error_in_opening_tail_the_file_with_option_f(self):
        self.newFile(1)
        f = None
        try:
            ctail._verbose = False
            ctail._follow_file = True

            target, exist, inode = ctail.get_tail_filename(
                self.file_path, True)
            self.assertEqual(True, exist)
            self.assertEqual(os.path.abspath(self.file_path), target)

            # file 이 지워지는 경우
            self.removeFile()

            f, error = ctail.open_tail(target)
            self.assertEqual(True, error)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    # test 해보니 open 후에 파일이 지워지면 에러가 안남
    def test_error_in_keeping_tail_the_file_with_option_f(self):
        self.newFile(1)
        f = None
        try:
            ctail._verbose = False
            ctail._follow_file = True

            target, exist, inode = ctail.get_tail_filename(
                self.file_path, True)
            print("get tail file:{}, {} ".format(
                os.path.abspath(self.file_path), target))
            self.assertEqual(True, exist)
            self.assertEqual(os.path.abspath(self.file_path), target)

            f, error = ctail.open_tail(target)
            self.assertEqual(False, error)

            offset = f.tell()
            size = os.path.getsize(target)
            self.assertEqual(8, size)
            self.assertEqual(0, offset)

            # 첫 번째 tail
            offset, error = ctail.keep_tail(f)
            self.assertEqual(False, error)
            self.assertEqual(8, size)
            self.assertEqual(8, offset)

            # file 이 지워지는 경우
            self.removeFile()

            # file 이 지워져도 f 가 유효한 건지, error가 나지 않음
            offset, error = ctail.keep_tail(f)
            self.assertEqual(False, error)
            self.assertEqual(8, offset)

            offset, error = ctail.keep_tail(f)
            self.assertEqual(False, error)
            self.assertEqual(8, offset)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    # -f option, soft link file 의 inode 값 변경
    def test_open_soft_link_change_point_with_option_f(self):
        self.newFile(1)
        self.newAnotherFile(1)
        f = None
        try:
            self.linkFile(self.file_name)
            original_path = os.readlink(self.soft_link_file_path)
            # print("link:{} to original:{} ".format(
            #     self.soft_link_file_path, original_path))

            ctail._verbose = False
            ctail._follow_file = True

            target, exist, inode = ctail.get_tail_filename(
                self.soft_link_file_path, True)

            #print("target:{}, exist:{}, inode:{} ".format(target, exist, inode))

            self.assertEqual(True, exist)
            self.assertEqual(os.path.abspath(self.soft_link_file_path), target)

            self.linkFile(self.another_file_name)
            original_path = os.readlink(self.soft_link_file_path)
            # print("link:{} to original:{} ".format(
            #     self.soft_link_file_path, original_path))

            target, exist, new_inode = ctail.get_tail_filename(
                self.soft_link_file_path, True)

            #print("target:{}, exist:{}, inode:{} ".format(target, exist, new_inode))

            self.assertEqual(True, exist)
            self.assertNotEqual(inode, new_inode)

        except Exception as e:
            self.assertTrue(False, "error, {}".format(e))
        finally:
            if f is not None:
                f.close()

    def test_exists_isfile_isdir_islink_to_soft_link(self):
        self.newFile(1)
        self.linkFile(self.file_name)
        file = self.soft_link_file_path

        self.assertEqual(True, os.path.exists(file))
        self.assertEqual(True, os.path.isfile(file))
        self.assertEqual(False, os.path.isdir(file))
        self.assertEqual(True, os.path.islink(file))


if __name__ == '__main__':
    unittest.main()
