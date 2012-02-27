
def first(aGrammar, symbols):
   '''Finds the 'first' set of terminals that there are derived from 'symbols'.
         
      - If symbols are 'axxx', where 'a' is a terminal, then, the first of symbols is 'a'.
      - If symbols are 'Axxx', where 'A' is a nonterminal and it don't derive in a empty
      string, then, the 'first' of symbols is the 'first of A'.
      - If symbols are 'ABCx', where 'A' is a nonterminal and it derives in a empty
      string, then, the 'first' of symbols is the 'first of A' union the 'first of B'. If 
      B derives in a empty string too, then, append the 'first of C' and so on. If there 
      aren't more symbols in 'symbols', add the EMPTY terminal to set 'first of 'symbols'.

      This algorithm works for left and right recursive functions.
      '''
      
   symbol_derive_empty = set()
   first_set = set()
   previous_first_set = set()

   previous_len_symbol_derive_empty = -1
   while len(previous_first_set) < len(first_set.union(previous_first_set)) or \
         previous_len_symbol_derive_empty < len(symbol_derive_empty):

      previous_first_set = first_set.union(previous_first_set)
      previous_len_symbol_derive_empty = len(symbol_derive_empty)

      stack_of_rules = [[list(symbols)]]
      first_set = set()
      seen = set()
      while True:
         rules = stack_of_rules[-1]
         if not rules:
            del stack_of_rules[-1]
            if aGrammar.EMPTY in first_set:
               if stack_of_rules and len(stack_of_rules[-1][0]) > 1:
                  first_set.remove(aGrammar.EMPTY)
               
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

         if aGrammar.is_a_terminal(s) or aGrammar.is_empty(s):
            first_set.add(s)
            del stack_of_rules[-1][0]
         elif s not in seen:
            seen.add(s)
            stack_of_rules.append([list(rule) for rule in aGrammar[s]])
         else:
            if s in symbol_derive_empty:
               del stack_of_rules[-1][0][0]
               if not stack_of_rules[-1][0]:
                  first_set.add(aGrammar.EMPTY)
            else:
               del stack_of_rules[-1][0]

   return frozenset(first_set)


def follow(aGrammar, symbol, seen = None):
   '''Return the set of terminal that 'follow' the nonterminal symbol 'symbol'.
      
      Let be X the nonterminal symbol.
      If A -> aX, the set 'follow of A' is in 'follow of X'
      If A -> aXB, the set 'first of B' is in 'follow of X' and if the empty terminal
      is in 'first of B', then the follow of A is in follow of X too.
      If X is the 'start symbol', add the terminal 'End Of File' to the 'follow of X'.

      Precondition: the grammar must be a augment grammar.
      '''

   target = symbol

   follow_set = set()
   seen = seen if seen else set()
   seen.add(symbol)
   if aGrammar.is_start_symbol(target):
      follow_set.add(aGrammar.EOF)

   for s in aGrammar.iter_nonterminals():
      if not aGrammar.is_augmented_start_symbol(s):
         for rule in aGrammar[s]:
            if target in rule:
               tail = rule[rule.index(target) + 1: ]
               
               terminals = ()
               if tail:
                  terminals = first(aGrammar, tail)
      
               more_terminals = ()
               if (not tail or aGrammar.EMPTY in terminals) and s not in seen:
                  more_terminals = follow(aGrammar, s, seen)

               follow_set.update(more_terminals)
               follow_set.update(set(terminals) - set([aGrammar.EMPTY]))
   
   return frozenset(follow_set)
