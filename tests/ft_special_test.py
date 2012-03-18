import unittest
from dragon.grammar import Grammar
from dragon.util import first, follow
from dragon.lr.util import canonical_collection, build_parsing_table
from dragon.item import Item

class FunctionalTestSpecial(unittest.TestCase):
   def setUp(self):
      self.simple = Grammar('A', ['a'])
      
      self.simple.add_rule('A', ['M', 'a'])
      self.simple.add_empty('M')

      self.twolevels = Grammar('A', ['c'])

      self.twolevels.add_rule('A', ['B', 'c'])
      self.twolevels.add_rule('B', ['M'])
      self.twolevels.add_empty('M')

      self.no_empty = Grammar('A', ['a', 'd', 'c'])

      self.no_empty.add_rule('A', ['B', 'a'])
      self.no_empty.add_rule('B', ['d', 'C'])
      self.no_empty.add_rule('C', ['c'])

      self.follow_empty = Grammar('A', ['c', 'x'])

      self.follow_empty.add_rule('A', ['B', 'c'])
      self.follow_empty.add_rule('B', ['C', 'M'])
      self.follow_empty.add_rule('C', ['x'])
      self.follow_empty.add_empty('M')

   def test_functions_simple_grammar(self):
      expected = first(self.simple, ['A'])
      self.assertTrue(len(expected) == 1)
      self.assertTrue('a' in expected)
      
      expected = follow(self.simple, 'M')
      self.assertTrue(len(expected) == 1)
      self.assertTrue('a' in expected)
   
   def test_functions_twolevels_grammar(self):
      expected = first(self.twolevels, ['A'])
      self.assertTrue(len(expected) == 1)
      self.assertTrue('c' in expected)
      
      expected = first(self.twolevels, ['B'])
      self.assertTrue(len(expected) == 1)
      self.assertTrue(self.twolevels.EMPTY in expected)
      
      expected = follow(self.twolevels, 'B')
      self.assertTrue(len(expected) == 1)
      self.assertTrue('c' in expected)
      
      expected = follow(self.twolevels, 'M')
      self.assertTrue(expected == follow(self.twolevels, 'B'))

   def test_functions_no_empty_grammar(self):
      expected = follow(self.no_empty, 'B')
      self.assertTrue(len(expected) == 1)
      self.assertTrue('a' in expected)
      
      expected = follow(self.no_empty, 'C')
      self.assertTrue(expected == follow(self.no_empty, 'B'))

   def test_functions_follow_empty(self):
      expected = follow(self.follow_empty, 'B')
      self.assertTrue(len(expected) == 1)
      self.assertTrue('c' in expected)

      expected = follow(self.follow_empty, 'C')
      self.assertTrue(expected == follow(self.follow_empty, 'B'))


if __name__ == '__main__':
   unittest.main()
