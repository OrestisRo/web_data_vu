import json

f = open('output.txt', 'r')
results = json.loads(f)

for r in results:
	print r
	raw_input()