#########################################################################
#                                                                       #
#                        This work is licensed under a                  #
#   CC BY-SA        Creative Commons Attribution-ShareAlike             #
#                           3.0 Unported License.                       #
#                                                                       #
#########################################################################

class Lexer(object):
   def tokenizer(self):
      '''Return a iterable or generator of all tokens.
         Each token is a tuple with at least one value, the terminal id. 
         The next values, if any, are the attributes of the token.'''
      raise NotImplementedError


class Driver(object):
   def parse(self, lexer):
      raise NotImplementedError


   class UnexpectedToken(Exception):
      def __init__(self, token_readed, expecteds):
         Exception.__init__(self)
         self.msg = "Unexpected token of type '%s' and value '%s'.\
\nExpected {  %s  } types of tokens." % (
      token_readed[0], 
      token_readed[1], 
      " ".join("'%s'" % e for e in expecteds))

      def __str__(self):
         return self.msg
