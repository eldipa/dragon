import unittest
import dragon.grammar as grammar
from StringIO import StringIO
import re
from dragon.lr.builder import build_parsing_table
from dragon.lr.driver import Driver
from dragon.driver import Lexer
from dragon.lr.item import LR1

class IntegralTestParseCalculatorForLR1Grammar(unittest.TestCase):
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
                  yield ('num', int(match_id.group()))
                  i = match_id.end()
               elif match_var:
                  yield ('id', match_var.group())
                  i = match_var.end()
               else:
                  yield (line[i], None)
                  i += 1

         yield (grammar.Grammar.EOF, None)
         return 

   def setUp(self):
      self.lrvalue = grammar.Grammar(None, ('=', '*', ';', 'id', 'num'))
      self.symbol_table = dict()
      self.last_value = None

      def set_var(lv, rv): 
         self.symbol_table[lv] = rv; 
         return self.symbol_table[lv]

      def get_var(rv): 
         if rv in self.symbol_table:
            return self.symbol_table[rv]
         
         raise KeyError(rv)

      def grab_last_value(rv):
         self.last_value = rv if isinstance(rv, int) else self.symbol_table[rv]
         return rv

      self.lrvalue.augment('S')

      self.lrvalue.add_rule('S', ['E', ';', 'S',   lambda e, s: s])
      self.lrvalue.add_rule('S', ['E', ';',        lambda v: v])
      self.lrvalue.add_rule('E', ['L', '=', 'R',   set_var])
      self.lrvalue.add_rule('E', ['R',             grab_last_value])
      self.lrvalue.add_rule('L', ['*', 'R',        get_var])
      self.lrvalue.add_rule('L', ['id',            lambda v: v])
      self.lrvalue.add_rule('R', ['L',             lambda v: v])
      self.lrvalue.add_rule('R', ['num',           lambda v: v])

      self.action_table, self.goto_table, self.start_state = build_parsing_table(self.lrvalue, LR1(self.lrvalue.START, 0, 0, self.lrvalue.EOF), False)
      self.driver = Driver(self.action_table, self.goto_table, self.start_state)

   
   def test_parse_simple_expresion(self):
      source = StringIO("2;")
      lexer = IntegralTestParseCalculatorForLR1Grammar.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.last_value == 2)

   def test_parse_assign_expresion(self):
      source = StringIO('''a = 2;
                           a;''')
      lexer = IntegralTestParseCalculatorForLR1Grammar.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.last_value == 2)

   def test_parse_simple_derefered(self):
      source = StringIO('''a = 2;
                           b = *a;
                           a = 4;
                           b;''')
      lexer = IntegralTestParseCalculatorForLR1Grammar.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.last_value == 2)

   def test_parse_complex_derefered(self):
      source = StringIO('''a = 0; b = 0; c = 0;

                           a = 2;
                           b = a;
                           c = **b;
                           
                           a = 0; b = 0;
                           c;''')
      lexer = IntegralTestParseCalculatorForLR1Grammar.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.last_value == 2)

if __name__ == '__main__':
   unittest.main()
