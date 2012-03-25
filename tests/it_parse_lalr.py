import unittest
import dragon.grammar as grammar
from StringIO import StringIO
import re
from dragon.lr.builder import build_parsing_table_lalr
from dragon.lr.driver import Driver
from dragon.driver import Lexer
from dragon.lr.item import LR0

class IntegralTestParseCalculatorForLALRGrammar(unittest.TestCase):
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
                  yield (line[i], line[i])
                  i += 1

         yield (grammar.Grammar.EOF, grammar.Grammar.EOF)
         return 

   def setUp(self):
      self.lrvalue = grammar.Grammar(None, ('=', '*', ';', 'id', 'num'))
      self.symbol_table = dict()
      self.last_value = None

      def set_var(args): 
         self.symbol_table[args[0]] = args[2]; 
         return self.symbol_table[args[0]]

      def get_var(args): 
         if args[1] in self.symbol_table:
            return self.symbol_table[args[1]]
         
         raise KeyError(args[1])

      def grab_last_value(args):
         self.last_value = args[0] if isinstance(args[0], int) else self.symbol_table[args[0]]
         return args[0]

      self.lrvalue.augment('S')

      self.lrvalue.add_rule('S', ['E', ';', 'S',   lambda args: args[2]])
      self.lrvalue.add_rule('S', ['E', ';',        lambda args: args[0]])
      self.lrvalue.add_rule('E', ['L', '=', 'R',   set_var])
      self.lrvalue.add_rule('E', ['R',             grab_last_value])
      self.lrvalue.add_rule('L', ['*', 'R',        get_var])
      self.lrvalue.add_rule('L', ['id',            lambda args: args[0]])
      self.lrvalue.add_rule('R', ['L',             lambda args: args[0]])
      self.lrvalue.add_rule('R', ['num',           lambda args: args[0]])

      self.action_table, self.goto_table, self.start_state = build_parsing_table_lalr(self.lrvalue, LR0(self.lrvalue.START, 0, 0), False)
      self.driver = Driver(self.action_table, self.goto_table, self.start_state)

   
   def test_parse_simple_expresion(self):
      source = StringIO("2;")
      lexer = IntegralTestParseCalculatorForLALRGrammar.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.last_value == 2)

   def test_parse_assign_expresion(self):
      source = StringIO('''a = 2;
                           a;''')
      lexer = IntegralTestParseCalculatorForLALRGrammar.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.last_value == 2)

   def test_parse_simple_derefered(self):
      source = StringIO('''a = 2;
                           b = *a;
                           a = 4;
                           b;''')
      lexer = IntegralTestParseCalculatorForLALRGrammar.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.last_value == 2)

   def test_parse_complex_derefered(self):
      source = StringIO('''a = 0; b = 0; c = 0;

                           a = 2;
                           b = a;
                           c = **b;
                           
                           a = 0; b = 0;
                           c;''')
      lexer = IntegralTestParseCalculatorForLALRGrammar.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.last_value == 2)

if __name__ == '__main__':
   unittest.main()
