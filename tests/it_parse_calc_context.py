import unittest
import dragon.grammar as grammar
from StringIO import StringIO
import re
from dragon.lr.util import build_parsing_table
from dragon.lr.driver import Driver
from dragon.driver import Lexer
from dragon.lr.item import LR0

class IntegralTestParseCalculatorWithContexts(unittest.TestCase):
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
      self.arith = grammar.Grammar('S', ('+', '*', '(', ')', 'id', 'var', '=', 'let'))
      self.symbol_table = [dict()]
      self.result = None

      def get_result(args): self.result = args[0]; return args[0]
      def add(args): t = args[0] + args[2]; return t
      def mul(args): t = args[0] * args[2]; return t

      def set_var(args): self.symbol_table[-1][args[0]] = args[2]; return args[2]
      def get_var(args): 
         for table in reversed(self.symbol_table):
            if args[0] in table:
               return table[args[0]]
         
         raise KeyError(args[0])

      def push(args): assert args[0] == "let"; self.symbol_table.append(dict())
      def pop(args): assert args[0] == "let"; self.symbol_table.pop()


      self.arith.add_rule('S', ['E',                             get_result])
      self.arith.add_rule('E', ['E', '+', 'T',                   add])
      self.arith.add_rule('E', ['T',                             lambda args: args[0]])
      self.arith.add_rule('T', ['T', '*', 'F',                   mul])
      self.arith.add_rule('T', ['F',                             lambda args: args[0]])
      self.arith.add_rule('F', ['(', 'E', ')',                   lambda args: args[1]])
      self.arith.add_rule('F', ['id',                            lambda args: args[0]])
      self.arith.add_rule('F', ['var', '=', 'E',                 set_var])
      self.arith.add_rule('F', ['var',                           get_var])
      self.arith.add_rule('F', ['let', push, '(', 'E', ')', pop, lambda args: args[3]])

      self.action_table, self.goto_table, self.start_state = build_parsing_table(self.arith, LR0(self.arith.START, 0, 0))
      self.driver = Driver(self.action_table, self.goto_table, self.start_state)

   
   def test_parse_simple_expression(self):
      source = StringIO("3 + 2")
      lexer = IntegralTestParseCalculatorWithContexts.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.result == 3+2)

   def test_parse_var_expression(self):
      source = StringIO("X = 3 * 2 + 9")
      lexer = IntegralTestParseCalculatorWithContexts.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.result == (3*2) + 9)
      self.assertTrue(self.symbol_table[-1]['X'] == (3*2) + 9)

   def test_parse_complex_var_expression(self):
      source = StringIO("Z= (X=9) + 3 * (Y=2)")
      lexer = IntegralTestParseCalculatorWithContexts.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.result == (3*2) + 9)
      self.assertTrue(self.symbol_table[-1]['X'] == 9)
      self.assertTrue(self.symbol_table[-1]['Y'] == 2)

   def test_parse_complex_let_var_expression(self):
      source = StringIO("(X=5) + let ((X=2) + 3) + X")
      lexer = IntegralTestParseCalculatorWithContexts.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.result == 5 + (2 + 3) + 5)
      self.assertTrue(self.symbol_table[-1]['X'] == 5)

if __name__ == '__main__':
   unittest.main()
