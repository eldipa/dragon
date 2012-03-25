import collections
from dragon.lr.driver import Driver
from dragon.lr.item import LR1, LALR

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


def goto(items, symbol, grammar, only_kernel = False):
   '''For each given item A -> a*Bb, collect all items A -> aB*b where B == 'symbol'.
      Then return the closure of the collected set.'''
   to_process = frozenset([i.item_shifted(grammar) for i in items if i.next_symbol(grammar) == symbol])
   return closure(to_process, grammar) if not only_kernel else to_process


def canonical_collection(grammar, start_item):
   start_set = frozenset([start_item])
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

def kernel_collection(grammar, start_item):
   start_set = frozenset([start_item])
   collection = set()
   to_process = list()
   to_process.append(start_set)

   while to_process:
      kernel_set = to_process.pop()
      _set = closure(kernel_set, grammar)
      for symbol in grammar.iter_on_all_symbols():
         next_set = goto(_set, symbol, grammar, only_kernel=True)
         if next_set and next_set not in collection:
            to_process.append(next_set)

      collection.add(kernel_set)

   return frozenset(collection)


class LRConflict(Exception):
   def __init__(self, msg):
      Exception.__init__(self)
      self.msg = msg

   def __str__(self):
      return str(self.msg)

class ReduceReduce(LRConflict):
   def __init__(self, new, old, sym):
      LRConflict.__init__(self, "A Reduce-Reduce conflict discovered during process '%s' terminal. This is because there are two productions that are ready to be reduced at the same time, but only one of them can be effectively reduced. So, which production must be reduced?\nThese are the conflicting productions:\n%s\n%s" % (sym, new.production_str(), old.production_str()))

class ShiftReduce(LRConflict):
   def __init__(self, new, old, sym):
      LRConflict.__init__(self, "A Shift-Reduce conflict discovered during process '%s' terminal. This is because there are two productions, one that is ready to be reduced and the other can still shift more terminals at the same time. So, which action must be choosed? By default, it's choosed the shift action.\nThese are the conflicting productions:\n%s\n%s" % (sym, new.production_str(), old.production_str()))

def handler_conflict(new_action, old_action, next_symbol, handle_shift_reduce):
   new_action_str = str(new_action)
   old_action_str = str(old_action)

   is_new_reduce = "Reduce" in str(new_action)
   is_old_reduce = "Reduce" in str(old_action)
   
   if is_new_reduce and is_old_reduce:
      raise ReduceReduce(new_action, old_action, next_symbol)
   elif not is_new_reduce and not is_old_reduce:
      print "Shift-Shift conflict."
      raise KeyError(next_symbol)
   else:
      if handle_shift_reduce:
         return new_action if not is_new_reduce else old_action
      else:
         raise ShiftReduce(new_action, old_action, next_symbol)


def populate_goto_table_from_state(grammar, state_set, goto_table):
   for anysymbol in grammar.iter_on_all_symbols():
      g = goto(state_set, anysymbol, grammar)
      if g:
         goto_table[hash(state_set)][anysymbol] = hash(g) 

def populate_action_table_from_state(grammar, state_set, start_item, action_table, handle_shift_reduce):
   for item in state_set:

      next_symbol = item.next_symbol(grammar)
      if item.sym_production == grammar.START and item.position == 1: #Item is S' -> S*
         action = Driver.Accept()
         if grammar.EOF in action_table[hash(state_set)] and action != action_table[hash(state_set)][grammar.EndOfSource]:
            raise KeyError(grammar.EOF)

         action_table[hash(state_set)][grammar.EOF] = action

      elif next_symbol and not grammar.is_a_nonterminal(next_symbol): #Item is A -> a*bc
         assert not grammar.is_empty(next_symbol)
         goto_state_hash = hash(goto(state_set, next_symbol, grammar))
         action = Driver.Shift(goto_state_hash, item.sym_production, grammar[item.sym_production][item.alternative])

         if next_symbol in action_table[hash(state_set)] and action != action_table[hash(state_set)][next_symbol]:
            action = handler_conflict(action, action_table[hash(state_set)][next_symbol], next_symbol, handle_shift_reduce)

         action_table[hash(state_set)][next_symbol] = action


      elif not next_symbol:    #Item is A -> abc*
         for terminal in item.followers(grammar): 
            semantic_definition = grammar.semantic_definition(item.sym_production, item.alternative)
            action = Driver.Reduce(item.sym_production, grammar[item.sym_production][item.alternative], semantic_definition, grammar.is_empty_rule((grammar[item.sym_production][item.alternative])) )
            if terminal in action_table[hash(state_set)] and action != action_table[hash(state_set)][terminal]:
               action = handler_conflict(action, action_table[hash(state_set)][terminal], terminal, handle_shift_reduce)

            action_table[hash(state_set)][terminal] = action


