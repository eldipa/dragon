from dragon.driver import Driver as DriverInterface

class Driver(DriverInterface):
   def __init__(self, action_table, goto_table, start_state):
      '''The driver is in charge of moving between the states (from the start stage)
         using the goto table. In each state a decision must be taken, given a token
         readed by the lexer, the parser must...
            ...continue asking for tokens to the lexer (called a 'shift' action).
            ...stop and try to figure out what rule in the grammar is in and possibly 
               execute some semantic action (called a 'reduce' action)
            ...stop and finish the parser, because a end of file condition was reached 
               (called an 'accept action')
            ...stop with a error because the token readed is unexpected and there is no
               other action to do.

         The action to do in each state is described in the action table.
      '''
      self._action_table = action_table
      self._goto_table = goto_table
      self._start_state = start_state

   def parse(self, lexer):
      stack_of_states = [self._start_state]
      synthesized = []
      finish = False
      request_token = False

      for token in lexer.tokenizer():
         terminal = token[0]
         request_token = False
         while not request_token and not finish:
            if terminal not in self._action_table[stack_of_states[-1]]:
               raise DriverInterface.UnexpectedToken(token, self._action_table[stack_of_states[-1]].keys())
 
            action = self._action_table[stack_of_states[-1]][terminal]
            action.do(stack_of_states, self._goto_table, synthesized)
            request_token = action.request_token()
            finish = action.finish()

         if finish:
            break
 
         synthesized.append(token[1])


   class Shift(object):
      def __init__(self, state_to_shift, sym_production, production):
         self._state_to_shift = state_to_shift
         self._production_str = sym_production + " -> " + " ".join(production)

      def do(self, stack_of_states, goto_table, synthesized):
         stack_of_states.append(self._state_to_shift) #push
      
      def production_str(self):
         return self._production_str

      def request_token(self): return True
      def finish(self): return False
      def __str__(self): return "Shift %s" % hex(self._state_to_shift)
      def __ne__(self, other): return not self == other

      def __eq__(self, other):
         return isinstance(other, Driver.Shift) and other._state_to_shift == self._state_to_shift


   class Reduce(object):
      def __init__(self, sym_production, production, semantic_definition, empty_production):
         self._sym_production = sym_production
         self._len_production = len(production)
         self._empty_production = empty_production

         self._production_str = sym_production + " -> " + " ".join(production)

         if semantic_definition == None:
            self._count_stack_read = self._len_production
            self._consume = True
            self._semantic_action = lambda args : args
         else:
            self._count_stack_read, self._consume, self._semantic_action = semantic_definition

      def production_str(self):
         return self._production_str

      def do(self, stack_of_states, goto_table, synthesized):
         if not self._empty_production:
            del stack_of_states[-self._len_production : ] #multiple pops

         assert goto_table[stack_of_states[-1]]
         stack_of_states.append(goto_table[stack_of_states[-1]][self._sym_production]) #push

         new_attribute_synthesized = self._semantic_action(synthesized[-self._count_stack_read: ])
         if self._consume:
            del synthesized[-self._count_stack_read: ] #multiple pops
         
         synthesized.append(new_attribute_synthesized) #push
      
      def request_token(self): return False
      def finish(self): return False
      def __str__(self): return "Reduce %s, %i pops" % (self._sym_production, self._len_production)
      def __ne__(self, other): return not self == other

      def __eq__(self, other):
         return isinstance(other, Driver.Reduce) and other._sym_production == self._sym_production and other._len_production == self._len_production


   class Accept(object):
      def do(self, stack_of_states, goto_table, synthesized):
         pass
      
      def request_token(self): return False
      def finish(self): return True
      def __str__(self): return "Accept"
      def __ne__(self, other): return not self == other
      
      def __eq__(self, other):
         return isinstance(other, Driver.Accept)

