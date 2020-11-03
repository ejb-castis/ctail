import os
import unittest
import jtail as ctail

class CtailTests(unittest.TestCase):
  def setUp(self):
    self.dir = "unittest/test"
    try:
      exist = os.path.exists(self.dir)
      if exist == False:
        os.makedirs(self.dir)
    except OSError as e:
        print "error : %s, %s" % (self.dir, e)
    else:
        print "made dir : %s" % (self.dir)

  def tearDown(self):
    os.removedirs(self.dir)
    print "removed dir : %s" % (self.dir)

  # -f, 파일 크기가 2048보다 작은 경우
  def test_the_file_deleted_while_tailing_a_file(self):
        expected = True
        result = True
        self.assertEqual(result, expected)


# -f, tail 중인 파일이 지워지는 경우
  # def test_the_file_deleted_while_tailing_a_file(self):
  #     code = r"""
  #     a
  #     """
  #     expected = r"""
  #     a;
  #     """
  #     result = el.add_semicolon_to_end_of_statement(code)
  #     self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
