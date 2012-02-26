from unittest import TestLoader, TextTestRunner, main, TestSuite
import sys

if __name__ == '__main__':
   if sys.argv[1:]:
      patterns = sys.argv[1:]
   else:
      patterns = ['test*.py', 'ft_*.py', 'it_*.py', 'rt_*.py']
   
   start_dir_tests = '.'
   loader = TestLoader()
   suite = TestSuite([loader.discover(start_dir_tests, pattern) for pattern in patterns])

   TextTestRunner(verbosity=1).run(suite)
