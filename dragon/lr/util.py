'''This module contains some useful functions used by the generator 
   of LR parser.'''
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
def closure(kernel_items, grammar):
   '''Returns the set of items that represent the same position in the grammar.
      
      That is, for each given item A -> ab*B, collect all items B -> *cd
      and return them union with the initial items.
      
      This means that the item A -> ab*B is equivalent to B -> *cd.
      
      Precondition: the kernel_items are expected to be a iterable of items 
      of the form A -> a*b where 'a' is a symbol, terminal or nonterminal and 
      'b' is another symbol and that may exist or not.'''
   to_process = set(kernel_items)
   finished = set()

   while to_process:
      item = to_process.pop()
      finished.add(item)

      next_items = set(item.next_items(grammar))
      news = next_items - finished
      to_process.update(news)

   return frozenset(finished)


def goto(items, symbol, grammar, only_kernel = False):
   '''For each given item A -> a*Bb, collect all items A -> aB*b where 
      B == 'symbol'.
      Then return the closure of the collected set.'''
   to_process = frozenset([i.item_shifted(grammar) for i in items 
                                       if i.next_symbol(grammar) == symbol])
   return closure(to_process, grammar) if not only_kernel else to_process


def canonical_collection(grammar, start_item):
   '''The collection represents a collections of 'states' of the parser where
      each 'state' is a set of items.
      The algorithm starts from an item 'seed' and builds all of the rest of 
      sets.
   '''
   start_set = frozenset([start_item])
   collection = set()
   to_process = list()
   to_process.append(closure(start_set, grammar))

   while to_process:
      _set = to_process.pop()
      for symbol in grammar.iter_on_all_symbols():
         next_set = goto(_set, symbol, grammar)
         if next_set and next_set not in collection:
            to_process.append(next_set)

      collection.add(_set)

   return frozenset(collection)

def kernel_collection(grammar, start_item):
   '''Similar to 'canonical_collection' except that the returned collection 
      is made of kernels items. 
      All the nonkernel items are removed to improve the memory consume.
      '''
   start_set = frozenset([start_item])
   collection = set()
   to_process = list()
   to_process.append(start_set)

   while to_process:
      kernel_set = to_process.pop()
      _set = closure(kernel_set, grammar)
      for symbol in grammar.iter_on_all_symbols():
         next_set = goto(_set, symbol, grammar, only_kernel=True)
         if next_set and next_set not in collection:
            to_process.append(next_set)

      collection.add(kernel_set)

   return frozenset(collection)


