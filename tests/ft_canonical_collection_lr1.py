import unittest
import dragon.grammar as grammar
from dragon.lr.util import canonical_collection
from dragon.lr.item import LR1

class FunctionalTestCanonicalCollectionUsingLR1LR1s(unittest.TestCase):

   def setUp(self):
      self.arith = grammar.Grammar('S', ('c', 'd'))

      self.arith.add_rule('S', ['C', 'C'])
      self.arith.add_rule('C', ['c', 'C'])
      self.arith.add_rule('C', ['d'])

      self.StartExtendedSymbol = grammar.Grammar.START


   def test_canonical_collection_arith(self):
      collection = canonical_collection(self.arith, LR1(self.StartExtendedSymbol, 0, 0, self.arith.EOF))
      self.assertTrue(len(collection) == 10)

      EOF = self.arith.EOF

      states = frozenset([
      frozenset([
         LR1(self.StartExtendedSymbol, 0, 0, EOF),
         LR1('S', 0, 0, EOF),
         LR1('C', 0, 0, 'c'), LR1('C', 0, 0, 'd'),
         LR1('C', 1, 0, 'c'), LR1('C', 1, 0, 'd'), ]),
      
      frozenset([
         LR1(self.StartExtendedSymbol, 0, 1, EOF),
         ]),

      frozenset([
         LR1('S', 0, 1, EOF),
         LR1('C', 0, 0, EOF),
         LR1('C', 1, 0, EOF)]),

      frozenset([
         LR1('C', 0, 1, 'c'), LR1('C', 0, 1, 'd'),
         LR1('C', 0, 0, 'c'), LR1('C', 0, 0, 'd'),
         LR1('C', 1, 0, 'c'), LR1('C', 1, 0, 'd'), ]),

      frozenset([
         LR1('C', 1, 1, 'c'), LR1('C', 1, 1, 'd'),]),
         
      frozenset([
         LR1('C', 0, 1, EOF),
         LR1('C', 0, 0, EOF), 
         LR1('C', 1, 0, EOF),  ]),

      frozenset([
         LR1('S', 0, 2, EOF),
         ]),

      frozenset([
         LR1('C', 1, 1, EOF), 
         ]),
      
      frozenset([
         LR1('C', 0, 2, 'c'), LR1('C', 0, 2, 'd'),]),

      frozenset([
         LR1('C', 0, 2, EOF), ]),

      ])

      assert len(states) == 10
      self.assertTrue(states == collection)


if __name__ == '__main__':
   unittest.main()
