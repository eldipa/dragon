'''See the documentation of the class Grammar in this package.'''

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
import itertools
from collections import defaultdict 

class Grammar(object):
   '''Represents the grammar of the language to parse. This include syntactic
      constructions and semantic actions.
      The class contains three groups of methods. There is a group to add new
      syntactic rules and optional semantic actions.
      The second group are test methods and iterators to see what rules are
      in the grammar.
      And in the last group, there are a set of methods to check the integrity of
      the grammar.
   '''
   EMPTY = "<<e>>"
   START = "<<S>>"
   EOF = "<<$>>"
   ACTION_INSIDE = "<<@%i %s>>"
   PROBE = "<<#>>"

   def __init__(self, start_symbol = None, terminals = None):
      '''Creates a Grammar with an optional 'start' symbol and a optional 
         initial set of terminals.
         
         If the 'start' symbol is set, an additional rule is added:
            self.START -> start_symbol
         In this case, the grammar is 'augmented'.
         This property is required by some algorithms so if the 
         'start_symbol' is None, you must set this symbol using the 
         'augment' method after build the grammar.

         The initial set of terminals can be extended calling 'add_terminal'
         method. So, it is not necessary to provide the set in the same 
         time that the grammar is builded.
         '''

      self._productions = defaultdict(list)
      self._terminals = set() if not terminals else set(terminals)
      self._semantic = dict()
      self._counter_generator = 0

      if start_symbol:
         self.augment(start_symbol)


   def _assign_semantic_action(self, symbol, semantic_action, 
         count = None, consume = None):
      '''Internal method which adds a semantic action in the last defined 
         production of 'symbol'.

         If 'count' is a number, then the semantic action will read 'count' 
         values from a stack of synthesized values. If it is None, 
         len(production) values will be readed where 'production' is the last
         defined production of 'symbol'.

         If 'consume' is True, then 'count' values will be removed from the 
         stack. If it es False, none is removed. By default, 'consume' is True.

         In any case, the value returned by the semantic action is pushed in 
         the stack of synthesized values, even if the action return None.
         '''

      if semantic_action:
         count = count if count != None else len(self[symbol][-1])
         consume = consume if consume != None else True
         key = (symbol, len(self[symbol]) - 1)
         self._semantic[key] = (count, consume, semantic_action)
   
   # pylint: disable=C0103
   def _generate_symbol_for_semantic_action_inside(self, semantic): 
      '''Makes a unique name used by the artificial symbols of semantic 
         actions in the middle of a production.'''
      self._counter_generator += 1
      return self.ACTION_INSIDE % (self._counter_generator, semantic.__name__)
         
   def add_terminal(self, terminal):
      '''Adds a terminal.'''
      self._terminals.add(terminal)

   def add_rule(self, symbol, rule):
      '''Adds a rule, like symbol -> rule.
         The 'rule' must be a sequence (list or tuple) being each element 
         a string or a callable. Each string must be the name of a symbol, 
         terminal or nonterminal.
         
         Each callable it will be interpreted as a middle semantic action 
         with a exception. If the last item of 'rule' is callable, then that 
         element will be interpreted as a 'full' semantic action and not as 
         a 'middle' semantic action.
         In this case, this last element will be removed and stored in other
         place, so the 'full' semantic action it will not be part of the 
         production.
         
         If the last element is not callable, a default semantic action is 
         provided. This action will read (and remove) N synthesized values 
         and return a tuple with those values, where N is the length of the 
         rule.
         
         This method can be called many times with the same 'symbol' 
         argument. This its interpreted as alternative productions like
            
            A -> abc | cde'''

      assert rule
      assert Grammar.EMPTY not in rule

      rule = list(rule)

      semantic_action = rule.pop() if hasattr(rule[-1], '__call__') else None

      for i in range(len(rule)):
         if hasattr(rule[i], '__call__'):
            assert not (i == 0) and "The first must not be a semantic action."
            __semantic_action = rule[i]
            rule[i] = self._generate_symbol_for_semantic_action_inside(
                                                         __semantic_action)
            self._productions[rule[i]].append((Grammar.EMPTY,))
            self._assign_semantic_action(rule[i], __semantic_action, i, False)

      self._productions[symbol].append(tuple(rule))
      self._assign_semantic_action(symbol, semantic_action)


   def add_empty(self, symbol, semantic_action = None):
      ''' Adds a special rule which represent the empty string.
            symbol -> <<empty>> 
          
          This method cannot be called many time with the same 'symbol' 
          argument but can be combined several times with the 'add_rule' 
          method.
          
          The 'semantic_action' argument has the same meaning that the 
          semantic action described in 'add_rule'. '''
      self._productions[symbol].append((Grammar.EMPTY,))
      self._assign_semantic_action(symbol, semantic_action)

      assert self.is_empty_rule(self[symbol][-1])

   
   def augment(self, symbol_start):
      '''Augments a grammar selecting a start symbol and adding the rule
            self.START -> symbol_start

         The grammar can be augment only once.'''
      assert not symbol_start in self._productions
      assert not self.is_augment()
      self.add_rule(Grammar.START, (symbol_start, ))

   def start_symbol(self):
      '''Returns the 'start_symbol' which form the rule
            self.START -> symbol_start

         Precondition: the grammar must be augmented.'''
      assert self.is_augment()
      return self[self.START][0][0]

   def semantic_definition(self, symbol, num_of_production):
      '''Returns a semantic definition, a tuple with three parameters, 
         associated to a 'symbol' and a particular production.

         This tuple contains 
            (count, consume, semantic_action)

         each parameters is explained in the documentation of the method 
         '_assign_semantic_action'.

         In case of a 'default' semantic action (a unspecified semantic 
         action), None will be returned. '''
      key = (symbol, num_of_production)
      if key in self._semantic:
         return self._semantic[key]
      
      return None

   def __getitem__(self, symbol):
      '''A overloaded operator []. 
         Returns a secuence of rules (and each rule is a secuence of strings 
         or callables) If there is not any rule, (the symbol is not a symbol 
         of the grammar) the method will return None.
         '''
      return self._productions[symbol] if symbol in self._productions else None
   
   @classmethod
   def is_empty(cls, symbol):
      '''Returns True if 'symbol' is the special 'empty' symbol. 
         False in other case.'''
      return symbol == cls.EMPTY

   @classmethod
   def is_empty_rule(cls, rule):
      '''Returns True if 'rule' is the special rule that derive in the empty
         string. 
         False in other case.'''
      return (cls.EMPTY, ) == rule

   def is_a_terminal(self, symbol):
      '''Returns True if 'symbol' is a terminal. False in other case.

         This include the special terminal 'self.EOF' and 'self.PROBE'.
         '''
      return symbol in self._terminals or symbol in (self.EOF, self.PROBE)

   def is_a_nonterminal(self, symbol):
      '''Returns True if 'symbol' is a nonterminal. That is, the 'symbol'
         has one o more productions to be derived. False in other case.
         
         This include the special nonterminal symbol 'self.START' if the 
         grammar is augmented.'''
      return symbol in self._productions

   def is_augment(self):
      '''Returns True if grammar is augmented. False in other case.'''
      return Grammar.START in self._productions

   def is_start_symbol(self, symbol):
      '''Returns True if 'symbol' is the start symbol. That is, if exist a rule
            self.START -> symbol
         
         Returns False in other case.'''
      return symbol == self.start_symbol()
   
   def is_augmented_start_symbol(self, symbol):
      '''Returns True if 'symbol' is the special 'self.START' nonterminal 
         symbol. 
         Returns False in other case.'''
      return symbol == self.START

   def iter_nonterminals(self):
      '''Returns an iterator to iterate over all nonterminal symbols included 
         the special self.START.'''
      return iter(self._productions.keys())
   
   def iter_on_all_symbols(self):
      '''Returns an iterator of all symbols, terminals and nonterminals, 
         included the special nonterminal symbol self.START. 
         This NOT include the self.EMPTY and self.EOF symbols.'''
      return itertools.chain(self._productions.iterkeys(), self._terminals)
   
   def __str__(self):
      '''Return a string representing the grammar and each rule.'''
      return '\n'.join([
         str(r) + " -> " + \
               str("\n  | ".join(map(lambda x: str(x)[1:-1], self[r]))) 
               for r in self.iter_nonterminals()])
