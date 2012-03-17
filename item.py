import collections

Item = collections.namedtuple('Item', ('sym_production', 'alternative', 'position'))

def _at_the_end(self, my_alternative, grammar):
   '''Return True if the items is A -> abc* .'''
   return len(my_alternative) == self.position or grammar.is_empty_rule(my_alternative)

def _next_items(self, grammar):
   '''Given the item A -> abc*Bd, return each alternative of B -> *efg.
      Return a empty list if B is not a production or not exist B.'''
   alternative = grammar[self.sym_production][self.alternative]
   if self._at_the_end(alternative, grammar): # No exist 'next'
      return []

   next_sym_production = alternative[self.position]
   if grammar.is_a_nonterminal(next_sym_production):
      return [Item(next_sym_production, i, 0) for i in range(len(grammar[next_sym_production]))]

   else:
      return []


def _next_symbol(self, grammar):
   '''Given the item A -> abc*Xde, return X.'''
   alternative = grammar[self.sym_production][self.alternative]
   if self._at_the_end(alternative, grammar):
      return None

   return alternative[self.position]


def _item_shifted(self, grammar):
   '''Given the item A -> abc*Xde, return a new item A -> abcX*de.
      
      Precondition: The initial item must not be A -> abc* .'''
   assert self.next_symbol(grammar)
   return Item(self.sym_production, self.alternative, self.position + 1)


Item.next_items = _next_items
Item.next_symbol = _next_symbol
Item.item_shifted = _item_shifted
Item._at_the_end = _at_the_end
