
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
