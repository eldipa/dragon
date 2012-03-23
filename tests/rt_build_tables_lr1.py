import unittest
import dragon.grammar as grammar
from dragon.lr.util import build_parsing_table, ReduceReduce, ShiftReduce
from dragon.lr.lookahead import LookAhead

class RegresionTestBuildActionGotoTableForLR1Grammar(unittest.TestCase):
   def setUp(self):
      self.lrvalue = grammar.Grammar('S', ('=', '*', '(', ')', 'id'))

      self.lrvalue.add_rule('S', ['L', '=', 'R'])
      self.lrvalue.add_rule('S', ['R'])
      self.lrvalue.add_rule('L', ['*', 'R'])
      self.lrvalue.add_rule('L', ['id'])
      self.lrvalue.add_rule('R', ['L'])
      self.lrvalue.add_rule('R', ['(', 'S', ')'])

      
   def test_shift_reduce_conflict_from_LR0_solved_with_LR1(self):
      action_table, goto_table, start_set = build_parsing_table(self.lrvalue, LookAhead(self.lrvalue.START, 0, 0, self.lrvalue.EOF), False)
      self.assertTrue(True) #No raised any exception


if __name__ == '__main__':
   unittest.main()
