import pandas as pd

print(pd.to_numeric(['1', '2'], errors='raise'))  # ValueError: Unable to parse string "xyz" at position 2