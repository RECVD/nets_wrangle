import json
from pprint import pprint

with open('json_test.json') as f:
    j_test = json.load(f)

def classify_business(business_code, business_code2, business_name):
    for key, _ in j_test:
        if (business_code in j_test[key]['business_code'] or
                    business_code2 in j_test[key]['business_code2'] or
                    business_name in j_test[key]['business_name']):
            break
        else:
            continue
    return key



pprint(j_test)

