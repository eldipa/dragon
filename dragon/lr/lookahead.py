import collections
from dragon.lr.item import Item
from dragon.util import first

class LookAhead(Item):
   def __init__(self, sym_production, alternative, position, lookahead):
      Item.__init__(self, sym_production, alternative, position)
      self.lookahead = lookahead

   def self_factory(self, sym_production, alternative, position):
      return LookAhead(sym_production, alternative, position, self.lookahead)

   def next_items(self, grammar):
      '''Given the item A -> abc*Bd [x], where x is the lookahead terminal, return 
         each alternative of B -> *efg [y], for each 'y' in first(dx).
         Return a empty list if B is not a production or not exist B.'''
      alternative = grammar[self.sym_production][self.alternative]
      if self.at_the_end(alternative, grammar): # No exist 'next'
         return []

      next_sym_production = alternative[self.position]
      if grammar.is_a_nonterminal(next_sym_production):
         result = []
         first_set = first(grammar, alternative[self.position + 1:] + (self.lookahead,)) 
         for terminal in first_set:
            result.extend([LookAhead(next_sym_production, i, 0, terminal) for i in range(len(grammar[next_sym_production]))])
         
         return result
      else:
         return []


   def followers(self, grammar):
      return frozenset([self.lookahead])

   def __hash__(self):
      return hash((self.sym_production, self.alternative, self.position, self.lookahead))
   
   def __eq__(self, other):
      return hash(self) == hash(other)
