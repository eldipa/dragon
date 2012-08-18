from ast import *
from parser import ParserError
from copy import deepcopy
from dragon.grammar import Grammar
from dragon.syntax import Syntax
import mmap

def _visit_decorator(visit_func):
   def wrapper(self, node):
      if hasattr(node, '_already_process'): 
         self.generic_visit(node)
         return node
      call_node = deepcopy(visit_func(self, node).body)
      node._already_process = True
      call_node.args[0] = node if not isinstance(node, Subscript) else node.value
      
      if hasattr(node, 'production_name'):
         call_node.args[1] = node.production_name
         self._hint_name = str(node.production_name.s)
         self._counter = 0
      elif not isinstance(node, (Str, Name)):
         call_node.args[1] = Str(s=self._generate_name())
      else:
         call_node.args[1] = Str(s=self._last_generate_name())
      
      call_node.args[1]._already_process = True

      
      call_node = copy_location(call_node, node)
      self.generic_visit(call_node)

      return call_node

   return wrapper



class NotationASTTransformer(NodeTransformer):
   
   class ParserASTError(ParserError):
      def __init__(self, node, argument):
         ParserError.__init__(self, "(Line %i, Col %i) " % (node.lineno, node.col_offset) + argument)
   
   __filename_parsed_expression = '<string>'
   __notation_object = 'Syntax'
   __parsed_terminal = parse(__notation_object + ".terminal((1,), None)", __filename_parsed_expression, mode='eval')
   __parsed_rule = parse(__notation_object + ".rule((1,), None)", __filename_parsed_expression, mode='eval')
   __parsed_optional = parse(__notation_object + ".optional((1,), None)", __filename_parsed_expression, mode='eval')
   __parsed_choice = parse(__notation_object + ".choice((1,), None)", __filename_parsed_expression, mode='eval')
   __parsed_repeat = parse(__notation_object + ".repeat((1,), None)", __filename_parsed_expression, mode='eval')
   __parsed_tuple = parse("(1,)", __filename_parsed_expression, mode='eval')

   def __init__(self):
      self._production_name = None
      self._hint_name = ""
      self._counter = 0

   def _generate_name(self):
      assert self._hint_name and "The 'hint name' must no be null."
      self._counter += 1
      return str(self._hint_name) + "#" + str(self._counter)
   
   def _last_generate_name(self):
      assert self._hint_name and "The 'hint name' must no be null."
      return str(self._hint_name) + "#" + str(self._counter)

   def get_notation_object_name(self):
      return NotationASTTransformer.__notation_object

   @_visit_decorator
   def visit_Str(self, node):
      if not node.s:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '' expression. Literal strings must be non-empty.")
      
      return NotationASTTransformer.__parsed_terminal

   def transform_Name_to_Str(self, elts):
      for node, i in zip(elts, range(len(elts))):
         if isinstance(node, Name):
            elts[i] = Str(node.id)
            if not node.id.isupper():
               elts[i]._already_process = True #it's the name of other rule, and it's NOT the name od a terminal like 'NAME' 


   @_visit_decorator
   def visit_Tuple(self, node):
      if not node.elts:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '()' expression. A empty 'rule' is not allowed.")

      self.transform_Name_to_Str(node.elts)
      return NotationASTTransformer.__parsed_rule
      
   @_visit_decorator
   def visit_List(self, node):
      if not node.elts:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '[]' expression. A empty 'optional' is not allowed.")

      self.transform_Name_to_Str(node.elts)
      return NotationASTTransformer.__parsed_optional

   def _collapse(self, node):
      if isinstance(node.left, BinOp) and isinstance(node.left.op, BitOr):
         left = self._collapse(node.left)
      else:
         left = [node.left]
      
      if isinstance(node.right, BinOp) and isinstance(node.right.op, BitOr):
         right = self._collapse(node.right)
      else:
         right = [node.right]

      result = []
      result.extend(left)
      result.append(node.op)
      result.extend(right)
      return result

      
   def _split_set_elts(self, elts):
      collapsed = []
      for element in elts:
         if isinstance(element, BinOp) and isinstance(element.op, BitOr):
            collapsed.extend(self._collapse(element))
         else:
            collapsed.append(element)

      last_choice = []
      choices = [last_choice]
      for element in collapsed:
         if isinstance(element, BitOr):
            last_choice = []
            choices.append(last_choice)
         else:
            last_choice.append(element)

      splitted = []
      for choice in choices:
         if len(choice) > 1:
            splitted.append(Tuple(choice, Load()))
         else:
            splitted.append(choice[0])
 
      return splitted


   def visit_BinOp(self, node):
      if isinstance(node.op, BitOr):
         raise NotationASTTransformer.ParserASTError(node, "Invalid '|' expression. The | operator must be between { }, in a 'choice' expression.")

      return node

   def visit_Lambda(self, node):
      node._already_process = True
      return node
   
   def visit_UnaryOp(self, node):
      if not isinstance(node.op, Invert):
         raise NotationASTTransformer.ParserASTError(node, "Invalid unary operator. The only operator valid is '!' to mark semantic actions.")

      node.operand._already_process = True
      return node.operand


   @_visit_decorator
   def visit_Set(self, node):
      if not node.elts:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '{}' expression. A empty 'choices' is not allowed.")
      
      node.elts = self._split_set_elts(node.elts)
      if len(node.elts) == 1:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '{A}' expression. A 'choices' with only one alternative is not allowed.")
      
      self.transform_Name_to_Str(node.elts)
      return NotationASTTransformer.__parsed_choice

   def visit_Dict(self, node):
      if hasattr(node, '_already_process'): return node
      if not node.keys:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '{}' expression. A empty 'choices' is not allowed.")
      else:
         raise NotationASTTransformer.ParserASTError(node, "Dict expressions '{A:b, C:d}' are not allowed.")

   
   @_visit_decorator
   def visit_Subscript(self, node):
      if not isinstance(node.slice, Ellipsis):
         raise NotationASTTransformer.ParserASTError(node, "The only expression valid use the subscript '[...]'. Other subscripts are allowed. ")
      
      if isinstance(node.value, Name):
         elts = [node.value]
         self.transform_Name_to_Str(elts)
         node.value = elts[0]

      return NotationASTTransformer.__parsed_repeat

   def visit_Assign(self, node):
      if len(node.targets) != 1 or not isinstance(node.targets[0], Name):
         raise NotationASTTransformer.ParserASTError(node, "Only one assign 'A = ...' is allowed and 'A' must be a variable with a valid name.")

      # We allow 'Dict' to handle better error messages.
      if not isinstance(node.value, (Tuple, List, Set, Name, Str, Subscript, Dict)):
         raise NotationASTTransformer.ParserASTError(node, "The value to assign is invalid. The 'rule', 'optional', 'choices', 'repeated', a variable name and a literal string are allowes.")

      if isinstance(node.value, (Name, Str)):
         new_node = deepcopy(NotationASTTransformer.__parsed_tuple.body)
         new_node.elts[0] = node.value
         node.value = new_node

      node.value.production_name = Str(node.targets[0].id)
      node.value.production_name._already_process = True
      node.targets[0]._already_process = True
      self.generic_visit(node)
      
      return node


def _generate_grammar(ast_root, start_symbol):
   transformer = NotationASTTransformer()
   root = transformer.visit(ast_root)
   
   notation = Syntax(start_symbol)

   fix_missing_locations(root)
   root = compile(root, '<string>', 'exec')
   eval(root, {transformer.get_notation_object_name(): notation})
   return notation.as_grammar()



def from_string(string, start_symbol):
   root = parse(string)
   return _generate_grammar(root, start_symbol)

def from_file(filename, start_symbol):
   with open(filename, 'r') as source:
      iomap = mmap.mmap(source.fileno(), length=0, access=mmap.ACCESS_READ)
      return from_string(iomap, start_symbol)
