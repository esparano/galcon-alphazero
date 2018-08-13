These are scripts for testing training data output in Galcon. test.lua saves some JSON data to g2.data whenever the "ADD" button is pressed. The Python script testReader.py, when run, constantly polls g2.data and, whenever g2.data is updated, copies the contents of g2.data and appends them to a log file that it creates in a configurable location.

On Windows 10, the non-Steam (standalone .exe) version of Galcon 2 saves the contents of g2.data to 
C:\Users\{Username}\AppData\Roaming\Galcon 2\{mod name}.bin
as a plain JSON string.
