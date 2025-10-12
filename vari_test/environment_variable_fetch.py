# $env:XXXX = "valore"  

import os
value = os.environ.get("XXXX")

print(f"Value of XXXX is: {value}") 