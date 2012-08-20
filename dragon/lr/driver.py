'''See the documentation of the Driver class in this package.'''
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
from dragon.driver import Driver as DriverInterface

class Driver(DriverInterface):
   '''See the __init__ method.'''
   def __init__(self, action_table, goto_table, start_state):
      '''The driver is in charge of moving between the states (from the start 
         stage) using the goto table. In each state a decision must be taken, 
         given a token readed by the lexer, the parser must...
            ...continue asking for tokens to the lexer (called a 'shift' 
               action).
            ...stop and try to figure out what rule in the grammar is in and
               possibly execute some semantic action (called a 'reduce' action)
            ...stop and finish the parser, because a end of file condition was 
               reached (called an 'accept action')
            ...stop with a error because the token readed is unexpected and 
               there is no other action to do.

         The action to do in each state is described in the action table.
      '''
      DriverInterface.__init__(self)
      self._action_table = action_table
      self._goto_table = goto_table
      self._start_state = start_state

   def parse_by_step(self, lexer):
      stack_of_states = [self._start_state]
      synthesized = []
      finish = False
      request_token = False

      for token in lexer.tokenizer():
         terminal = token[0]
         request_token = False
         while not request_token and not finish:
            if terminal not in self._action_table[stack_of_states[-1]]:
               raise DriverInterface.UnexpectedToken(
                           token, 
                           self._action_table[stack_of_states[-1]].keys())
 
            action = self._action_table[stack_of_states[-1]][terminal]
            action.eval(stack_of_states, self._goto_table, synthesized)
            request_token = action.request_token()
            finish = action.finish()
            yield token, action, stack_of_states, request_token
                  

         if finish:
            break
 
         synthesized.append(token[1])


   class Shift(object):
      # pylint: disable=C0111
      def __init__(self, state_to_shift, sym_production, production):
         self._state_to_shift = state_to_shift
         self._production_str = sym_production + " -> " + " ".join(production)

      def eval(self, stack_of_states, _goto_table, _synthesized):
         stack_of_states.append(self._state_to_shift) #push
      
      def production_str(self):
         return self._production_str
      
      @classmethod
      def request_token(cls): 
         return True
      @classmethod
      def finish(cls): 
         return False
      def __str__(self): 
         return "Shift %s" % hex(self._state_to_shift)
      def __ne__(self, other): 
         return not self == other

      # pylint: disable=W0212
      def __eq__(self, other):
         return isinstance(other, Driver.Shift) and \
                     other._state_to_shift == self._state_to_shift


   class Reduce(object):
      # pylint: disable=C0111
      def __init__(self, sym_production, production, semantic_definition, 
                                                         empty_production):
         self._sym_production = sym_production
         self._len_production = len(production)
         self._empty_production = empty_production

         self._production_str = sym_production + " -> " + " ".join(production)

         if semantic_definition == None:
            self._count_stack_read = self._len_production
            self._consume = True
            self._semantic_action = lambda *args : args[0] if args else None
         else:
            self._count_stack_read, self._consume, self._semantic_action = \
                                                            semantic_definition

      def production_str(self):
         return self._production_str

      def eval(self, stack_of_states, goto_table, synthesized):
         if not self._empty_production:
            del stack_of_states[-self._len_production : ] #multiple pops

         assert goto_table[stack_of_states[-1]]
         stack_of_states.append(
               goto_table[stack_of_states[-1]][self._sym_production]) #push

         new_attribute_synthesized = \
               self._semantic_action(*filter(lambda x: x is not None, 
                                    synthesized[-self._count_stack_read: ]))

         if self._consume:
            del synthesized[-self._count_stack_read: ] #multiple pops
         
         synthesized.append(new_attribute_synthesized) #push
      
      @classmethod
      def request_token(cls): 
         return False
      @classmethod
      def finish(cls): 
         return False
      def __str__(self): 
         return "Reduce %s, %i pops" % (self._sym_production, 
                                        self._len_production)
      def __ne__(self, other): 
         return not self == other

      # pylint: disable=W0212
      def __eq__(self, other):
         return isinstance(other, Driver.Reduce) and \
               other._sym_production == self._sym_production and \
               other._len_production == self._len_production


   class Accept(object):
      # pylint: disable=C0111
      def eval(self, _stack_of_states, _goto_table, _synthesized):
         pass
      
      @classmethod
      def request_token(cls): 
         return False
      @classmethod
      def finish(cls): 
         return True
      def __str__(self): 
         return "Accept"
      def __ne__(self, other): 
         return not self == other
      
      def __eq__(self, other):
         return isinstance(other, Driver.Accept)

