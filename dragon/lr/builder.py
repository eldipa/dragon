'''This module contains functions to build the states used by a drver to parse.
   See the function build_parsing_table in this module.
   '''
#########################################################################
#                                                                       #
#                        This work is licensed under a                  #
#   CC BY-SA        Creative Commons Attribution-ShareAlike             #
#                           3.0 Unported License.                       #
#                                                                       #
#########################################################################

###############################################################################
#                                                                             #
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS        #
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT          #
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A    #
#  PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER  #
#  OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,   #
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,        #
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR         #
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF     #
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING       #
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS         #
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.               #
#                                                                             #
###############################################################################
import collections
from dragon.lr.driver import Driver
from dragon.lr.item import LR1, LALR
from dragon.lr.util import kernel_collection, closure, goto
from dragon.lr.conflict import handler_conflict

class UserFriendlyMapping:
   '''See the documentation of __init__.'''

   def __init__(self, disable_mapping):
      '''Helper class to map hashes of states to simplest identifiers.
         If 'disable_mapping' is True, no mapping is made.
         '''
      self._last_id = 0
      self._id_by_state = {}
      self._disable_mapping = disable_mapping

   def __getitem__(self, state):
      '''Takes a hasheable object 'state', obtains its hash and then map it to
         a simplest id.'''
      hashed_state = hash(state)
      if self._disable_mapping:
         return hashed_state

      if hashed_state not in self._id_by_state:
         self._id_by_state[hashed_state] = self._last_id
         self._last_id += 1
      
      return self._id_by_state[hashed_state]

def populate_goto_table_from_state(grammar, state_set, goto_table, to_id):
   '''Builds the Goto table.'''
   for anysymbol in grammar.iter_on_all_symbols():
      next_state = goto(state_set, anysymbol, grammar)
      if next_state:
         goto_table[to_id[state_set]][anysymbol] = to_id[next_state]

# pylint: disable=C0103
def populate_action_table_from_state(grammar, state_set, 
      action_table, handle_shift_reduce, to_id):
   '''Builds the Action table.'''
   for item in state_set:
      next_symbol = item.next_symbol(grammar)
      if item.sym_production == grammar.START and item.position == 1: 
         #Item is S' -> S*
         action = Driver.Accept()
         if grammar.EOF in action_table[to_id[state_set]] and \
               action != action_table[to_id[state_set]][grammar.EndOfSource]:
            raise KeyError(grammar.EOF)

         action_table[to_id[state_set]][grammar.EOF] = action

      elif next_symbol and not grammar.is_a_nonterminal(next_symbol): 
         #Item is A -> a*bc
         assert not grammar.is_empty(next_symbol)
         goto_state_hash = to_id[goto(state_set, next_symbol, grammar)]
         action = Driver.Shift(
               goto_state_hash, 
               item.sym_production, 
               grammar[item.sym_production][item.alternative])

         if next_symbol in action_table[to_id[state_set]] and \
               action != action_table[to_id[state_set]][next_symbol]:
            action = handler_conflict(
                  action, 
                  action_table[to_id[state_set]][next_symbol], 
                  next_symbol, 
                  handle_shift_reduce)

         action_table[to_id[state_set]][next_symbol] = action


      elif not next_symbol:    #Item is A -> abc*
         for terminal in item.followers(grammar): 
            semantic_definition = grammar.semantic_definition(
                  item.sym_production, 
                  item.alternative)
            action = Driver.Reduce(
                  item.sym_production, 
                  grammar[item.sym_production][item.alternative], 
                  semantic_definition, 
                  grammar.is_empty_rule(
                     (grammar[item.sym_production][item.alternative])) )
            if terminal in action_table[to_id[state_set]] and \
                  action != action_table[to_id[state_set]][terminal]:
               action = handler_conflict(
                     action, 
                     action_table[to_id[state_set]][terminal], 
                     terminal,
                     handle_shift_reduce)

            action_table[to_id[state_set]][terminal] = action


def build_parsing_table(grammar, start_item, handle_shift_reduce = True,
      disable_mapping = False):
   '''Builds the Action and Goto tables for be used by a driver returning
      these tables and the id of the start state, where the driver will use
      as a point of start to parse.
      
      See the documentation of handler_conflict function for more info with
      respect the handle_shift_reduce parameter.

      The start_item can be an instance of Item (see the module item).
      This works well with LR0 and LR1 items, but with LALR items, the
      algorithm used is the build_parsing_table_lalr (see that function, in
      this module)

      If 'disable_mapping' is True, the internal states are identified by
      its hash. This is only useful for testing and should not be modified
      in the normal case.

      Preconditions: the grammar must be already processed.'''
   if isinstance(start_item, LALR):
      return build_parsing_table_lalr(grammar, start_item, handle_shift_reduce)

   action_table = collections.defaultdict(dict)
   goto_table = collections.defaultdict(dict)
   kernels = kernel_collection(grammar, start_item)
   start_set_hash = None

   to_id = UserFriendlyMapping(disable_mapping)

   for kernel in kernels:
      state_set = closure(kernel, grammar)
      
      populate_goto_table_from_state(grammar, state_set, goto_table, to_id)
      populate_action_table_from_state(
            grammar, 
            state_set, 
            action_table, 
            handle_shift_reduce,
            to_id)
      
      if not start_set_hash:
         for item in state_set:
            if item == start_item:
               start_set_hash = to_id[state_set]

   return dict(action_table), dict(goto_table), start_set_hash


