# run ./bin/fsub {"workload": "fsub-haskell", "strategy": "HedgehogCBC", "property": "prop_SinglePreserve", "timeout": 5.0}
# parse JSON line result
# Loop until we find a line where "counterexample" is empty

import json
import os

for i in range(1000):
    result = os.popen(
        './bin/fsub \'{"workload": "fsub-haskell", "strategy": "HedgehogCBC", "property": "prop_SinglePreserve", "timeout": 5.0}\''
    ).read()
    result = json.loads(result)
    print(f"Line {i + 1}: {result}")
    if not result.get("counterexample"):
        print(f"Found empty counterexample after {i + 1} lines: {result}")
        break
