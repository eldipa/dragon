from collections import defaultdict 

class GrammarBuilder:
   EMPTY = "<<e>>"
   START = "<<S>>"
   EOF = "<<$>>"
   def __init__(self, start_symbol = None, terminals = None):
      self._productions = defaultdict(list)
      self._terminals = set() if not terminals else set(terminals)
      self._semantic = defaultdict(list)

      if start_symbol:
         self.augment(start_symbol)


   def _assign_semantic_action(self, symbol, semantic_action):
      if semantic_action:
         self._semantic[symbol].append((len(self._productions[symbol]) - 1, semantic_action))

   def add_terminal(self, terminal):
      self._terminals.add(terminal)

   def add_rule(self, symbol, rule, semantic_action = None):
      '''Add a rule, like symbol -> rule.'''
      assert rule
      assert GrammarBuilder.EMPTY not in rule
      assert not any(map(lambda s: hasattr(s, '__call__'), rule))

      self._productions[symbol].append(tuple(rule))
      self._assign_semantic_action(symbol, semantic_action)


   def add_empty(self, symbol, semantic_action = None):
      ''' Add a rule: symbol -> <<empty>> '''
      self._productions[symbol].append((GrammarBuilder.EMPTY,))
      self._assign_semantic_action(symbol, semantic_action)

   
   def augment(self, symbol_start, semantic_action = None):
      assert not symbol_start in self._productions
      assert not self.is_augment()
      self.add_rule(GrammarBuilder.START, (symbol_start, GrammarBuilder.EOF), semantic_action)

   def start_symbol(self):
      assert self.is_augment()
      return self[self.START][0][0]
   
   def __getitem__(self, symbol):
      return self._productions[symbol] if symbol in self._productions else None
   
   def is_empty(self, symbol):
      return symbol == GrammarBuilder.EMPTY

   def is_empty_rule(self, rule):
      return (GrammarBuilder.EMPTY, ) == rule

   def is_a_terminal(self, symbol):
      return symbol in self._terminals

   def is_a_nonterminal(self, symbol):
      return symbol in self._productions

   def is_augment(self):
      return GrammarBuilder.START in self._productions

   def is_start_symbol(self, symbol):
      return symbol == self.start_symbol()
   
   def is_augmented_start_symbol(self, symbol):
      return symbol == self.START

   def iter_nonterminals(self):
      return iter(self._productions.keys())
