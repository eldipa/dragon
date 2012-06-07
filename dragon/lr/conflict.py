'''No all the grammars can be parsed by a LR parser. In this case, is said 
   that the grammar has a conflict.
   This module contains the possibles conflicts that can be appear with
   a LR parser.
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

class LRConflict(Exception):
   '''The grammar is not a LR grammar and because that, 
      a conflict was raised.'''
   def __init__(self, msg):
      Exception.__init__(self)
      self.msg = msg

   def __str__(self):
      return str(self.msg)

class ReduceReduce(LRConflict):
   '''A Reduce-Reduce conflict is detected when there are two productions 
      that are ready to be reduced at the same time, but only one of them 
      can be effectively reduced.
      '''
   def __init__(self, new, old, sym):
      LRConflict.__init__(self, "A Reduce-Reduce conflict discovered during \
process '%s' terminal. This is because there are two productions \
that are ready to be reduced at the same time, but only one of \
them can be effectively reduced. So, which production must be \
reduced?\nThese are the conflicting productions:\n%s\n%s" % (
               sym, 
               new.production_str(), 
               old.production_str()))

class ShiftReduce(LRConflict):
   '''A Shift-Reduce conflict is detected when there are two productions,
      one that is ready to be reduced and the other can still shift 
      more terminals at the same time.
      '''
   def __init__(self, new, old, sym):
      LRConflict.__init__(self, "A Shift-Reduce conflict discovered during \
process '%s' terminal. This is because there are two productions, \
one that is ready to be reduced and the other can still shift \
more terminals at the same time. So, which action must be choosed? \
By default, it's choosed the shift action.\nThese are the \
conflicting productions:\n%s\n%s" % (
               sym, 
               new.production_str(), 
               old.production_str()))

def handler_conflict(new_action, old_action, next_symbol, handle_shift_reduce):
   '''Evaluates the actions and if both are Reduce action, then raise a 
      ReduceReduce exception.
      
      If one action is a Shift action and the other is a Reduce action, 
      then a Shift-Reduce conflict is detected. If the parameter 
      handle_shift_reduce is False, then a ShiftReduce exception is raised.
      In other case, the Shift action takes precedence before the 
      Reduce action.

      If both actions are Shift action, the behaviour is undefined.
      '''
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


