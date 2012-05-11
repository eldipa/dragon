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

# pylint: disable=R0912
def first(a_grammar, symbols):
   '''Finds the 'first' set of terminals that there are derived from 'symbols'.
         
      - If symbols are 'axxx', where 'a' is a terminal, then, the first of 
        symbols is 'a'.
      - If symbols are 'Axxx', where 'A' is a nonterminal and it don't derive 
        in a empty string, then, the 'first' of symbols is the 'first of A'.
      - If symbols are 'ABCx', where 'A' is a nonterminal and it derives in 
        a empty string, then, the 'first' of symbols is the 'first of A' union
        the 'first of B'. If B derives in a empty string too, then, append 
        the 'first of C' and so on. If there aren't more symbols in 'symbols',
        add the EMPTY terminal to the set 'first of 'symbols'.

      This algorithm works for left and right recursive grammars.
      '''
      
   symbol_derive_empty = set()
   first_set = set()
   previous_first_set = set()
   
   # pylint: disable=C0103
   previous_len_symbol_derive_empty = -1
   while len(previous_first_set) < len(first_set.union(previous_first_set)) \
         or previous_len_symbol_derive_empty < len(symbol_derive_empty):

      previous_first_set = first_set.union(previous_first_set)
      previous_len_symbol_derive_empty = len(symbol_derive_empty)

      stack_of_rules = [[list(symbols)]]
      first_set = set()
      seen = set()
      while True:
         rules = stack_of_rules[-1]
         if not rules:
            del stack_of_rules[-1]
            if a_grammar.EMPTY in first_set:
               if stack_of_rules and len(stack_of_rules[-1][0]) > 1:
                  first_set.remove(a_grammar.EMPTY)
               
               if stack_of_rules and stack_of_rules[-1][0]:
                  symbol_derive_empty.add(stack_of_rules[-1][0][0])
                  del stack_of_rules[-1][0][0]


               if not stack_of_rules:
                  break
            else:
               if stack_of_rules:
                  del stack_of_rules[-1][0]
               else:
                  break
            continue

         rule = rules[0]
         if not rule:
            del stack_of_rules[-1][0]
            continue

         s = rule[0]

         if a_grammar.is_a_terminal(s) or a_grammar.is_empty(s):
            first_set.add(s)
            del stack_of_rules[-1][0]
         elif s not in seen:
            seen.add(s)
            stack_of_rules.append([list(rule) for rule in a_grammar[s]])
         else:
            if s in symbol_derive_empty:
               del stack_of_rules[-1][0][0]
               if not stack_of_rules[-1][0]:
                  first_set.add(a_grammar.EMPTY)
            else:
               del stack_of_rules[-1][0]

   return frozenset(first_set)


def follow(a_grammar, symbol, _seen = None):
   '''Returns the set of terminals that 'follow' the nonterminal symbol 
      'symbol'.
      
      Let be X the nonterminal symbol.
      If A -> aX, the set 'follow of A' is in 'follow of X'
      If A -> aXB, the set 'first of B' is in 'follow of X' and if the empty
      terminal is in 'first of B', then the follow of A is in follow of X too.
      If X is the 'start symbol', add the terminal 'End Of File' to the 
      'follow of X'.

      Precondition: the grammar must be a grammar augmented.

      The optional parameter '_seen' is a special parameter for internal 
      use only.
      This algorithm works in a recursive way, for both left and right 
      recursive grammars.
      '''

   target = symbol

   follow_set = set()
   _seen = _seen if _seen else set()
   _seen.add(symbol)
   if a_grammar.is_start_symbol(target):
      follow_set.add(a_grammar.EOF)

   for sym in a_grammar.iter_nonterminals():
      if not a_grammar.is_augmented_start_symbol(sym):
         for rule in a_grammar[sym]:
            if target in rule:
               tail = rule[rule.index(target) + 1: ]
               
               terminals = ()
               if tail:
                  terminals = first(a_grammar, tail)
      
               more_terminals = ()
               if (not tail or a_grammar.EMPTY in terminals) and \
                     sym not in _seen:
                  more_terminals = follow(a_grammar, sym, _seen)

               follow_set.update(more_terminals)
               follow_set.update(set(terminals) - set([a_grammar.EMPTY]))
   
   assert a_grammar.EMPTY not in follow_set
   return frozenset(follow_set)
