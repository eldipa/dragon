import unittest
import dragon.grammar as grammar
from dragon.lr.builder import generate_spontaneously_lookaheads, propagate_lookaheads
from dragon.lr.item import LR0

class FunctionalTestGotoTableForLALRGrammar(unittest.TestCase):

   def setUp(self):
      self.lrvalue = grammar.Grammar('S', ('c', 'd'))

      self.lrvalue.add_rule('S', ['C', 'C'])
      self.lrvalue.add_rule('C', ['c', 'C'])
      self.lrvalue.add_rule('C', ['d'])
      
      self.StartExtendedSymbol = grammar.Grammar.START
      
      self.kernels_lalr, self.goto_table = generate_spontaneously_lookaheads(self.lrvalue, LR0(self.lrvalue.START, 0, 0), False)

   def test_kernel_collection_lalr(self):
      collection = self.kernels_lalr
      propagate_lookaheads(self.lrvalue, collection)
      self.assertTrue(len(collection) == 7)
      
      expecteds = [
         (LR0(self.lrvalue.START, 0, 0), [self.lrvalue.EOF]),
         (LR0(self.lrvalue.START, 0, 1), [self.lrvalue.EOF]),
         (LR0('S', 0, 1),                [self.lrvalue.EOF]),
         (LR0('C', 0, 1),                ['c', 'd', self.lrvalue.EOF]),
         (LR0('C', 1, 1),                ['c', 'd', self.lrvalue.EOF]),
         (LR0('S', 0, 2),                [self.lrvalue.EOF]),
         (LR0('C', 0, 2),                ['c', 'd', self.lrvalue.EOF]), 
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
