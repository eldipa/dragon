import collections
from dragon.util import follow, first

class Item(object):
   def __init__(self, sym_production, alternative, position):
      '''A item represent a position in the parser. This is codified according the
         'symbol' of the productions, the number of the production or 'alternative'
         and the position in the rule.

         That is, if exists two rules A -> ab | cd, then the Item (A, 0, 1) represents
         the rule number 0 (the first) of the rules of A, in the 1 position (the second)
         Graphically, the item correspond to A -> a*b, where * marks the position of the
         item.

         Both parameters, alternative and position, starts from 0.
         '''
      self.sym_production = sym_production
      self.alternative = alternative
      self.position = position
   
   def at_the_end(self, my_alternative, grammar):
      '''Return True if the item is of the form A -> abc* 
         
         Precondition: the parameter 'my_alternative' must be according the 'alternative'
         codified in this item.'''
      return len(my_alternative) == self.position or grammar.is_empty_rule(my_alternative)
   
   def next_symbol(self, grammar):
      '''Given the item A -> abc*Xde, returns the symbol X.
         If the item has not X (that is, the item is of the form A -> abc*), returns
         None.'''
      alternative = grammar[self.sym_production][self.alternative]
      if self.at_the_end(alternative, grammar):
         return None

      return alternative[self.position]

   def item_shifted(self, grammar):
      '''Given the item A -> abc*Xde, return a new item A -> abcX*de.
         
         Precondition: The initial item must not be of the form A -> abc* .'''
      assert self.next_symbol(grammar)
      return self.self_factory(self.sym_production, self.alternative, self.position + 1)

   def __eq__(self, other):
      return hash(self) == hash(other)

   def self_factory(self, sym_production, alternative, position):
      '''Builds a other item with these parameters.'''
      raise NotImplementedError()

   def next_items(self, grammar):
      '''At first, given the item A -> abc*Bd, return each alternative of B -> *efg.
         The exact meaning of this method is specified in each overridden method.'''
      raise NotImplementedError()

   def followers(self, grammar):
      '''Return a set of terminals that 'follow' this item. 
         The exact meaning of this method is specified in each overridden method.'''
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
      '''The item start as a LR0 item but can learn and register the lookaheads
         as a LR1. In fact, the LALR item can register more than one lookahead so
         it can be seen as the union of many LR1 items.
      '''
      LR0.__init__(self, sym_production, alternative, position)
      self.lookaheads = set()
      self.new_lookaheads = set()
      self.subscribeds = set()

   def close(self):
      '''Close the learning stage. The item can not accept any new lookahead.'''
      assert self.lookaheads
      assert not self.new_lookaheads
      del self.new_lookaheads
      del self.subscribeds

   def self_factory(self, sym_production, alternative, position):
      return LALR(sym_production, alternative, position)

   def add_new(self, lookahead):
      '''Adds a new lookahead terminal.'''
      if lookahead not in self.lookaheads:
         self.new_lookaheads.add(lookahead)
   
   def add_news(self, lookaheads):
      '''Adds many news lookahead terminals.'''
      self.new_lookaheads.update(lookaheads)
      self.new_lookaheads -= self.lookaheads

   def subscribe(self, item_lalr):
      '''Adds a other LALR item as a subscriber of this. 
         The items LALR can be interested in the lookahead terminals of others 
         and learn from them. So each new terminal registred by this item
         can be propagated to the subscribers.'''
      self.subscribeds.add(item_lalr)

   def propagate(self):
      '''Propagates the new lookahead terminals to the LALR subscribers.
         It's guaranteed that the lookahead are effectively new, and none terminal
         is propagate more than once.

         Returns True if some lookahead was propagated, False in other case.'''
      if self.new_lookaheads:
         for subscribed in self.subscribeds:
            subscribed.add_news(self.new_lookaheads)

         self.lookaheads.update(self.new_lookaheads)
         self.new_lookaheads.clear()
         return True

      return False

   def followers(self, grammar):
      '''Returns the lookaheads terminals registered. 
         Precondition: The 'close' method must be called before.'''
      assert not hasattr(self, 'new_lookaheads') and not hasattr(self, 'subscribed') #its closed
      return frozenset(self.lookaheads)

   def __hash__(self): #Exactly equal to Item::__hash__
      return LR0.__hash__(self)

