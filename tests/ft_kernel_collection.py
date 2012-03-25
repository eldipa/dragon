import unittest
import dragon.grammar as grammar
from dragon.lr.util import kernel_collection
from dragon.lr.item import LR0

class FunctionalTestKernelCollection(unittest.TestCase):

   def setUp(self):
      self.arith = grammar.Grammar('E', ('+', '*', '(', ')', 'id'))

      self.arith.add_rule('E', ['E', '+', 'T'])
      self.arith.add_rule('E', ['T'])
      self.arith.add_rule('T', ['T', '*', 'F'])
      self.arith.add_rule('T', ['F'])
      self.arith.add_rule('F', ['(', 'E', ')'])
      self.arith.add_rule('F', ['id'])

      self.lrvalue = grammar.Grammar('S', ('=', '*', 'id'))

      self.lrvalue.add_rule('S', ['L', '=', 'R'])
      self.lrvalue.add_rule('S', ['R'])
      self.lrvalue.add_rule('L', ['*', 'R'])
      self.lrvalue.add_rule('L', ['id'])
      self.lrvalue.add_rule('R', ['L'])
      

      self.StartExtendedSymbol = grammar.Grammar.START


   def test_kernel_collection_arith(self):
      collection = kernel_collection(self.arith, LR0(self.StartExtendedSymbol, 0, 0))
      self.assertTrue(len(collection) == 12)

      states = frozenset([
      frozenset([
         LR0(self.StartExtendedSymbol, 0, 0),
         ]),
      
      frozenset([
         LR0(self.StartExtendedSymbol, 0, 1),
         LR0('E', 0, 1), ]),

      frozenset([
         LR0('E', 1, 1),
         LR0('T', 0, 1), ]),

      frozenset([
         LR0('F', 1, 1), ]),

      frozenset([
         LR0('F', 0, 1),
         ]),

      frozenset([
         LR0('T', 1, 1), ]),
         
      frozenset([
         LR0('E', 0, 2),
         ]),

      frozenset([
         LR0('T', 0, 2),
         ]),

      frozenset([
         LR0('E', 0, 1),
         LR0('F', 0, 2), ]),

      frozenset([
         LR0('E', 0, 3),
         LR0('T', 0, 1), ]),
      
      frozenset([
         LR0('T', 0, 3), ]),

      frozenset([
         LR0('F', 0, 3), ]),
      ])

      self.assertTrue(states == collection)


   def test_kernel_collection_lr_value(self):
      collection = kernel_collection(self.lrvalue, LR0(self.StartExtendedSymbol, 0, 0))
      self.assertTrue(len(collection) == 10)

      states = frozenset([
      frozenset([
         LR0(self.StartExtendedSymbol, 0, 0),
         ]),
      
      frozenset([
         LR0(self.StartExtendedSymbol, 0, 1), ]),
      
      frozenset([
         LR0('S', 0, 1),
         LR0('R', 0, 1), ]),
      
      frozenset([
         LR0('S', 1, 1), ]),
      
      frozenset([
         LR0('L', 0, 1),
         ]),
      
      frozenset([
         LR0('L', 1, 1), ]),
      
      frozenset([
         LR0('S', 0, 2),
         ]),
      
      frozenset([
         LR0('L', 0, 2), ]),
      
      frozenset([
         LR0('R', 0, 1), ]),

      frozenset([
         LR0('S', 0, 3), ]),
      ])

      self.assertTrue(states == collection)


if __name__ == '__main__':
   unittest.main()
