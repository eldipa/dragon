import unittest
import os.path as Path
import os


class QualityAssuranceLicense(unittest.TestCase):
   def setUp(self):
      self.count = 10  #The first 10 lines of each file
      self.basepath = Path.join(Path.dirname(__file__), "..")
      self.src_basepath = Path.join(self.basepath, "dragon")

      self.src_mark = '''
#########################################################################
#                                                                       #
#                        This work is licensed under a                  #
#   CC BY-SA        Creative Commons Attribution-ShareAlike             #
#                           3.0 Unported License.                       #
#                                                                       #
#########################################################################
'''.strip()

   def test_license_file(self):
      self.assertTrue(Path.isfile(Path.join(self.basepath, "license.txt")))

   def _thrower(self, error):
      raise error

   def test_license_marks_in_python_modules(self):
      for dirpath, dirnames, filenames in os.walk(self.src_basepath, onerror=self._thrower):
         for filename in filenames:
            ext = Path.splitext(filename)[1]
            if ext == ".py":
               with open(Path.join(dirpath, filename), "rt") as source:
                  first_lines = []
                  count = self.count
                  for line in source:
                     first_lines.append(line)
                     count -= 1
                     if not count:
                        break

                  header = "".join(first_lines)
                  self.assertTrue(self.src_mark in header)


if __name__ == '__main__':
   unittest.main()
