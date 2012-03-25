import collections
from dragon.util import follow, first

class Item:
   def __init__(self, sym_production, alternative, position):
      self.sym_production = sym_production
      self.alternative = alternative
      self.position = position
   
   def at_the_end(self, my_alternative, grammar):
      '''Return True if the items is A -> abc* .'''
      return len(my_alternative) == self.position or grammar.is_empty_rule(my_alternative)
   
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
      return self.self_factory(self.sym_production, self.alternative, self.position + 1)

   def __eq__(self, other):
      return hash(self) == hash(other)

   def self_factory(self, sym_production, alternative, position):
      raise NotImplementedError()

   def next_items(self, grammar):
      raise NotImplementedError()

   def followers(self, grammar):
      raise NotImplementedError()
   
   def __hash__(self):
      raise NotImplementedError()


class LR0(Item):
   def __init__(self, sym_production, alternative, position):
      Item.__init__(self, sym_production, alternative, position)

   def self_factory(self, sym_production, alternative, position):
      return LR0(sym_production, alternative, position)

   def next_items(self, grammar):
      '''Given the item A -> abc*Bd, return each alternative of B -> *efg.
         Return a empty list if B is not a production or not exist B.'''
      alternative = grammar[self.sym_production][self.alternative]
      if self.at_the_end(alternative, grammar): # No exist 'next'
         return []

      next_sym_production = alternative[self.position]
      if grammar.is_a_nonterminal(next_sym_production):
         return [self.self_factory(next_sym_production, i, 0) for i in range(len(grammar[next_sym_production]))]

      else:
         return []

   def followers(self, grammar):
      return follow(grammar, self.sym_production)

   def __hash__(self):
      return hash((self.sym_production, self.alternative, self.position))


class LR1(LR0):
   def __init__(self, sym_production, alternative, position, lookahead):
      LR0.__init__(self, sym_production, alternative, position)
      self.lookahead = lookahead

   def self_factory(self, sym_production, alternative, position):
      return LR1(sym_production, alternative, position, self.lookahead)

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
            result.extend([LR1(next_sym_production, i, 0, terminal) for i in range(len(grammar[next_sym_production]))])
         
         return result
      else:
         return []

   def followers(self, grammar):
      return frozenset([self.lookahead])

   def __hash__(self):
      return hash((self.sym_production, self.alternative, self.position, self.lookahead))
   

class LALR(LR0):
   def __init__(self, sym_production, alternative, position):
      LR0.__init__(self, sym_production, alternative, position)
      self.lookaheads = set()
      self.new_lookaheads = set()
      self.subscribeds = set()

   def close(self):
      assert self.lookaheads
      assert not self.new_lookaheads
      del self.new_lookaheads
      del self.subscribeds

   def self_factory(self, sym_production, alternative, position):
      return LALR(sym_production, alternative, position)

   def add_new(self, lookahead):
      if lookahead not in self.lookaheads:
         self.new_lookaheads.add(lookahead)
   
   def add_news(self, lookaheads):
      self.new_lookaheads.update(lookaheads)
      self.new_lookaheads -= self.lookaheads

   def subscribe(self, item_lalr):
      self.subscribeds.add(item_lalr)

   def propagate(self):
      if self.new_lookaheads:
         for subscribed in self.subscribeds:
            subscribed.add_news(self.new_lookaheads)

         self.lookaheads.update(self.new_lookaheads)
         self.new_lookaheads.clear()
         return True

      return False

   def followers(self, grammar):
      return frozenset(self.lookaheads)

   def __hash__(self): #Exactly equal to Item::__hash__
      return LR0.__hash__(self)

