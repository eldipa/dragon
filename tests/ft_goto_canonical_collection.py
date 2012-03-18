import unittest
import dragon.grammar as grammar
from dragon.lr.util import goto, canonical_collection
from dragon.item import Item

class FunctionalTestGotoCanonicalCollection(unittest.TestCase):

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


   def test_goto_arith(self):
      a1 = set([
         Item('E', 0, 2), 
         Item('T', 0, 0), Item('T', 1, 0),
         Item('F', 0, 0), Item('F', 1, 0), ])

      a2 = set([Item('E', 0, 1), ])

      a3 = set([Item('T', 0, 3), ])

      self.assertTrue(a1 == goto(set([Item(self.StartExtendedSymbol, 0, 1), Item('E', 0, 1)]), '+', self.arith))
      self.assertTrue(a2 == goto(set([Item('E', 0, 0)]), 'E', self.arith))
      self.assertTrue(a3 == goto(set([Item('T', 0, 2), Item('F', 0, 0), Item('F', 1, 0),]), 'F', self.arith))


   def test_canonical_collection_arith(self):
      collection = canonical_collection(self.arith, Item(self.StartExtendedSymbol, 0, 0))
      self.assertTrue(len(collection) == 12)

      states = frozenset([
      frozenset([
         Item(self.StartExtendedSymbol, 0, 0),
         Item('E', 0, 0), Item('E', 1, 0),
         Item('T', 0, 0), Item('T', 1, 0),
         Item('F', 0, 0), Item('F', 1, 0), ]),
      
      frozenset([
         Item(self.StartExtendedSymbol, 0, 1),
         Item('E', 0, 1), ]),

      frozenset([
         Item('E', 1, 1),
         Item('T', 0, 1), ]),

      frozenset([
         Item('F', 1, 1), ]),

      frozenset([
         Item('F', 0, 1),
         Item('E', 0, 0), Item('E', 1, 0),
         Item('T', 0, 0), Item('T', 1, 0),
         Item('F', 0, 0), Item('F', 1, 0), ]),

      frozenset([
         Item('T', 1, 1), ]),
         
      frozenset([
         Item('E', 0, 2),
         Item('T', 0, 0), Item('T', 1, 0),
         Item('F', 0, 0), Item('F', 1, 0), ]),

      frozenset([
         Item('T', 0, 2),
         Item('F', 0, 0), Item('F', 1, 0), ]),

      frozenset([
         Item('E', 0, 1),
         Item('F', 0, 2), ]),

      frozenset([
         Item('E', 0, 3),
         Item('T', 0, 1), ]),
      
      frozenset([
         Item('T', 0, 3), ]),

      frozenset([
         Item('F', 0, 3), ]),
      ])

      self.assertTrue(states == collection)

   def test_canonical_collection_lr_value(self):
      collection = canonical_collection(self.lrvalue, Item(self.StartExtendedSymbol, 0, 0))
      self.assertTrue(len(collection) == 10)

      states = frozenset([
      frozenset([
         Item(self.StartExtendedSymbol, 0, 0),
         Item('S', 0, 0), Item('S', 1, 0),
         Item('L', 0, 0), Item('L', 1, 0),
         Item('R', 0, 0), ]),
      
      frozenset([
         Item(self.StartExtendedSymbol, 0, 1), ]),
      
      frozenset([
         Item('S', 0, 1),
         Item('R', 0, 1), ]),
      
      frozenset([
         Item('S', 1, 1), ]),
      
      frozenset([
         Item('L', 0, 1),
         Item('L', 0, 0), Item('L', 1, 0),
         Item('R', 0, 0), ]),
      
      frozenset([
         Item('L', 1, 1), ]),
      
      frozenset([
         Item('S', 0, 2),
         Item('L', 0, 0), Item('L', 1, 0),
         Item('R', 0, 0), ]),
      
      frozenset([
         Item('L', 0, 2), ]),
      
      frozenset([
         Item('R', 0, 1), ]),

      frozenset([
         Item('S', 0, 3), ]),
      ])

      self.assertTrue(states == collection)


if __name__ == '__main__':
   unittest.main()