# pylint: disable=C0103
# pylint: disable=R0914
def generate_spontaneously_lookaheads(grammar, start_item, to_id):
   '''Builds a LR0 table using as a seed the start_item and then tries to 
      determinate what terminals are lookahead of each item (in which case, 
      these lookaheads are spontaneously generated), building initially the
      LALR items (they are very similar to the LR0 item but can be modified
      adding to him lookaheads, see the documentation of LALR class in the 
      item module).
      '''

   goto_table = collections.defaultdict(dict)
   
   lalr_start_item = LALR(
         start_item.sym_production, 
         start_item.alternative, 
         start_item.position)
   lalr_start_item.add_new(grammar.EOF)
   kernels_lalr = kernel_collection(grammar, lalr_start_item)

   ids_kernes_lalr = dict()
   for kernels in kernels_lalr:
      closure_lalr = closure(kernels, grammar)
      ids_kernes_lalr[to_id[closure_lalr]] = kernels
      populate_goto_table_from_state(grammar, closure_lalr, goto_table, to_id)

   for id_, kernels in ids_kernes_lalr.iteritems():
      for item_lalr in kernels:
         closure_lr1 = closure(set([LR1(
            item_lalr.sym_production, 
            item_lalr.alternative, 
            item_lalr.position, 
            grammar.PROBE)]), grammar)

         for item_lr1 in closure_lr1:
            next_symbol = item_lr1.next_symbol(grammar)
            if not next_symbol:
               continue
            item_lr1_shifted = item_lr1.item_shifted(grammar)
               
            assert id_ in goto_table
            goto_set_id = goto_table[id_][next_symbol]
            goto_set = ids_kernes_lalr[goto_set_id]

            item_lalr_from_shifted = LALR(
                  item_lr1_shifted.sym_production, 
                  item_lr1_shifted.alternative, 
                  item_lr1_shifted.position)
            assert item_lalr_from_shifted in goto_set
            
            singleton = (goto_set - (goto_set - {item_lalr_from_shifted}))
            assert len(singleton) == 1
            
            item_lalr_hidden = set(singleton).pop()

            if item_lr1.lookahead != grammar.PROBE:
               item_lalr_hidden.add_new(item_lr1.lookahead)

            else:
               item_lalr.subscribe(item_lalr_hidden)

   return kernels_lalr, goto_table

def propagate_lookaheads(kernels_lalr):
   '''The spontaneously generated terminals are propagated from one item to 
      other. 
      Initially, the items are LALR items, but with few or none lookaheads 
      terminals. This function completes these LALR items.
      '''
   changes = True
   while changes:
      changes = False
      for kernels in kernels_lalr:
         for item_lalr in kernels:
            changes |= item_lalr.propagate()

   for kernels in kernels_lalr:
      for item_lalr in kernels:
         item_lalr.close()

def build_parsing_table_lalr(grammar, start_item, handle_shift_reduce = True,
      disable_mapping=False):
   '''Builds a LALR table, first builds a LR0 table using as a seed the 
      start_item and then tries to determinate what terminals are lookahead of 
      each item (in which case, these lookaheads are spontaneously generated)
      In a second stage, the spontaneously generated terminals are propagated
      from one item to other.
      When no more terminals propagated, the algorithm builds a kernel
      of items LALR.
      With this, the function returns the action and goto tables used by the
      driver.

      See the documentation of handler_conflict function for more info with
      respect the handle_shift_reduce parameter.
      
      If 'disable_mapping' is True, the internal states are identified by
      its hash. This is only useful for testing and should not be modified
      in the normal case.
   '''

   to_id = UserFriendlyMapping(disable_mapping)
   action_table = collections.defaultdict(dict)
   start_set_hash = None
   
   kernels_lalr, goto_table = generate_spontaneously_lookaheads(
         grammar, 
         start_item,
         to_id)
   propagate_lookaheads(kernels_lalr)
   for kernel in kernels_lalr:
      state_set = closure(kernel, grammar)
      populate_action_table_from_state(
            grammar, 
            state_set, 
            action_table, 
            handle_shift_reduce,
            to_id)
      
      if not start_set_hash:
         for item in state_set:
            if item == start_item:
               start_set_hash = to_id[state_set]
               break
   
   return dict(action_table), dict(goto_table), start_set_hash
