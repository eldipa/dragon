import unittest
import dragon.grammar as grammar
from dragon.lr.util import goto, kernel_collection
from dragon.lr.lookahead_compress import LookAheadCompress
from dragon.lr.item import Item

class FunctionalTestKernelCollectionForLALRGrammar(unittest.TestCase):

   def setUp(self):
      self.lrvalue = grammar.Grammar('S', ('c', 'd'))

      self.lrvalue.add_rule('S', ['C', 'C'])
      self.lrvalue.add_rule('C', ['c', 'C'])
      self.lrvalue.add_rule('C', ['d'])
      
      self.StartExtendedSymbol = grammar.Grammar.START


   def test_kernel_collection_lalr(self):
      collection = kernel_collection(self.lrvalue, LookAheadCompress(self.StartExtendedSymbol, 0, 0))
      self.assertTrue(len(collection) == 7)

      states = frozenset([
      frozenset([
         LookAheadCompress(self.StartExtendedSymbol, 0, 0),
         ]),
      
      frozenset([
         LookAheadCompress(self.StartExtendedSymbol, 0, 1),
         ]),

      frozenset([
         LookAheadCompress('S', 0, 1),
         ]),

      frozenset([
         LookAheadCompress('C', 0, 1), ]),

      frozenset([
         LookAheadCompress('C', 1, 1),
         ]),

      frozenset([
         LookAheadCompress('S', 0, 2), ]),
         
      frozenset([
         LookAheadCompress('C', 0, 2),
         ]),

      ])

      self.assertTrue(states == collection)

   def test_equivalence_sets_lalr_and_sets_lr0(self):
      states_lalr = frozenset([
      frozenset([
         LookAheadCompress(self.StartExtendedSymbol, 0, 0),
         ]),
      
      frozenset([
         LookAheadCompress(self.StartExtendedSymbol, 0, 1),
         ]),

      frozenset([
         LookAheadCompress('S', 0, 1),
         ]),

      frozenset([
         LookAheadCompress('C', 0, 1), ]),

      frozenset([
         LookAheadCompress('C', 1, 1),
         ]),

      frozenset([
         LookAheadCompress('S', 0, 2), ]),
         
      frozenset([
         LookAheadCompress('C', 0, 2),
         ]),

      ])

      states_lr0 = frozenset([
      frozenset([
         Item(self.StartExtendedSymbol, 0, 0),
         ]),
      
      frozenset([
         Item(self.StartExtendedSymbol, 0, 1),
         ]),

      frozenset([
         Item('S', 0, 1),
         ]),

      frozenset([
         Item('C', 0, 1), ]),

      frozenset([
         Item('C', 1, 1),
         ]),

      frozenset([
         Item('S', 0, 2), ]),
         
      frozenset([
         Item('C', 0, 2),
         ]),

      ])

      self.assertTrue(states_lr0 == states_lalr)


if __name__ == '__main__':
   unittest.main()
