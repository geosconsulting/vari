# $env:XXXX = "valore"  

import os
value = os.environ.get("TEMP")

print(f"Value of TEMP is: {value}") 