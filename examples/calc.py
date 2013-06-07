import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dragon.grammar import Grammar
from dragon.driver import Lexer
from dragon.lr.driver import Driver
from dragon.notation.pythonic import from_string
from dragon.lr.item import LR0
from dragon.lr.builder import build_parsing_table

rpcalc_grammar = '''

input = line

line = [{ NL, ~prompt, FLUSH, line | expr, NL, ~print_result, ~prompt, FLUSH, line}]

expr = {   term, '+', expr, ~add
         | term, '-', expr, ~sub
         | term
         }

term = {   factor, '*', term, ~mul
         | factor, '/', term, ~div
         | factor, '%', term, ~mod
         | factor
         }

factor =  {   NUM
            | '(', expr, ')'
            | '-', factor, ~neg
          }
         
''' 


class CalcLexer(Lexer):
   def __init__(self, source):
      self._source = source
      self._white_characters = (' ', '\t', '\v', '\r')
      self._number = re.compile('\d+(\.\d+)?')
   
   def tokenizer(self):
      '''Return a iterable or generator of all tokens.
         Each token is a tuple with at least one value, the terminal id. 
         The next values, if any, are the attributes of the token.'''
 
      line = self._source.readline()
      while line:
         i = 0

         while i < len(line):
            # skip whitespaces
            while i < len(line) and line[i] in self._white_characters:
               i += 1

            match = self._number.match(line, i)
            if i == len(line):
               continue
            elif line[i] == '\n':
               yield 'NL', None
               yield 'FLUSH', None #hack
            elif match:
               yield ('NUM', int(match.group()))
               i = match.end() - 1
            else:
               yield line[i], None

            i += 1
         
         line = self._source.readline()
      yield (Grammar.EOF, None)
      

def print_result(val):
   print "Result:  ", val

def probe(*args):
   print "--", len(args), "-", " ".join(map(str, args))

def prompt(*args):
   print ">>> ",

grammar = from_string(rpcalc_grammar, 'input', 
      print_result=print_result,
      probe=probe,
      prompt=prompt,
      up=lambda x: x,
      add=lambda x, y: x + y,
      sub=lambda x, y: x - y,
      mul=lambda x, y: x * y,
      div=lambda x, y: x / y,
      mod=lambda x, y: x % y,
      neg=lambda x: -x)

states, gotos, first = build_parsing_table(grammar, LR0(grammar.START, 0, 0))
driver = Driver(states, gotos, first)

print "Reverse polish calculator. Write expressions like "
print " >>> 2 + 3       (result in 2 + 3 = 5)  or "
print " >>> 2 + 4 * 5   (result in 2 + (4 * 5) = 22)"
print 
prompt()
driver.parse(CalcLexer(sys.stdin))
