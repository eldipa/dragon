import unittest
import dragon.grammar as grammar
from StringIO import StringIO
import re
from dragon.lr.util import build_parsing_table
from dragon.lr.driver import Driver
from dragon.driver import Lexer
from dragon.lr.item import Item

class IntegralTestParseCalculator(unittest.TestCase):
   class CalcLexer(Lexer):
      def __init__(self, source):
         self._source = source
         self._white_characters = (' ', '\t', '\v', '\n', '\r')
         self._number = re.compile('[+-]?\d+(\.\d+)?')
      
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

               match = self._number.match(line, i)
               if match:
                  yield ('id', int(match.group()))
                  i = match.end()
               else:
                  yield (line[i], line[i])
                  i += 1

         yield (grammar.Grammar.EOF, grammar.Grammar.EOF)
         return 


   def setUp(self):
      self.arith = grammar.Grammar('S', ('+', '*', '(', ')', 'id'))
      self.result = None

      def get_result(args): self.result = args[0]; return args[0]
      def add(args): t = args[0] + args[2]; return t
      def mul(args): t = args[0] * args[2]; return t

      self.arith.add_rule('S', ['E',           get_result])
      self.arith.add_rule('E', ['E', '+', 'T', add])
      self.arith.add_rule('E', ['T',           lambda args: args[0]])
      self.arith.add_rule('T', ['T', '*', 'F', mul])
      self.arith.add_rule('T', ['F',           lambda args: args[0]])
      self.arith.add_rule('F', ['(', 'E', ')', lambda args: args[1]])
      self.arith.add_rule('F', ['id',          lambda args: args[0]])

      self.action_table, self.goto_table, self.start_state = build_parsing_table(self.arith, Item(self.arith.START, 0, 0))
      self.driver = Driver(self.action_table, self.goto_table, self.start_state)

   
   def test_parse_simple_expresion(self):
      source = StringIO("3 + 2")
      lexer = IntegralTestParseCalculator.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.result == 3+2)

   def test_parse_complex_expresion(self):
      source = StringIO("3 * 2 + 9")
      lexer = IntegralTestParseCalculator.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.result == (3*2) + 9)

   def test_parse_complex_expresion_reversed(self):
      source = StringIO("9 + 3 * 2")
      lexer = IntegralTestParseCalculator.CalcLexer(source)
      self.driver.parse(lexer)

      self.assertTrue(self.result == (3*2) + 9)


if __name__ == '__main__':
   unittest.main()
