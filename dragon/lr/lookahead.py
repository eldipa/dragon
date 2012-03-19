import collections
import dragon.lr.item
from dragon.util import first

LookAhead = collections.namedtuple('LookAhead', ('sym_production', 'alternative', 'position', 'lookahead'))

def _next_items(self, grammar):
   '''Given the item A -> abc*Bd [x], where x is the lookahead terminal, return 
      each alternative of B -> *efg [y], for each 'y' in first(dx).
      Return a empty list if B is not a production or not exist B.'''
   alternative = grammar[self.sym_production][self.alternative]
   if self._at_the_end(alternative, grammar): # No exist 'next'
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


def _item_shifted(self, grammar):
   '''Given the item A -> abc*Xde [x], return a new item A -> abcX*de [x] where x is
      the terminal lookahead.
      
      Precondition: The initial item must not be A -> abc* .'''
   assert self.next_symbol(grammar)
   return LookAhead(self.sym_production, self.alternative, self.position + 1, self.lookahead)


LookAhead.next_items = _next_items
LookAhead.next_symbol = dragon.lr.item._next_symbol
LookAhead.item_shifted = _item_shifted
LookAhead._at_the_end = dragon.lr.item._at_the_end
