'''This module contains two interfaces, Lexer and Driver and these contain
   documentation only. 
   Python is a dynamic language so its not necessary inherit from these 
   classes.
   However it is required that your classes have the same interface.
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
class Lexer(object):
   '''See the tokenizer method.'''
   def tokenizer(self):
      '''Return a iterable or generator of all tokens.
         Each token is a tuple with at least one value, the terminal id. 
         The next values, if any, are the attributes of the token.'''
      raise NotImplementedError


class Driver(object):
   '''See the parse method.'''
   def parse(self, lexer):
      '''This will extract tokens from the lexer and try to parse the input.
         The lexer must implement the Lexer interface.'''
      for _dummy in self.parse_by_step(lexer):
         pass

   def parse_by_step(self, lexer):
      '''This will extract tokens from the lexer and try to parse the input.
         The lexer must implement the Lexer interface.
         
         The implementation must be a generator, so the parse process is
         realized step by step. 
         The objects yielded in each iteration is defined by the implementer.
         '''
      raise NotImplementedError

   class UnexpectedToken(Exception):
      '''This exception will be raised by the Driver when an unexpected 
         token will be readed.
         The exception contains some basic data to guess what was wrong.
         The particular Driver implementation can include more specific
         data for even try to continue the parse.
         '''
      def __init__(self, token_readed, expecteds, additional_msg=""):
         Exception.__init__(self)
         self.msg = "Unexpected token of type '%s' and value '%s'.\
\nExpected {  %s  } types of tokens.\n%s" % (
      token_readed[0], 
      token_readed[1], 
      " ".join("'%s'" % e for e in expecteds), additional_msg)

      def __str__(self):
         return self.msg
