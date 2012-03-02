
import collections
from driver import Driver
from util import follow

def closure(kernel_items, grammar):
   '''For each given item A -> ab*B, collect all items B -> *cd
      and return them union with the initial items.'''
   to_process = set(kernel_items)
   finished = set()

   while to_process:
      item = to_process.pop()
      finished.add(item)

      next_items = set(item.next_items(grammar))
      news = next_items - finished
      to_process.update(news)

   return frozenset(finished)


def goto(items, symbol, grammar):
   '''For each given item A -> a*Bb, collect all items A -> aB*b where B == 'symbol'.
      Then return the closure of the collected set.'''
   to_process = set([i.item_shifted(grammar) for i in items if i.next_symbol(grammar) == symbol])
   return closure(to_process, grammar)


def canonical_collection(grammar, start_item):
   start_set = set([start_item])
   collection = set()
   to_process = list()
   to_process.append(closure(start_set, grammar))

   while to_process:
      _set = to_process.pop()
      for symbol in grammar.iter_on_all_symbols():
         next_set = goto(_set, symbol, grammar)
         if next_set and next_set not in collection:
            to_process.append(next_set)

      collection.add(_set)

   return frozenset(collection)


def build_parsing_table(grammar, start_item):
   '''Preconditions: the grammar must be already processed.'''
   action_table = collections.defaultdict(dict)
   goto_table = collections.defaultdict(dict)
   canonical = canonical_collection(grammar, start_item)

   for state_set in canonical:
      for nonterminal in grammar.iter_nonterminals():
         goto_table[hash(state_set)][nonterminal] = hash(goto(state_set, nonterminal, grammar))

      #TODO Raise a better exception
      for item in state_set:
         if item == start_item:
            start_set_hash = hash(state_set)

         next_symbol = item.next_symbol(grammar)
         if next_symbol and not grammar.is_a_nonterminal(next_symbol): #Item is A -> a*bc
            goto_state_hash = hash(goto(state_set, next_symbol, grammar))
            action = Driver.Shift(goto_state_hash)

            if next_symbol in action_table[hash(state_set)] and action != action_table[hash(state_set)][next_symbol]:
               raise KeyError(next_symbol)   

            action_table[hash(state_set)][next_symbol] = action
   

         elif item.sym_production == grammar.START and item.position == 1: #Item is S' -> S*
            action = Driver.Accept()
            if grammar.EOF in action_table[hash(state_set)] and action != action_table[hash(state_set)][grammar.EndOfSource]:
               raise KeyError(grammar.EOF)

            action_table[hash(state_set)][grammar.EOF] = action

         elif not next_symbol:    #Item is A -> abc*
            for terminal in follow(grammar, item.sym_production): 
               semantic_definition = grammar.semantic_definition(item.sym_production, item.alternative)
               action = Driver.Reduce(item.sym_production, len(grammar[item.sym_production][item.alternative]), semantic_definition)
               if terminal in action_table[hash(state_set)] and action != action_table[hash(state_set)][terminal]:
                  raise KeyError(terminal)

               action_table[hash(state_set)][terminal] = action

   return action_table, goto_table, start_set_hash
