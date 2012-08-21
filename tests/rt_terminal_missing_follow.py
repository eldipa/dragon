import unittest
import dragon.grammar as grammar
import dragon.syntax as syntax
from StringIO import StringIO
import re
from dragon.lr.builder import build_parsing_table
from dragon.lr.driver import Driver
from dragon.driver import Lexer
from dragon.lr.item import LR0
from dragon.lr.helper import show_states
from dragon.lr.util import kernel_collection, closure
from dragon.util import follow

class RegressionTestParser(unittest.TestCase):
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
               elif match:
                  yield ('NUM', int(match.group()))
                  i = match.end() - 1
               else:
                  yield line[i], None

               i += 1
            
            line = self._source.readline()
         yield (grammar.Grammar.EOF, None)


   def setUp(self):
      syn = syntax.Syntax('input')
      self.result = []

      syn.terminal('NL', None)
      syn.terminal('NUM', None)
      syn.terminal('+', None)
      syn.terminal('-', None)

      syn.repeat(('line',), 'input')
      syn.choice((('NL',), ('expr','NL', lambda x: self.result.append(x))),'line')
      syn.choice((('NUM',), ('expr','expr', '+', lambda x, y: x+y), ('expr','expr', '-', lambda x, y: x-y)),'expr')

      self.grammar = syn.as_grammar()
      
      self.start_item = LR0(self.grammar.START, 0, 0)
      self.action_table, self.goto_table, self.start_state = build_parsing_table(self.grammar, self.start_item, disable_mapping=True)
      self.driver = Driver(self.action_table, self.goto_table, self.start_state)
      
      self.kernel_states = [
         frozenset([
            LR0(self.grammar.START, 0, 0),
            ]),
         frozenset([
            LR0(self.grammar.START, 0, 1),
            ]),
         frozenset([
            LR0('input', 0, 1),
            LR0('input', 1, 1),
            ]),
         frozenset([
            LR0('line', 0, 1),
            ]),
         frozenset([
            LR0('line', 1, 1),
            LR0('expr', 1, 1),
            LR0('expr', 2, 1),
            ]),
         frozenset([
            LR0('expr', 0, 1),
            ]),
         frozenset([
            LR0('input', 0, 2),
            ]),
         frozenset([
            LR0('line', 1, 2),
            ]),
         frozenset([
            LR0('expr', 1, 1),
            LR0('expr', 1, 2),
            LR0('expr', 2, 1),
            LR0('expr', 2, 2),
            ]),
         frozenset([
            LR0('expr', 1, 3),
            ]),
         frozenset([
            LR0('expr', 2, 3),
            ])
         ]

   
   def test_grammar(self):
      self.assertTrue(set(self.grammar.iter_on_all_symbols()) - set(self.grammar.iter_nonterminals()) ==\
            {'NL', 'NUM', '+', '-'})

      self.assertTrue(set(self.grammar.iter_nonterminals()) == \
            {'input', 'line', 'expr', self.grammar.START})

      self.assertTrue(set(self.grammar[self.grammar.START]) == \
            {('input',)})

      self.assertTrue(set(self.grammar['input']) == \
            {('line',), ('line', 'input')})
      
      self.assertTrue(set(self.grammar['line']) == \
            {('NL',), ('expr', 'NL')})
      
      self.assertTrue(set(self.grammar['expr']) == \
            {('NUM',), ('expr', 'expr', '+'), ('expr', 'expr', '-')})


   def test_canonical(self):
      collection = kernel_collection(self.grammar, self.start_item)
      self.assertTrue(len(collection) == 11)
      self.assertTrue(frozenset(self.kernel_states) == collection)

   def test_action_table(self):
      states = [closure(kernel, self.grammar) for kernel in self.kernel_states]
      
      expected_terminal_shift = [
            {'NL', 'NUM'},
            {},
            {'NL', 'NUM'},
            {},
            {'NL', 'NUM'},
            {},
            {},
            {},
            {'NUM', '+', '-'},
            {},
            {},
            ]
   
      for state, terminals in zip(states, expected_terminal_shift):
         keys = self.action_table[hash(state)].keys()
         keys = filter(lambda k: "Shift" in str(self.action_table[hash(state)][k]), keys) 
         self.assertTrue(frozenset(keys) == frozenset(terminals))

      expected_terminal_reduce = [
            {},
            {},
            {self.grammar.EOF}, #input
            {self.grammar.EOF, 'NL', 'NUM'}, #line
            {},
            {'NL', '+', '-', 'NUM'}, #expr
            {self.grammar.EOF}, #input
            {self.grammar.EOF, 'NL', 'NUM'}, #line
            {},
            {'NL', '+', '-', 'NUM'}, #expr
            {'NL', '+', '-', 'NUM'}, #expr
            ]
      
      for state, terminals in zip(states, expected_terminal_reduce):
         keys = self.action_table[hash(state)].keys()
         keys = filter(lambda k: "Reduce" in str(self.action_table[hash(state)][k]), keys) 
         self.assertTrue(frozenset(keys) == frozenset(terminals))
      

   def test_bug_missing_terminals_found_by_follow_algorithm(self):
      '''The problem is due the 'follow' algorithm assumes that if
         a rule has the nonterminal X, the rules has only one X.
         Obviously, this is not true in general.
         '''
      found = follow(self.grammar, 'expr')
      self.assertTrue({'NL', 'NUM'} & found) #found by the 'first' algorithm
      self.assertTrue({'+', '-'} & found)    #found by the 'follow' algorithm

      self.assertTrue(frozenset(['NUM', 'NL', '+', '-']) == found)


   def test_single_number(self):
      source = StringIO("3\n")
      lexer = RegressionTestParser.CalcLexer(source)
      self.driver.parse(lexer)
      self.assertTrue(self.result == [3])
   
   def test_multiple_numbers(self):
      source = StringIO("3\n\n\n2\n1\n")
      lexer = RegressionTestParser.CalcLexer(source)
      self.driver.parse(lexer)
      self.assertTrue(self.result == [3, 2, 1])

   def test_add(self):
      source = StringIO("3 2 +\n")
      lexer = RegressionTestParser.CalcLexer(source)
      self.driver.parse(lexer)
      self.assertTrue(self.result == [3+2])

if __name__ == '__main__':
   unittest.main()
