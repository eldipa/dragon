import unittest
import os.path as Path
import os
import sys

class QualityAssuranceCodingStyle(unittest.TestCase):
   from pylint.reporters import BaseReporter
   class SilentReporter(BaseReporter):
      def __init__(self):
         self.msg = []
      def add_message(self, msg_id, location, msg):
         if msg_id[0] != 'I':
            self.msg.append((msg_id, "->".join(location[1:-2]) + ":%i:%i" % location[-2:], msg))
      def display_results(self, _layout):
         pass
      def writeln(self, _string=''):
         pass

   def setUp(self):
      self.style = Path.join(Path.dirname(__file__), "coding_style.txt")
      self.src_basepath = Path.join(Path.dirname(__file__), "..", "dragon")

   def test_coding(self):
      from pylint.lint import Run
      from pylint.reporters.text import TextReporter
      reporter = QualityAssuranceCodingStyle.SilentReporter()
      Run([("--rcfile=%s" % self.style), self.src_basepath], reporter=reporter, exit=False)

      if len(reporter.msg):
         print
         for msg in reporter.msg:
            print ' '.join(msg)

      self.assertTrue(len(reporter.msg) == 0)

if __name__ == '__main__':
   unittest.main()
