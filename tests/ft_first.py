import unittest
from grammar import Grammar
from util import first

class FunctionalTestFirst(unittest.TestCase):
   def setUp(self):
      self.simple = Grammar('S', ('a', 'b', 's'))

      self.simple.add_rule('S', ('A', 'B', 's'))

      self.simple.add_rule('A', ('a', 'A', 'A'))
      self.simple.add_empty('A')

      self.simple.add_rule('B', ('b', 'B', 'B'))
      self.simple.add_empty('B')

      self.lrvalue = Grammar('S', ('=', '*', '(', ')', 'id'))

      self.lrvalue.add_rule('S', ['L', '=', 'R'])
      self.lrvalue.add_rule('S', ['R'])
      self.lrvalue.add_rule('L', ['*', 'R'])
      self.lrvalue.add_rule('L', ['id'])
      self.lrvalue.add_rule('R', ['L'])
      self.lrvalue.add_rule('R', ['(', 'S', ')'])

      self.simple_terminal = Grammar('S', ('$',))

      self.simple_terminal.add_rule('S', ['$'])

      self.more_complex = Grammar('S', ['a', 'b', 'c', 'd', 'q', 'r'])

      self.more_complex.add_rule('S', ['A', 'q'])
      self.more_complex.add_rule('S', ['B', 'r'])

      self.more_complex.add_rule('A', ['C', 'a'])
      self.more_complex.add_empty('A')

      self.more_complex.add_rule('B', ['D', 'b'])
      
      self.more_complex.add_rule('C', ['c'])
      self.more_complex.add_empty('C')
      
      self.more_complex.add_rule('D', ['d'])
      self.more_complex.add_empty('D')

      self.left_recursive = Grammar('E', ('+', '-', 'id', '(', ')'))

      self.left_recursive.add_rule('E', ['E', '+', 'T'])
      self.left_recursive.add_rule('E', ['E', '-', 'T'])
      self.left_recursive.add_rule('E', ['T'])

      self.left_recursive.add_rule('T', ['id'])
      self.left_recursive.add_rule('T', ['(', 'E', ')'])

      self.left_recursive_epsilon = Grammar('E', ('+', '-', 'id', '(', ')'))

      self.left_recursive_epsilon.add_rule('E', ['E', '+', 'T'])
      self.left_recursive_epsilon.add_rule('E', ['E', '-', 'T'])
      self.left_recursive_epsilon.add_rule('E', ['T'])

      self.left_recursive_epsilon.add_rule('T', ['id'])
      self.left_recursive_epsilon.add_rule('T', ['(', 'E', ')'])
      self.left_recursive_epsilon.add_empty('T')
      
      self.right_recursive = Grammar('E', ('+', '-', 'id', '(', ')'))

      self.right_recursive.add_rule('E', ['T', '+', 'E'])
      self.right_recursive.add_rule('E', ['T', '-', 'E'])
      self.right_recursive.add_rule('E', ['T'])

      self.right_recursive.add_rule('T', ['id'])
      self.right_recursive.add_rule('T', ['(', 'E', ')'])
      
      self.right_recursive_epsilon = Grammar('E', ('+', '-', 'id', '(', ')'))

      self.right_recursive_epsilon.add_rule('E', ['T', '+', 'E'])
      self.right_recursive_epsilon.add_rule('E', ['T', '-', 'E'])
      self.right_recursive_epsilon.add_rule('E', ['T'])

      self.right_recursive_epsilon.add_rule('T', ['id'])
      self.right_recursive_epsilon.add_rule('T', ['(', 'E', ')'])
      self.right_recursive_epsilon.add_empty('T')

   def test_simple(self):
      expected = first(self.simple, ['A'])
      self.assertTrue(len(expected) == 2)
      self.assertTrue('a' in expected)
      self.assertTrue(self.simple.EMPTY in expected)

      expected = first(self.simple, ['B'])
      self.assertTrue(len(expected) == 2)
      self.assertTrue('b' in expected)
      self.assertTrue(self.simple.EMPTY in expected)
      
      expected = first(self.simple, ['S'])
      self.assertTrue(len(expected) == 3)
      self.assertTrue('s' in expected)
      self.assertTrue('b' in expected)
      self.assertTrue('a' in expected)

   
   def test_lr_value(self):
      expected = first(self.lrvalue, ['S'])
      self.assertTrue(len(expected) == 3)
      self.assertTrue('(' in expected)
      self.assertTrue('*' in expected)
      self.assertTrue('id' in expected)
      
      expected = first(self.lrvalue, ['L'])
      self.assertTrue(len(expected) == 2)
      self.assertTrue('*' in expected)
      self.assertTrue('id' in expected)
      
      expected = first(self.lrvalue, ['R'])
      self.assertTrue(len(expected) == 3)
      self.assertTrue('(' in expected)
      self.assertTrue('*' in expected)
      self.assertTrue('id' in expected)
      
   def test_more_complex(self):
      expected = first(self.more_complex, ['A'])
      self.assertTrue(len(expected) == 3)
      self.assertTrue('a' in expected)
      self.assertTrue('c' in expected)
      self.assertTrue(self.more_complex.EMPTY in expected)
      
      expected = first(self.more_complex, ['B'])
      self.assertTrue(len(expected) == 2)
      self.assertTrue('d' in expected)
      self.assertTrue('b' in expected)
      
      expected = first(self.more_complex, ['S'])
      self.assertTrue(len(expected) == 5)
      self.assertTrue('d' in expected)
      self.assertTrue('b' in expected)
      self.assertTrue('a' in expected)
      self.assertTrue('c' in expected)
      self.assertTrue('q' in expected)
   
   def test_left_recursive(self):
      expected = first(self.left_recursive, ['T'])
      self.assertTrue(len(expected) == 2)
      self.assertTrue('id' in expected)
      self.assertTrue('(' in expected)
      
      expected = first(self.left_recursive, ['E'])
      self.assertTrue(len(expected) == 2)
      self.assertTrue('id' in expected)
      self.assertTrue('(' in expected)
   
   def test_left_recursive_epsilon(self):
      expected = first(self.left_recursive_epsilon, ['T'])
      self.assertTrue(len(expected) == 3)
      self.assertTrue('id' in expected)
      self.assertTrue('(' in expected)
      self.assertTrue(self.left_recursive_epsilon.EMPTY in expected)
      
      expected = first(self.left_recursive_epsilon, ['E'])
      self.assertTrue(len(expected) == 5)
      self.assertTrue('id' in expected)
      self.assertTrue('(' in expected)
      self.assertTrue('+' in expected)
      self.assertTrue('-' in expected)
      self.assertTrue(self.left_recursive_epsilon.EMPTY in expected)
   
   def test_right_recursive(self):
      expected = first(self.right_recursive, ['T'])
      self.assertTrue(len(expected) == 2)
      self.assertTrue('id' in expected)
      self.assertTrue('(' in expected)
      
      expected = first(self.right_recursive, ['E'])
      self.assertTrue(len(expected) == 2)
      self.assertTrue('id' in expected)
      self.assertTrue('(' in expected)
   
   def test_right_recursive_epsilon(self):
      expected = first(self.right_recursive_epsilon, ['T'])
      self.assertTrue(len(expected) == 3)
      self.assertTrue('id' in expected)
      self.assertTrue('(' in expected)
      self.assertTrue(self.right_recursive_epsilon.EMPTY in expected)
      
      expected = first(self.right_recursive_epsilon, ['E'])
      self.assertTrue(len(expected) == 5)
      self.assertTrue('id' in expected)
      self.assertTrue('(' in expected)
      self.assertTrue('+' in expected)
      self.assertTrue('-' in expected)
      self.assertTrue(self.right_recursive_epsilon.EMPTY in expected)

if __name__ == '__main__':
   unittest.main()
