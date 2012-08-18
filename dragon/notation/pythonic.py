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
      '''Interprets literals strings like "foo" or 'bar' as terminals. The 
         meaning of the terminal is given by the lexer, so ":" can significate 
         a colon ":" or anything else.

         Empty strings are not allowed.
         '''
      if not node.s:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '' expression. Literal strings must be non-empty.")
      
      return NotationASTTransformer.__parsed_terminal

   def transform_Name_to_Str(self, elts):
      for node, i in zip(elts, range(len(elts))):
         if isinstance(node, Name):
            elts[i] = Str(node.id)
            if not node.id.isupper():
               elts[i]._already_process = True #it's the name of other rule, and it's NOT the name of a terminal like 'NAME' 


   @_visit_decorator
   def visit_Tuple(self, node):
      '''Interprets a tuple (a, b, c) like an expression (rule) 
         'a' follow by 'b' and then, follow by 'c'. 

         Empty tuples are not allowed.
         '''
      if not node.elts:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '()' expression. A empty 'rule' is not allowed.")

      self.transform_Name_to_Str(node.elts)
      return NotationASTTransformer.__parsed_rule
      
   @_visit_decorator
   def visit_List(self, node):
      '''Interprets a list [a, b, c] like an expression (rule) 
         'a' follow by 'b' and then, follow by 'c' that is optional.
         This means that the parser can expect "abc" or the empty string.

         Empty lists are not allowed.
         '''
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
      '''Interprets a the sequence a | b | c like a set of alternative 
         expresions 'a' or 'b' or 'c'.
         But this is only allowed if the operator | is inside of a set
         { } expression (a 'choice' expression)
         '''

      if isinstance(node.op, BitOr):
         raise NotationASTTransformer.ParserASTError(node, "Invalid '|' expression. The | operator must be between { }, in a 'choice' expression.")

      return node

   def visit_Lambda(self, node):
      node._already_process = True
      return node
   
   def visit_UnaryOp(self, node):
      if not isinstance(node.op, Invert):
         raise NotationASTTransformer.ParserASTError(node, "Invalid unary operator. The only operator valid is '~' to mark semantic actions.")

      node.operand._already_process = True
      return node.operand


   @_visit_decorator
   def visit_Set(self, node):
      '''Interprets a the sequence {a | b | c} like a set of alternative 
         expresions 'a' or 'b' or 'c' (choices)

         The expression can not be an empty {} or a singleton {a} choice.
         '''
      if not node.elts:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '{}' expression. A empty 'choices' is not allowed.")
      
      node.elts = self._split_set_elts(node.elts)
      if len(node.elts) == 1:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '{A}' expression. A 'choices' with only one alternative is not allowed.")
      
      self.transform_Name_to_Str(node.elts)
      return NotationASTTransformer.__parsed_choice

   def visit_Dict(self, node):
      '''The expression can not be an empty {} choice.
         The 'dict' expressions like {a:b, c:d} are not allowed.
         '''
      if hasattr(node, '_already_process'): return node
      if not node.keys:
         raise NotationASTTransformer.ParserASTError(node, "Invalid '{}' expression. A empty 'choices' is not allowed.")
      else:
         raise NotationASTTransformer.ParserASTError(node, "Dict expressions '{A:b, C:d}' are not allowed.")

   
   @_visit_decorator
   def visit_Subscript(self, node):
      '''Only the expression [...] is allowed, meaning that the previous 
         expression can be repeated one or more times.
         That is, A[...] can be A, AA, AAA, A...A and 
                  [A][...] can be A, AA, AAA, A...A or the empty string.

         Other 'subscript' like [1], [1:2] or [1:2:3] are not allowed.
         '''
      if not isinstance(node.slice, Ellipsis):
         raise NotationASTTransformer.ParserASTError(node, "The only expression valid use the subscript '[...]'. Other subscripts are allowed. ")
      
      if isinstance(node.value, Name):
         elts = [node.value]
         self.transform_Name_to_Str(elts)
         node.value = elts[0]

      return NotationASTTransformer.__parsed_repeat

   def visit_Assign(self, node):
      '''Interprets an assignament as a definition of a new nonterminal symbol.
         
         Only can be assigned rules, optionals, choices, nonterminals,
         terminals and repeated expressions.
         Valid:
            A = B, C       meaning  A := B follow by C
            A = [B, C]     meaning  A := B follow by C or the empty string
            A = {B | C}    meaning  A := B or C
            A = B          meaning  A := B (other nonterminal symbol)
            A = c          meaning  A := c (a terminal symbol)a
            A = B[...]     meaning  A := B one or more times

         It is not allowed multiples assignaments like A, B = C
         and in all the cases the name of the symbol (A in the case A=...)
         must be a valid name.
         '''
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


def _generate_grammar(ast_root, start_symbol, semantic_objets):
   transformer = NotationASTTransformer()
   root = transformer.visit(ast_root)
   
   notation = Syntax(start_symbol)

   fix_missing_locations(root)
   root = compile(root, '<string>', 'exec')
   ctx = {transformer.get_notation_object_name(): notation}
   ctx.update(semantic_objets)
   eval(root, ctx)
   return notation.as_grammar()


def from_string(string, start_symbol, **semantic_objets):
   root = parse(string)
   return _generate_grammar(root, start_symbol, semantic_objets)

def from_file(filename, start_symbol, **semantic_objets):
   with open(filename, 'r') as source:
      iomap = mmap.mmap(source.fileno(), length=0, access=mmap.ACCESS_READ)
      return from_string(iomap, start_symbol, semantic_objets)
