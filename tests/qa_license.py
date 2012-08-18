import unittest
import os.path as Path
import os


class QualityAssuranceLicense(unittest.TestCase):
   def setUp(self):
      self.count = 45  #The first N lines of each file to search the license
      self.basepath = Path.join(Path.dirname(__file__), "..")
      self.src_basepath = Path.join(self.basepath, "dragon")

      self.src_mark = '''
#########################################################################
#                                                                       #
#                        This work is licensed under a                  #
#   CC BY-SA        Creative Commons Attribution-ShareAlike             #
#                           3.0 Unported License.                       #
#                                                                       #
#########################################################################
'''.strip()
      
      self.src_as_is = '''
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
'''.strip()

   def test_license_file(self):
      self.assertTrue(Path.isfile(Path.join(self.basepath, "license.txt")))

   def _thrower(self, error):
      raise error

   def test_license_marks_in_python_modules(self):
      for dirpath, dirnames, filenames in os.walk(self.src_basepath, onerror=self._thrower):
         for filename in filenames:
            ext = Path.splitext(filename)[1]
            if ext == ".py":
               with open(Path.join(dirpath, filename), "rt") as source:
                  first_lines = []
                  count = self.count
                  for line in source:
                     first_lines.append(line)
                     count -= 1
                     if not count:
                        break

                  header = "".join(first_lines)
                  self.assertTrue(self.src_mark in header)

   def test_license_AS_IS_in_python_modules(self):
      for dirpath, dirnames, filenames in os.walk(self.src_basepath, onerror=self._thrower):
         for filename in filenames:
            ext = Path.splitext(filename)[1]
            if ext == ".py":
               with open(Path.join(dirpath, filename), "rt") as source:
                  first_lines = []
                  count = self.count
                  for line in source:
                     first_lines.append(line)
                     count -= 1
                     if not count:
                        break

                  header = "".join(first_lines)
                  self.assertTrue(self.src_as_is in header)

if __name__ == '__main__':
   unittest.main()
