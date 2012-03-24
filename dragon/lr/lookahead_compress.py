from dragon.lr.item import Item

class LookAheadCompress(Item):
   def __init__(self, sym_production, alternative, position):
      Item.__init__(self, sym_production, alternative, position)
      self.lookaheads = set()
      self.new_lookaheads = set()
      self.subscribeds = set()

   def close(self):
      assert self.lookaheads
      assert not self.new_lookaheads
      del self.new_lookaheads
      del self.subscribeds


   def self_factory(self, sym_production, alternative, position):
      return LookAheadCompress(sym_production, alternative, position)

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

   def __hash__(self): #Exactly equal to Item::__hash__ and Item::__eq__
      return hash((self.sym_production, self.alternative, self.position))

   def __eq__(self, other):
      return hash(self) == hash(other)

