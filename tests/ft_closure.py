import unittest
import dragon.grammar as grammar
from dragon.lr.util import closure
from dragon.lr.item import LR0

class FunctionalTestClosure(unittest.TestCase):

   def setUp(self):
      self.arith = grammar.Grammar('E', ('+', '*', '(', ')', 'id'))

      self.arith.add_rule('E', ['E', '+', 'T'])
      self.arith.add_rule('E', ['T'])
      self.arith.add_rule('T', ['T', '*', 'F'])
      self.arith.add_rule('T', ['F'])
      self.arith.add_rule('F', ['(', 'E', ')'])
      self.arith.add_rule('F', ['id'])

      self.lrvalue = grammar.Grammar('S', ('=', '*', '(', ')', 'id'))

      self.lrvalue.add_rule('S', ['L', '=', 'R'])
      self.lrvalue.add_rule('S', ['R'])
      self.lrvalue.add_rule('L', ['*', 'R'])
      self.lrvalue.add_rule('L', ['id'])
      self.lrvalue.add_rule('R', ['L'])
      self.lrvalue.add_rule('R', ['(', 'S', ')'])
      
      self.some = grammar.Grammar('S', ('c', 'd'))
      
      self.some.add_rule('S', ['C', 'C'])
      self.some.add_rule('C', ['c', 'C'])
      self.some.add_rule('C', ['d'])
      
      self.lrvalue_with_actions = grammar.Grammar('S', ('=', '*', '(', ')', 'id'))

      self.lrvalue_with_actions.add_rule('S', ['L', '=', 'R', lambda args: 'assign', lambda args:args])
      self.lrvalue_with_actions.add_rule('S', ['R'])
      self.lrvalue_with_actions.add_rule('L', ['*', 'R', lambda args: 'deref', lambda args:args])
      self.lrvalue_with_actions.add_rule('L', ['id'])
      self.lrvalue_with_actions.add_rule('R', ['L'])
      self.lrvalue_with_actions.add_rule('R', ['(', lambda args: 'push', 'S', lambda args: 'pop', ')', lambda args:args])

      self.StartExtendedSymbol = grammar.Grammar.START


   def test_closures_ofArith(self):
      a1 = set([LR0(self.StartExtendedSymbol, 0, 0),
            LR0('E', 0, 0), LR0('E', 1, 0), 
            LR0('T', 0, 0), LR0('T', 1, 0),
            LR0('F', 0, 0), LR0('F', 1, 0)])
      
      a2 = set([LR0('F', 0, 1),
            LR0('E', 0, 0), LR0('E', 1, 0), 
            LR0('T', 0, 0), LR0('T', 1, 0),
            LR0('F', 0, 0), LR0('F', 1, 0)])

      self.assertTrue(a1 == closure(set([LR0(self.StartExtendedSymbol, 0, 0)]), self.arith))
      self.assertTrue(a2 == closure(set([LR0('F', 0, 1)]), self.arith))
   
   def test_closures_ofLRValue(self):
      a1 = set([LR0(self.StartExtendedSymbol, 0, 0),
            LR0('S', 0, 0), LR0('S', 1, 0), 
            LR0('R', 0, 0), LR0('R', 1, 0),
            LR0('L', 0, 0), LR0('L', 1, 0)])
      
      a2 = set([
            LR0('S', 0, 0), LR0('S', 1, 0), 
            LR0('R', 0, 0), LR0('R', 1, 0), LR0('R', 1, 1),
            LR0('L', 0, 0), LR0('L', 0, 1), LR0('L', 1, 0)])

      self.assertTrue(a1 == closure(set([LR0(self.StartExtendedSymbol, 0, 0)]), self.lrvalue))
      self.assertTrue(a2 == closure(set([LR0('L', 0, 1), LR0('R', 1, 1)]), self.lrvalue))


   def test_closures_ofSome(self):
      a1 = set([LR0(self.StartExtendedSymbol, 0, 0),
            LR0('S', 0, 0),
            LR0('C', 0, 0), LR0('C', 1, 0)])
      
      a2 = set([
            LR0('S', 0, 1), 
            LR0('C', 0, 0), LR0('C', 1, 0), LR0('C', 1, 1)])

      self.assertTrue(a1 == closure(set([LR0(self.StartExtendedSymbol, 0, 0)]), self.some))
      self.assertTrue(a2 == closure(set([LR0('S', 0, 1), LR0('C', 1, 1)]), self.some))

   def test_closures_ofLRValue_with_actions(self):
      a1 = set([LR0(self.StartExtendedSymbol, 0, 0),
            LR0('S', 0, 0), LR0('S', 1, 0), 
            LR0('R', 0, 0), LR0('R', 1, 0),
            LR0('L', 0, 0), LR0('L', 1, 0)])
      
      a2 = set([
            LR0(self.lrvalue_with_actions.ACTION_INSIDE % (3, '<lambda>'), 0, 0), 
            LR0('R', 0, 0), LR0('R', 1, 0), LR0('R', 1, 1),
            LR0('L', 0, 0), LR0('L', 0, 1), LR0('L', 1, 0)])

      self.assertTrue(a1 == closure(set([LR0(self.StartExtendedSymbol, 0, 0)]), self.lrvalue_with_actions))
      self.assertTrue(a2 == closure(set([LR0('L', 0, 1), LR0('R', 1, 1)]), self.lrvalue_with_actions))

if __name__ == '__main__':
   unittest.main()
