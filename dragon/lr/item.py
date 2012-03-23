import collections
from dragon.util import follow

class Item:
   def __init__(self, sym_production, alternative, position):
      self.sym_production = sym_production
      self.alternative = alternative
      self.position = position

   def at_the_end(self, my_alternative, grammar):
      '''Return True if the items is A -> abc* .'''
      return len(my_alternative) == self.position or grammar.is_empty_rule(my_alternative)

   def next_items(self, grammar):
      '''Given the item A -> abc*Bd, return each alternative of B -> *efg.
         Return a empty list if B is not a production or not exist B.'''
      alternative = grammar[self.sym_production][self.alternative]
      if self.at_the_end(alternative, grammar): # No exist 'next'
         return []

      next_sym_production = alternative[self.position]
      if grammar.is_a_nonterminal(next_sym_production):
         return [Item(next_sym_production, i, 0) for i in range(len(grammar[next_sym_production]))]

      else:
         return []


   def next_symbol(self, grammar):
      '''Given the item A -> abc*Xde, return X.'''
      alternative = grammar[self.sym_production][self.alternative]
      if self.at_the_end(alternative, grammar):
         return None

      return alternative[self.position]


   def item_shifted(self, grammar):
      '''Given the item A -> abc*Xde, return a new item A -> abcX*de.
         
         Precondition: The initial item must not be A -> abc* .'''
      assert self.next_symbol(grammar)
      return Item(self.sym_production, self.alternative, self.position + 1)

   def followers(self, grammar):
      return follow(grammar, self.sym_production)

   def __hash__(self):
      return hash((self.sym_production, self.alternative, self.position))

   def __eq__(self, other):
      return hash(self) == hash(other)
   
