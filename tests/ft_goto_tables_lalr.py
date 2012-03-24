import unittest
import dragon.grammar as grammar
from dragon.lr.util import goto, kernel_collection, generate_spontaneously_lookaheads, propagate_lookaheads
from dragon.lr.lookahead_compress import LookAheadCompress
from dragon.lr.item import Item

class FunctionalTestGotoTableForLALRGrammar(unittest.TestCase):

   def setUp(self):
      self.lrvalue = grammar.Grammar('S', ('c', 'd'))

      self.lrvalue.add_rule('S', ['C', 'C'])
      self.lrvalue.add_rule('C', ['c', 'C'])
      self.lrvalue.add_rule('C', ['d'])
      
      self.StartExtendedSymbol = grammar.Grammar.START
      
      self.kernels_lalr, self.goto_table = generate_spontaneously_lookaheads(self.lrvalue, Item(self.lrvalue.START, 0, 0), False)

   def test_kernel_collection_lalr(self):
      collection = self.kernels_lalr
      propagate_lookaheads(self.lrvalue, collection)
      self.assertTrue(len(collection) == 7)
      
      expecteds = [
         (Item(self.lrvalue.START, 0, 0), [self.lrvalue.EOF]),
         (Item(self.lrvalue.START, 0, 1), [self.lrvalue.EOF]),
         (Item('S', 0, 1),                [self.lrvalue.EOF]),
         (Item('C', 0, 1),                ['c', 'd', self.lrvalue.EOF]),
         (Item('C', 1, 1),                ['c', 'd', self.lrvalue.EOF]),
         (Item('S', 0, 2),                [self.lrvalue.EOF]),
         (Item('C', 0, 2),                ['c', 'd', self.lrvalue.EOF]), 
         ]
   
      for kernels in collection:
         self.assertTrue(len(kernels) == 1)
         found = False
         count = 0
         for item_lookaheads in expecteds:
            item, lookaheads = item_lookaheads
            if item in kernels:
               self.assertTrue(set(kernels).pop().lookaheads == set(lookaheads))
               found = True
               del expecteds[count]
               break
            count += 1

         self.assertTrue(found)


if __name__ == '__main__':
   unittest.main()
