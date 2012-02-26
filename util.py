
def first(aGrammar, symbols):
   stack_of_rules = [[list(symbols)]]
   seen = set()
   symbol_derive_empty = set()
   first_set = set()

   while True:
      rules = stack_of_rules[-1]
      if not rules:
         del stack_of_rules[-1]
         if aGrammar.EMPTY in first_set:
            if stack_of_rules and len(stack_of_rules[-1][0]) > 1:
               first_set.remove(aGrammar.EMPTY)
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
         else:
            del stack_of_rules[-1][0]

   return frozenset(first_set)