def build_parsing_table(grammar, start_item, handle_shift_reduce = True):
   '''Preconditions: the grammar must be already processed.'''
   action_table = collections.defaultdict(dict)
   goto_table = collections.defaultdict(dict)
   kernels = kernel_collection(grammar, start_item)
   start_set_hash = None

   for kernel in kernels:
      state_set = closure(kernel, grammar)
      
      populate_goto_table_from_state(grammar, state_set, goto_table)
      populate_action_table_from_state(grammar, state_set, start_item, action_table, handle_shift_reduce)
      
      if not start_set_hash:
         for item in state_set:
            if item == start_item:
               start_set_hash = hash(state_set)

   return dict(action_table), dict(goto_table), start_set_hash


def generate_spontaneously_lookaheads(grammar, start_item, handle_shift_reduce = True):
   goto_table = collections.defaultdict(dict)
   
   lalr_start_item = LALR(start_item.sym_production, start_item.alternative, start_item.position)
   lalr_start_item.add_new(grammar.EOF)
   kernels_lalr = kernel_collection(grammar, lalr_start_item)

   ids_kernes_lalr = dict()
   for kernels in kernels_lalr:
      closure_lalr = closure(kernels, grammar)
      ids_kernes_lalr[hash(closure_lalr)] = kernels
      populate_goto_table_from_state(grammar, closure_lalr, goto_table)

   for id_, kernels in ids_kernes_lalr.iteritems():
      for item_lalr in kernels:
         closure_lr1 = closure(set([LR1(item_lalr.sym_production, item_lalr.alternative, item_lalr.position, grammar.PROBE)]), grammar)

         for item_lr1 in closure_lr1:
            next_symbol = item_lr1.next_symbol(grammar)
            if not next_symbol:
               continue
            item_lr1_shifted = item_lr1.item_shifted(grammar)
               
            assert id_ in goto_table
            goto_set_id = goto_table[id_][next_symbol]
            goto_set = ids_kernes_lalr[goto_set_id]

            item_lalr_from_shifted = LALR(item_lr1_shifted.sym_production, item_lr1_shifted.alternative, item_lr1_shifted.position)
            assert item_lalr_from_shifted in goto_set
            
            singleton = (goto_set - (goto_set - {item_lalr_from_shifted}))
            assert len(singleton) == 1
            
            item_lalr_hidden = set(singleton).pop()

            if item_lr1.lookahead != grammar.PROBE:
               item_lalr_hidden.add_new(item_lr1.lookahead)

            else:
               item_lalr.subscribe(item_lalr_hidden)

   return kernels_lalr, goto_table

def propagate_lookaheads(grammar, kernels_lalr):
   changes = True
   while changes:
      changes = False
      for kernels in kernels_lalr:
         for item_lalr in kernels:
            changes |= item_lalr.propagate()

   for kernels in kernels_lalr:
      for item_lalr in kernels:
         item_lalr.close()

def build_parsing_table_lalr(grammar, start_item, handle_shift_reduce = True):
   action_table = collections.defaultdict(dict)
   start_set_hash = None
   
   kernels_lalr, goto_table = generate_spontaneously_lookaheads(grammar, start_item, handle_shift_reduce)
   propagate_lookaheads(grammar, kernels_lalr)
   for kernel in kernels_lalr:
      state_set = closure(kernel, grammar)
      populate_action_table_from_state(grammar, state_set, start_item, action_table, handle_shift_reduce)
      
      if not start_set_hash:
         for item in state_set:
            if item == start_item:
               start_set_hash = hash(state_set)
               break
   
   for i in goto_table:
      for j in goto_table[i]:
         goto_table[i][j] = hash(goto_table[i][j])

   return dict(action_table), dict(goto_table), start_set_hash