import unittest
import dragon.grammar as grammar
from dragon.lr.builder import build_parsing_table
from dragon.lr.conflict import ReduceReduce, ShiftReduce
from dragon.lr.item import LR0

class FunctionalTestBuildActionGotoTable(unittest.TestCase):

   def setUp(self):
      self.arith = grammar.Grammar('E', ('+', '*', '(', ')', 'id'))

      semantic_action = lambda args : args

      self.arith.add_rule('E', ['E', '+', 'T', semantic_action])
      self.arith.add_rule('E', ['T'])
      self.arith.add_rule('T', ['T', '*', 'F', semantic_action])
      self.arith.add_rule('T', ['F'])
      self.arith.add_rule('F', ['(', 'E', ')', semantic_action])
      self.arith.add_rule('F', ['id'])

      self.lrvalue = grammar.Grammar('S', ('=', '*', '(', ')', 'id'))

      self.lrvalue.add_rule('S', ['L', '=', 'R'])
      self.lrvalue.add_rule('S', ['R'])
      self.lrvalue.add_rule('L', ['*', 'R'])
      self.lrvalue.add_rule('L', ['id'])
      self.lrvalue.add_rule('R', ['L'])
      self.lrvalue.add_rule('R', ['(', 'S', ')'])

      self.reduce_reduce = grammar.Grammar('S', ('=', '?', '#'))

      self.reduce_reduce.add_rule('S', ['A', '#', '='])
      self.reduce_reduce.add_rule('S', ['B', '#', '?'])
      self.reduce_reduce.add_rule('A', ['=', '?'])
      self.reduce_reduce.add_rule('B', ['=', '?'])
      
      self.StartExtendedSymbol = grammar.Grammar.START
      
   
   def test_build_tables(self):
      action_table, goto_table, start_set = build_parsing_table(self.arith, LR0(self.StartExtendedSymbol, 0, 0))
      self.assertTrue(len(action_table) == 12)

   def test_shift_reduce_conflict(self):
      self.assertRaisesRegexp(ShiftReduce, "during process '=' terminal", build_parsing_table, self.lrvalue, LR0(self.StartExtendedSymbol, 0, 0), False)

   def test_reduce_reduce_conflict(self):
      self.assertRaisesRegexp(ReduceReduce, "during process '#' terminal", build_parsing_table, self.reduce_reduce, LR0(self.StartExtendedSymbol, 0, 0), False)
   
   def test_build_tables_of_arithmetic_grammar(self):
      action_table, goto_table, start_set = build_parsing_table(self.arith, LR0(self.StartExtendedSymbol, 0, 0))
      states = action_table.keys()


      s5 = None      #Shift to state number 5
      s4 = None      #Shift to state number 4
      count = 0
      for state in states:
         if 'id' in action_table[state]:
            s5 = action_table[state]['id'] if s5 == None else s5
            s4 = action_table[state]['('] if s4 == None else s4
            self.assertTrue(s5 == action_table[state]['id'])
            self.assertTrue(s4 == action_table[state]['('])
            count += 1
      
      self.assertTrue(count == 4)
      state_5, state_4 = s5._state_to_shift, s4._state_to_shift

      self.assertTrue(action_table[state_5]['+'] == \
            action_table[state_5]['*'] == \
            action_table[state_5][')'] == \
            action_table[state_5][self.arith.EOF])
      self.assertTrue(len(action_table[state_5]) == 4)

      
      count = 0
      for state in states:
         s = action_table[state]
         try:
            if s['+'] == s['*'] == s[')'] == s[self.arith.EOF]:
               self.assertTrue(hasattr(s['+'], '_semantic_action'))
               count += 1
         except:
            pass

      self.assertTrue(count == 4)

      count = 0
      s7 = None
      for state in states:
         s = action_table[state]
         try:
            if s['+'] == s[')'] == s[self.arith.EOF]:
               count += 1
               if self.assertTrue(hasattr(s['*'], '_state_to_shift')):
                  s7 = s['*'] if s7 == None else s7
                  self.assertTrue(s7 == s['*'])

         except:
            pass

      self.assertTrue(count == 6)

if __name__ == '__main__':
   unittest.main()
