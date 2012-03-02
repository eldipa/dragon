
class Lexer:
   def tokenizer(self):
      '''Return a iterable or generator of all tokens.
         Each token is a tuple with at least one value, the terminal id. 
         The next values, if any, are the attributes of the token.'''
      raise NotImplementedError


class Driver:
   def __init__(self, action_table, goto_table, start_state):
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
            action = self._action_table[stack_of_states[-1]][terminal]
            action.do(stack_of_states, self._goto_table, synthesized)
            request_token = action.request_token()
            finish = action.finish()

         if finish:
            break
         
         synthesized.append(token[1])


   class Shift:
      def __init__(self, state_to_shift):
         self._state_to_shift = state_to_shift

      def do(self, stack_of_states, goto_table, synthesized):
         stack_of_states.append(self._state_to_shift) #push

      def request_token(self): return True
      def finish(self): return False
      def __str__(self): return "Shift %s" % hex(self._state_to_shift)
      def __ne__(self, other): return not self == other

      def __eq__(self, other):
         return isinstance(other, Driver.Shift) and other._state_to_shift == self._state_to_shift


   class Reduce:
      def __init__(self, sym_production, len_production, semantic_definition):
         self._sym_production = sym_production
         self._len_production = len_production

         if semantic_definition == None:
            self._count_stack_read = len_production
            self._consume = True
            self._semantic_action = lambda args : args
         else:
            self._count_stack_read, self._consume, self._semantic_action = semantic_definition

      def do(self, stack_of_states, goto_table, synthesized):
         del stack_of_states[-self._len_production : ] #multiple pops
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


   class Accept:
      def do(self, stack_of_states, goto_table, synthesized):
         pass
      
      def request_token(self): return False
      def finish(self): return True
      def __str__(self): return "Accept"
      def __ne__(self, other): return not self == other
      
      def __eq__(self, other):
         return isinstance(other, Driver.Accept)

