import unittest
import dragon.notation.pythonic as notation
from ast import *

class FunctionalTestNotationPythonic(unittest.TestCase):
   def setUp(self):
      self.transformer = notation.NotationASTTransformer()
      self.importer = notation

      self.class_base = [Module, Assign, Name]
      self.class_call = [Call, Attribute, Name]

      self.funcdef = "funcdef = 'def', NAME, parameters, ':', suite"
      self.stmt = "stmt = {simple_stmt | compound_stmt}"
      self.single_input = "single_input = { NEWLINE | simple_stmt | compound_stmt, NEWLINE}"
      self.pass_stmt = "pass_stmt = 'pass'"
      self.yield_stmt = "yield_stmt = yield_expr"
      self.decorators = "decorators = decorator[...]"
      self.parameters = "parameters = '(', [varargslist], ')'"
      self.dotted_name = "dotted_name = NAME, ['.', NAME][...]"


      self.file_input = "file_input = [{NEWLINE | stmt}][...]"
      self.simple_stmt = "simple_stmt = small_stmt, [';', small_stmt][...], [';'], NEWLINE"
      self.raise_stmt = "raise_stmt = 'raise', [test, [',', test, [',', test]]]"
      self.import_from = "import_from = 'from', {(['.'][...], dotted_name) | '.'[...]}, 'import', {'*' | ('(', import_as_names, ')') | import_as_names}"
      self.term = "term = factor, [{'*' | '/' | '%' | '//'}, factor][...]"
      self.expr_stmt = "expr_stmt = testlist, {augassign, {yield_expr | testlist} | ['=', {yield_expr | testlist}][...]}"

      self.terminal_uppercase_repeated = "s = STRING[...]"
      
      self.atom_str_empty = "A = ''"
      self.rule_empty = "A = ()"
      self.choices_monopath = "A = {'a'}"
      self.choices_empty = "A = {}"
      self.optional_empty = "A = []"
      self.repeat_empty = "A = [][...]"
      self.invalid_repeat_expr_index = "A = 'a'[1]"
      self.invalid_repeat_expr_range = "A = 'a'[1:2]"
      self.invalid_repeat_expr_mixed = "A = 'a'[1:2, ...]"
      self.invalid_repeat_expr_str_empty = "A = ''[...]"
      self.missing_orbit_operator = "A = {'a', 'b'}"
      self.missing_set_operator = "A = 'a' | 'b'"

   def _validate_AST(self, str_expr, root_node, class_nodes):
      expected = class_nodes
      expected.reverse()
      deep_search = [root_node]
      while deep_search and expected:
         sub_root = deep_search.pop()
         expected_sub_root = expected.pop()

         if sub_root.__class__ != expected_sub_root:
            print "Testing %s. Error found %s, but expected %s." % (str_expr, sub_root, expected_sub_root)

         self.assertTrue(sub_root.__class__ == expected_sub_root)

         childrens = [children for children in iter_child_nodes(sub_root) if children.__class__ not in (Store, Load, Del, AugLoad, AugStore, Param)]
         childrens.reverse()
         deep_search.extend(childrens)

      for node in deep_search:
         print "Testing %s. Not expected %s." % (str_expr, node)

      for node in expected:
         print "Testing %s. Not found %s." % (str_expr, node)

      self.assertTrue(not deep_search)
      self.assertTrue(not expected)
 
   
   def _call(self, *args_list, **kw):
      args = list()
      for a in args_list:
         if hasattr(a, '__iter__'):
            args.extend(a)
         else:
            args.append(a)
      
      return self.class_call + args + [Str] #([Str] if 'finish' in kw else [Name])

   def test_rule_AST(self):
      "funcdef = 'def', NAME, parameters, ':', suite"
      root = parse(self.funcdef)
      class_args = [Tuple, Str, Name, Name, Str, Name]
      self._validate_AST(self.funcdef, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.funcdef, root, self.class_base + self._call(Tuple, self._call(Str), self._call(Str), Str, self._call(Str), Str, finish=True))

      grammar = self.importer.from_string(self.funcdef, "funcdef")

      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["def", "NAME", ":"]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 1 + 1)
      self.assertTrue(set(grammar["funcdef"]) == set([("def", "NAME", "parameters", ":", "suite")]))


   def test_choice_AST(self):
      "stmt = {simple_stmt | compound_stmt}"
      root = parse(self.stmt)
      class_args = [Set, BinOp, Name, BitOr, Name]
      self._validate_AST(self.stmt, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.stmt, root, self.class_base + self._call(Set, Str, Str, finish=True))

      grammar = self.importer.from_string(self.stmt, "stmt")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set())
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 1 + 1)
      self.assertTrue(set(grammar["stmt"]) == set([("simple_stmt",), ("compound_stmt",)]))

   def test_multiple_choice_AST(self):
      "single_input = { NEWLINE | simple_stmt | compound_stmt, NEWLINE}"
      root = parse(self.single_input)
      class_args = [Set, BinOp, BinOp, Name, BitOr, Name, BitOr, Name, Name]
      self._validate_AST(self.single_input, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.single_input, root, self.class_base + self._call(Set, self._call(Str), Str, self._call(Tuple, Str, self._call(Str)), finish=True))

      grammar = self.importer.from_string(self.single_input, "single_input")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["NEWLINE"]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 2 + 1)
      self.assertTrue(set(grammar["single_input"]) == set([("NEWLINE",), ("simple_stmt",), ("single_input#1",)]))
      self.assertTrue(set(grammar["single_input#1"]) == set([("compound_stmt", "NEWLINE",), ]))

   def test_rule_atom_str_AST(self):
      "pass_stmt = 'pass'"
      root = parse(self.pass_stmt)
      class_args = [Str]
      self._validate_AST(self.pass_stmt, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.pass_stmt, root, self.class_base + self._call(Tuple, self._call(Str), finish=True))

      grammar = self.importer.from_string(self.pass_stmt, "pass_stmt")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["pass"]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 1 + 1)
      self.assertTrue(set(grammar["pass_stmt"]) == set([("pass",),]))

   def test_rule_atom_name_AST(self):
      "yield_stmt = yield_expr"
      root = parse(self.yield_stmt)
      class_args = [Name]
      self._validate_AST(self.yield_stmt, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.yield_stmt, root, self.class_base + self._call(Tuple, Str, finish=True))

      grammar = self.importer.from_string(self.yield_stmt, "yield_stmt")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set())
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 1 + 1)
      self.assertTrue(set(grammar["yield_stmt"]) == set([("yield_expr",),]))

   def test_repeat_name_AST(self):
      "decorators = decorator[...]"
      root = parse(self.decorators)
      class_args = [Subscript, Name, Ellipsis]
      self._validate_AST(self.decorators, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.decorators, root, self.class_base + self._call(Str, finish=True))

      grammar = self.importer.from_string(self.decorators, "decorators")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set())
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 1 + 1)
      self.assertTrue(set(grammar["decorators"]) == set([("decorator","decorators"),("decorator",)]))
   
   def test_optional_name_in_rule_AST(self):
      "parameters = '(', [varargslist], ')'"
      root = parse(self.parameters)
      class_args = [Tuple, Str, List, Name, Str]
      self._validate_AST(self.parameters, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.parameters, root, self.class_base + self._call(Tuple, self._call(Str), self._call(List, Str), self._call(Str), finish=True))

      grammar = self.importer.from_string(self.parameters, "parameters")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["(", ")"]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 2 + 1)
      self.assertTrue(set(grammar["parameters"]) == set([
         ("(","parameters#1", ")"),
         ]))
      self.assertTrue(set(grammar["parameters#1"]) == set([
         ("varargslist",),
         (grammar.EMPTY,),
         ]))
   
   def test_optional_repeated_in_rule_AST(self):
      "dotted_name = NAME, ['.', NAME][...]"
      root = parse(self.dotted_name)
      class_args = [Tuple, Name, Subscript, List, Str, Name, Ellipsis]
      self._validate_AST(self.dotted_name, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.dotted_name, root, self.class_base + self._call(Tuple, self._call(Str), self._call(self._call(List, self._call(Str), self._call(Str))), finish=True))

      grammar = self.importer.from_string(self.dotted_name, "dotted_name")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["NAME", "."]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 3 + 1)
      self.assertTrue(set(grammar["dotted_name"]) == set([
         ("NAME","dotted_name#1"),
         ]))
      self.assertTrue(set(grammar["dotted_name#1"]) == set([
         ("dotted_name#2","dotted_name#1"),
         ("dotted_name#2",),
         ]))
      self.assertTrue(set(grammar["dotted_name#2"]) == set([
         (".", "NAME",),
         (grammar.EMPTY,),
         ]))

   def test_invalid_expression(self):
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "Invalid ''", self.transformer.visit, parse(self.atom_str_empty))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "Invalid '\(\)'", self.transformer.visit, parse(self.rule_empty))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "Invalid '\{.+\}'", self.transformer.visit, parse(self.choices_monopath))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "Invalid '\{\}'", self.transformer.visit, parse(self.choices_empty))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "Invalid '\[\]'", self.transformer.visit, parse(self.optional_empty))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "Invalid '\[\]'", self.transformer.visit, parse(self.optional_empty))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "use the subscript '\[\.\.\.\]'", self.transformer.visit, parse(self.invalid_repeat_expr_index))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "use the subscript '\[\.\.\.\]'", self.transformer.visit, parse(self.invalid_repeat_expr_range))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "use the subscript '\[\.\.\.\]'", self.transformer.visit, parse(self.invalid_repeat_expr_mixed))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "Invalid ''", self.transformer.visit, parse(self.invalid_repeat_expr_str_empty))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "Invalid '\{.+\}'", self.transformer.visit, parse(self.missing_orbit_operator))
      self.assertRaisesRegexp(notation.NotationASTTransformer.ParserASTError, "Invalid '|'", self.transformer.visit, parse(self.missing_set_operator))

   def test_alternative_in_optional_repeated(self):
      "file_input = [{NEWLINE | stmt}][...]"
      root = parse(self.file_input)
      class_args = [Subscript, List, Set, BinOp, Name, BitOr, Name, Ellipsis]
      self._validate_AST(self.file_input, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.file_input, root, self.class_base + self._call(self._call(List, self._call(Set, self._call(Str), Str)), finish=True))

      grammar = self.importer.from_string(self.file_input, "file_input")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["NEWLINE"]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 3 + 1)
      self.assertTrue(set(grammar["file_input"]) == set([
         ("file_input#1","file_input"),
         ("file_input#1",),
         ]))
      self.assertTrue(set(grammar["file_input#1"]) == set([
         ("file_input#2",),
         (grammar.EMPTY,),
         ]))
      self.assertTrue(set(grammar["file_input#2"]) == set([
         ("NEWLINE",),
         ("stmt",),
         ]))

   def test_rule_of_optional_repeated_and_optional(self):
      "simple_stmt = small_stmt, [';', small_stmt][...], [';'], NEWLINE"
      root = parse(self.simple_stmt)
      class_args = [Tuple, Name, Subscript, List, Str, Name, Ellipsis, List, Str, Name]
      self._validate_AST(self.simple_stmt, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.simple_stmt, root, self.class_base + self._call(Tuple, Str, self._call(self._call(List, self._call(Str), Str)), self._call(List, self._call(Str)), self._call(Str), finish=True))

      grammar = self.importer.from_string(self.simple_stmt, "simple_stmt")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["NEWLINE", ";"]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 4 + 1)
      self.assertTrue(set(grammar["simple_stmt"]) == set([
         ("small_stmt", "simple_stmt#1", "simple_stmt#3", "NEWLINE"),
         ]))
      self.assertTrue(set(grammar["simple_stmt#1"]) == set([
         ("simple_stmt#2","simple_stmt#1"),
         ("simple_stmt#2",),
         ]))
      self.assertTrue(set(grammar["simple_stmt#2"]) == set([
         (";", "small_stmt"),
         (grammar.EMPTY,),
         ]))
      self.assertTrue(set(grammar["simple_stmt#3"]) == set([
         (";",),
         (grammar.EMPTY,),
         ]))

   def test_optional_in_optional_in_optional_in_rule(self):
      "raise_stmt = 'raise', [test, [',', test, [',', test]]]"
      root = parse(self.raise_stmt)
      class_args = [Tuple, Str, List, Name, List, Str,  Name, List, Str, Name]
      self._validate_AST(self.raise_stmt, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.raise_stmt, root, self.class_base + self._call(Tuple, self._call(Str), self._call(List, Str, self._call(List, self._call(Str), Str, self._call(List, self._call(Str), Str))), finish=True))

      grammar = self.importer.from_string(self.raise_stmt, "raise_stmt")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["raise", ","]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 4 + 1)
      self.assertTrue(set(grammar["raise_stmt"]) == set([
         ("raise", "raise_stmt#1"),
         ]))
      self.assertTrue(set(grammar["raise_stmt#1"]) == set([
         ("test", "raise_stmt#2"),
         (grammar.EMPTY,),
         ]))
      self.assertTrue(set(grammar["raise_stmt#2"]) == set([
         (",", "test", "raise_stmt#3"),
         (grammar.EMPTY,),
         ]))
      self.assertTrue(set(grammar["raise_stmt#3"]) == set([
         (",", "test"),
         (grammar.EMPTY,),
         ]))
      
      
   def test_all_optional_repeated_str_repeated_rule_choices(self):
      "import_from = 'from', {(['.'][...], dotted_name) | '.'[...]}, 'import', {'*' | ('(', import_as_names, ')') | import_as_names}"
      root = parse(self.import_from)
      class_args = [Tuple, Str, Set, BinOp, Tuple, Subscript, List, Str, Ellipsis, Name, BitOr, Subscript, Str, Ellipsis, Str, Set, BinOp, BinOp, Str, BitOr, Tuple, Str, Name, Str, BitOr, Name]
      self._validate_AST(self.import_from, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.import_from, root, 
            self.class_base + 
            self._call(Tuple, self._call(Str), 
               self._call(Set,
                  self._call(Tuple, 
                     self._call(self._call(List, self._call(Str))), 
                     Str),
                  self._call(self._call(Str))), 
               self._call(Str), 
               self._call(Set, self._call(Str), 
                 self._call(Tuple, self._call(Str), Str, self._call(Str)), Str), 
              finish=True))

      grammar = self.importer.from_string(self.import_from, "import_from")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["from", "import", ".", "*", "(", ")"]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 8 + 1)
      self.assertTrue(set(grammar["import_from"]) == set([
         ("from","import_from#1", "import", "import_from#6"),
         ]))
      self.assertTrue(set(grammar["import_from#1"]) == set([
         ("import_from#2",),
         ("import_from#5",),
         ]))
      self.assertTrue(set(grammar["import_from#2"]) == set([
         ("import_from#3", "dotted_name"),
         ]))
      self.assertTrue(set(grammar["import_from#3"]) == set([
         ("import_from#4", "import_from#3"),
         ("import_from#4", ),
         ]))
      self.assertTrue(set(grammar["import_from#4"]) == set([
         (".",),
         (grammar.EMPTY,),
         ]))
      self.assertTrue(set(grammar["import_from#5"]) == set([
         (".", "import_from#5"),
         (".",),
         ]))
      self.assertTrue(set(grammar["import_from#6"]) == set([
         ("*",),
         ("import_from#7",),
         ("import_as_names",),
         ]))
      self.assertTrue(set(grammar["import_from#7"]) == set([
         ("(", "import_as_names", ")"),
         ]))

   def test_optional_repeated_choices_in_rule(self):
      "term = factor, [{'*' | '/' | '%' | '//'}, factor][...]"
      root = parse(self.term)
      class_args = [Tuple, Name, Subscript, List, Set, BinOp, BinOp, BinOp, Str, BitOr, Str, BitOr, Str, BitOr, Str, Name, Ellipsis]
      self._validate_AST(self.term, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.term, root, self.class_base + self._call(Tuple, Str, self._call(self._call(List, self._call(Set, self._call(Str), self._call(Str), self._call(Str), self._call(Str)), Str)), finish=True))

      grammar = self.importer.from_string(self.term, "term")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["*", "/", "%", "//"]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 4 + 1)
      self.assertTrue(set(grammar["term"]) == set([
         ("factor","term#1"),
         ]))
      self.assertTrue(set(grammar["term#1"]) == set([
         ("term#2","term#1"),
         ("term#2",),
         ]))
      self.assertTrue(set(grammar["term#2"]) == set([
         ("term#3", "factor"),
         (grammar.EMPTY,),
         ]))
      self.assertTrue(set(grammar["term#3"]) == set([
         ("*",),
         ("/",),
         ("%",),
         ("//",),
         ]))

   def test_choice_in_choice(self):
      "expr_stmt = testlist, {augassign, {yield_expr | testlist} | ['=', {yield_expr | testlist}][...]}"
      root = parse(self.expr_stmt)
      class_args = [Tuple, Name, Set, Name, BinOp, Set, BinOp, Name, BitOr, Name, BitOr, Subscript, List, Str, Set, BinOp, Name, BitOr, Name, Ellipsis]
      self._validate_AST(self.expr_stmt, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.expr_stmt, root, self.class_base + self._call(Tuple, Str, self._call(Set, self._call(Tuple, Str, self._call(Set, Str, Str)), self._call(self._call(List, self._call(Str), self._call(Set, Str, Str)))), finish=True))

      grammar = self.importer.from_string(self.expr_stmt, "expr_stmt")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["="]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 7 + 1)
      self.assertTrue(set(grammar["expr_stmt"]) == set([
         ("testlist","expr_stmt#1"),
         ]))
      self.assertTrue(set(grammar["expr_stmt#1"]) == set([
         ("expr_stmt#2",),
         ("expr_stmt#4",),
         ]))
      self.assertTrue(set(grammar["expr_stmt#2"]) == set([
         ("augassign","expr_stmt#3"),
         ]))
      self.assertTrue(set(grammar["expr_stmt#3"]) == set([
         ("yield_expr",),
         ("testlist",),
         ]))
      self.assertTrue(set(grammar["expr_stmt#4"]) == set([
         ("expr_stmt#5", "expr_stmt#4"),
         ("expr_stmt#5", ),
         ]))
      self.assertTrue(set(grammar["expr_stmt#5"]) == set([
         ("=", "expr_stmt#6"),
         (grammar.EMPTY,),
         ]))
      self.assertTrue(set(grammar["expr_stmt#6"]) == set([
         ("yield_expr",),
         ("testlist",),
         ]))

   def test_terminal_uppercase_repeated_AST(self):
      "s = STRING[...]"
      root = parse(self.terminal_uppercase_repeated)
      class_args = [Subscript, Name, Ellipsis]
      self._validate_AST(self.terminal_uppercase_repeated, root, self.class_base + class_args)
      
      root = self.transformer.visit(root)
      self._validate_AST(self.terminal_uppercase_repeated, root, self.class_base + self._call(self._call(Str), finish=True))

      grammar = self.importer.from_string(self.terminal_uppercase_repeated, "s")
      
      self.assertTrue(set(grammar.iter_on_all_symbols()) - set(grammar.iter_nonterminals()) == set(["STRING"]))
      self.assertTrue(len(list(grammar.iter_nonterminals())) == 1 + 1)
      self.assertTrue(set(grammar["s"]) == set([("STRING","s"),("STRING",)]))

if __name__ == '__main__':
   unittest.main()
