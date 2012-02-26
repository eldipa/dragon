
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
