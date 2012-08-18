'''Each module in this package should contain at least two functions:
   
      from_file(filename, start_symbol) -> None
      from_string(string, start_symbol) -> None

   The first open 'filename' and builds a Grammar object from it.
   The second builds a Grammar from 'string'.
   In both cases, the 'start_symbol' is specified and should yield equivalent
   results.

   As a tip, the file version can be implemented in this manner:

      import mmap
      def from(filename, start_symbol):
         with open(filename, 'r') as source:
            iomap_string = mmap.mmap(source.fileno(), length=0, access=mmap.ACCESS_READ)
            return from_string(iomap_string, start_symbol)
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
