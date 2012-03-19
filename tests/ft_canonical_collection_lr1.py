import unittest
import dragon.grammar as grammar
from dragon.lr.util import goto, canonical_collection
from dragon.lr.lookahead import LookAhead

class FunctionalTestCanonicalCollectionUsingLR1LookAheads(unittest.TestCase):

   def setUp(self):
      self.arith = grammar.Grammar('S', ('c', 'd'))

      self.arith.add_rule('S', ['C', 'C'])
      self.arith.add_rule('C', ['c', 'C'])
      self.arith.add_rule('C', ['d'])

      self.StartExtendedSymbol = grammar.Grammar.START


   def test_canonical_collection_arith(self):
      collection = canonical_collection(self.arith, LookAhead(self.StartExtendedSymbol, 0, 0, self.arith.EOF))
      self.assertTrue(len(collection) == 10)

      EOF = self.arith.EOF

      states = frozenset([
      frozenset([
         LookAhead(self.StartExtendedSymbol, 0, 0, EOF),
         LookAhead('S', 0, 0, EOF),
         LookAhead('C', 0, 0, 'c'), LookAhead('C', 0, 0, 'd'),
         LookAhead('C', 1, 0, 'c'), LookAhead('C', 1, 0, 'd'), ]),
      
      frozenset([
         LookAhead(self.StartExtendedSymbol, 0, 1, EOF),
         ]),

      frozenset([
         LookAhead('S', 0, 1, EOF),
         LookAhead('C', 0, 0, EOF),
         LookAhead('C', 1, 0, EOF)]),

      frozenset([
         LookAhead('C', 0, 1, 'c'), LookAhead('C', 0, 1, 'd'),
         LookAhead('C', 0, 0, 'c'), LookAhead('C', 0, 0, 'd'),
         LookAhead('C', 1, 0, 'c'), LookAhead('C', 1, 0, 'd'), ]),

      frozenset([
         LookAhead('C', 1, 1, 'c'), LookAhead('C', 1, 1, 'd'),]),
         
      frozenset([
         LookAhead('C', 0, 1, EOF),
         LookAhead('C', 0, 0, EOF), 
         LookAhead('C', 1, 0, EOF),  ]),

      frozenset([
         LookAhead('S', 0, 2, EOF),
         ]),

      frozenset([
         LookAhead('C', 1, 1, EOF), 
         ]),
      
      frozenset([
         LookAhead('C', 0, 2, 'c'), LookAhead('C', 0, 2, 'd'),]),

      frozenset([
         LookAhead('C', 0, 2, EOF), ]),

      ])

      assert len(states) == 10
      self.assertTrue(states == collection)


if __name__ == '__main__':
   unittest.main()
