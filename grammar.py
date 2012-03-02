import itertools
from collections import defaultdict 

class Grammar:
   EMPTY = "<<e>>"
   START = "<<S>>"
   EOF = "<<$>>"
   def __init__(self, start_symbol = None, terminals = None):
      self._productions = defaultdict(list)
      self._terminals = set() if not terminals else set(terminals)
      self._semantic = dict()

      if start_symbol:
         self.augment(start_symbol)


   def _assign_semantic_action(self, symbol, semantic_action, count = None, consume = None):
      if semantic_action:
         count = count if count != None else len(self[symbol][-1])
         consume = consume if consume != None else True
         self._semantic[(symbol, len(self[symbol]) - 1)] = (count, consume, semantic_action)
         

   def add_terminal(self, terminal):
      self._terminals.add(terminal)

   def add_rule(self, symbol, rule, semantic_action = None):
      '''Add a rule, like symbol -> rule.'''
      assert rule
      assert Grammar.EMPTY not in rule
      assert not any(map(lambda s: hasattr(s, '__call__'), rule))

      self._productions[symbol].append(tuple(rule))
      self._assign_semantic_action(symbol, semantic_action)


   def add_empty(self, symbol, semantic_action = None):
      ''' Add a rule: symbol -> <<empty>> '''
      self._productions[symbol].append((Grammar.EMPTY,))
      self._assign_semantic_action(symbol, semantic_action)

   
   def augment(self, symbol_start, semantic_action = None):
      assert not symbol_start in self._productions
      assert not self.is_augment()
      self.add_rule(Grammar.START, (symbol_start, Grammar.EOF), semantic_action)

   def start_symbol(self):
      assert self.is_augment()
      return self[self.START][0][0]

   def semantic_definition(self, symbol, num_of_production):
      key = (symbol, num_of_production)
      if key in self._semantic:
         return self._semantic[key]
      
      return None

   def __getitem__(self, symbol):
      return self._productions[symbol] if symbol in self._productions else None
   
   def is_empty(self, symbol):
      return symbol == Grammar.EMPTY

   def is_empty_rule(self, rule):
      return (Grammar.EMPTY, ) == rule

   def is_a_terminal(self, symbol):
      return symbol in self._terminals

   def is_a_nonterminal(self, symbol):
      return symbol in self._productions

   def is_augment(self):
      return Grammar.START in self._productions

   def is_start_symbol(self, symbol):
      return symbol == self.start_symbol()
   
   def is_augmented_start_symbol(self, symbol):
      return symbol == self.START

   def iter_nonterminals(self):
      return iter(self._productions.keys())
   
   def iter_on_all_symbols(self):
      '''Return a iterator of all symbols, symbols of production and terminals.'''
      return itertools.chain(self._productions.iterkeys(), self._terminals)
