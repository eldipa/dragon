from grammar import Grammar

class Syntax:
   def __init__(self, start_symbol, terminals = None):
      '''Creates the syntax of some language which grammar is defined
         by the calls to the methods of this class.
         It is a high level view of the class Grammar which provides
         a much more rich and high level expressions.

         The parameters 'start_symbol' and 'terminals' are the same
         parameters of the constructor of Grammar, but a difference of Grammar,
         the 'start_symbol' is an required element.

         See the documentation of Grammar.

         '''
      if start_symbol is None:
         raise ValueError("The parameter 'start_symbol' must not be None.")

      self._grammar = Grammar(start_symbol, terminals)

   def _symbols(self, symbols, sym_production=None):
      '''Utility to make 'symbols' a tuple, concatenated with 'sym_production'
         if it is not None.
         '''
      if not isinstance(symbols, (list, tuple)):
         symbols = (str(symbols), )

      if sym_production:
         return tuple(symbols)+(sym_production,)
      else:
         return tuple(symbols)
         

   def terminal(self, terminal, _unused):
      '''Adds a terminal element. 
         See the documentation of 'add_terminal' of Grammar.
         '''
      self._grammar.add_terminal(terminal)
      return terminal

   def rule(self, symbols, production_name):
      '''Adds a rule 'production_name' -> 'symbols'. 
         See the documentation of 'add_production' of Grammar.
         '''
      self._grammar.add_production(production_name, self._symbols(symbols))
      return production_name

   def choice(self, alternatives, production_name):
      '''Adds multiples rules, each rule assigned to the same 'production_name'
         symbol, making each one a possible alternative.
         See the documentation of 'add_production' of Grammar.
         '''
      if len(alternatives) <= 1:
         raise ValueError('''Expected two or more alternatives, 
                             but received '%s'.''' % str(alternatives))
      
      for alternative in alternatives:
         self._grammar.add_production(production_name, 
                                       self._symbols(alternative))
   
      return production_name
 
   
   def repeat(self, symbols, production_name):
      '''Adds a high level rule which derivates in "zero or more" times
         the 'production_name' symbol.'''
      self._grammar.add_production(production_name, 
                                    self._symbols(symbols, production_name))
      self._grammar.add_production(production_name, 
                                    self._symbols(symbols))
      return production_name

   def optional(self, symbols, production_name):
      '''Adds a high level rule which derivates in "zero or one" times
         the 'production_name' symbol.'''
      self._grammar.add_production(production_name, self._symbols(symbols))
      self._grammar.add_empty_production(production_name)
      return production_name
      

