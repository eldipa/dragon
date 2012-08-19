import unittest
import dragon.grammar as grammar
from StringIO import StringIO
import re
from dragon.lr.builder import build_parsing_table
from dragon.lr.util import canonical_collection
from dragon.lr.driver import Driver
from dragon.driver import Lexer
from dragon.lr.item import LR0
from dragon.util import follow

class RegressionTestUnknowGotoState(unittest.TestCase):
   class CalcLexer(Lexer):
      def __init__(self, source):
         self._source = source
         self._white_characters = (' ', '\t', '\v', '\n', '\r')
         self._number = re.compile('[+-]?\d+(\.\d+)?')
         self._var_name = re.compile('\w+')
      
      def tokenizer(self):
         '''Return a iterable or generator of all tokens.
            Each token is a tuple with at least one value, the terminal id. 
            The next values, if any, are the attributes of the token.'''
      
         for line in self._source:
            i = 0
            while i < len(line):
               while i < len(line) and line[i] in self._white_characters:
                  i += 1 

               if len(line) == i:
                  continue

               match_id = self._number.match(line, i)
               match_var = self._var_name.match(line, i)
               if match_id:
                  yield ('id', int(match_id.group()))
                  i = match_id.end()
               elif match_var:
                  if match_var.group() == 'let':
                     yield ('let', 'let')
                  else:
                     yield ('var', match_var.group())
                  i = match_var.end()
               else:
                  yield (line[i], line[i])
                  i += 1

         yield (grammar.Grammar.EOF, grammar.Grammar.EOF)
         return 


   def setUp(self):
      self.arith = grammar.Grammar('S', ('(', ')', 'id', 'let'))
      self.symbol_table = [dict()]

      def push(*args): pass
      def pop(*args): pass

      self.arith.add_rule('S', ['E'])
      self.arith.add_rule('E', ['id'])
      self.arith.add_rule('E', ['let', push, '(', 'E', ')', pop, lambda *args:args])

      self.action_table, self.goto_table, self.start_state = build_parsing_table(self.arith, LR0(self.arith.START, 0, 0))
      self.driver = Driver(self.action_table, dict(self.goto_table), self.start_state)

   def test_cannonical_collection(self):
      collection = canonical_collection(self.arith, LR0(self.arith.START, 0, 0))
      
      states = frozenset([
      frozenset([
         LR0(self.arith.START, 0, 0),
         LR0('S', 0, 0), 
         LR0('E', 0, 0), LR0('E', 1, 0),]),
      
      frozenset([
         LR0(self.arith.START, 0, 1),]),
      
      frozenset([
         LR0('E', 0, 1),]),

      frozenset([
         LR0('S', 0, 1),]),
      
      frozenset([
         LR0('E', 1, 1), 
         LR0(self.arith.ACTION_INSIDE % 1, 0, 0),]),
      
      frozenset([
         LR0('E', 1, 2),]),
      
      frozenset([
         LR0('E', 1, 4),]),
      
      frozenset([
         LR0('E', 1, 6),]),
      
      frozenset([
         LR0('E', 1, 5), 
         LR0(self.arith.ACTION_INSIDE % 2, 0, 0),]),

      frozenset([
         LR0('E', 1, 3), 
         LR0('E', 0, 0), LR0('E', 1, 0),]),
      ])
      
      self.assertTrue(states == collection)


   def test_goto_table(self):
      states_gotos = [
      (frozenset([
         LR0(self.arith.START, 0, 0),
         LR0('S', 0, 0), 
         LR0('E', 0, 0), LR0('E', 1, 0),]),  (('S', 1), ('id', 2), ('E', 3), ('let', 4))),
      
      (frozenset([
         LR0(self.arith.START, 0, 1),]),  ()),
      
      (frozenset([
         LR0('E', 0, 1),]),  ()),

      (frozenset([
         LR0('S', 0, 1),]),  ()),
      
      (frozenset([
         LR0('E', 1, 1), 
         LR0(self.arith.ACTION_INSIDE % 1, 0, 0),]),  ((self.arith.ACTION_INSIDE % 1, 5),)),
      
      (frozenset([
         LR0('E', 1, 2),]),  (('(', 9),)),
      
      (frozenset([
         LR0('E', 1, 4),]),  ((')', 8),)),
      
      (frozenset([
         LR0('E', 1, 6),]),  ()),
      
      (frozenset([
         LR0('E', 1, 5), 
         LR0(self.arith.ACTION_INSIDE % 2, 0, 0),]), ((self.arith.ACTION_INSIDE % 2, 7),) ),

      (frozenset([
         LR0('E', 1, 3), 
         LR0('E', 0, 0), LR0('E', 1, 0),]),  (('E', 6), ('id', 2), ('let', 4))),
      ]

      checked = 0
      for state, gotos in states_gotos:
         h = hash(state)
         if not gotos:
            self.assertTrue(h not in self.goto_table)
            continue

         checked += 1
         expected_keys, expected_states_id = zip(*gotos)

         found_gotos_keys = frozenset(self.goto_table[h].keys())
         found_gotos_hashs = frozenset(self.goto_table[h].values())

         self.assertTrue(frozenset(expected_keys) == found_gotos_keys)
         self.assertTrue(frozenset([hash(states_gotos[i][0]) for i in expected_states_id]) == found_gotos_hashs)

      self.assertTrue(checked == len(self.goto_table.keys()))


   def test_action_table(self):
      states_shifts_reduce_actions = [
      (frozenset([
         LR0(self.arith.START, 0, 0),
         LR0('S', 0, 0), 
         LR0('E', 0, 0), LR0('E', 1, 0),]), (('id', 2), ('let', 4)), () ),
      
      (frozenset([
         LR0(self.arith.START, 0, 1),]), (), () ),
      
      (frozenset([
         LR0('E', 0, 1),]), (), () ),

      (frozenset([
         LR0('S', 0, 1),]), (), () ),
      
      (frozenset([
         LR0('E', 1, 1), 
         LR0(self.arith.ACTION_INSIDE % 1, 0, 0),]), (), () ),
      
      (frozenset([
         LR0('E', 1, 2),]), (('(', 9),), () ),
      
      (frozenset([
         LR0('E', 1, 4),]), ((')', 8),), () ),
      
      (frozenset([
         LR0('E', 1, 6),]), (), () ),
      
      (frozenset([
         LR0('E', 1, 5), 
         LR0(self.arith.ACTION_INSIDE % 2, 0, 0),]), (), () ),

      (frozenset([
         LR0('E', 1, 3), 
         LR0('E', 0, 0), LR0('E', 1, 0),]), (('id', 2), ('let', 4)), () ),
      ]

      self.assertTrue(len(states_shifts_reduce_actions) == len(self.action_table.keys()))
      
      for state, shifts, reduces in states_shifts_reduce_actions:
         h = hash(state)

         self.assertTrue(len(shifts) == len(filter(lambda action: "Shift" in str(action), self.action_table[h].values())))

         if not shifts:
            continue
         keys, ids = zip(*shifts)
         found_ids = [i for i in range(len(states_shifts_reduce_actions)) if ("Shift %s" % hex(hash(states_shifts_reduce_actions[i][0]))) in map(lambda a: str(a), self.action_table[h].values())]
         found_keys = self.action_table[h].keys()

         self.assertTrue(frozenset(ids) == frozenset(found_ids))
         self.assertTrue(frozenset(keys) == frozenset(found_keys))


   def test_parse_complex_let_var_expression(self):
      source = StringIO("let (2)")
      lexer = RegressionTestUnknowGotoState.CalcLexer(source)
      self.driver.parse(lexer)


if __name__ == '__main__':
   unittest.main()
