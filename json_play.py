import json
from pprint import pprint

with open('json_test.json') as f:
    j_test = json.load(f)

pprint(j_test)

