import unittest
import dragon.grammar as grammar
from dragon.lr.util import kernel_collection
from dragon.lr.item import LR0, LALR

class FunctionalTestKernelCollectionForLALRGrammar(unittest.TestCase):

   def setUp(self):
      self.lrvalue = grammar.Grammar('S', ('c', 'd'))

      self.lrvalue.add_rule('S', ['C', 'C'])
      self.lrvalue.add_rule('C', ['c', 'C'])
      self.lrvalue.add_rule('C', ['d'])
      
      self.StartExtendedSymbol = grammar.Grammar.START


   def test_kernel_collection_lalr(self):
      collection = kernel_collection(self.lrvalue, LALR(self.StartExtendedSymbol, 0, 0))
      self.assertTrue(len(collection) == 7)

      states = frozenset([
      frozenset([
         LALR(self.StartExtendedSymbol, 0, 0),
         ]),
      
      frozenset([
         LALR(self.StartExtendedSymbol, 0, 1),
         ]),

      frozenset([
         LALR('S', 0, 1),
         ]),

      frozenset([
         LALR('C', 0, 1), ]),

      frozenset([
         LALR('C', 1, 1),
         ]),

      frozenset([
         LALR('S', 0, 2), ]),
         
      frozenset([
         LALR('C', 0, 2),
         ]),

      ])

      self.assertTrue(states == collection)

   def test_equivalence_sets_lalr_and_sets_lr0(self):
      states_lalr = frozenset([
      frozenset([
         LALR(self.StartExtendedSymbol, 0, 0),
         ]),
      
      frozenset([
         LALR(self.StartExtendedSymbol, 0, 1),
         ]),

      frozenset([
         LALR('S', 0, 1),
         ]),

      frozenset([
         LALR('C', 0, 1), ]),

      frozenset([
         LALR('C', 1, 1),
         ]),

      frozenset([
         LALR('S', 0, 2), ]),
         
      frozenset([
         LALR('C', 0, 2),
         ]),

      ])

      states_lr0 = frozenset([
      frozenset([
         LR0(self.StartExtendedSymbol, 0, 0),
         ]),
      
      frozenset([
         LR0(self.StartExtendedSymbol, 0, 1),
         ]),

      frozenset([
         LR0('S', 0, 1),
         ]),

      frozenset([
         LR0('C', 0, 1), ]),

      frozenset([
         LR0('C', 1, 1),
         ]),

      frozenset([
         LR0('S', 0, 2), ]),
         
      frozenset([
         LR0('C', 0, 2),
         ]),

      ])

      self.assertTrue(states_lr0 == states_lalr)


if __name__ == '__main__':
   unittest.main()
